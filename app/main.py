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
