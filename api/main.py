
import uvicorn
import os
import sys
from pathlib import Path
from fastapi import FastAPI, Request, Response, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import time
import collections
from datetime import datetime, timezone
from typing import List, Optional

# Import models and database modules
import models
import database

# Add ai-service to path so loader.py is importable (local dev or Docker)
for _candidate in [
    Path(__file__).resolve().parent.parent / "ai-service",  # local dev
    Path(__file__).resolve().parent / "ai_service",         # Docker
]:
    if (_candidate / "loader.py").exists():
        sys.path.insert(0, str(_candidate))
        break
from loader import get_resume_dict

# Phase 2: Import new middleware and DB initializer
# Corrected imports for Docker context
from middleware.logging import LoggingMiddleware
from database import init_db

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Portfolio API",
    description="A comprehensive API serving resume data and simulated analytics.",
    version="1.0.0",
)

# --- Database Initialization ---
@app.on_event("startup")
def startup_event():
    """
    Initializes the database connection and tables on application startup.
    This is the recommended way to manage resources in FastAPI.
    """
    init_db()

# --- Middleware ---

# Phase 2: Add the new logging middleware.
# This captures request data, including custom headers for analytics.
app.add_middleware(LoggingMiddleware)

# CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"]
    ,
    allow_credentials=True,
    allow_methods=["GET", "POST"],  # Updated for Phase 2
    allow_headers=["*"],
)

# The old @app.middleware("http") has been removed and replaced by LoggingMiddleware.


def _build_resume_data() -> dict:
    """Load resume from YAML and adapt to the API's pydantic model shapes."""
    data = get_resume_dict()
    data["certifications"] = [{"name": c} for c in data["certifications"]]
    data.pop("portfolio_projects", None)
    return data


RESUME_DATA = _build_resume_data()

# --- API Endpoints ---

@app.get("/", response_model=models.HealthStatus)
def get_health_status():
    return {
        "status": "healthy",
        "version": "1.0",
        "endpoints": [
            "/",
            "/resume",
            "/resume/experience",
            "/resume/skills",
            "/resume/education",
            "/resume/certifications",
            "/resume/contact",
            "/resume/shortlist",
            "/analytics/queries",
            "/analytics/top-domains",
            "/analytics/performance",
        ]
    }

@app.get("/resume", response_model=models.Resume)
def get_resume():
    return RESUME_DATA


@app.get("/resume/experience", response_model=List[models.Experience])
def get_resume_experience(company: Optional[str] = None, after: Optional[int] = None):
    experience = RESUME_DATA["experience"]
    if company:
        experience = [exp for exp in experience if company.lower() in exp['company'].lower()]
    if after:
        experience = [exp for exp in experience if int(exp['dates'].split('–')[0].split()[-1]) >= after]
    if not experience:
        raise HTTPException(status_code=404, detail="No experience found matching the criteria.")
    return experience


@app.get("/resume/skills")
def get_resume_skills(category: Optional[str] = None, keyword: Optional[str] = None):
    skills = RESUME_DATA["skills"]
    if category:
        if category in skills:
            return JSONResponse(content={category: skills[category]})
        else:
            raise HTTPException(status_code=404, detail=f"Skill category '{category}' not found.")
    if keyword:
        filtered_skills = collections.defaultdict(list)
        for cat, skill_list in skills.items():
            for skill in skill_list:
                if keyword.lower() in skill.lower():
                    filtered_skills[cat].append(skill)
        if not filtered_skills:
            raise HTTPException(status_code=404, detail=f"No skills found with keyword '{keyword}'.")
        return JSONResponse(content=dict(filtered_skills))
    return skills


@app.get("/resume/education", response_model=List[models.Education])
def get_resume_education():
    return RESUME_DATA["education"]


@app.get("/resume/certifications", response_model=List[models.Certification])
def get_resume_certifications():
    return RESUME_DATA["certifications"]

@app.post("/resume/contact", response_model=models.ActionResponse)
def request_contact(request_data: models.ContactRequest):
    """Recruiter requests an interview or sends a message.

    This is a portfolio demo — no actual message is sent.
    The request is logged by middleware for pipeline analytics.
    """
    import uuid
    return models.ActionResponse(
        status="received",
        confirmation_id=f"conf_{uuid.uuid4().hex[:8]}",
        message="Contact request logged. This is a portfolio demo — no actual message is sent."
    )

@app.post("/resume/shortlist", response_model=models.ActionResponse)
def shortlist_candidate(request_data: models.ShortlistRequest):
    """Recruiter saves candidate to a shortlist.

    This is a portfolio demo — no actual list is maintained.
    The request is logged by middleware for pipeline analytics.
    """
    return models.ActionResponse(
        status="shortlisted",
        message="Candidate added to shortlist. This is a portfolio demo."
    )

@app.get("/analytics/queries", response_model=List[models.AnalyticsQuery])
def get_analytics_queries(domain: Optional[str] = None, limit: int = 50, offset: int = 0):
    conn = database.get_db_connection()
    query = "SELECT query_id as id, timestamp, recruiter_domain as domain, path FROM queries"
    params = []
    if domain:
        query += " WHERE recruiter_domain = ?"
        params.append(domain)
    query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    queries = conn.execute(query, tuple(params)).fetchall()
    conn.close()
    if not queries:
        raise HTTPException(status_code=404, detail="No queries found for the given criteria.")
    results = []
    for q in queries:
        query_dict = dict(q)
        query_dict['timestamp'] = datetime.fromtimestamp(query_dict['timestamp'], tz=timezone.utc).isoformat()
        query_dict['client_ip'] = 'N/A'
        results.append(query_dict)
    return results


@app.get("/analytics/top-domains", response_model=models.TopDomains)
def get_top_domains(n: int = 10):
    conn = database.get_db_connection()
    domains = [row['recruiter_domain'] for row in conn.execute("SELECT recruiter_domain FROM queries").fetchall()]
    conn.close()
    if not domains:
        return {"top_domains": {}}
    counter = collections.Counter(domains)
    top_domains_counter = dict(counter.most_common(n))
    return {"top_domains": top_domains_counter}


@app.get("/analytics/performance", response_model=models.Performance)
def get_performance_analytics():
    return {
        "p50": 50.0,
        "p95": 250.0,
        "p99": 750.0
    }

