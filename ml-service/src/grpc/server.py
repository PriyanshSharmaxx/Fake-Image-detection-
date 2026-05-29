import asyncio
import logging
import os
import grpc
from typing import Any

# Import compiled protobuf models
try:
    from src.grpc import inference_pb2
    from src.grpc import inference_pb2_grpc
except ImportError:
    # Fail-safe or compilation fallback
    inference_pb2 = None
    inference_pb2_grpc = None

from src.pipeline.ensemble import ensemble_detector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ml-grpc-server")


class ImageDetectorServicer(inference_pb2_grpc.ImageDetectorServicer if inference_pb2_grpc else object):
    async def AnalyzeImage(
        self, 
        request: Any, 
        context: grpc.aio.ServicerContext
    ) -> Any:
        logger.info(f"Received inference request for S3 URL: {request.image_s3_url}")
        
        try:
            result = await ensemble_detector.analyze(
                image_s3_url=request.image_s3_url,
                generate_heatmap=request.generate_heatmap,
                threshold=request.threshold
            )
            
            # Map Python dict to protobuf output
            detections_pb = []
            for det in result["detections"]:
                bbox_pb = None
                if det["bbox"]:
                    bbox_pb = inference_pb2.FaceBoundingBox(
                        xmin=det["bbox"]["xmin"],
                        ymin=det["bbox"]["ymin"],
                        xmax=det["bbox"]["xmax"],
                        ymax=det["bbox"]["ymax"]
                    )
                
                detections_pb.append(
                    inference_pb2.DetectionResult(
                        classification=det["classification"],
                        confidence=det["confidence"],
                        spatial_score=det["spatial_score"],
                        freq_score=det["freq_score"],
                        bbox=bbox_pb
                    )
                )

            return inference_pb2.InferenceResponse(
                detection_id=result["detection_id"],
                detections=detections_pb,
                heatmap_s3_url=result["heatmap_s3_url"],
                inference_time_ms=result["inference_time_ms"]
            )
            
        except Exception as e:
            logger.error(f"Inference execution failed: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return inference_pb2.InferenceResponse()


async def serve() -> None:
    if not inference_pb2 or not inference_pb2_grpc:
        raise RuntimeError("gRPC compiled server files (inference_pb2/grpc) are missing. Run protoc compilation.")

    port = os.getenv("GRPC_SERVER_PORT", "50051")
    server = grpc.aio.server()
    inference_pb2_grpc.add_ImageDetectorServicer_to_server(ImageDetectorServicer(), server)
    
    server.add_insecure_port(f"[::]:{port}")
    logger.info(f"Starting gRPC server on port {port}...")
    await server.start()
    await server.wait_for_termination()


if __name__ == "__main__":
    asyncio.run(serve())
