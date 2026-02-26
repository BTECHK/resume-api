# Bug Fix Log

## Bug 1: `/resume/skills` returning 500 error with `category` parameter

**Symptom:** The `/resume/skills` endpoint with a `category` query parameter was returning a 500 error.

**Root Cause:** The Pydantic `response_model` for the `Skills` model was expecting all skill categories to be present in the response. When a `category` was specified, the endpoint only returned that single category, which caused a validation error.

**Fix:** The `get_resume_skills` function in `api/main.py` was modified to use FastAPI's `JSONResponse` when a `category` or `keyword` is provided. This bypasses the Pydantic model validation for filtered results while still enforcing it for the unfiltered case.

---

## Bug 2: Web preview not loading

**Symptom:** Web preview panel in Firebase Studio would not load the application.

**Root Cause:** The application was hard-coded to run on port 8000, but the web preview environment expects the application to run on the port specified by the `PORT` environment variable.

**Fix:** Modified the `.idx/dev.nix` file to use `sh -c "uv run -- python -m uvicorn api.main:app --reload --port ${PORT:-8000} --host 0.0.0.0"`. This makes the server start on the port defined by the `PORT` environment variable, defaulting to 8000 if unset.
