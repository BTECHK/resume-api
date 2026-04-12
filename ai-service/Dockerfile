# Single-stage build: install deps + download model in one image
# CPU-only PyTorch avoids ~2.5GB of NVIDIA/CUDA libs
FROM python:3.11-slim

# Security: non-root user
RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /sbin/nologin appuser

WORKDIR /app

# Install all Python deps in one pip invocation (one resolver pass, one download round)
COPY requirements.txt .
RUN pip install --no-cache-dir \
      torch --index-url https://download.pytorch.org/whl/cpu \
 && pip install --no-cache-dir -r requirements.txt

# Embedding model is vendored in ./model/ (see ADR-0001) — no HF Hub call at
# build or runtime. TRANSFORMERS_OFFLINE ensures the library never tries.
ENV TRANSFORMERS_OFFLINE=1
ENV HF_HUB_OFFLINE=1

# Copy application code (includes ./model/paraphrase-MiniLM-L3-v2/)
COPY . .

# Set ownership on app code (includes vendored model under ./model/)
RUN chown -R appuser:appuser /app

# Switch to non-root
USER appuser

EXPOSE 8080

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"]
