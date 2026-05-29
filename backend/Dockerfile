FROM python:3.10-slim

WORKDIR /workspace

# Install system dependencies (build-essential for compiling grpc)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create app directory structure
RUN mkdir -p app/services/grpc

# Copy protobuf definition and source code
COPY ./app/services/grpc/__init__.py ./app/services/grpc/__init__.py
# During build, we will expect inference.proto to be inside app/services/grpc
# Or we can build it from a build arg. Let's design the Dockerfile to expect
# inference.proto to be copied locally first, then compiled.
COPY ./app/services/grpc/inference.proto ./app/services/grpc/inference.proto

# Compile protobufs to Python grpc files
RUN python -m grpc_tools.protoc \
    -I. \
    --python_out=. \
    --grpc_python_out=. \
    app/services/grpc/inference.proto

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
