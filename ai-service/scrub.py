"""
Auto-scrub script for anonymizing raw resume/interview documents.

Reads from resume_corpus/raw/, applies anonymization rules from
ANONYMIZATION_GUIDE.md, writes to resume_corpus/sanitized/.

Usage:
    python scrub.py                    # Scrub all files in raw/
    python scrub.py --file raw/foo.txt # Scrub a single file
    python scrub.py --dry-run          # Preview changes without writing

The output MUST be manually reviewed before committing.
"""

import argparse
import os
import re
from pathlib import Path

# Directories
RAW_DIR = Path(__file__).parent / "resume_corpus" / "raw"
SANITIZED_DIR = Path(__file__).parent / "resume_corpus" / "sanitized" / "mock_interviews"

# ──────────────────────────────────────────────────────────────
# Replacement mappings — company names → consulting descriptors
# ──────────────────────────────────────────────────────────────
COMPANY_REPLACEMENTS = {
    # Employers
    r"\bDeloitte\b": "a Big Four professional services firm",
    r"\bConsulting Firm B\b": "a mid-size technology consulting firm",
    # Clients & companies
    r"\bMeta\b": "a top-3 social media conglomerate",
    r"\bFacebook\b": "a top-3 social media conglomerate",
    r"\bDell\b": "a Fortune 100 technology manufacturer",
    r"\bKroger\b": "a top-5 US grocery retailer",
    r"\bExelon\b": "a Fortune 100 energy utility",
    r"\bWake Forest\b": "a regional academic medical center",
    r"\bFinancial Services Program\b": "a multi-state community banking group",
    r"\bNGA\b": "a federal defense intelligence agency",
    r"\bDoD\b": "the Department of Defense",
    r"\bDoJ\b": "the Department of Justice",
    # Interview companies (from transcript filenames and content)
    r"\bRiot Games?\b": "a major gaming company",
    r"\bRiot\b": "a major gaming company",
    r"\bGoogle\b": "a leading technology company",
    r"\bgTech\b": "a technical solutions division at a leading technology company",
    r"\bBCG\b": "a top-3 management consulting firm",
    r"\bBoston Consulting Group\b": "a top-3 management consulting firm",
    r"\bBoeing\b": "a Fortune 50 aerospace and defense company",
    r"\bFanDuel\b": "a leading sports technology company",
    r"\bJP Morgan\b": "a top-3 global financial institution",
    r"\bJPMorgan\b": "a top-3 global financial institution",
    r"\bKPMG\b": "a Big Four professional services firm",
    r"\bWavestone\b": "a European management consulting firm",
    r"\bGuidehouse\b": "a federal technology consulting firm",
    r"\bTwelveLabs\b": "an AI video understanding startup",
    r"\bExtraHop\b": "a network security analytics company",
    r"\bPortswigger\b": "a web security tooling company",
    r"\bMoody'?s\b": "a global financial analytics company",
    r"\bBloomberg\b": "a global financial data company",
    r"\bCare\s*First\b": "a regional health insurance provider",
    r"\bBlue Cross\b": "a national health insurance provider",
    r"\bRecorded Future\b": "a threat intelligence company",
    r"\bLogic\s*20/?20\b": "a federal IT services company",
    r"\bL20\s*20\b": "a federal IT services company",
    r"\bbeacon\s*hills?\b": "a technology staffing firm",
    r"\bFairly\b": "a proptech startup",
    r"\bVacasa\b": "a vacation rental management company",
    r"\bMicroStrategy\b": "an enterprise BI platform",
    r"\bOracle\b": "an enterprise database and cloud company",
    r"\bPeopleSoft\b": "a legacy HR management system",
}

# ──────────────────────────────────────────────────────────────
# PII patterns
# ──────────────────────────────────────────────────────────────
PII_REPLACEMENTS = {
    # Real name variations
    r"\bKyle\s+Candidate\b": "the candidate",
    r"\bcandidate\s+Candidate\b": "the candidate",
    r"\bCandidate\b": "the candidate",
    # Phone numbers
    r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b": "[PHONE REDACTED]",
    # Email addresses (generic pattern)
    r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b": "[EMAIL REDACTED]",
    # LinkedIn URLs
    r"https?://(?:www\.)?linkedin\.com/in/[a-zA-Z0-9_-]+/?": "[LINKEDIN REDACTED]",
    # Street addresses (basic pattern)
    r"\b\d+\s+[A-Z][a-z]+\s+(?:St|Ave|Blvd|Dr|Rd|Ln|Way|Ct)\b": "[ADDRESS REDACTED]",
    # Clearance levels
    r"\bTop Secret/?SCI\b": "[CLEARANCE LEVEL]",
    r"\bTS/?SCI\b": "[CLEARANCE LEVEL]",
    r"\bSecret\s+clearance\b": "[CLEARANCE LEVEL]",
}

