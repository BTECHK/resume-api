# Resume Corpus

This directory contains the knowledge base for the RAG-powered resume chatbot.

## Directory Structure

```
resume_corpus/
├── raw/              # GITIGNORED — Original documents with PII. Never committed.
├── sanitized/        # Anonymized versions ready for RAG ingestion. Committed.
│   ├── work_experience.md    # Tier 1: Anchor document (anonymized work history)
│   ├── star_stories.md       # Tier 2: Behavioral interview answers (anonymized)
│   ├── architecture_faq.md   # Tier 1: How and why this system was built
│   └── mock_interviews/      # Tier 2: Sanitized interview Q&A patterns
└── examples/         # Sample documents showing the anonymization pattern. Committed.
```

## Two-Tier RAG System

- **Tier 1 (Resume Facts)**: Work experience, skills, certifications, accomplishments. Always retrieved. Grounding source of truth.
- **Tier 2 (Mock Interview Patterns)**: How the candidate talks about their work. Supplementary. Informs framing and style, never referenced as "interview" context.

## Anonymization Rules

All sanitized documents follow `ANONYMIZATION_GUIDE.md` in the repo root:
- No real names — use "the candidate"
- No company names — use consulting-style descriptors
- Certifications and skills are named directly
- Metrics and outcomes preserved
- Interview context never surfaces — only the question/answer patterns

## Workflow

1. Place raw documents in `raw/` (gitignored, never committed)
2. Run `python scrub.py` to auto-anonymize → outputs to `sanitized/`
3. Review sanitized output manually
4. Commit sanitized files
5. RAG ingestion reads from `sanitized/` only
