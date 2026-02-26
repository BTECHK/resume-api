# Project Context — Resume API
**Read this before every task. Do not implement anything beyond what is asked.**

## Project Purpose
This is a **technical portfolio project** demonstrating cloud engineering and API design skills. It demonstrates:
- API design and REST principles (FastAPI)
- Dual-database architecture (SQLite for serving, BigQuery for analytics)
- SQL progression from naive queries to optimized/partitioned approaches
- Cloud deployment (Docker → Cloud Run)
- Data modeling that mirrors digital advertising reporting patterns
- Technical documentation and design decision communication

The project is intentionally scoped as a read-only Resume API with simulated analytics data. The data model maps to ad tech concepts: recruiter_domain ≈ advertiser, endpoint_hit ≈ campaign, skill_searched ≈ keyword, response_time_ms ≈ latency.

## Implementation Scope
The full project has 5 phases:
1. Environment setup (Firebase Studio, dependencies, dev.nix)
2. Build the API (endpoints, data generation, Dockerfile)
3. BigQuery setup (upload CSV, write tiered SQL queries)
4. Deploy to Cloud Run (Docker build, gcloud deploy)
5. GitHub + README (documentation, screenshots, design decisions)

**I am working through these phases one step at a time. Architecture decisions are informed by both Gemini and Claude. I will tell you which step I'm on and what I need you to do. Do not skip ahead, combine steps, or implement future phases.**

## Roles & Responsibilities

### What I do:
- Decide which step to work on next
- Provide the specific prompt for what to build
- Run verification commands and confirm results
- Debug issues with my external coach
- Make architectural decisions

### What you (Gemini) do:
- Execute ONLY the specific task I give you
- Write code, create files, or fix bugs AS INSTRUCTED
- Explain what you did and why (briefly)
- Stop and ask if my instructions are ambiguous
- **Never** refactor existing code unless I specifically ask
- **Never** add features, dependencies, or files I didn't request
- **Never** overwrite configuration files (dev.nix, pyproject.toml, database.py) unless I specifically ask you to edit them

### What you should NOT do:
- Run ahead to the next step
- "Improve" working code without being asked
- Add packages, imports, or dependencies I didn't request
- Change table names, file paths, or port numbers from what's documented below
- Replace `uv run` commands with bare `uvicorn` or `python3`
- **Open, read, edit, or modify `.idx/dev.nix` for any reason**
- Assume what I want — ask if unclear

**This is a learning exercise.** I am building understanding as I go. Even if you know the "better" way to do something, wait for me to ask. If you see something that could cause a problem later, mention it briefly but do not fix it unless I say so.

## Environment
- **IDE:** Firebase Studio (Nix-based, ephemeral workspace)
- **Python:** 3.11 (managed by uv, NOT system python)
- **Package manager:** uv (NOT pip)
- **Project root:** ~/resume-api
- **Virtual env:** ~/resume-api/.venv (auto-managed by uv)
- **GCP project:** resume-api-portfolio
- **GCP region:** us-central1
- **Author's role:** Owner (project creator — all permissions already granted)

## Critical Commands
| Do This | NEVER Do This |
|---------|--------------|
| `uv run -- python -m uvicorn api.main:app` | `uvicorn api.main:app` |
| `uv run -- python script.py` | `python3 script.py` |
| `uv add package-name` | `pip install package-name` |
| `uv pip compile pyproject.toml -o requirements.txt` | `pip freeze > requirements.txt` |

**Why:** Nix intercepts bare commands (`uvicorn`, `python3`) and uses system Python, which doesn't have project packages installed. `uv run --` forces execution through the project's virtual environment.

