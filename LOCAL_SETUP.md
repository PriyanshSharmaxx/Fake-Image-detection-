# Local Development Setup (Without Docker)

## Prerequisites

### 1. Install System Dependencies

#### macOS
```bash
# Using Homebrew
brew install postgresql@15
brew install redis
brew install python@3.10
brew install node@18
```

#### Verify Installation
```bash
postgres --version
redis-cli --version
python3 --version
node --version
npm --version
```

---

## Setup Instructions

### STEP 1: Start PostgreSQL (Terminal 1)

```bash
# Start PostgreSQL server
brew services start postgresql@15

# Verify it's running
psql --version
psql -U postgres

# Create database
createdb -U postgres deepfake_db

# Exit psql
\q
```

**Verify Database**:
```bash
psql -U postgres -d deepfake_db -c "SELECT 1;"
```

---

### STEP 2: Start Redis (Terminal 2)

```bash
# Start Redis server
redis-server

# Keep this terminal open (Redis will show logs)
```

**In another terminal, verify**:
```bash
redis-cli ping
# Should return: PONG
```

---

### STEP 3: Setup Backend (Terminal 3)

```bash
cd "/Users/priyanshsharma/Downloads/fake detectionn/final vs project/backend"

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file
cat > .env << 'EOF'
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/deepfake_db
REDIS_URL=redis://localhost:6379/0
GRPC_INFERENCE_HOST=localhost
GRPC_INFERENCE_PORT=50051
AWS_ACCESS_KEY_ID=minioadmin
AWS_SECRET_ACCESS_KEY=minioadmin
S3_ENDPOINT_URL=http://localhost:9000
S3_BUCKET_NAME=uploads
S3_REGION_NAME=us-east-1
SECRET_KEY=your-secret-key-change-in-production
EOF

# Run database migrations
alembic upgrade head

# Start backend API
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Backend will be available at**: http://localhost:8000/docs

---

### STEP 4: Setup ML Service (Terminal 4)

```bash
cd "/Users/priyanshsharma/Downloads/fake detectionn/final vs project/ml-service"

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Compile gRPC proto
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. src/grpc/inference.proto

# Start gRPC server
python -m src.grpc.server
```

**gRPC Server will listen on**: localhost:50051

---

### STEP 5: Setup Frontend (Terminal 5)

```bash
cd "/Users/priyanshsharma/Downloads/fake detectionn/final vs project/frontend"

# Install dependencies
npm install

# Create .env.local
cat > .env.local << 'EOF'
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
EOF

# Start development server
npm run dev
```

**Frontend will be available at**: http://localhost:3000

---

## Quick Start Command Reference

### Terminal 1: PostgreSQL
```bash
brew services start postgresql@15
# Logs: /usr/local/var/log/postgres.log
```

### Terminal 2: Redis
```bash
redis-server
```

### Terminal 3: Backend
```bash
cd backend
source venv/bin/activate
python -m uvicorn app.main:app --reload --port 8000
```

### Terminal 4: ML Service
```bash
cd ml-service
source venv/bin/activate
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. src/grpc/inference.proto
python -m src.grpc.server
```

### Terminal 5: Frontend
```bash
cd frontend
npm run dev
```

---

## Verify All Services Running

Open a new terminal and run:

```bash
# Check PostgreSQL
psql -U postgres -d deepfake_db -c "SELECT 1;" && echo "✓ PostgreSQL OK"

# Check Redis
redis-cli ping && echo "✓ Redis OK"

# Check Backend
curl http://localhost:8000/health 2>/dev/null && echo "✓ Backend OK" || echo "✗ Backend not ready"

# Check Frontend
curl http://localhost:3000 2>/dev/null && echo "✓ Frontend OK" || echo "✗ Frontend not ready"

