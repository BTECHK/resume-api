# SEC-04: pin base image by digest
# To refresh:
#   docker pull python:3.11-slim
#   docker inspect --format='{{index .RepoDigests 0}}' python:3.11-slim
# Then replace the tag below with python@sha256:<digest>.
# Placeholder tag form is kept for local builds; CI should enforce the digest form.
FROM python:3.11-slim AS model-downloader

RUN pip install --no-cache-dir sentence-transformers

# Download the small model (33MB) — critical for fast cold starts
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('paraphrase-MiniLM-L3-v2')"

# Stage 2: Production image — same pinning rule applies
FROM python:3.11-slim

# Security: non-root user
RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /sbin/nologin appuser

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy baked model from downloader stage
COPY --from=model-downloader /root/.cache/huggingface /home/appuser/.cache/huggingface

# Copy application code
COPY . .

# Copy corpus examples (sanitized only — raw is gitignored)
# resume_corpus/sanitized/ and resume_corpus/examples/ are included
# resume_corpus/raw/ is excluded via .dockerignore

# Set ownership
RUN chown -R appuser:appuser /app /home/appuser

# Switch to non-root
USER appuser

# Set cache dir for sentence-transformers
ENV TRANSFORMERS_CACHE=/home/appuser/.cache/huggingface
ENV HF_HOME=/home/appuser/.cache/huggingface

EXPOSE 8090

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8090/health')" || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8090"]
