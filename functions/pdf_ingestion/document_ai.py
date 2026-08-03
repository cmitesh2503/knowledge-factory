"""
Google Document AI service wrapper.
"""

from pathlib import Path

from google.cloud import documentai
from google.api_core.client_options import ClientOptions


class DocumentAIService:
    """Wrapper around Google Document AI."""

    def __init__(
        self,
        project_id: str,
        location: str,
        processor_id: str,
    ) -> None:

        opts = ClientOptions(
            api_endpoint=f"{location}-documentai.googleapis.com"
        )

        self.client = documentai.DocumentProcessorServiceClient(
            client_options=opts
        )
        print(f"Using endpoint: {location}-documentai.googleapis.com")
        self.processor_name = self.client.processor_path(
            project_id,
            location,
            processor_id,
        )
        
        

    def process_file(self, file_path: str):
        """
        Process a local PDF file with Document AI.

        Parameters
        ----------
        file_path : str
            Local path to PDF.

        Returns
        -------
        documentai.ProcessResponse
        """

        pdf_bytes = Path(file_path).read_bytes()
        
        print(f"Bytes sent to Document AI: {len(pdf_bytes)}")
        print(f"PDF header: {pdf_bytes[:16].hex()}")

        raw_document = documentai.RawDocument(
            content=pdf_bytes,
            mime_type="application/pdf",
        )

        request = documentai.ProcessRequest(
            name=self.processor_name,
            raw_document=raw_document,
        )

        print(">>> BEFORE process_document")
        response = self.client.process_document(request=request)
        print(">>> AFTER process_document")
        print(f">>> process_document response type: {type(response)}")
        print(">>> RETURNING Document AI response")

        return response
