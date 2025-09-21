# app/main.py
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import storage

app = FastAPI()

# 👇 Add this block to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this to your frontend URL later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GCP Storage setup
storage_client = storage.Client()
bucket_name = "legal-docs-ingest"

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    blob_name = file.filename

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_string(contents, content_type=file.content_type)

    return {"message": f"File '{blob_name}' uploaded successfully to {bucket_name}"}

from google.cloud import pubsub_v1
import json

# Initialize Pub/Sub publisher
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path("uthoindia-43d2c", "doc-upload-trigger")

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    blob_name = file.filename

    # Upload to Cloud Storage
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_string(contents, content_type=file.content_type)

    # Publish message to Pub/Sub
    message_data = json.dumps({"filename": blob_name})
    publisher.publish(topic_path, data=message_data.encode("utf-8"))

    return {"message": f"File '{blob_name}' uploaded successfully to {bucket_name}"}

import base64
import json

def process_upload(event, context):
    if 'data' in event:
        message_data = base64.b64decode(event['data']).decode('utf-8')
        payload = json.loads(message_data)
        filename = payload.get("filename")

        print(f"Received file: {filename}")
        # TODO: Add logic to process the file (e.g., extract metadata, call Agentspace, etc.)
    else:
        print("No data found in event.")

from google.cloud import documentai_v1 as documentai
from google.cloud import storage
import base64
import json

# Set your processor info
project_id = "uthoindia-43d2c"
location = "us"
processor_id = "YOUR_PROCESSOR_ID"  # Replace with actual ID

def process_upload(event, context):
    if 'data' not in event:
        print("No data found in event.")
        return

    message_data = base64.b64decode(event['data']).decode('utf-8')
    payload = json.loads(message_data)
    filename = payload.get("filename")

    print(f"Received file: {filename}")

    # Load file from Cloud Storage
    storage_client = storage.Client()
    bucket = storage_client.bucket("legal-docs-ingest")
    blob = bucket.blob(filename)
    file_content = blob.download_as_bytes()

    # Set up Document AI client
    client = documentai.DocumentProcessorServiceClient()
    name = f"projects/{project_id}/locations/{location}/processors/{processor_id}"

    # Prepare the document
    raw_document = documentai.RawDocument(content=file_content, mime_type="application/pdf")
    request = documentai.ProcessRequest(name=name, raw_document=raw_document)

    # Parse the document
    result = client.process_document(request=request)
    document = result.document

    # Extract text
    full_text = document.text
    print(f"Extracted text from {filename}:\n{full_text[:500]}...")  # Show first 500 chars
