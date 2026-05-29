# Fake Image Detection — Production Ready

Professional, production-ready repository for a DeepFake / AI-generated image detection platform.

Built components
- Frontend: Next.js (React) + TailwindCSS
- Backend: FastAPI (authentication, REST API, Postgres persistence)
- ML service: PyTorch inference service with gRPC and explainability (Grad-CAM)
- Orchestration: Docker Compose and Kubernetes manifests (k8s/)

**Status:** Integration complete. This repository is prepared for a production-ready push — see audit and instructions below.

## Features
- Real-time image analysis and detection pipeline (spatial + frequency models)
- TorchScript and optimized PyTorch model variants for production inference
- REST API (FastAPI) and Next.js frontend
- Object storage integration (MinIO/S3), Postgres for persistence
- Monitoring with Prometheus + Grafana

## Architecture

```mermaid
graph LR
   F[Frontend (Next.js)] -->|REST API| B[Backend (FastAPI)]
   B -->|gRPC / HTTP| M[ML Service (PyTorch gRPC server)]
   B --> DB[(Postgres)]
   B --> S3[(MinIO / S3)]
   M --> S3
   M -->|Grad-CAM| XAI[Explainability]
   Monitoring -->|metrics| Prom[Prometheus]
   Prom --> Graf[Grafana]
```

## Technology Stack
- Frontend: Next.js, React, Tailwind CSS, TypeScript
- Backend: FastAPI, Pydantic, SQLAlchemy, Alembic, PostgreSQL
- ML: PyTorch, TorchScript, Grad-CAM
- DevOps: Docker, docker-compose, Kubernetes manifests

## Quick Installation (local)
Prerequisites: Docker, Docker Compose, Node (for frontend), Python 3.9+ (for local development)

1. Clone the repo:
```bash
git clone https://github.com/PriyanshSharmaxx/Fake-Image-detection-.git
cd Fake-Image-detection-
```

2. Create `.env` files for services (copy sample values from `LOCAL_SETUP.md`), **do not commit `.env`**.

3. Build and run with Docker Compose (recommended):
```bash
docker-compose up --build
```

Frontend (dev):
```bash
cd frontend
npm install
npm run dev
```

Backend (dev):
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

ML service (dev):
```bash
cd ml-service
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/grpc/server.py
```

## Docker setup
- Root `docker-compose.yml` orchestrates `frontend`, `backend`, and `ml-service` along with MinIO, Postgres, Redis.
- Use environment variables to provide credentials (see `LOCAL_SETUP.md`).

## API Documentation
- OpenAPI docs available at `http://localhost:8000/docs` when backend is running.
- Key endpoints:
   - `POST /api/v1/detections`: submit an image for inference
   - `GET /api/v1/history`: retrieve detection history
   - `POST /api/v1/auth/token`: get access token

See `backend/app/api` for request/response schemas.

## Screenshots
- Add screenshots under `frontend/public/screenshots/` and reference them here. (Placeholders present)

## Deployment
- Kubernetes manifests are in `k8s/base/`. Use kustomize overlays in `k8s/` as needed.
- For production, host model binaries in an object store (S3/MinIO) and fetch at startup rather than committing large binaries to Git.

## Future Improvements
- Move model weights to Git LFS or external artifact storage and provide automated download in CI/CD.
- Add CI for linting, tests, and container image scanning.
- Harden secrets management with HashiCorp Vault or cloud secret managers.

## Where to start
- Review `LOCAL_SETUP.md` for environment variables and local development steps.

---
For contributors: please follow the repository's contribution guidelines and avoid committing secrets or large binaries.