# ──────────────────────────────────────────────────────────────
# Interviewer names — common first names from transcripts
# These get replaced with generic labels
# ──────────────────────────────────────────────────────────────
INTERVIEWER_PATTERNS = [
    # Named interviewers from filenames
    r"\bYev\b",
    r"\bErika\b",
    r"\bRyan\b",
    r"\bJeff Kim\b",
    r"\bWalter\b",
    r"\bEric Breon\b",
]


def scrub_text(text: str, filename: str = "") -> str:
    """Apply all anonymization rules to a text string."""
    result = text

    # 1. PII first (most specific patterns)
    for pattern, replacement in PII_REPLACEMENTS.items():
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

    # 2. Company names
    for pattern, replacement in COMPANY_REPLACEMENTS.items():
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

    # 3. Interviewer names → "the interviewer"
    for pattern in INTERVIEWER_PATTERNS:
        result = re.sub(pattern, "the interviewer", result, flags=re.IGNORECASE)

    # 4. Remove Otter AI attribution lines
    result = re.sub(r"^.*otter\.ai.*$", "", result, flags=re.MULTILINE | re.IGNORECASE)
    result = re.sub(r"^.*Transcribed by.*$", "", result, flags=re.MULTILINE)

    # 5. Clean up multiple blank lines
    result = re.sub(r"\n{3,}", "\n\n", result)

    return result.strip()


def scrub_filename(filename: str) -> str:
    """Anonymize a filename by removing company/person references."""
    name = filename
    # Remove company names from filenames
    for pattern, replacement in COMPANY_REPLACEMENTS.items():
        clean_pattern = pattern.replace(r"\b", "").replace("?", "")
        name = re.sub(clean_pattern, "", name, flags=re.IGNORECASE)

    # Remove interviewer names
    for pattern in INTERVIEWER_PATTERNS:
        clean_pattern = pattern.replace(r"\b", "")
        name = re.sub(clean_pattern, "", name, flags=re.IGNORECASE)

    # Remove "otter_ai" suffix
    name = re.sub(r"_otter_ai", "", name, flags=re.IGNORECASE)
    name = re.sub(r"\(\d+\)", "", name)  # Remove (1) suffixes

    # Clean up underscores and spaces
    name = re.sub(r"[_\s]+", "_", name).strip("_")
    name = re.sub(r"_+", "_", name)

    return name if name else "interview_transcript"


def process_file(raw_path: Path, output_dir: Path, dry_run: bool = False) -> str:
    """Process a single file: read, scrub, write."""
    text = raw_path.read_text(encoding="utf-8", errors="replace")
    scrubbed = scrub_text(text, raw_path.name)

    # Anonymize the output filename too
    clean_name = scrub_filename(raw_path.stem) + ".md"
    output_path = output_dir / clean_name

    if dry_run:
        print(f"\n{'='*60}")
        print(f"  {raw_path.name} → {clean_name}")
        print(f"{'='*60}")
        # Show first 500 chars of scrubbed output
        print(scrubbed[:500])
        print(f"\n... ({len(scrubbed)} chars total)")
        return clean_name

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path.write_text(scrubbed, encoding="utf-8")
    print(f"  ✓ {raw_path.name} → {clean_name}")
    return clean_name


def main():
    parser = argparse.ArgumentParser(description="Anonymize raw resume/interview documents")
    parser.add_argument("--file", type=str, help="Scrub a single file from raw/")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    args = parser.parse_args()

    if not RAW_DIR.exists():
        print(f"Error: {RAW_DIR} does not exist. Place raw documents there first.")
        return

    if args.file:
        raw_path = RAW_DIR / args.file if not Path(args.file).is_absolute() else Path(args.file)
        if not raw_path.exists():
            print(f"Error: {raw_path} not found")
            return
        process_file(raw_path, SANITIZED_DIR, args.dry_run)
    else:
        files = sorted(RAW_DIR.glob("*.txt"))
        if not files:
            print(f"No .txt files found in {RAW_DIR}")
            return

        print(f"Scrubbing {len(files)} files from {RAW_DIR}...")
        if args.dry_run:
            print("(DRY RUN — no files will be written)\n")

        for f in files:
            process_file(f, SANITIZED_DIR, args.dry_run)

        if not args.dry_run:
            print(f"\nDone. {len(files)} files written to {SANITIZED_DIR}")
            print("⚠️  REVIEW the sanitized files before committing!")


if __name__ == "__main__":
    main()
