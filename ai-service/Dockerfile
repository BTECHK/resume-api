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

# Cache location for the embedding model — set before download so files land here directly
ENV HF_HOME=/home/appuser/.cache/huggingface
ENV TRANSFORMERS_CACHE=/home/appuser/.cache/huggingface

# Pre-download the embedding model (33MB) to speed up cold starts.
# Best-effort: if HF Hub is rate-limiting the build, fall back to runtime download.
RUN mkdir -p "$HF_HOME" \
 && (python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('paraphrase-MiniLM-L3-v2')" \
     || echo "WARN: HF model pre-download failed; will fetch at runtime")

# Copy application code
COPY . .

# Set ownership (model cache + app code)
RUN chown -R appuser:appuser /app /home/appuser

# Switch to non-root
USER appuser

EXPOSE 8080

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"]
