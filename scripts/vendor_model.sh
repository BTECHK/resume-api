#!/usr/bin/env bash
# Re-download the MiniLM embedding model from HuggingFace Hub and save it into
# ai-service/model/ so it can be vendored in-repo. Run this manually only when
# switching models — the weights are committed to git (see ADR-0001).
#
# Usage:  bash scripts/vendor_model.sh
set -euo pipefail

MODEL_NAME="paraphrase-MiniLM-L3-v2"
OUT_DIR="ai-service/model/${MODEL_NAME}"

python - <<PY
from sentence_transformers import SentenceTransformer
m = SentenceTransformer("${MODEL_NAME}")
m.save("${OUT_DIR}")
print("Saved to ${OUT_DIR}")
PY

echo "Now: git add ${OUT_DIR} && git commit -m 'chore: re-vendor ${MODEL_NAME}'"
