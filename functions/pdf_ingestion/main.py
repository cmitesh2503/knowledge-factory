"""
Knowledge Factory PDF ingestion entry point.

Production flow
---------------

Cloud Storage PDF
        |
        v
Download to /tmp
        |
        v
Inspect PDF page count
        |
        +------------------------------+
        |                              |
        v                              v
Single PDF                     Split into chunks
        |                              |
        +--------------+---------------+
                       |
                       v
             Document AI per chunk
                       |
                       v
        Temporary Document AI JSON artifacts
                       |
                       v
             Merge Document AI chunks
                       |
                       v
       Provider-independent canonical blocks
                       |
                       v
              Visual figure enrichment
                       |
                       v
        Final Canonical Document JSON
                       |
                       +----------------------+
                       |                      |
                       v                      v
              Processed GCS bucket     KnowledgePackage
                                              |
                                              v
                                      Firestore
                                      knowledge_packages

Temporary provider-specific artifacts are used only
inside the function execution and are not persisted
to the processed bucket.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import time
from datetime import datetime, timezone
from pathlib import Path

import functions_framework

from canonical_document_builder import CanonicalDocumentBuilder
from chunk_processor import DocumentAIChunkProcessor
from config import load_settings
from extraction_quality import ExtractionQualityEvaluator
from pdf_text_extractor import PDFTextExtractor
from document_ai import DocumentAIService
from document_ai_artifact import save_document_ai_response
from document_ai_canonical_adapter import DocumentAICanonicalAdapter
from document_ai_merger import DocumentAIChunkMerger
from event_parser import parse_storage_event
from firestore_metadata import FirestoreMetadataService
from ingestion_coordinator import IngestionCoordinator
from logger import configure_logger
from storage import StorageService
from utils import (
    delete_file,
    get_temp_file_path,
)

from services.integration.knowledge_package_builder import (
    KnowledgePackageBuilder,
)
from services.integration.visual_figure_pipeline import (
    VisualFigurePipeline,
)
from services.repositories.firestore_knowledge_package_repository import (
    FirestoreKnowledgePackageRepository,
)


# ==============================================================
# APPLICATION CONFIGURATION
# ==============================================================

settings = load_settings()

logger = configure_logger()


# ==============================================================
# APPLICATION SERVICES
# ==============================================================

storage_service = StorageService(logger)

canonical_builder = CanonicalDocumentBuilder()
extraction_quality_evaluator = (
    ExtractionQualityEvaluator()
)

pdf_text_extractor = PDFTextExtractor()

firestore_metadata = FirestoreMetadataService(
    logger=logger,
    project_id=settings.project_id,
    database_name=settings.firestore_database,
)

document_ai = DocumentAIService(
    project_id=settings.project_id,
    location=settings.document_ai_location,
    processor_id=settings.document_ai_processor,
)

ingestion_coordinator = IngestionCoordinator(
    max_pages=settings.max_chunk_pages,
)

chunk_processor = DocumentAIChunkProcessor(
    document_ai=document_ai,
    max_pages=settings.max_chunk_pages,
)

document_ai_merger = DocumentAIChunkMerger()

canonical_adapter = DocumentAICanonicalAdapter()

knowledge_package_builder = KnowledgePackageBuilder()

visual_figure_pipeline = VisualFigurePipeline(
    logger=logger,
)

knowledge_package_repository = (
    FirestoreKnowledgePackageRepository()
)


# ==============================================================
# HELPER FUNCTIONS
# ==============================================================

def _utc_now() -> str:
    """
    Return current UTC time in ISO-8601 format.
    """

    return (
        datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _is_pdf(name: str) -> bool:
    """
    Determine whether an object name is a PDF.
    """

    return name.lower().endswith(".pdf")


def _should_skip_object(
    bucket: str,
    object_name: str,
) -> bool:
    """
    Ignore objects that must never enter ingestion.

    The Cloud Function is normally triggered only by
    the raw bucket, but this protection prevents future
    configuration mistakes or manually generated artifacts
    from being processed accidentally.
    """

    normalized_name = object_name.lstrip("/")

    ignored_prefixes = (
        "processed/",
        "debug/",
        "artifacts/",
        "chunks/",
        "tmp/",
        "temporary/",
    )

    if normalized_name.startswith(
        ignored_prefixes
    ):
        logger.info(
            "Skipping generated artifact: %s",
            object_name,
        )
        return True

    if not _is_pdf(object_name):
        logger.info(
            "Skipping non-PDF object: %s",
            object_name,
        )
        return True

    if bucket != settings.raw_bucket:
        logger.warning(
            "Skipping object from unexpected bucket. "
            "Expected=%s Actual=%s Object=%s",
            settings.raw_bucket,
            bucket,
            object_name,
        )
        return True

    return False


def _safe_delete(
    file_path: str | Path | None,
) -> None:
    """
    Delete a temporary file without masking the
    original processing error.
    """

    if not file_path:
        return

    path = Path(file_path)

    try:
        if path.exists() and path.is_file():
            delete_file(str(path))

            logger.info(
                "Temporary file removed: %s",
                path,
            )

    except Exception:

        logger.exception(
            "Failed to remove temporary file: %s",
            path,
        )


def _safe_remove_directory(
    directory: str | Path | None,
) -> None:
    """
    Remove a temporary directory recursively.
    """

    if not directory:
        return

    path = Path(directory)

    try:
        if path.exists() and path.is_dir():

            shutil.rmtree(
                path,
                ignore_errors=True,
            )

            logger.info(
                "Temporary directory removed: %s",
                path,
            )

    except Exception:

        logger.exception(
            "Failed to remove temporary directory: %s",
            path,
        )


def _canonical_block_count(
    canonical_document: dict,
) -> int:
    """Return the number of canonical page blocks."""

    return sum(
        len(
            page.get(
                "blocks",
                [],
            )
        )
        for page in canonical_document.get(
            "pages",
            [],
        )
    )


# ==============================================================
# CLOUD FUNCTION ENTRY POINT
# ==============================================================

@functions_framework.cloud_event
def ingest_pdf(cloud_event):
    """
    Production Knowledge Factory PDF ingestion pipeline.

    Trigger:
        Google Cloud Storage Object Finalized
    """

    start_time = time.perf_counter()

    local_file: str | None = None

    chunk_directory: Path | None = None

    artifact_directory: Path | None = None

    merged_file: Path | None = None

    canonical_file: str | None = None

    visual_figure_metadata = {
        "status": "not_run",
    }

    try:

        # ======================================================
        # STEP 1
        # RECEIVE EVENT
        # ======================================================

        logger.info(
            "========== KNOWLEDGE FACTORY INGESTION START =========="
        )

        logger.info(
            json.dumps(
                cloud_event.data,
                indent=2,
                default=str,
            )
        )

        event = parse_storage_event(
            cloud_event
        )

        bucket = event.bucket

        name = event.object_name

        generation = event.generation

        logger.info(
            "Event received."
        )

        logger.info(
            json.dumps(
                {
                    "bucket": bucket,
                    "object": name,
                    "generation": generation,
                    "project_id": (
                        settings.project_id
                    ),
                    "region": settings.region,
                    "max_chunk_pages": (
                        settings.max_chunk_pages
                    ),
                },
                indent=2,
            )
        )

        # ======================================================
        # STEP 2
        # FILTER EVENT
        # ======================================================

        if _should_skip_object(
            bucket=bucket,
            object_name=name,
        ):
            return

        # ======================================================
        # STEP 3
        # DOWNLOAD RAW PDF
        # ======================================================

        logger.info(
            "========== STEP 3: DOWNLOAD PDF =========="
        )

        local_file = get_temp_file_path(
            name
        )

        logger.info(
            "Downloading gs://%s/%s "
            "to %s",
            bucket,
            name,
            local_file,
        )

        file_size = (
            storage_service.download_blob(
                bucket_name=bucket,
                blob_name=name,
                generation=generation,
                destination_file=local_file,
            )
        )

        if file_size is None:

            logger.warning(
                "Skipping stale CloudEvent because "
                "the object no longer exists."
            )

            return

        logger.info(
            "Download completed. "
            "Size=%d bytes",
            file_size,
        )

        if not os.path.exists(
            local_file
        ):
            raise RuntimeError(
                "Downloaded PDF does not exist: "
                f"{local_file}"
            )

        # ======================================================
        # STEP 4
        # SOURCE DOCUMENT HASH
        # ======================================================

        with open(
            local_file,
            "rb",
        ) as source_file:

            file_sha256 = (
                hashlib.sha256(
                    source_file.read()
                ).hexdigest()
            )

        logger.info(
            "Source SHA256: %s",
            file_sha256,
        )

        # ======================================================
        # STEP 5
        # INSPECT AND SPLIT PDF
        # ======================================================

        logger.info(
            "========== STEP 5: PDF PREPARATION =========="
        )

        local_path = Path(
            local_file
        )

        chunk_directory = (
            local_path.parent
            / (
                f"{local_path.stem}"
                "_document_ai_chunks"
            )
        )

        chunk_paths = (
            ingestion_coordinator.prepare(
                file_path=local_path,
                output_dir=chunk_directory,
            )
        )

        if not chunk_paths:

            raise RuntimeError(
                "PDF preparation returned no chunks."
            )

        logger.info(
            "PDF prepared for Document AI."
        )

        logger.info(
            "Chunk count=%d "
            "Max pages per chunk=%d",
            len(chunk_paths),
            settings.max_chunk_pages,
        )

        for index, chunk_path in enumerate(
            chunk_paths,
            start=1,
        ):

            logger.info(
                "Chunk %d: %s",
                index,
                chunk_path,
            )

        # ======================================================
        # STEP 6
        # DOCUMENT AI PROCESSING
        # ======================================================

        logger.info(
            "========== STEP 6: DOCUMENT AI =========="
        )

        logger.info(
            "Document AI processor: %s",
            document_ai.processor_name,
        )

        chunk_results = (
            chunk_processor.process(
                chunk_paths
            )
        )

        if not chunk_results:

            raise RuntimeError(
                "Document AI returned no chunk results."
            )

        logger.info(
            "Document AI completed for %d chunk(s).",
            len(chunk_results),
        )

        # ======================================================
        # STEP 7
        # TEMPORARY DOCUMENT AI ARTIFACTS
        # ======================================================

        logger.info(
            "========== STEP 7: SAVE TEMPORARY CHUNK ARTIFACTS =========="
        )

        artifact_directory = (
            local_path.parent
            / (
                f"{local_path.stem}"
                "_document_ai_artifacts"
            )
        )

        artifact_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        chunk_artifact_files: list[
            Path
        ] = []

        for chunk_result in chunk_results:

            artifact_file = (
                artifact_directory
                / (
                    "chunk_"
                    f"{chunk_result.chunk_index:03d}"
                    ".json"
                )
            )

            save_document_ai_response(
                response=(
                    chunk_result
                    .document_ai_result
                ),
                output_file=artifact_file,
            )

            chunk_artifact_files.append(
                artifact_file
            )

            logger.info(
                "Saved temporary Document AI artifact. "
                "Chunk=%d Pages=%d-%d File=%s",
                chunk_result.chunk_index,
                chunk_result.start_page,
                chunk_result.end_page,
                artifact_file,
            )

        # ======================================================
        # STEP 8
        # MERGE DOCUMENT AI CHUNKS
        # ======================================================

        logger.info(
            "========== STEP 8: MERGE DOCUMENT AI CHUNKS =========="
        )

        merged_file = (
            artifact_directory
            / "merged_document_ai.json"
        )

        document_ai_merger.merge(
            chunk_files=chunk_artifact_files,
            output_file=merged_file,
        )

        logger.info(
            "Document AI chunks merged: %s",
            merged_file,
        )


        # ======================================================
        # STEP 9
        # DOCUMENT AI -> CANONICAL BLOCKS
        # ======================================================

        logger.info(
            "========== STEP 9: CANONICAL BLOCK ADAPTER =========="
        )

        merged_document_ai_json = (
            canonical_adapter.load(
                merged_file
            )
        )

        blocks = (
            canonical_adapter.extract_blocks(
                merged_document_ai_json
            )
        )

        page_count = (
            canonical_adapter.page_count(
                merged_document_ai_json
            )
        )

        # ======================================================
        # STEP 9A
        # EVALUATE DOCUMENT AI EXTRACTION QUALITY
        # ======================================================

        logger.info(
            "========== STEP 9A: EXTRACTION QUALITY CHECK =========="
        )

        document_ai_quality = (
            extraction_quality_evaluator.evaluate(
                blocks=blocks,
                page_count=page_count,
            )
        )

        logger.info(
            "Document AI extraction quality. "
            "Acceptable=%s "
            "Pages=%d "
            "Blocks=%d "
            "PagesWithContent=%d "
            "CoverageRatio=%.3f "
            "Characters=%d "
            "AverageCharactersPerPage=%.1f "
            "Reason=%s",
            document_ai_quality.is_acceptable,
            document_ai_quality.page_count,
            document_ai_quality.block_count,
            document_ai_quality.pages_with_content,
            document_ai_quality.coverage_ratio,
            document_ai_quality.total_characters,
            document_ai_quality.average_characters_per_page,
            document_ai_quality.reason,
        )

        # ======================================================
        # STEP 9B
        # FALL BACK TO NATIVE PDF TEXT EXTRACTION
        # ======================================================

        if not document_ai_quality.is_acceptable:

            logger.warning(
                "Document AI extraction quality is insufficient. "
                "Falling back to native PDF text extraction."
            )

            fallback_blocks = (
                pdf_text_extractor.extract_blocks(
                    local_path
                )
            )

            fallback_page_count = (
                pdf_text_extractor.page_count(
                    local_path
                )
            )

            fallback_quality = (
                extraction_quality_evaluator.evaluate(
                    blocks=fallback_blocks,
                    page_count=fallback_page_count,
                )
            )

            logger.info(
                "Native PDF extraction quality. "
                "Acceptable=%s "
                "Pages=%d "
                "Blocks=%d "
                "PagesWithContent=%d "
                "CoverageRatio=%.3f "
                "Characters=%d "
                "AverageCharactersPerPage=%.1f "
                "Reason=%s",
                fallback_quality.is_acceptable,
                fallback_quality.page_count,
                fallback_quality.block_count,
                fallback_quality.pages_with_content,
                fallback_quality.coverage_ratio,
                fallback_quality.total_characters,
                fallback_quality.average_characters_per_page,
                fallback_quality.reason,
            )

            if not fallback_quality.is_acceptable:

                raise RuntimeError(
                    "Document extraction failed quality validation. "
                    "Document AI reason="
                    f"{document_ai_quality.reason}; "
                    "Native PDF reason="
                    f"{fallback_quality.reason}"
                )

            blocks = fallback_blocks
            page_count = fallback_page_count

            logger.warning(
                "Using native PDF text extraction as the "
                "canonical block source."
            )

        else:

            logger.info(
                "Using Document AI extraction as the "
                "canonical block source."
            )


        logger.info(
            "Final canonical block source selected. "
            "Pages=%d Blocks=%d",
            page_count,
            len(blocks),
        )

        # ======================================================
        # STEP 10
        # BUILD CANONICAL DOCUMENT
        # ======================================================

        logger.info(
            "========== STEP 10: BUILD CANONICAL DOCUMENT =========="
        )

        created_at = _utc_now()

        canonical_document = (
            canonical_builder.build(
                blocks=blocks,
                page_count=page_count,
                filename=name,
                raw_bucket=bucket,
                raw_object=name,
                generation=generation,
                mime_type=(
                    "application/pdf"
                ),
                created_at=created_at,
            )
        )

        document_metadata = (
            canonical_document.get(
                "document",
                {},
            )
        )

        document_id = (
            document_metadata.get(
                "document_id"
            )
        )

        if not document_id:

            raise RuntimeError(
                "Canonical document does not "
                "contain document_id."
            )

        canonical_page_count = int(
            document_metadata.get(
                "page_count",
                0,
            )
        )

        block_count = _canonical_block_count(
            canonical_document
        )

        logger.info(
            "Canonical document built. "
            "Document ID=%s Pages=%d Blocks=%d",
            document_id,
            canonical_page_count,
            block_count,
        )

        # ======================================================
        # STEP 11
        # VISUAL FIGURE PIPELINE
        # ======================================================

        logger.info(
            "========== STEP 11: VISUAL FIGURE PIPELINE =========="
        )

        try:
            visual_figure_result = (
                visual_figure_pipeline.run(
                    pdf_path=local_path,
                    canonical_document=(
                        canonical_document
                    ),
                )
            )

            visual_figure_metadata = {
                "status": "completed",
                **visual_figure_result.to_metadata(),
            }

            block_count = _canonical_block_count(
                canonical_document
            )

            logger.info(
                "Canonical document enriched with visual figures. "
                "Blocks=%d Metadata=%s",
                block_count,
                json.dumps(
                    visual_figure_metadata,
                    sort_keys=True,
                ),
            )

        except Exception as exc:

            visual_figure_metadata = {
                "status": "failed",
                "error": str(exc),
            }

            logger.exception(
                "Visual figure pipeline failed. "
                "Continuing without visual figure enrichment."
            )

        # ======================================================
        # STEP 12
        # UPLOAD FINAL CANONICAL JSON
        # ======================================================

        logger.info(
            "========== STEP 12: UPLOAD FINAL CANONICAL JSON =========="
        )

        processed_object = (
            f"processed/{document_id}.json"
        )

        canonical_file = (
            get_temp_file_path(
                f"{document_id}.json"
            )
        )

        with open(
            canonical_file,
            "w",
            encoding="utf-8",
        ) as output_file:

            json.dump(
                canonical_document,
                output_file,
                indent=2,
                ensure_ascii=False,
            )

            output_file.write(
                "\n"
            )

        storage_service.upload_blob(
            bucket_name=(
                settings.processed_bucket
            ),
            source_file=canonical_file,
            blob_name=processed_object,
            content_type=(
                "application/json"
            ),
        )

        document_uri = (
            "gs://"
            f"{settings.processed_bucket}"
            f"/{processed_object}"
        )

        logger.info(
            "Final canonical JSON uploaded: %s",
            document_uri,
        )

        # ======================================================
        # STEP 13
        # BUILD KNOWLEDGE PACKAGE
        # ======================================================

        logger.info(
            "========== STEP 13: BUILD KNOWLEDGE PACKAGE =========="
        )

        knowledge_package = (
            knowledge_package_builder.build(
                canonical_document
            )
        )

        if not knowledge_package.document_id:

            raise RuntimeError(
                "KnowledgePackage does not "
                "contain document_id."
            )

        if (
            knowledge_package.document_id
            != document_id
        ):

            raise RuntimeError(
                "KnowledgePackage document_id does "
                "not match canonical document_id."
            )

        logger.info(
            "KnowledgePackage built. "
            "Document ID=%s",
            knowledge_package.document_id,
        )

        # ======================================================
        # STEP 14
        # SAVE KNOWLEDGE PACKAGE TO FIRESTORE
        # ======================================================

        logger.info(
            "========== STEP 14: SAVE KNOWLEDGE PACKAGE =========="
        )

        knowledge_package_repository.save(
            knowledge_package
        )

        logger.info(
            "KnowledgePackage saved to Firestore "
            "collection knowledge_packages. "
            "Document ID=%s",
            knowledge_package.document_id,
        )

        # ======================================================
        # STEP 15
        # WRITE PROCESSING METADATA
        # ======================================================

        logger.info(
            "========== STEP 15: FIRESTORE METADATA =========="
        )

        processing_duration_ms = int(
            (
                time.perf_counter()
                - start_time
            )
            * 1000
        )

        metadata = {
            "document_id": document_id,
            "filename": os.path.basename(
                name
            ),
            "raw_bucket": bucket,
            "raw_object": name,
            "generation": generation,
            "source_sha256": file_sha256,
            "processed_bucket": (
                settings.processed_bucket
            ),
            "processed_object": (
                processed_object
            ),
            "page_count": (
                canonical_page_count
            ),
            "block_count": block_count,
            "chunk_count": len(
                chunk_results
            ),
            "max_chunk_pages": (
                settings.max_chunk_pages
            ),
            "status": "PUBLISHED",
            "processor": (
                document_metadata.get(
                    "processor"
                )
            ),
            "created_at": created_at,
            "processing_duration_ms": (
                processing_duration_ms
            ),
            "document_uri": document_uri,
            "knowledge_package_document_id": (
                knowledge_package.document_id
            ),
            "visual_figure_pipeline": (
                visual_figure_metadata
            ),
        }

        firestore_document = (
            firestore_metadata
            .write_processing_metadata(
                metadata
            )
        )

        logger.info(
            "Processing metadata written. "
            "Firestore document=%s",
            firestore_document,
        )

        # ======================================================
        # SUCCESS
        # ======================================================

        total_duration_ms = int(
            (
                time.perf_counter()
                - start_time
            )
            * 1000
        )

        logger.info(
            "========== KNOWLEDGE FACTORY INGESTION COMPLETE =========="
        )

        logger.info(
            json.dumps(
                {
                    "status": "PUBLISHED",
                    "document_id": (
                        document_id
                    ),
                    "source_object": name,
                    "page_count": (
                        canonical_page_count
                    ),
                    "block_count": (
                        block_count
                    ),
                    "chunk_count": len(
                        chunk_results
                    ),
                    "processed_object": (
                        processed_object
                    ),
                    "visual_figure_pipeline": (
                        visual_figure_metadata
                    ),
                    "knowledge_package": (
                        knowledge_package
                        .document_id
                    ),
                    "duration_ms": (
                        total_duration_ms
                    ),
                },
                indent=2,
            )
        )

    except Exception:

        logger.exception(
            "Knowledge Factory PDF ingestion failed."
        )

        raise

    finally:

        # ======================================================
        # CLEANUP
        # ======================================================

        logger.info(
            "========== TEMPORARY FILE CLEANUP =========="
        )

        _safe_delete(
            canonical_file
        )

        _safe_delete(
            local_file
        )

        _safe_remove_directory(
            artifact_directory
        )

        # Only remove chunk directory when it
        # contains generated chunks.
        #
        # For a PDF below the page limit,
        # IngestionCoordinator returns the original
        # PDF and the directory may never be created.

        _safe_remove_directory(
            chunk_directory
        )

        logger.info(
            "Temporary cleanup completed."
        )
