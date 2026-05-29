from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


# Auth Schemas
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


# API Key Schemas
class ApiKeyCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    expires_in_days: Optional[int] = Field(None, ge=1)


class ApiKeyResponse(BaseModel):
    id: UUID
    name: str
    prefix: str
    status: str
    created_at: datetime
    expires_at: Optional[datetime]
    raw_key: Optional[str] = None # Only returned once upon creation

    class Config:
        from_attributes = True


# Detection Schemas
class UploadUrlRequest(BaseModel):
    filename: str
    content_type: str = Field(..., pattern="^image/(jpeg|png|webp)$")


class UploadUrlResponse(BaseModel):
    url: str
    fields: Dict[str, str]
    object_key: str


class DetectionRequest(BaseModel):
    object_key: str
    generate_heatmap: Optional[bool] = True
    threshold: Optional[float] = 0.5


class BboxSchema(BaseModel):
    xmin: float
    ymin: float
    xmax: float
    ymax: float


class DetectionItem(BaseModel):
    classification: str
    confidence: float
    spatial_score: float
    freq_score: float
    bbox: Optional[BboxSchema] = None


class DetectionResponse(BaseModel):
    id: UUID
    img_s3_url: str
    heatmap_s3_url: Optional[str] = None
    result: str
    confidence: float
    spatial_score: float
    freq_score: float
    xai_meta: Optional[Dict[str, Any]] = None
    latency_ms: int
    created_at: datetime

    class Config:
        from_attributes = True


class SystemMetricsResponse(BaseModel):
    cpu_usage: float
    memory_usage: float
    gpu_usage: List[float]
    gpu_memory_free: List[float]
    total_scans: int
    scans_breakdown: Dict[str, int]
    avg_latency_ms: float
