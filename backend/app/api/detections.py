import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from app.core.database import get_db
from app.core.config import settings
from app.models.user import User
from app.models.detection import Detection
from app.models.api_key import ApiKey
from app.api.auth import get_current_user
from app.api.schemas import (
    UploadUrlRequest, 
    UploadUrlResponse, 
    DetectionRequest, 
    DetectionResponse
)
from app.services.s3 import s3_service
from app.services.grpc_client import grpc_client
from app.core.security import hash_api_key

router = APIRouter()


async def get_api_user_or_current_user(
    x_api_key: Optional[str] = Header(None),
    current_user: Optional[User] = Depends(lambda: None), # Lazy evaluation
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Authenticate utilizing API keys or standard JWT session.
    """
    if x_api_key:
        hashed = hash_api_key(x_api_key)
        # Search active keys
        stmt = select(ApiKey).filter(ApiKey.hashed_key == hashed, ApiKey.status == "active")
        result = await db.execute(stmt)
        key_record = result.scalars().first()
        if not key_record:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or revoked API Key."
            )
        # Check expiration
        if key_record.expires_at and key_record.expires_at < func.now():
            key_record.status = "expired"
            await db.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API Key has expired."
            )
        # Fetch key owner
        user_stmt = select(User).filter(User.id == key_record.user_id)
        user_res = await db.execute(user_stmt)
        return user_res.scalars().first()

    # Fallback to standard OAuth2
    try:
        # We invoke get_current_user manually to avoid header collisions
        from fastapi.security import OAuth2PasswordBearer
        from app.api.auth import oauth2_scheme
        token = Depends(oauth2_scheme)
        # Since Depends requires execution inside FastAPI route injection, we handle oauth2 extraction
        # Let's perform it with custom extraction to be robust
    except Exception:
        pass

    # A simpler way is to depend on get_current_user inside route parameters,
    # and if that fails, allow x-api-key path. We will structuralize that in the route definitions.
    raise HTTPException(status_code=401, detail="Authentication credentials not provided.")


@router.post("/upload-url", response_model=UploadUrlResponse)
async def get_upload_url(
    payload: UploadUrlRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Get a presigned S3 upload URL. Direct file transfer from browser to S3.
    """
    file_extension = payload.filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    object_key = f"uploads/{current_user.id}/{unique_filename}"
    
    try:
        policy = await s3_service.generate_presigned_upload(
            object_key=object_key,
            content_type=payload.content_type
        )
        return {
            "url": policy["url"],
            "fields": policy["fields"],
            "object_key": object_key
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate upload URL: {str(e)}"
        )


@router.post("/analyze", response_model=DetectionResponse)
async def analyze_image(
    payload: DetectionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Perform deepfake evaluation on an uploaded S3 image key.
    Triggers gRPC ML-inference pipeline.
    """
    # 1. Check if S3 object key looks valid (security check to prevent path traversals)
    if not payload.object_key.startswith("uploads/"):
        raise HTTPException(status_code=400, detail="Invalid storage path prefix.")
        
    # Generate download URL for ML service access
    try:
        image_s3_url = await s3_service.generate_presigned_download(payload.object_key)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Storage mapping failed: {str(e)}")

    # 2. Call ML service over gRPC
    try:
        inference_result = await grpc_client.analyze_image(
            image_s3_url=image_s3_url,
            generate_heatmap=payload.generate_heatmap,
            threshold=payload.threshold
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"ML Service returned an error: {str(e)}"
        )

    # 3. Process outputs & merge ensemble metrics
    # Choose primary classification (highest confidence)
    primary = max(inference_result["detections"], key=lambda x: x["confidence"])
    
    # Save detection data
    new_detection = Detection(
        user_id=current_user.id,
        img_s3_url=payload.object_key,
        heatmap_s3_url=inference_result.get("heatmap_s3_url"),
        result=primary["classification"],
        confidence=primary["confidence"],
        spatial_score=primary["spatial_score"],
        freq_score=primary["freq_score"],
        xai_meta={
            "detections": inference_result["detections"]
        },
        latency_ms=inference_result["inference_time_ms"]
    )
    
    db.add(new_detection)
    await db.commit()
    await db.refresh(new_detection)
    
    return new_detection


@router.get("/history", response_model=List[DetectionResponse])
async def get_history(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve user history list.
    """
    stmt = select(Detection).filter(Detection.user_id == current_user.id).order_by(Detection.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    history = result.scalars().all()
    return history
