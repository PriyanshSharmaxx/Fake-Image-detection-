import aioboto3
from typing import Dict, Any, Optional
from app.core.config import settings


class S3Service:
    def __init__(self):
        self.session = aioboto3.Session()

    def _get_client_args(self) -> Dict[str, Any]:
        args = {
            "region_name": settings.S3_REGION_NAME,
            "aws_access_key_id": settings.AWS_ACCESS_KEY_ID,
            "aws_secret_access_key": settings.AWS_SECRET_ACCESS_KEY,
        }
        if settings.S3_ENDPOINT_URL:
            args["endpoint_url"] = settings.S3_ENDPOINT_URL
        return args

    async def generate_presigned_upload(self, object_key: str, content_type: str, expires_in: int = 3600) -> Dict[str, Any]:
        """
        Generate a pre-signed POST policy for uploading a file directly from client browser to S3.
        """
        async with self.session.client("s3", **self._get_client_args()) as s3_client:
            # Ensure bucket exists (helpful for local MinIO startup)
            try:
                await s3_client.create_bucket(Bucket=settings.S3_BUCKET_NAME)
            except Exception:
                pass  # Bucket already exists or creation failed

            response = await s3_client.generate_presigned_post(
                Bucket=settings.S3_BUCKET_NAME,
                Key=object_key,
                Fields={"Content-Type": content_type},
                Conditions=[
                    {"Content-Type": content_type},
                    ["content-length-range", 1, 10 * 1024 * 1024] # Max 10MB
                ],
                ExpiresIn=expires_in
            )
            return response

    async def generate_presigned_download(self, object_key: str, expires_in: int = 3600) -> str:
        """
        Generate a pre-signed GET URL for reading protected images.
        """
        async with self.session.client("s3", **self._get_client_args()) as s3_client:
            url = await s3_client.generate_presigned_url(
                ClientMethod="get_object",
                Params={"Bucket": settings.S3_BUCKET_NAME, "Key": object_key},
                ExpiresIn=expires_in
            )
            return url


s3_service = S3Service()