# Check gRPC (optional)
python3 -c "import grpc; print('✓ gRPC available')" 2>/dev/null || echo "✗ gRPC check requires grpcio"
```

---

## Access Services

| Service | URL |
|---------|-----|
| **Frontend** | http://localhost:3000 |
| **Backend API Docs** | http://localhost:8000/docs |
| **Backend API** | http://localhost:8000/api/v1 |
| **PostgreSQL** | localhost:5432 |
| **Redis** | localhost:6379 |
| **gRPC Server** | localhost:50051 |

---

## Testing the Full Flow

1. **Open Frontend**: http://localhost:3000
2. **Register/Login** with test credentials
3. **Upload Image**: Use the dashboard uploader
4. **Analyze**: Click analyze button
5. **View Results**: Check confidence, verdict, and heatmap
6. **Check History**: View past detections

---

## Troubleshooting

### PostgreSQL Connection Error
```bash
# Check if PostgreSQL is running
brew services list | grep postgres

# If not running, start it
brew services start postgresql@15

# Check connection
psql -U postgres
```

### Redis Connection Error
```bash
# Check if Redis is running
redis-cli ping

# If error, start Redis
redis-server
```

### gRPC Compilation Error
```bash
# Make sure grpc-tools is installed
pip install grpcio-tools

# Recompile proto
cd ml-service
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. src/grpc/inference.proto
```

### ML Service Model Not Found
```bash
# Ensure model files exist
ls -lh /Users/priyanshsharma/Downloads/fake\ detectionn/final\ vs\ project/*.pth
ls -lh /Users/priyanshsharma/Downloads/fake\ detectionn/final\ vs\ project/*.pt

# If missing, download or copy them to the workspace root
```

### Port Already in Use
```bash
# Find process using port
lsof -i :8000    # Backend
lsof -i :3000    # Frontend
lsof -i :5432    # PostgreSQL
lsof -i :6379    # Redis
lsof -i :50051   # gRPC

# Kill the process (replace PID)
kill -9 <PID>
```

---

## Stopping All Services

### Clean Shutdown (in each terminal)
```bash
# Backend/ML Service: Press Ctrl+C
# Frontend: Press Ctrl+C
# Redis: Press Ctrl+C

# PostgreSQL
brew services stop postgresql@15

# Redis (if using services)
brew services stop redis
```

---

## Environment Variables (.env files)

### Backend: `backend/.env`
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/deepfake_db
REDIS_URL=redis://localhost:6379/0
GRPC_INFERENCE_HOST=localhost
GRPC_INFERENCE_PORT=50051
AWS_ACCESS_KEY_ID=minioadmin
AWS_SECRET_ACCESS_KEY=minioadmin
S3_ENDPOINT_URL=http://localhost:9000
S3_BUCKET_NAME=uploads
SECRET_KEY=your-secret-key-change-in-production
```

### Frontend: `frontend/.env.local`
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

---

## Database Migrations

### Run Migrations
```bash
cd backend
source venv/bin/activate
alembic upgrade head
```

### Rollback Migrations
```bash
alembic downgrade -1
```

### Create New Migration
```bash
alembic revision --autogenerate -m "description"
```

---

## Logs & Debugging

### Backend Logs
```bash
# Tail real-time logs
tail -f /tmp/backend.log

# Or check stdout of running terminal
```

### ML Service Logs
```bash
# Check stdout of running terminal
# Look for model loading messages and inference logs
```

### PostgreSQL Logs
```bash
tail -f /usr/local/var/log/postgres.log
```

### Redis Logs
```bash
# Check stdout of running terminal
```

---

## Performance Notes

### Expected Startup Times
- PostgreSQL: 2-3 seconds
- Redis: 1-2 seconds
- Backend: 5-10 seconds (dependency loading)
- ML Service: 10-30 seconds (model loading + warmup)
- Frontend: 5-10 seconds (Next.js build)

### Expected Inference Time
- First request: 100-500ms (warm-up)
- Subsequent requests: 50-150ms per image (GPU), 200-500ms (CPU)

---

## Next Steps

1. Verify all services are running
2. Test the upload/analysis flow
3. Check database for saved detections
4. Review logs for any errors
5. Deploy to production using Docker

