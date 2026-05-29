# DeepFake Shield: Project Mapping & Architecture Documentation

This document provides a comprehensive mapping of the file structure, system components, API endpoints, database schemas, and data flows for the DeepFake & AI Image Detection platform.

---

## 1. System Components & Port Allocations

When running the system via `docker-compose.yml`, the services are mapped as follows:

| Service Name | Description | Host Port | Internal Port | Technology |
| :--- | :--- | :--- | :--- | :--- |
| **frontend** | Next.js Single Page Application | `3000` | `3000` | React, Next.js, TailwindCSS |
| **backend-api** | FastAPI Gateway & Orchestrator | `8000` | `8000` | Python, FastAPI, SQLAlchemy |
| **ml-service** | PyTorch Deep Learning Inference Server | `50051` | `50051` | PyTorch, gRPC, timm, OpenCV |
| **postgres** | Database metadata store | `5432` | `5432` | PostgreSQL 15 |
| **redis** | Queue broker and key-value store | `6379` | `6379` | Redis 7 |
| **minio** | Local S3-compatible object storage | `9000` (API)<br>`9001` (UI) | `9000`<br>`9001` | MinIO |
| **prometheus** | Metrics scraper and storage | `9090` | `9090` | Prometheus |

---

## 2. File-by-File Mapping

Below is the layout of the generated source files, grouped by service.

