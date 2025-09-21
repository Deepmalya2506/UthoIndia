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
