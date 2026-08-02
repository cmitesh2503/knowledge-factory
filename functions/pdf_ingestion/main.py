import json
import logging
import os
import tempfile

import functions_framework
from google.cloud import documentai
from google.cloud import storage

logging.basicConfig(level=logging.INFO)

storage_client = storage.Client()
documentai_client = documentai.DocumentProcessorServiceClient()


@functions_framework.cloud_event
def ingest_pdf(cloud_event):
    """
    Entry point for Cloud Functions Gen2.

    Trigger:
        Cloud Storage Object Finalized
    """

    local_file = None

    try:
        # ------------------------------------------------------------------
        # RAW EVENT
        # ------------------------------------------------------------------

        logging.warning("========== RAW CLOUD EVENT ==========")
        logging.warning(str(cloud_event))

        data = cloud_event.data

        logging.warning("========== RAW DATA ==========")
        logging.warning(json.dumps(data, indent=2, default=str))

        logging.warning(f"type(data) = {type(data)}")
        logging.warning(f"keys = {list(data.keys())}")

        bucket = data.get("bucket")
        name = data.get("name")
        generation = data.get("generation")

        # ------------------------------------------------------------------
        # STEP 4
        # ------------------------------------------------------------------

        logging.warning("========== STEP 4 ==========")

        logging.warning(
            json.dumps(
                {
                    "bucket": bucket,
                    "object": name,
                    "generation": generation,
                    "project": os.getenv("PROJECT_ID"),
                    "region": os.getenv("REGION"),
                },
                indent=2,
            )
        )

        # ------------------------------------------------------------------
        # STEP 5
        # ------------------------------------------------------------------

        logging.warning("========== STEP 5 ==========")
        logging.warning("Basic validation")

        if not bucket:
            raise ValueError("Bucket name missing")

        if not name:
            raise ValueError("Object name missing")

        logging.warning("Validation successful")

        # ------------------------------------------------------------------
        # STEP 6
        # ------------------------------------------------------------------

        logging.warning("========== STEP 6 ==========")
        logging.warning("Downloading PDF from Cloud Storage")

        logging.warning(f"Bucket from event : {bucket}")
        logging.warning(f"Object from event : {name}")
        logging.warning(f"repr(object)      : {repr(name)}")
        logging.warning(f"Generation        : {generation}")

        bucket_ref = storage_client.bucket(bucket)

        logging.warning("Bucket object created.")

        blob = bucket_ref.blob(name)

        logging.warning(f"Blob path : gs://{bucket}/{name}")

        exists = blob.exists(storage_client)

        logging.warning(f"Blob exists : {exists}")

        if not exists:
            raise FileNotFoundError(
                f"Blob gs://{bucket}/{name} does not exist."
            )

        logging.warning("Blob confirmed by Storage API.")

        local_file = os.path.join(
            tempfile.gettempdir(),
            os.path.basename(name),
        )

        logging.warning(f"Downloading to {local_file}")

        blob.download_to_filename(local_file)

        logging.warning("Download completed.")

        file_size = os.path.getsize(local_file)

        logging.warning(
            json.dumps(
                {
                    "local_file": local_file,
                    "file_size_bytes": file_size,
                },
                indent=2,
            )
        )

        # ------------------------------------------------------------------
        # STEP 7
        # ------------------------------------------------------------------

        logging.warning("========== STEP 7 ==========")
        logging.warning("Calling Document AI")

        processor_name = documentai_client.processor_path(
            os.environ["PROJECT_ID"],
            os.environ["DOCUMENT_AI_LOCATION"],
            os.environ["DOCUMENT_AI_PROCESSOR"],
        )

        logging.warning(f"Processor: {processor_name}")

        with open(local_file, "rb") as pdf_file:
            pdf_bytes = pdf_file.read()

        logging.warning(f"Read {len(pdf_bytes)} bytes")

        raw_document = documentai.RawDocument(
            content=pdf_bytes,
            mime_type="application/pdf",
        )

        request = documentai.ProcessRequest(
            name=processor_name,
            raw_document=raw_document,
        )

        logging.warning("Calling process_document()")

        result = documentai_client.process_document(
            request=request
        )

        logging.warning("STEP 7 completed")

        document = result.document

        # ------------------------------------------------------------------
        # STEP 8 - Deep inspection of Document AI response
        # ------------------------------------------------------------------

        logging.warning("========== STEP 8 ==========")

        logging.warning("========== PROCESS RESPONSE ==========")
        logging.warning(str(result))

        logging.warning("========== DOCUMENT ==========")
        logging.warning(str(document))

        logging.warning("========== BASIC METADATA ==========")

        logging.warning(
            json.dumps(
                {
                    "document_type": str(type(document)),
                    "pages": len(document.pages),
                    "text_length": len(document.text),
                    "entities": len(document.entities),
                    "mime_type": document.mime_type,
                    "text_preview": document.text[:500],
                },
                indent=2,
                default=str,
            )
        )

        logging.warning("========== PAGE DETAILS ==========")

        for index, page in enumerate(document.pages):
            logging.warning(
                json.dumps(
                    {
                        "page_index": index,
                        "blocks": len(page.blocks),
                        "paragraphs": len(page.paragraphs),
                        "lines": len(page.lines),
                        "tokens": len(page.tokens),
                        "tables": len(page.tables),
                        "form_fields": len(page.form_fields),
                        "visual_elements": len(page.visual_elements),
                    },
                    indent=2,
                )
            )

        logging.warning("========== DOCUMENT FIELDS ==========")

        for field in sorted(document.DESCRIPTOR.fields_by_name.keys()):
            try:
                value = getattr(document, field)

                if isinstance(value, str):
                    summary = f"string(length={len(value)})"
                elif hasattr(value, "__len__"):
                    summary = f"{type(value).__name__}(length={len(value)})"
                else:
                    summary = str(type(value))

                logging.warning(f"{field}: {summary}")

            except Exception as ex:
                logging.warning(f"{field}: ERROR -> {ex}")

        logging.warning("========== STEP 8 COMPLETE ==========")
        logging.warning("Document AI processing completed successfully.")
        

    except Exception:
        logging.exception("========== UNHANDLED EXCEPTION ==========")
        raise

    finally:
        if local_file and os.path.exists(local_file):
            try:
                os.remove(local_file)
                logging.warning(f"Temporary file removed: {local_file}")
            except Exception:
                logging.exception("Failed to delete temporary file.")