## Project Structure
```
~/resume-api/
├── api/
│   ├── __init__.py       # Explicit package declaration
│   ├── main.py           # FastAPI app — endpoints + resume data + middleware
│   ├── models.py         # Pydantic response models (validation schemas)
│   └── database.py       # SQLite connection (DATABASE_FILE = "data/analytics.db")
├── benchmarks/           # Performance benchmarks (Python vs SQLite vs BigQuery)
│   ├── __init__.py
│   ├── benchmark_small.py
│   ├── benchmark_medium.py
│   └── benchmark_large.py
├── data/
│   ├── analytics.db      # SQLite database (10,000 rows in api_queries table)
│   ├── recruiter_queries.csv  # 500K rows for BigQuery upload
│   └── sql/              # BigQuery SQL queries (Tier 1, 2, 3)
├── docs/
│   ├── gemini-context.md # This file
│   ├── implementation-guide.md
│   ├── phase-2-implementation-guide.md
│   ├── phase-2-approach.md
│   ├── bug-fix-log.md
│   ├── PRD.md
│   └── screenshots/
├── scripts/              # Operational scripts (run from project root)
│   ├── __init__.py
│   ├── generate_data.py  # Creates fake analytics data (10K SQLite + 500K CSV)
│   ├── check_db.py
│   └── clean_db.py
├── tests/                # Test directory
│   ├── __init__.py
│   └── conftest.py
├── .idx/
│   └── dev.nix           # LOCKED — do NOT read or modify (git-protected)
├── Dockerfile            # Uses python:3.11-slim, pip install, port 8080
├── pyproject.toml        # Dependencies managed by uv
└── README.md
```

## How Components Connect

### Data Flow
```
scripts/generate_data.py
  ├─→ writes to: data/analytics.db (table: api_queries, 10K rows)
  └─→ writes to: data/recruiter_queries.csv (500K rows)

api/database.py
  └─→ reads from: data/analytics.db (DATABASE_FILE = "data/analytics.db")

api/main.py
  ├─→ imports: api/database.py (for SQLite connection)
  ├─→ imports: api/models.py (for Pydantic validation)
  ├─→ resume endpoints (/resume, /resume/experience, etc.)
  │     └─→ reads from: hardcoded Python dict in main.py (NOT from database)
  └─→ analytics endpoints (/analytics/queries, /analytics/top-domains, etc.)
        └─→ reads from: api_queries table in data/analytics.db (via database.py)

Dockerfile
  ├─→ copies: api/ directory
  ├─→ copies: data/analytics.db
  ├─→ installs from: requirements.txt (generated from pyproject.toml)
  └─→ runs: uvicorn api.main:app on port 8080

data/recruiter_queries.csv
  └─→ uploaded to: BigQuery (resume_analytics.recruiter_queries) in Phase 3
```

### Key Connections to Preserve
- `database.py` says `DATABASE_FILE = "data/analytics.db"` → data must be at that path
- Analytics endpoints in `main.py` query the `api_queries` table → that table must exist in `data/analytics.db`
- `models.py` defines Pydantic schemas that `main.py` uses for response validation → field names must match
- Resume data is a Python dict in `main.py` → NOT in the database, NOT in a JSON file
- The `queries` table in `analytics.db` is for live request logging → analytics endpoints must NOT read from it

## Database Schema
**SQLite table: `api_queries`** (in data/analytics.db) — the MAIN analytics table
- query_id, timestamp, recruiter_domain, endpoint_hit, skill_searched, response_time_ms, http_status, user_agent, referer_url
- 10,000 rows of simulated recruiter traffic

**SQLite table: `queries`** (in data/analytics.db) — live request log ONLY
- id, timestamp, domain, path, client_ip
- Created by database.py on startup, populated by middleware
- **Analytics endpoints must NEVER read from this table**

## API Endpoints
1. GET / — health check
2. GET /resume — full resume JSON (from hardcoded dict)
3. GET /resume/experience — ?company=, ?after= (from hardcoded dict)
4. GET /resume/skills — ?category=, ?keyword= (returns plain dict when filtering, NOT validated against full Pydantic model)
5. GET /resume/education (from hardcoded dict)
6. GET /resume/certifications (from hardcoded dict)
7. GET /analytics/queries — reads from `api_queries` table, ?domain=, ?limit=, ?offset=
8. GET /analytics/top-domains — aggregates `recruiter_domain` from `api_queries` table, ?n=
9. GET /analytics/performance — response time percentiles from `api_queries` table

