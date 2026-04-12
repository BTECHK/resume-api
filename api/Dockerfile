# ---- Stage 1: Builder ----
# Install dependencies in an isolated virtual environment
FROM python:3.11-slim AS builder

# Create a virtual environment 
RUN python -m venv /opt/venv
#Ensure the venv's bin is first in PATH so pip/python resolve there
ENV PATH="/opt/venv/bin:$PATH"

# Copy only requirements first (Docker caches this layer —
# dependencies only reinstall if requirements.txt changes)
COPY api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---- Stage 2: Runtime ----
# Start fresh — no build tools, just Python
FROM python:3.11-slim 

# Copy the prebuilt virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install curl (needed for Docker healthcheck in docker-compose.yml)
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*
# Set the working directory inside the container 
WORKDIR /app

# Copy the API application code and shared YAML data + loader
COPY api/ ./
COPY ai-service/loader.py ./ai_service/
COPY ai-service/data/ ./ai_service/data/

# Create a non root user for security - if someone exploits the app, they can't modify the system files 
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Start the FastAPI server
# Main:app because the Dockerfile is in api/, so main.py is at the root
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]