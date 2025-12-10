from flask import Flask, request, render_template, send_file, redirect, url_for
import boto3
import os
from config import AWS_BUCKET_NAME, AWS_REGION

app = Flask(__name__)

# Create S3 client (uses EC2 IAM Role or env vars)
s3 = boto3.client('s3', region_name=AWS_REGION)


@app.route("/")
def index():
    """List files in S3 bucket"""

    print("Bucket Name Loaded:", AWS_BUCKET_NAME, type(AWS_BUCKET_NAME))

    try:
        response = s3.list_objects_v2(Bucket=AWS_BUCKET_NAME)
    except Exception as e:
        return f"Error accessing S3 bucket: {str(e)}"

    files = []

    # If bucket contains files
    if "Contents" in response:
        files = [obj["Key"] for obj in response["Contents"]]

    # Send bucket name to template so images load
    return render_template("index.html", files=files, bucket=AWS_BUCKET_NAME)


@app.route("/upload", methods=["POST"])
def upload():
    """Upload file to S3"""

    if "file" not in request.files:
        return "No file part"

    file = request.files["file"]

    if file.filename == "":
        return "No selected file"

    try:
        s3.upload_fileobj(file, AWS_BUCKET_NAME, file.filename)
    except Exception as e:
        return f"Upload failed: {str(e)}"

    return redirect(url_for("index"))


@app.route("/download/<filename>")
def download(filename):
    """Download file from S3"""

    try:
        s3.download_file(AWS_BUCKET_NAME, filename, filename)
    except Exception as e:
        return f"Download failed: {str(e)}"

    return send_file(filename, as_attachment=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
