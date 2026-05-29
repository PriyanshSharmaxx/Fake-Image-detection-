import uuid
from sqlalchemy import Column, String, Numeric, Integer, DateTime, ForeignKey, Enum, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base


class Detection(Base):
    __tablename__ = "detections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    img_s3_url = Column(String(512), nullable=False)
    heatmap_s3_url = Column(String(512), nullable=True)
    result = Column(Enum("real", "ai_generated", "manipulated", name="detection_result"), nullable=False)
    confidence = Column(Numeric(5, 2), nullable=False)
    spatial_score = Column(Numeric(5, 4), nullable=False)
    freq_score = Column(Numeric(5, 4), nullable=False)
    xai_meta = Column(JSONB, nullable=True)  # Bounding boxes, activation layers info
    latency_ms = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="detections")
