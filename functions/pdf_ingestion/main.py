import json
import os
import hashlib
import time
from datetime import datetime, timezone

import functions_framework

from canonical_document_builder import CanonicalDocumentBuilder
from document_ai import DocumentAIService
from firestore_metadata import FirestoreMetadataService
from storage import StorageService
from logger import configure_logger
from event_parser import parse_storage_event
from config import load_settings
from utils import (
    get_temp_file_path,
    delete_file,
)
from document_processor import DocumentProcessor
from ingestion_coordinator import (
    IngestionCoordinator,
)
from google.protobuf.json_format import MessageToDict


settings = load_settings()

logger = configure_logger()


storage_service = StorageService(logger)

canonical_builder = CanonicalDocumentBuilder()

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

document_processor = DocumentProcessor(logger)

ingestion_coordinator = IngestionCoordinator(
    max_pages=settings.max_chunk_pages,
)


@functions_framework.cloud_event
def ingest_pdf(cloud_event):
    """
    Entry point for Cloud Functions Gen2.

    Trigger:
        Cloud Storage Object Finalized
    """

    print("===================================")
    print("FUNCTION STARTED")
    print(cloud_event.data)
    print("===================================")

    start_time = time.perf_counter()

    local_file = None
    canonical_file = None

    try:

        # ------------------------------------------------------------------
        # RAW EVENT
        # ------------------------------------------------------------------

        logger.info(
            "========== RAW CLOUD EVENT =========="
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

        if not name.lower().endswith(".pdf"):

            logger.info(
                "Skipping non-PDF object: %s",
                name,
            )

            return

        logger.info(
            "Parsed object_name: %s",
            name,
        )

        logger.info(
            "CloudEvent ID   : %s",
            cloud_event["id"],
        )

        logger.info(
            "CloudEvent Type : %s",
            cloud_event["type"],
        )

        logger.info(
            "CloudEvent Src  : %s",
            cloud_event["source"],
        )

        # ------------------------------------------------------------------
        # STEP 4
        # ------------------------------------------------------------------

        logger.info(
            "========== STEP 4 =========="
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
                },
                indent=2,
            )
        )

        # ------------------------------------------------------------------
        # STEP 5
        # ------------------------------------------------------------------

        logger.info(
            "========== STEP 5 =========="
        )

        logger.info(
            "Downloading PDF from Cloud Storage"
        )

        logger.info(
            "Bucket from event : %s",
            bucket,
        )

        logger.info(
            "Object from event : %s",
            name,
        )

        logger.info(
            "repr(object)      : %r",
            name,
        )

        logger.info(
            "Generation        : %s",
            generation,
        )

        local_file = get_temp_file_path(
            name
        )

        logger.info(
            "Downloading to %s",
            local_file,
        )

        file_size = storage_service.download_blob(
            bucket_name=bucket,
            blob_name=name,
            generation=generation,
            destination_file=local_file,
        )

        if file_size is None:

            logger.warning(
                "Skipping stale CloudEvent because "
                "the object no longer exists."
            )

            return

        logger.info(
            "Download completed."
        )

        logger.info(
            json.dumps(
                {
                    "local_file": local_file,
                    "file_size_bytes": file_size,
                },
                indent=2,
            )
        )

        # ------------------------------------------------------------------
        # STEP 6
        # Prepare PDF for Document AI
        # ------------------------------------------------------------------

        logger.info(
            "========== STEP 6 =========="
        )

        logger.info(
            "Preparing PDF for Document AI"
        )

        logger.info(
            "Local file: %s",
            local_file,
        )

        logger.info(
            "Exists: %s",
            os.path.exists(
                local_file
            ),
        )

        logger.info(
            "Size: %d",
            os.path.getsize(
                local_file
            ),
        )

        with open(
            local_file,
            "rb",
        ) as file:

            logger.info(
                "Magic bytes: %s",
                file.read(16).hex(),
            )

        with open(
            local_file,
            "rb",
        ) as file:

            file_sha256 = (
                hashlib.sha256(
                    file.read()
                ).hexdigest()
            )

        logger.info(
            "SHA256: %s",
            file_sha256,
        )

        # --------------------------------------------------------------
        # Phase 5.1.1
        # Inspect and split oversized PDFs.
        #
        # The coordinator returns:
        # - the original PDF when within max page limit
        # - multiple chunk PDFs when splitting is required
        # --------------------------------------------------------------

        prepared_files = (
            ingestion_coordinator.prepare(
                local_file
            )
        )

        logger.info(
            "PDF prepared into %d file(s)",
            len(prepared_files),
        )

        for prepared_file in prepared_files:

            logger.info(
                "Prepared file: %s",
                prepared_file,
            )

        # --------------------------------------------------------------
        # Phase 5.1.1 intentionally stops here for
        # multi-chunk PDFs.
        #
        # Phase 5.1.2 will wire:
        #
        # DocumentAIChunkProcessor
        #          +
        # DocumentAIChunkMerger
        #
        # so that all chunks become one original
        # document before canonical processing.
        # --------------------------------------------------------------

        if len(prepared_files) != 1:

            raise RuntimeError(
                "PDF was split into multiple chunks. "
                "Multi-chunk Document AI processing "
                "has not yet been wired into the "
                "production pipeline."
            )

        prepared_file = prepared_files[0]

        logger.info(
            "Processing prepared PDF using "
            "Document AI"
        )

        logger.info(
            "Document AI processor name: %s",
            document_ai.processor_name,
        )

        result = document_ai.process_file(
            prepared_file
        )

        logger.info(
            "STEP 6 completed"
        )

        logger.info(
            "Document AI result type: %s",
            type(result),
        )

        document = result.document

        # ------------------------------------------------------------------
        # DEBUG - Dump raw Document AI response
        # ------------------------------------------------------------------

        raw_doc = MessageToDict(
            document._pb
        )

        debug_file = (
            "/tmp/document_ai_raw.json"
        )

        with open(
            debug_file,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                raw_doc,
                file,
                indent=2,
                ensure_ascii=False,
            )

        storage_service.upload_blob(
            bucket_name=(
                settings.processed_bucket
            ),
            source_file=debug_file,
            blob_name=(
                "debug/document_ai_raw.json"
            ),
            content_type=(
                "application/json"
            ),
        )

        logger.info(
            "Raw Document AI JSON written "
            "to /tmp/document_ai_raw.json"
        )

        logger.info(
            "Top-level keys: %s",
            list(
                raw_doc.keys()
            ),
        )

        if "documentLayout" in raw_doc:

            logger.info(
                "documentLayout keys: %s",
                list(
                    raw_doc[
                        "documentLayout"
                    ].keys()
                ),
            )

        if document.pages:

            logger.info(
                "page proto type: %s",
                type(
                    document.pages[0]
                ),
            )

            page0 = MessageToDict(
                document.pages[0]._pb
            )

            logger.info(
                "Page0 JSON keys: %s",
                list(
                    page0.keys()
                ),
            )

            with open(
                "/tmp/page0_raw.json",
                "w",
                encoding="utf-8",
            ) as file:

                json.dump(
                    page0,
                    file,
                    indent=2,
                    ensure_ascii=False,
                )

            storage_service.upload_blob(
                bucket_name=(
                    settings.processed_bucket
                ),
                source_file=(
                    "/tmp/page0_raw.json"
                ),
                blob_name=(
                    "debug/page0_raw.json"
                ),
                content_type=(
                    "application/json"
                ),
            )

            logger.info(
                "Uploaded "
                "debug/page0_raw.json"
            )

        has_document_layout = hasattr(
            document,
            "document_layout",
        )

        logger.info(
            "========== DOCUMENT SUMMARY =========="
        )

        logger.info(
            "Document type: %s",
            type(document),
        )

        logger.info(
            "Pages: %d",
            len(document.pages),
        )

        logger.info(
            "Text length: %d",
            len(
                document.text
                or ""
            ),
        )

        logger.info(
            "Has document_layout: %s",
            has_document_layout,
        )

        if has_document_layout:

            logger.info(
                "Number of layout blocks: %d",
                len(
                    document
                    .document_layout
                    .blocks
                ),
            )

            if (
                document
                .document_layout
                .blocks
            ):

                first_block = (
                    document
                    .document_layout
                    .blocks[0]
                )

                if (
                    first_block.text_block
                ):

                    logger.info(
                        "First block type: %s",
                        first_block
                        .text_block
                        .type_,
                    )

                    logger.info(
                        "First block text: %s",
                        first_block
                        .text_block
                        .text,
                    )

        # ------------------------------------------------------------------
        # STEP 7 - Process Document AI Response
        # ------------------------------------------------------------------

        blocks = document_processor.process(
            document=document,
            result=result,
        )

        if not blocks:

            raise RuntimeError(
                "No layout blocks extracted; "
                "canonical JSON generation stopped."
            )

        # ------------------------------------------------------------------
        # STEP 8 - Canonical JSON
        # ------------------------------------------------------------------

        logger.info(
            "========== STEP 8 =========="
        )

        logger.info(
            "Building canonical document..."
        )

        created_at = (
            datetime.now(
                timezone.utc
            )
            .isoformat()
            .replace(
                "+00:00",
                "Z",
            )
        )

        canonical_document = (
            canonical_builder.build(
                blocks=blocks,
                page_count=(
                    document_processor
                    .page_count(
                        document
                    )
                ),
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

        document_id = (
            canonical_document[
                "document"
            ][
                "document_id"
            ]
        )

        page_count = (
            canonical_document[
                "document"
            ][
                "page_count"
            ]
        )

        block_count = sum(
            len(
                page["blocks"]
            )
            for page in (
                canonical_document[
                    "pages"
                ]
            )
        )

        logger.info(
            "Canonical JSON created."
        )

        logger.info(
            "Pages: %d",
            page_count,
        )

        logger.info(
            "Blocks: %d",
            block_count,
        )

        # ------------------------------------------------------------------
        # STEP 9 - Upload Canonical JSON
        # ------------------------------------------------------------------

        logger.info(
            "========== STEP 9 =========="
        )

        logger.info(
            "Uploading canonical JSON..."
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
        ) as file:

            json.dump(
                canonical_document,
                file,
                indent=2,
                ensure_ascii=False,
            )

            file.write("\n")

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
            f"gs://"
            f"{settings.processed_bucket}/"
            f"{processed_object}"
        )

        logger.info(
            "Upload successful."
        )

        logger.info(
            "Output URI: %s",
            document_uri,
        )

        # ------------------------------------------------------------------
        # STEP 10 - Firestore Metadata
        # ------------------------------------------------------------------

        logger.info(
            "========== STEP 10 =========="
        )

        logger.info(
            "Writing Firestore metadata..."
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
            "processed_bucket": (
                settings.processed_bucket
            ),
            "processed_object": (
                processed_object
            ),
            "page_count": page_count,
            "block_count": block_count,
            "status": "PUBLISHED",
            "processor": (
                canonical_document[
                    "document"
                ][
                    "processor"
                ]
            ),
            "created_at": created_at,
            "processing_duration_ms": (
                processing_duration_ms
            ),
            "document_uri": document_uri,
        }

        firestore_document = (
            firestore_metadata
            .write_processing_metadata(
                metadata
            )
        )

        logger.info(
            "Firestore metadata written."
        )

        logger.info(
            "Firestore document: %s",
            firestore_document,
        )

        logger.info(
            "========== STEP 11 =========="
        )

        logger.info(
            "PIPELINE COMPLETED SUCCESSFULLY"
        )

    except Exception:

        logger.exception(
            "========== UNHANDLED EXCEPTION =========="
        )

        raise

    finally:

        if canonical_file:

            try:

                delete_file(
                    canonical_file
                )

                logger.info(
                    "Temporary file removed: %s",
                    canonical_file,
                )

            except Exception:

                logger.exception(
                    "Failed to delete "
                    "temporary file."
                )

        if local_file:

            try:

                delete_file(
                    local_file
                )

                logger.info(
                    "Temporary file removed: %s",
                    local_file,
                )

            except Exception:

                logger.exception(
                    "Failed to delete "
                    "temporary file."
                )