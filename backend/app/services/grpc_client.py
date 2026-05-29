import grpc
from typing import Dict, Any, List
from app.core.config import settings

# These will be compiled dynamically via script or docker build
try:
    from app.services.grpc import inference_pb2
    from app.services.grpc import inference_pb2_grpc
except ImportError:
    # Fail-safe or fallback for development check
    inference_pb2 = None
    inference_pb2_grpc = None


class GrpcInferenceClient:
    def __init__(self) -> None:
        self.target = f"{settings.GRPC_INFERENCE_HOST}:{settings.GRPC_INFERENCE_PORT}"

    async def analyze_image(self, image_s3_url: str, generate_heatmap: bool = True, threshold: float = 0.5) -> Dict[str, Any]:
        if not inference_pb2 or not inference_pb2_grpc:
            raise RuntimeError("gRPC compiled client files (inference_pb2/grpc) are missing. Run protoc compilation.")

        async with grpc.aio.insecure_channel(self.target) as channel:
            stub = inference_pb2_grpc.ImageDetectorStub(channel)
            request = inference_pb2.InferenceRequest(
                image_s3_url=image_s3_url,
                generate_heatmap=generate_heatmap,
                threshold=threshold
            )
            
            try:
                response = await stub.AnalyzeImage(request, timeout=30.0)
            except grpc.RpcError as e:
                raise RuntimeError(f"gRPC service call failed: {e.code()} - {e.details()}")

            detections: List[Dict[str, Any]] = []
            for det in response.detections:
                detections.append({
                    "classification": det.classification,
                    "confidence": det.confidence,
                    "spatial_score": det.spatial_score,
                    "freq_score": det.freq_score,
                    "bbox": {
                        "xmin": det.bbox.xmin,
                        "ymin": det.bbox.ymin,
                        "xmax": det.bbox.xmax,
                        "ymax": det.bbox.ymax,
                    } if det.bbox else None
                })

            return {
                "detection_id": response.detection_id,
                "detections": detections,
                "heatmap_s3_url": response.heatmap_s3_url,
                "inference_time_ms": response.inference_time_ms
            }


grpc_client = GrpcInferenceClient()
