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

# Download the embedding model (33MB) into appuser's cache
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('paraphrase-MiniLM-L3-v2')" \
 && mv /root/.cache/huggingface /home/appuser/.cache/huggingface

# Copy application code
COPY . .

# Set ownership
RUN chown -R appuser:appuser /app /home/appuser

# Switch to non-root
USER appuser

ENV TRANSFORMERS_CACHE=/home/appuser/.cache/huggingface
ENV HF_HOME=/home/appuser/.cache/huggingface

EXPOSE 8080

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"]
