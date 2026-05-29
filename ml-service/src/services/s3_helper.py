import aioboto3
from typing import Dict, Any, Optional
import os


class MLS3Helper:
    def __init__(self) -> None:
        self.session = aioboto3.Session()
        self.endpoint_url = os.getenv("S3_ENDPOINT_URL", "http://localhost:9000")
        # Do not hard-code credentials; read from environment only
        self.access_key = os.getenv("AWS_ACCESS_KEY_ID")
        self.secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.bucket_name = os.getenv("S3_BUCKET_NAME", "uploads")

    def _get_client_args(self) -> Dict[str, Any]:
        args = {
            "region_name": "us-east-1",
            "aws_access_key_id": self.access_key,
            "aws_secret_access_key": self.secret_key,
        }
        if self.endpoint_url:
            args["endpoint_url"] = self.endpoint_url
        return args

    async def upload_bytes(self, data: bytes, object_key: str, content_type: str = "image/jpeg") -> str:
        """
        Upload binary data (like Grad-CAM heatmap images) to S3 bucket.
        """
        async with self.session.client("s3", **self._get_client_args()) as s3_client:
            # Ensure bucket exists
            try:
                await s3_client.create_bucket(Bucket=self.bucket_name)
            except Exception:
                pass

            await s3_client.put_object(
                Bucket=self.bucket_name,
                Key=object_key,
                Body=data,
                ContentType=content_type
            )
            return object_key


ml_s3_helper = MLS3Helper()
