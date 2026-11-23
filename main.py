import os
from flask import Flask, request, jsonify
from google.cloud import storage

app = Flask(__name__)

# এই পাসওয়ার্ডটি ChatGPT Actions-এ বসাতে হবে
MY_SECRET_KEY = "Chai@3600"

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
