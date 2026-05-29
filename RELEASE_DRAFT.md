# v1.0.0 — Production-ready release

## Summary
Production-ready release of DeepFake Shield — an end-to-end DeepFake and AI-generated image detection platform.

## Highlights
- Next.js frontend, FastAPI backend, and PyTorch inference gRPC service
- TorchScript production model included at `ml-service/models/deepfake_model_scripted.pt`
- Docker Compose and Kubernetes manifests (secrets now required via env or K8s Secret)
- Monitoring with Prometheus and Grafana

## Features
- Real-time image detection pipeline (spatial + frequency ensembles)
- Explainability with Grad-CAM
- REST API with OpenAPI docs
- Object storage integration (S3/MinIO), Postgres, Redis

## Architecture
Frontend (Next.js) ↔ Backend (FastAPI) ↔ ML Service (gRPC PyTorch)
Storage: Postgres (metadata), MinIO/S3 (artifacts)

## Model details
- `ml-service/models/deepfake_model_scripted.pt` — TorchScript model (production priority)
- Other variants removed from repo root to avoid duplication. Consider Git LFS or external artifact storage for large models.

## Deployment
1. Copy `.env.example` to `.env` and populate secrets (do NOT commit `.env`).
2. Local dev: `docker-compose up --build`
3. For Kubernetes, create Secrets for DB, MinIO and other credentials; manifests are in `k8s/base/`.

## Security notes
- `SECRET_KEY` must be set in environment; backend will fail to start if missing.

## Future roadmap
- CI pipelines for lint/test/build
- Move models to artifact registry or Git LFS
- Secrets management with Vault or cloud secret manager
