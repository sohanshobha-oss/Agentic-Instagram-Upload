import boto3
from pathlib import Path
import os
import uuid

def upload_to_s3(image_path: str) -> str:
    AWS_REGION = os.getenv("AWS_REGION")
    AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
    AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
    BUCKET_NAME = os.getenv("BUCKET_NAME")

    unique_id = uuid.uuid4().hex
    key = f"images/{unique_id}.png"

    if not all([AWS_REGION, AWS_ACCESS_KEY, AWS_SECRET_KEY, BUCKET_NAME]):
        raise ValueError("Missing AWS environment variables")

    s3 = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name=AWS_REGION
    )

    file_path = Path("output.png").resolve()
    print(file_path)

    if not file_path.exists():
        raise FileNotFoundError(file_path)

    s3_key = f"images/{file_path.name}"

    s3.upload_file(
        Filename=str(file_path),
        Bucket=BUCKET_NAME,
        Key=key,
        ExtraArgs={"ContentType": "image/png"}
    )

    return f"https://{BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{key}"
