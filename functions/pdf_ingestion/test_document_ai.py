from urllib import response

from google.api_core.client_options import ClientOptions
from google.cloud import documentai


PROJECT_ID = "knowledge-factory-prod"          # Project Number
LOCATION = "us"
PROCESSOR_ID = "eab1fbb0ebbc726e"

FILE_PATH = r"C:\Users\mites\Downloads\test_matrices_v9.pdf"   # <-- Change this


def main():

    opts = ClientOptions(
        api_endpoint=f"{LOCATION}-documentai.googleapis.com"
    )

    client = documentai.DocumentProcessorServiceClient(
        client_options=opts
    )

    name = client.processor_path(
        PROJECT_ID,
        LOCATION,
        PROCESSOR_ID,
    )

    with open(FILE_PATH, "rb") as f:
        pdf_bytes = f.read()

    request = documentai.ProcessRequest(
        name=name,
        raw_document=documentai.RawDocument(
            content=pdf_bytes,
            mime_type="application/pdf",
        ),
    )

    print("Calling Document AI...")
    response = client.process_document(request=request)

    print("SUCCESS")
    response = client.process_document(request=request)

    print("=" * 60)
    print("Pages:", len(response.document.pages))
    print("Text length:", len(response.document.text))

    if response.document.text:
        print(response.document.text[:500])
    else:
        print("No extracted text")

    print("=" * 60)
    print(response.document)