## Ports
- **Local development:** 8000
- **Docker / Cloud Run:** 8080
- **Firebase Studio preview:** uses $PORT variable (falls back to 8000)

## When Things Need to Be Rebuilt

| If you change... | You must also... |
|-----------------|-----------------|
| Resume data in `api/main.py` | Restart uvicorn (auto if `--reload` is on) |
| `api/models.py` (Pydantic schemas) | Restart uvicorn AND check that main.py still matches |
| `api/database.py` (DB path or schema) | Restart uvicorn AND verify analytics endpoints still work |
| `scripts/generate_data.py` | Re-run it: `uv run -- python scripts/generate_data.py` |
| `pyproject.toml` (dependencies) | Run `uv sync` to install, then restart uvicorn |
| Dockerfile | Rebuild: `docker build -t resume-api .` |
| Any code, then want it in production | Rebuild Docker image AND redeploy to Cloud Run |
| `requirements.txt` | Regenerate: `uv pip compile pyproject.toml -o requirements.txt` |

**Cloud Run is stateless.** The Docker image is a snapshot. Changes to local files do NOT appear in production until you rebuild and redeploy.

## Common Errors and Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `ModuleNotFoundError: No module named 'fastapi'` | Used bare `python3` or `uvicorn` instead of `uv run --` | Always use `uv run -- python -m uvicorn ...` |
| `uvicorn is not installed` (Nix offers packages) | Typed bare `uvicorn` in terminal | Use `uv run -- python -m uvicorn ...` |
| 500 error on `/resume/skills?category=X` | Pydantic model requires all categories, filter returns one | Return filtered result as plain dict, skip Pydantic validation |
| `/analytics/top-domains` returns localhost | Endpoints reading from `queries` table instead of `api_queries` | Update endpoints to query `api_queries` table |
| `Address already in use` | Previous uvicorn still running | `kill $(pgrep -f uvicorn)` then restart |
| `analytics.db` has no data | Database path mismatch: code says `analytics.db`, file is at `data/analytics.db` | Check: `grep DATABASE_FILE api/database.py` — must say `data/analytics.db` |
| `uv sync` removed a package | Package was manually installed, not in pyproject.toml | Use `uv add package-name` (writes to pyproject.toml) |
| Preview panel stuck on "Starting server" | Port mismatch or dev.nix misconfigured | Test with `curl http://localhost:8000/` — if curl works, API is fine |
| Gemini used `pip install` | Gemini defaults to standard patterns | Correct to `uv add` and remind it to follow this file |

## dev.nix — OFF LIMITS
**Do NOT read, open, edit, or modify `.idx/dev.nix` under any circumstances.**
This file is git-protected and managed manually. If the preview breaks,
the author will fix it. If you modify this file, the fix is `git checkout .idx/dev.nix`
which reverts your changes.

If asked to "fix the preview," respond: "dev.nix is marked as off-limits
in GEMINI_CONTEXT.md. Would you like me to suggest changes for you to apply manually?"

## Before Making Changes
Always check current state of files you're modifying:
```bash
head -20 api/main.py api/models.py api/database.py
```
Match your changes to existing patterns — same table names, same import style, same variable names.

## Rules
1. Only do what is explicitly asked — do not refactor, reorganize, or add features unprompted
2. Use `uv run --` for ALL Python execution
3. Never add pip, requirements.txt generation, or new package managers
4. **NEVER open, read, edit, or modify `.idx/dev.nix`** — this file is git-protected and off-limits
5. When creating new database queries, always target the `api_queries` table
6. Keep the Skills endpoint filtering as plain dict (not Pydantic validated)
7. Do not skip ahead to future phases — wait for my instruction
8. If you're unsure what I'm asking, ask for clarification instead of guessing
9. After making changes, tell me what you changed and which files were modified
10. Do not touch files outside the scope of the current task
11. Never use bare `uvicorn` or bare `python3` in any command, script, or configuration
12. If I ask you to "fix the preview," do NOT modify dev.nix — suggest changes for me to apply manually