from flask import Flask, request, jsonify
import requests, json
from google.auth import default
from google.auth.transport.requests import Request

app = Flask(__name__)

PROJECT_ID = "uthoindia-43d2c"
REGION = "us"
DATASTORE_ID = "legal-docs_1758459761283"  # Replace with your actual ID

def get_access_token():
    creds, _ = default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    creds.refresh(Request())
    return creds.token

@app.route("/upload-to-agentspace", methods=["POST"])
def upload_to_agentspace():
    data = request.get_json()
    filename = data.get("filename")
    content = data.get("text")

    if not filename or not content:
        return "Missing filename or text", 400

    endpoint = f"https://{REGION}-gen-app-builder.googleapis.com/v1alpha/projects/{PROJECT_ID}/locations/{REGION}/dataStores/{DATASTORE_ID}/documents:upload"
    headers = {
        "Authorization": f"Bearer {get_access_token()}",
        "Content-Type": "application/json"
    }

    payload = {
        "document": {
            "id": filename,
            "unstructured": {
                "text": content
            }
        }
    }

    response = requests.post(endpoint, headers=headers, json=payload)
    return jsonify({
        "status": response.status_code,
        "response": response.text
    })
