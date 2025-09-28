# PDF Sanitizer Service

Service to sanitize PDF files uploaded to external services.

## Requirements

- Python 3.10
- pip
- docker (optional, for containerized deployment)

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Sanitize PDF

```bash
curl -X POST \
  http://localhost:8000/api/v1/upload/00000000-0000-0000-0000-000000000000 \
  -F file=@/path/to/file.pdf
```

### List available services

```bash
curl http://localhost:8000/api/v1/upload
```

## Development

### Start server

```bash
uvicorn app.main:app --reload
```

### Run tests

```bash
PYTHONPATH=$(pwd) pytest -q
```

## Deployment

### Docker Compose

Build the Docker image:

```bash
docker-compose build
```

Run the Docker container:

```bash
docker-compose up
```

Stop the Docker container:

```bash
docker-compose down
```

### Kubernetes

Create a Kubernetes deployment:

```bash
kubectl apply -f k8s/deployment.yaml
```

Create a Kubernetes service:

```bash
kubectl apply -f k8s/service.yaml
```
