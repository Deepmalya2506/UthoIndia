from flask import Flask, request
from google.cloud import storage, documentai_v1 as documentai
import base64, json, os

app = Flask(__name__)

# Document AI setup
PROJECT_ID = "uthoindia-43d2c"
PROCESSOR_ID = "f4f068253713067f"
LOCATION = "us"
BUCKET_NAME = "legal-docs-ingest"

@app.route("/", methods=["POST"])
def receive_pubsub():
    envelope = request.get_json()
    if not envelope or "message" not in envelope:
        return "Invalid Pub/Sub message", 400

    message_data = envelope["message"].get("data")
    if not message_data:
        return "No data", 400

    payload = json.loads(base64.b64decode(message_data).decode("utf-8"))
    filename = payload.get("filename")
    print(f"Received file: {filename}")

    # Load file from Cloud Storage
    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(filename)
    file_content = blob.download_as_bytes()

    # Send to Document AI
    client = documentai.DocumentProcessorServiceClient()
    name = f"projects/{PROJECT_ID}/locations/{LOCATION}/processors/{PROCESSOR_ID}"
    raw_document = documentai.RawDocument(content=file_content, mime_type="application/pdf")
    request_doc = documentai.ProcessRequest(name=name, raw_document=raw_document)
    result = client.process_document(request=request_doc)
    document = result.document
    full_text = document.text

    print(f"Extracted text:\n{full_text[:500]}...")  # Preview first 500 chars
    return "Document parsed", 200
