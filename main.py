import os, json
from flask import Flask, request, jsonify
from google.cloud import storage
from google.oauth2 import service_account

app = Flask(__name__)
MY_SECRET_KEY = os.environ.get("MY_SECRET_KEY", "Chair@3600")

# Render-এর Environment Variable বা লোকাল ফাইল থেকে ক্রেডেনশিয়াল নেওয়া
if os.environ.get("GCP_CREDENTIALS_JSON"):
    creds_info = json.loads(os.environ.get("GCP_CREDENTIALS_JSON"))
    creds = service_account.Credentials.from_service_account_info(creds_info)
    storage_client = storage.Client(credentials=creds)
else:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials.json"
    storage_client = storage.Client()

@app.before_request
def check_auth():
    auth_header = request.headers.get("Authorization")
    if auth_header != f"Bearer {MY_SECRET_KEY}":
        return jsonify({"error": "Unauthorized"}), 401

@app.route("/buckets", methods=["GET"])
def list_buckets():
    buckets = [bucket.name for bucket in storage_client.list_buckets()]
    return jsonify({"buckets": buckets})

@app.route("/upload", methods=["POST"])
def upload_file():
    data = request.json
    bucket = storage_client.bucket(data["bucket_name"])
    blob = bucket.blob(data["file_name"])
    blob.upload_from_string(data["content"])
    return jsonify({"status": "Success", "file": data["file_name"]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
