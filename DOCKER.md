# Docker Deployment Guide

## Quick Start

### Prerequisites
- Docker installed ([Get Docker](https://docs.docker.com/get-docker/))
- Docker Compose installed (included with Docker Desktop)

### Run Locally

```bash
cd /path/to/StartupSimulator
docker-compose up
```

Visit http://localhost:5000

To stop:
```bash
docker-compose down
```

---

## What's Included

### Docker Image
- **Base**: `python:3.12-slim`
- **Size**: ~300MB
- **Python Version**: 3.12
- **Installed Packages**: Flask, matplotlib, requests, and dependencies

### Docker Compose Setup
- Single-service configuration for local development
- Automatic volume mounting for scenarios and configs
- Environment variables pre-configured
- Auto-restart on failure

---

## Detailed Setup

### 1. Build the Image

```bash
docker build -t startup-simulator:1.0.0 .
```

### 2. Run Container

```bash
# Basic run
docker run -p 5000:5000 startup-simulator:1.0.0

# With volume mounting for persistence
docker run -p 5000:5000 \
  -v $(pwd)/scenarios:/app/scenarios \
  -v $(pwd)/configs:/app/configs \
  startup-simulator:1.0.0

# Detached mode with name
docker run -d --name simulator \
  -p 5000:5000 \
  -v $(pwd)/scenarios:/app/scenarios \
  startup-simulator:1.0.0
```

### 3. Using Docker Compose (Recommended)

```bash
# Start
docker-compose up

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down

# Remove volumes too
docker-compose down -v
```

---

## Configuration

### Environment Variables

Set these in `docker-compose.yml` to customize:

```yaml
environment:
  FLASK_ENV: production      # Set to 'development' for debug mode
  FLASK_APP: src/webapp.py   # Flask app entry point
  PORT: 5000                 # Port (mapped via ports config)
```

### Volumes

The Compose file mounts:
- `./scenarios:/app/scenarios` - Saved scenario data
- `./configs:/app/configs` - Configuration files

These persist data between container restarts.

---

## Common Commands

### Check Container Status
```bash
docker ps
docker ps -a  # Including stopped containers
```

### View Logs
```bash
docker logs <container_id>
docker logs -f <container_id>  # Follow logs
docker-compose logs -f          # Follow compose logs
```

### Execute Commands in Container
```bash
docker exec -it <container_id> /bin/bash
docker-compose exec simulator bash
```

### Stop and Remove
```bash
docker stop <container_id>
docker rm <container_id>
docker rmi startup-simulator:1.0.0  # Remove image
```

### Clean Up
```bash
docker system prune              # Remove unused resources
docker system prune -a           # Remove all unused
docker image prune               # Remove unused images
```

---

## Production Deployment

### Best Practices

1. **Use a Web Server**
   - Don't run Flask directly in production
   - Use Gunicorn, uWSGI, or similar

2. **Add Nginx Reverse Proxy**
   ```yaml
   version: '3.8'
   services:
     web:
       build: .
       expose:
         - 5000
       restart: always
     
     nginx:
       image: nginx:latest
       ports:
         - "80:80"
       volumes:
         - ./nginx.conf:/etc/nginx/nginx.conf:ro
       depends_on:
         - web
       restart: always
   ```

3. **Use Production WSGI Server**
   ```bash
   # In Dockerfile
   RUN pip install gunicorn
   CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "src.webapp:app"]
   ```

4. **Environment Security**
   - Use `.env` files (not in repo)
   - Use secrets management for production
   - Never commit credentials

5. **Logging**
   - Mount log volumes
   - Use centralized logging (ELK, Splunk, etc.)

6. **Monitoring**
   - Add health check endpoint
   - Use monitoring tools (Prometheus, DataDog, etc.)
   - Set up alerts

---

## Docker Hub (Optional)

### Push to Registry

```bash
# Login
docker login

# Tag image
docker tag startup-simulator:1.0.0 yourusername/startup-simulator:1.0.0

# Push
docker push yourusername/startup-simulator:1.0.0
```

### Pull and Run
```bash
docker run -p 5000:5000 yourusername/startup-simulator:1.0.0
```

---

## Troubleshooting

### Container Won't Start
```bash
docker logs <container_id>
# Check for Python errors or port conflicts
```

### Port Already in Use
```bash
# Change port mapping in docker-compose.yml
ports:
  - "5001:5000"  # Use 5001 instead

# Or kill the process
lsof -i :5000
kill -9 <PID>
```

### Volume Mount Issues (Windows)
```yaml
# Use full paths
volumes:
  - C:\Users\YourName\project\scenarios:/app/scenarios
```

### Data Not Persisting
```bash
# Ensure volumes are mounted
docker inspect <container_id> | grep -A 10 Mounts

# Data should be in ./scenarios and ./configs
```

### Out of Disk Space
```bash
# Clean up Docker
docker system prune -a
docker volume prune
```

---

## Advanced Configuration

### Custom Dockerfile for Production

```dockerfile
FROM python:3.12-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.12-slim
WORKDIR /app
ENV PATH=/root/.local/bin:$PATH

# Copy only necessary files
COPY --from=builder /root/.local /root/.local
COPY src/ ./src/
COPY scenarios/ ./scenarios/
COPY configs/ ./configs/

# Install Gunicorn
RUN pip install gunicorn

EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "--access-logfile", "-", "src.webapp:app"]
```

### Docker Compose with Multiple Services

```yaml
version: '3.8'

services:
  simulator:
    build: .
    ports:
      - "5000:5000"
    environment:
      FLASK_ENV: production
    volumes:
      - scenarios:/app/scenarios
      - configs:/app/configs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:latest
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - simulator
    restart: unless-stopped

volumes:
  scenarios:
  configs:
```

---

## Performance Tuning

### Memory Limits
```yaml
services:
  simulator:
    mem_limit: 512m
    memswap_limit: 512m
```

### CPU Limits
```yaml
services:
  simulator:
    cpus: '0.5'
    cpuset: '0,1'
```

### Resource Requests
```yaml
services:
  simulator:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

---

## Integration Examples

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: startup-simulator
spec:
  replicas: 3
  selector:
    matchLabels:
      app: startup-simulator
  template:
    metadata:
      labels:
        app: startup-simulator
    spec:
      containers:
      - name: simulator
        image: startup-simulator:1.0.0
        ports:
        - containerPort: 5000
        env:
        - name: FLASK_ENV
          value: production
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

### AWS ECS Task Definition

```json
{
  "family": "startup-simulator",
  "containerDefinitions": [
    {
      "name": "simulator",
      "image": "youraccount.dkr.ecr.us-east-1.amazonaws.com/startup-simulator:1.0.0",
      "portMappings": [
        {
          "containerPort": 5000
        }
      ],
      "memory": 512,
      "environment": [
        {
          "name": "FLASK_ENV",
          "value": "production"
        }
      ]
    }
  ]
}
```

---

## Support & Issues

For Docker-specific issues:
1. Check logs: `docker logs <container_id>`
2. Rebuild image: `docker build --no-cache .`
3. Check Docker documentation: https://docs.docker.com/

For application issues, see the main README.md
