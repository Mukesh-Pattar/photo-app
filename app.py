from flask import Flask, render_template, request, redirect
import boto3
import uuid
import os

app = Flask(__name__)

# Boto3 will automatically use IAM Role when running on EC2
s3 = boto3.client('s3')

# Bucket name from env variable
AWS_BUCKET_NAME = os.environ.get("AWS_BUCKET_NAME")
AWS_REGION = os.environ.get("AWS_REGION", "ap-south-1")


@app.route('/')
def index():
    """List all images stored in S3 bucket."""

    contents = s3.list_objects_v2(Bucket=AWS_BUCKET_NAME)
    files = []

    if 'Contents' in contents:
        for item in contents['Contents']:
            url = f"https://{AWS_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{item['Key']}"
            files.append(url)

    return render_template('index.html', files=files)


@app.route('/upload', methods=['POST'])
def upload():
    """Upload a photo to S3."""
    file = request.files['file']

    if file:
        filename = str(uuid.uuid4()) + "_" + file.filename
        s3.upload_fileobj(file, AWS_BUCKET_NAME, filename)

    return redirect('/')


@app.route('/download/<filename>')
def download(filename):
    """Download a photo from S3 to server temp folder."""
    local_path = f"/tmp/{filename}"

    s3.download_file(AWS_BUCKET_NAME, filename, local_path)

    return f"Downloaded to: {local_path}"


if __name__ == "__main__":
    # run on EC2 public ip
    app.run(host="0.0.0.0", port=5000)