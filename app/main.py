# app/main.py
from fastapi import FastAPI, File, UploadFile
from google.cloud import storage
import os

app = FastAPI()

# Initialize GCP Storage client
storage_client = storage.Client()
bucket_name = "legal-docs-ingest"  # Your Cloud Storage bucket

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    blob_name = file.filename

    # Upload to Cloud Storage
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_string(contents, content_type=file.content_type)

    return {"message": f"File '{blob_name}' uploaded successfully to {bucket_name}"}
