# Use Python 3.12 slim image for minimal size
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY scenarios/ ./scenarios/
COPY configs/ ./configs/

# Expose Flask port
EXPOSE 5000

# Set working directory for Python modules
WORKDIR /app/src

# Run Flask app
CMD ["python", "-m", "flask", "--app", "webapp", "run", "--host", "0.0.0.0"]
