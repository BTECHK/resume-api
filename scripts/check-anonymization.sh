#!/usr/bin/env bash
# ----------------------------------------------------------------
# Build-time anonymization check (D-09)
#
# Scans ai-service/ source files for PII deny-list terms.
# Exits non-zero if any real names, company names, or personal
# contact info are found. Designed to run in CI (Phase 8) or
# locally before commits.
#
# Usage: bash scripts/check-anonymization.sh
# ----------------------------------------------------------------

set -euo pipefail

TARGET_DIR="ai-service"
# Only scan source files, not binaries or caches
INCLUDE_FLAGS="--include=*.py --include=*.txt --include=*.md --include=*.json --include=*.yaml --include=*.yml"

# Exclude paths that legitimately contain deny-list terms:
# - scrub.py and security.py own the deny-list as part of the sanitizer
# - resume_corpus/raw/** is non-anonymized source by design (gitignored in prod,
#   but developers may have local copies and it's the wrong target to scan)
# - tests/** references the deny-list to verify scrubbing works
EXCLUDE_FLAGS="--exclude-dir=__pycache__ --exclude-dir=resume_corpus --exclude-dir=tests --exclude=scrub.py --exclude=security.py"

# Deny-list: real names, company names, personal contact info
# Derived from ANONYMIZATION_GUIDE.md
DENY_PATTERNS=(
    "the candidate"
    "Candidate"
    "the candidate\.candidate"
    "candidatecandidate"
    "Deloitte"
    "Consulting Firm B"
    "Healthcare Program"
    "Financial Services Program"
    "linkedin\.com/in/the candidate"
)

FOUND=0

for pattern in "${DENY_PATTERNS[@]}"; do
    # shellcheck disable=SC2086
    if grep -rEi $INCLUDE_FLAGS $EXCLUDE_FLAGS "$pattern" "$TARGET_DIR" 2>/dev/null | grep -v "\.pyc"; then
        echo "FAIL: Found deny-list term matching: $pattern"
        FOUND=1
    fi
done

if [ "$FOUND" -eq 0 ]; then
    echo "PASS: No PII deny-list terms found in $TARGET_DIR"
    exit 0
else
    echo ""
    echo "FAIL: PII deny-list terms detected in $TARGET_DIR"
    echo "Fix: Replace real names/companies with anonymized descriptors per ANONYMIZATION_GUIDE.md"
    exit 1
fi