### 2.1 Backend API Service (`backend/`)
- [backend/Dockerfile](file:///Users/priyanshsharma/Downloads/fake%20detection/backend/Dockerfile): Container setup installing C++ build tools (for gRPC dependencies), coping source files, and compiling `.proto` files dynamically.
- [backend/requirements.txt](file:///Users/priyanshsharma/Downloads/fake%20detection/backend/requirements.txt): Backend packages list including FastAPI, SQLAlchemy asyncpg driver, aioboto3 for storage, and pyjwt.
- [backend/app/main.py](file:///Users/priyanshsharma/Downloads/fake%20detection/backend/app/main.py): FastAPI app startup. Configures CORS, sets up routers, and registers the async lifespan trigger which initializes Postgres tables on startup.
- [backend/app/core/config.py](file:///Users/priyanshsharma/Downloads/fake%20detection/backend/app/core/config.py): Configuration parsing utilizing Pydantic settings. Reads JWT signing secret keys, DB connection URLs, and S3 credentials.
- [backend/app/core/database.py](file:///Users/priyanshsharma/Downloads/fake%20detection/backend/app/core/database.py): Base engine initialization using `create_async_engine`. Defines the async session factory and the `get_db` FastAPI dependency.
- [backend/app/core/security.py](file:///Users/priyanshsharma/Downloads/fake%20detection/backend/app/core/security.py): Password hashing/verification using bcrypt and JWT token signing algorithms.
- [backend/app/models/user.py](file:///Users/priyanshsharma/Downloads/fake%20detection/backend/app/models/user.py): Database model representing users, passwords, and user roles (`admin`, `developer`, `user`).
- [backend/app/models/detection.py](file:///Users/priyanshsharma/Downloads/fake%20detection/backend/app/models/detection.py): Database model storing original and heatmap S3 URLs, ensemble scores, final classification, and latencies.
- [backend/app/models/api_key.py](file:///Users/priyanshsharma/Downloads/fake%20detection/backend/app/models/api_key.py): Database model managing third-party SHA-256 hashed API keys.
- [backend/app/api/schemas.py](file:///Users/priyanshsharma/Downloads/fake%20detection/backend/app/api/schemas.py): Pydantic validation schemas defining request and response payloads for users, keys, and scans.
- [backend/app/api/auth.py](file:///Users/priyanshsharma/Downloads/fake%20detection/backend/app/api/auth.py): Endpoint routes for registration, user logins, and fetching user profiles.
- [backend/app/api/detections.py](file:///Users/priyanshsharma/Downloads/fake%20detection/backend/app/api/detections.py): Router managing S3 presigned POST generation, history tracking, and coordinating gRPC model triggers.
- [backend/app/services/s3.py](file:///Users/priyanshsharma/Downloads/fake%20detection/backend/app/services/s3.py): Non-blocking S3 client utility (aioboto3) yielding presigned upload and download URLs.
- [backend/app/services/grpc_client.py](file:///Users/priyanshsharma/Downloads/fake%20detection/backend/app/services/grpc_client.py): Asynchronous gRPC client invoking model evaluations over port `50051`.
- [backend/app/services/grpc/inference.proto](file:///Users/priyanshsharma/Downloads/fake%20detection/backend/app/services/grpc/inference.proto): The Protobuf interface sharing contract definitions between client and server.
- [backend/tests/test_api.py](file:///Users/priyanshsharma/Downloads/fake%20detection/backend/tests/test_api.py): Basic FastAPI route test checking endpoint health.

### 2.2 Machine Learning Inference Service (`ml-service/`)
- [ml-service/Dockerfile.gpu](file:///Users/priyanshsharma/Downloads/fake%20detection/ml-service/Dockerfile.gpu): Container environment pulling CUDA PyTorch base layers, installing OpenCV dependencies, and compiling `.proto` files.
- [ml-service/requirements.txt](file:///Users/priyanshsharma/Downloads/fake%20detection/ml-service/requirements.txt): Deep learning packages including PyTorch, torchvision, timm, transformers, opencv, and onnxruntime-gpu.
- [ml-service/src/grpc/server.py](file:///Users/priyanshsharma/Downloads/fake%20detection/ml-service/src/grpc/server.py): gRPC async server mapping requests into the detection classes.
- [ml-service/src/pipeline/face_detector.py](file:///Users/priyanshsharma/Downloads/fake%20detection/ml-service/src/pipeline/face_detector.py): Face crop detection using OpenCV Haar Cascades with padded boundary scaling.
- [ml-service/src/pipeline/spatial_model.py](file:///Users/priyanshsharma/Downloads/fake%20detection/ml-service/src/pipeline/spatial_model.py): ConvNeXt classifier reading physical textures to evaluate generative anomalies.
- [ml-service/src/pipeline/frequency_model.py](file:///Users/priyanshsharma/Downloads/fake%20detection/ml-service/src/pipeline/frequency_model.py): ResNet-50 network running on 2D Discrete Cosine Transform (DCT) log-transformed power spectrums.
- [ml-service/src/pipeline/ensemble.py](file:///Users/priyanshsharma/Downloads/fake%20detection/ml-service/src/pipeline/ensemble.py): Execution orchestrator pulling S3 URLs, running cropping pipelines, computing spatial/spectral weights fusion, and running Grad-CAM.
- [ml-service/src/explainability/gradcam.py](file:///Users/priyanshsharma/Downloads/fake%20detection/ml-service/src/explainability/gradcam.py): Hook class fetching backward gradients and mapping feature activations to target layers.
- [ml-service/src/services/s3_helper.py](file:///Users/priyanshsharma/Downloads/fake%20detection/ml-service/src/services/s3_helper.py): Helper putting heatmap bytes directly back into storage.
- [ml-service/tests/test_pipeline.py](file:///Users/priyanshsharma/Downloads/fake%20detection/ml-service/tests/test_pipeline.py): Basic unit tests verifying image formatting outputs.

### 2.3 Frontend Application (`frontend/`)
- [frontend/Dockerfile](file:///Users/priyanshsharma/Downloads/fake%20detection/frontend/Dockerfile): Container utilizing Node 18 to build and launch the Next.js production server.
- [frontend/package.json](file:///Users/priyanshsharma/Downloads/fake%20detection/frontend/package.json): Script definitions and frontend packages (Next.js, Framer Motion, Zustand).
- [frontend/tailwind.config.js](file:///Users/priyanshsharma/Downloads/fake%20detection/frontend/tailwind.config.js): Custom themes mapping glassmorphism layout tokens and scanning animation keyframes.
- [frontend/src/app/globals.css](file:///Users/priyanshsharma/Downloads/fake%20detection/frontend/src/app/globals.css): Global variables mapping base colors and backdrop filter glass wrappers.
- [frontend/src/app/layout.tsx](file:///Users/priyanshsharma/Downloads/fake%20detection/frontend/src/app/layout.tsx): Root document framing navigation headers and footers.
- [frontend/src/app/page.tsx](file:///Users/priyanshsharma/Downloads/fake%20detection/frontend/src/app/page.tsx): Main landing page displaying project features.
- [frontend/src/app/dashboard/page.tsx](file:///Users/priyanshsharma/Downloads/fake%20detection/frontend/src/app/dashboard/page.tsx): Interactive analysis page supporting drag-and-drop uploads, scan animations, confidence gauges, and original vs Grad-CAM slider comparator.
- [frontend/src/app/history/page.tsx](file:///Users/priyanshsharma/Downloads/fake%20detection/frontend/src/app/history/page.tsx): Paginated table mapping past logs.
- [frontend/src/app/admin/page.tsx](file:///Users/priyanshsharma/Downloads/fake%20detection/frontend/src/app/admin/page.tsx): Live telemetry charts tracking CPU/GPU workloads and latency metrics.
- [frontend/src/lib/api.ts](file:///Users/priyanshsharma/Downloads/fake%20detection/frontend/src/lib/api.ts): Direct HTTP integrations supporting authorization context and presigned uploads.
- [frontend/src/store/auth.ts](file:///Users/priyanshsharma/Downloads/fake%20detection/frontend/src/store/auth.ts): Zustand state tracking local token sessions.

---

## 3. Data Flow Diagram

The diagram below details the path a request takes from file upload to final classification:

```
[ Next.js Client ]
      │
      │ 1. POST /upload-url (Auth Token)
      ▼
[ FastAPI Backend ] ──► (Generates storage key: uploads/userId/uuid.png)
      │
      │ 2. Returns S3 Presigned URL + Policy Fields
      ▼
[ Next.js Client ] ──► [ MinIO / S3 Storage ] (Direct File Upload via HTTP POST)
      │
      │ 3. POST /analyze (Submit storage key)
      ▼
[ FastAPI Backend ]
      │
      │ 4. Generate S3 Presigned GET download URL
      │ 5. Invoke AnalyzeImage(image_s3_url) via gRPC (port 50051)
      ▼
[ ML Inference Service ]
      │
      ├─► 6. Downloads Image via Presigned GET
      ├─► 7. Runs RetinaFace/Haar Bounding Box Extraction
      │
      ├── [ Crop Face Patches ]
      │         │
      │         ├─► [ Spatial Path: ConvNeXt ] ──► Class Probs (e.g. 94.2% AI)
      │         │                                        │
      │         │                                        ▼
      │         │                                (Trigger Grad-CAM)
      │         │                                        │
      │         │                                        ▼
      │         │                                (Generate Heatmap)
      │         │
      │         └─► [ Freq Path: 2D-DCT + ResNet ] ──► Class Probs (e.g. 99.1% AI)
      │
      ├─► 8. Dynamic Ensemble Fusion:
      │      Unified Score = (0.65 * Spatial) + (0.35 * Freq)
      │
      ├─► 9. Uploads Grad-CAM heatmap back to MinIO (heatmaps/uuid.jpg)
      │
      ▼ 10. Returns Protobuf InferenceResponse (Detections, Heatmap Key, Latency)
[ FastAPI Backend ]
      │
      │ 11. Write Detection record to PostgreSQL Database
      │ 12. Return JSON response payload
      ▼
[ Next.js Client ] (Displays results dashboard and Swipeable Image/Heatmap Overlay)
```

---

## 4. REST Endpoint & API Schema Maps

### 4.1 Authentication Router (`/api/v1/auth`)
- **`POST /register`**: Registers a new user. Enforces minimum 8-character password checks.
- **`POST /token`**: Exchanges client credentials for a signed JWT access token.
- **`GET /me`**: Returns profile info of the currently logged-in user.

### 4.2 Detections Router (`/api/v1/detections`)
- **`POST /upload-url`**: Generates a presigned POST payload for direct uploads to S3 storage. Max payload size is bounded to 10MB, and content-type is validated (`image/jpeg`, `image/png`, `image/webp`).
- **`POST /analyze`**: Submits the uploaded image S3 storage key to run ML evaluations.
- **`GET /history`**: Fetches user-specific history logs (paginated).

---

## 5. Database Schema Relations

```
+--------------------------------------+       +--------------------------------------+
|               users                  |       |              api_keys                |
+--------------------------------------+       +--------------------------------------+
| id (UUID, PK)                        |       | id (UUID, PK)                        |
| email (VARCHAR, UNIQUE)              |◄──────| user_id (UUID, FK)                   |
| hashed_password (VARCHAR)            |       | hashed_key (VARCHAR, INDEX)          |
| role (ENUM: admin, developer, user)  |       | name (VARCHAR)                       |
| created_at (TIMESTAMP)               |       | prefix (VARCHAR)                     |
| updated_at (TIMESTAMP)               |       | status (ENUM: active, revoked, exp)  |
+--------------------------------------+       | created_at (TIMESTAMP)               |
                   │                           | expires_at (TIMESTAMP, NULLABLE)     |
                   │                           +--------------------------------------+
                   │ 1
                   │
                   │ M
+--------------------------------------+
|             detections               |
+--------------------------------------+
| id (UUID, PK)                        |
| user_id (UUID, FK, NULLABLE)         |◄────── (Set to NULL if user is deleted)
| img_s3_url (VARCHAR)                 |
| heatmap_s3_url (VARCHAR, NULLABLE)   |
| result (ENUM: real, synthetic, manip)|
| confidence (NUMERIC(5,2))            |
| spatial_score (NUMERIC(5,4))         |
| freq_score (NUMERIC(5,4))            |
| xai_meta (JSONB, NULLABLE)           |
| latency_ms (INTEGER)                 |
| created_at (TIMESTAMP)               |
+--------------------------------------+
```
