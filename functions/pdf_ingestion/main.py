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

        logger.info("========== RAW CLOUD EVENT ==========")

        logger.info(
            json.dumps(
                cloud_event.data,
                indent=2,
                default=str,
            )
        )

        event = parse_storage_event(cloud_event)


        bucket = event.bucket
        name = event.object_name
        generation = event.generation

        if not name.lower().endswith(".pdf"):
            logger.info("Skipping non-PDF object: %s", name)
            return

        logger.info(f"Parsed object_name: {name}")
        logger.info(f"CloudEvent ID   : {cloud_event['id']}")
        logger.info(f"CloudEvent Type : {cloud_event['type']}")
        logger.info(f"CloudEvent Src  : {cloud_event['source']}")

        # ------------------------------------------------------------------
        # STEP 4
        # ------------------------------------------------------------------

        logger.info("========== STEP 4 ==========")

        logger.info(
            json.dumps(
                {
                    "bucket": bucket,
                    "object": name,
                    "generation": generation,
                    "project_id": settings.project_id,
                    "region": settings.region,
                },
                indent=2,
            )
        )

        # ------------------------------------------------------------------
        # STEP 5
        # ------------------------------------------------------------------

        logger.info("========== STEP 5 ==========")
        logger.info("Downloading PDF from Cloud Storage")

        logger.info(f"Bucket from event : {bucket}")
        logger.info(f"Object from event : {name}")
        logger.info(f"repr(object)      : {repr(name)}")
        logger.info(f"Generation        : {generation}")

        local_file = get_temp_file_path(name)

        logger.info(f"Downloading to {local_file}")

        file_size = storage_service.download_blob(
            bucket_name=bucket,
            blob_name=name,
            generation=generation,
            destination_file=local_file,
        )

        if file_size is None:
            logger.warning(
                "Skipping stale CloudEvent because the object no longer exists."
            )
            return

        logger.info("Download completed.")

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
        # ------------------------------------------------------------------

        logger.info("========== STEP 6 ==========")

        logger.info("Processing PDF using Document AI")
        logger.info("Local file: %s", local_file)
        logger.info("Exists: %s", os.path.exists(local_file))
        logger.info("Size: %d", os.path.getsize(local_file))

        with open(local_file, "rb") as f:
            logger.info("Magic bytes: %s", f.read(16).hex())

        with open(local_file, "rb") as f:
            file_sha256 = hashlib.sha256(f.read()).hexdigest()
            logger.info("SHA256: %s", file_sha256)

        logger.info("Document AI processor name: %s", document_ai.processor_name)
        result = document_ai.process_file(local_file)

        logger.info("STEP 6 completed")
        logger.info("Document AI result type: %s", type(result))

        document = result.document
        has_document_layout = hasattr(document, "document_layout")

        logger.info("========== DOCUMENT SUMMARY ==========")
        logger.info(f"Document type: {type(document)}")
        logger.info("Pages: %d", len(document.pages))
        logger.info("Text length: %d", len(document.text or ""))
        logger.info(f"Has document_layout: {has_document_layout}")

        if document.pages:
            first_page = document.pages[0]

            logger.info(
                "First page dimensions: width=%s height=%s unit=%s",
                first_page.dimension.width,
                first_page.dimension.height,
                first_page.dimension.unit,
            )

        if has_document_layout:
            logger.info(
                "Number of layout blocks: %d",
                len(document.document_layout.blocks),
            )

            if document.document_layout.blocks:
                first_block = document.document_layout.blocks[0]

                if first_block.text_block:
                    logger.info(
                        "First block type: %s",
                        first_block.text_block.type_,
                    )
                    logger.info(
                        "First block text: %s",
                        first_block.text_block.text,
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
                "No layout blocks extracted; canonical JSON generation stopped."
            )

        # ------------------------------------------------------------------
        # STEP 8 - Canonical JSON
        # ------------------------------------------------------------------

        logger.info("========== STEP 8 ==========")
        logger.info("Building canonical document...")

        created_at = datetime.now(timezone.utc).isoformat().replace(
            "+00:00",
            "Z",
        )
        canonical_document = canonical_builder.build(
            document=document,
            blocks=blocks,
            filename=name,
            raw_bucket=bucket,
            raw_object=name,
            generation=generation,
            mime_type="application/pdf",
            created_at=created_at,
        )

        document_id = canonical_document["document"]["document_id"]
        page_count = canonical_document["document"]["page_count"]
        block_count = sum(
            len(page["blocks"])
            for page in canonical_document["pages"]
        )

        logger.info("Canonical JSON created.")
        logger.info("Pages: %d", page_count)
        logger.info("Blocks: %d", block_count)

        # ------------------------------------------------------------------
        # STEP 9 - Upload Canonical JSON
        # ------------------------------------------------------------------

        logger.info("========== STEP 9 ==========")
        logger.info("Uploading canonical JSON...")

        processed_object = f"processed/{document_id}.json"
        canonical_file = get_temp_file_path(f"{document_id}.json")

        with open(canonical_file, "w", encoding="utf-8") as f:
            json.dump(
                canonical_document,
                f,
                indent=2,
                ensure_ascii=False,
            )
            f.write("\n")

        storage_service.upload_blob(
            bucket_name=settings.processed_bucket,
            source_file=canonical_file,
            blob_name=processed_object,
            content_type="application/json",
        )

        document_uri = (
            f"gs://{settings.processed_bucket}/{processed_object}"
        )

        logger.info("Upload successful.")
        logger.info("Output URI: %s", document_uri)

        # ------------------------------------------------------------------
        # STEP 10 - Firestore Metadata
        # ------------------------------------------------------------------

        logger.info("========== STEP 10 ==========")
        logger.info("Writing Firestore metadata...")

        processing_duration_ms = int(
            (time.perf_counter() - start_time) * 1000
        )

        metadata = {
            "document_id": document_id,
            "filename": os.path.basename(name),
            "raw_bucket": bucket,
            "raw_object": name,
            "processed_bucket": settings.processed_bucket,
            "processed_object": processed_object,
            "page_count": page_count,
            "block_count": block_count,
            "status": "PUBLISHED",
            "processor": canonical_document["document"]["processor"],
            "created_at": created_at,
            "processing_duration_ms": processing_duration_ms,
            "document_uri": document_uri,
        }

        firestore_document = (
            firestore_metadata.write_processing_metadata(metadata)
        )

        logger.info("Firestore metadata written.")
        logger.info("Firestore document: %s", firestore_document)

        logger.info("========== STEP 11 ==========")
        logger.info("PIPELINE COMPLETED SUCCESSFULLY")

    except Exception:
        logger.exception("========== UNHANDLED EXCEPTION ==========")
        raise

    finally:
        if canonical_file:
            try:
                delete_file(canonical_file)
                logger.info(f"Temporary file removed: {canonical_file}")
            except Exception:
                logger.exception("Failed to delete temporary file.")

        if local_file:
            try:
                delete_file(local_file)
                logger.info(f"Temporary file removed: {local_file}")
            except Exception:
                logger.exception("Failed to delete temporary file.")
