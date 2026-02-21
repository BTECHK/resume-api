
import uvicorn
import os
from fastapi import FastAPI, Request, Response, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import time
import collections
from typing import List, Optional

# Assuming models.py and database.py are in the same directory (api/)
from . import models
from . import database

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Portfolio API",
    description="A comprehensive API serving resume data and simulated analytics.",
    version="1.0.0",
)

# --- Middleware ---

# CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for this portfolio project
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_process_time_and_logging_header(request: Request, call_next):
    """
    Middleware to log requests, calculate response time, and add custom headers.
    """
    start_time = time.time()
    
    # Log the request to the database
    conn = database.get_db_connection()
    conn.execute(
        'INSERT INTO queries (domain, path, client_ip) VALUES (?, ?, ?)',
        (request.url.hostname, request.url.path, request.client.host)
    )
    conn.commit()
    conn.close()

    response = await call_next(request)
    
    process_time = (time.time() - start_time) * 1000  # in milliseconds
    response.headers["X-Process-Time-ms"] = str(process_time)
    
    # Simulated Rate Limiting Headers
    response.headers["X-RateLimit-Limit"] = "1000"
    response.headers["X-RateLimit-Remaining"] = "999" # Simplified for portfolio

    print(f"timestamp={time.time()} endpoint={request.url.path} response_time_ms={process_time:.2f} client_ip={request.client.host}")
    
    return response


# --- Hardcoded Resume Data ---
RESUME_DATA = {
    "contact": {
        "name": "[YOUR_NAME]",
        "email": "[YOUR_EMAIL]",
        "linkedin": "[YOUR_LINKEDIN_URL]",
        "location": "Washington D.C."
    },
    "summary": "Technical Solutions Consultant with 8+ years developing customized solutions for Fortune 500 enterprises (Meta, Dell, Kroger) and federal agencies. Combines hands-on programming expertise (Python, SQL, Bash) with proven ability to manage technical relationships and translate complex requirements into scalable implementations for diverse client portfolios. Demonstrated track record delivering end-to-end solutions—from prototypes and demos to production systems serving 50,000+ users—while conducting business analysis, building analytics dashboards, and advising executive stakeholders on strategic tradeoffs. Expert at technical troubleshooting across cloud infrastructure, data platforms, and enterprise systems. Skilled at identifying business opportunities through technical solutions that drive measurable outcomes: 30% cost reduction, 40% security risk reduction, and 100% regulatory compliance.",
    "skills": {
        "technical_development": [
            "Python scripting and automation",
            "SQL (PostgreSQL, Oracle, T-SQL)",
            "Bash",
            "System architecture design",
            "API integration",
            "ETL pipeline development",
            "Git version control",
            "Technical troubleshooting"
          ],
        "solutions_analytics": [
            "Business analysis and requirements gathering",
            "Dashboard development (CloudWatch, MicroStrategy, custom analytics)",
            "Data-driven recommendations",
            "Prototype and demo development",
            "Large volume data platform management"
          ],
        "client_partner_management": [
            "Technical relationship management",
            "Cross-functional team leadership (100+ engineers)",
            "Translating technical concepts to non-technical and executive audiences",
            "End-to-end implementation ownership",
            "Requirements collection and best practices guidance"
          ],
        "cloud_infrastructure": [
            "AWS (EC2, S3, IAM, VPC, CloudWatch, Lambda, Fargate, Config, Inspector)",
            "Infrastructure as Code (Terraform, CloudFormation)",
            "Docker",
            "CI/CD (GitLab)",
            "FinOps and cost optimization"
          ]
    },
    "experience": [
        {
          "company": "Consulting Firm A",
          "title": "Consultant → Senior Consultant",
          "dates": "May 2018 – July 2025",
          "projects": [
            {
              "name": "Go-to-Market AI Lab",
              "subtitle": "Technical Solutions Development & Client Enablement",
              "bullets": [
                "Designed and implemented RAG prototype: Leading team of 4 developers to build document intelligence solution using Python orchestration scripts, AWS Textract API integration, SQS/SNS event processing, and vector database architecture—enabling rapid querying across 500+ page documents and reducing manual analyst effort 30%",
                "Delivered end-to-end infrastructure solutions: Provisioning AWS resources for multiple development teams, collecting requirements, configuring load balancers for production-like demo environments, and creating standardized Dockerfile templates and GitLab CI/CD automation that reduced developer onboarding 40%",
                "Conducted technical troubleshooting: Resolving connectivity issues, application startup errors, and system misconfigurations across distributed cloud environments to ensure demo readiness and maintain development velocity for stakeholder presentations",
                "Built analytics dashboards for cost optimization: Implementing comprehensive resource tagging strategy using Python automation, enabling granular spend tracking across 10+ AI projects, identifying unutilized resources, and presenting recommendations that reduced infrastructure costs 25% ($135K annually)",
                "Translated technical requirements to business outcomes: Partnering with data scientists to right-size GPU/CPU instances, developing business cases for serverless architecture adoption (Lambda, Fargate), and mentoring 5 junior developers on infrastructure best practices"
              ]
            },
            {
              "name": "Federal Justice Program",
              "subtitle": "Technical Solutions for Business Analytics Platform (50,000+ Users)",
              "bullets": [
                "Managed technical relationships across client portfolio: Advising senior federal leadership on strategic tradeoffs for cloud-based tools, conducting requirements gathering sessions, and providing best practices guidance for platform decisions impacting 50,000+ end users across 6 environments",
                "Conducted large volume data analytics: Managing business intelligence platform (MicroStrategy, PostgreSQL) serving enterprise-scale user base, performing SQL script review and execution for developer use cases, and developing recommendations that improved system stability and performance",
                "Performed technical troubleshooting for enterprise systems: Investigating MicroStrategy database crashes through SQL query analysis, Intelligence Server error log review, and identifying root causes—implementing memory guardrails and educating power users on query optimization to prevent future incidents",
                "Delivered business analysis and executive dashboards: Creating cost analytics using CloudWatch metrics, Python automation, and custom reporting to enable data-driven resource allocation decisions for $450K annual budget, achieving 30% cost reduction through FinOps best practices",
                "Designed and implemented security solutions: Auditing 150+ IAM roles and 200+ security groups using Python/Bash automation scripts, identifying optimization opportunities, reducing attack surface 40%, and codifying findings in CloudFormation Infrastructure as Code templates",
                "Led end-to-end compliance implementation: Directing 5-person team through 300+ finding remediation within 30-day windows, managing technical relationships with CISO and security stakeholders, achieving 100% FedRAMP compliance and preserving $3M+ annual contract eligibility",
                "Facilitated cross-functional team coordination: Driving agile ceremonies for 4 teams (50+ engineers, business analysts, directors), facilitating sprint planning, demos, retrospectives, and strategic roadmap sessions to meet SLAs and stakeholder goals"
              ]
            },
            {
              "name": "Federal Defense Program",
              "subtitle": "Strategic Solutions for HR IT Procurement",
              "bullets": [
                "Designed strategic planning framework: Conducting 100+ stakeholder interviews across 15 departments to assess process drivers, identify gaps, and align IT procurement with DoD PPBE cycle—preventing future funding forfeitures",
                "Delivered end-to-end solution documentation: Creating workflows, instructional templates, and standard operating procedures for initiative and investment management—establishing repeatable process that reduced procurement cycle 50% (6 to 3 months)",
                "Led solution assessment and analysis of alternatives: Managing team of 3 contractors to evaluate analytics platforms (Tableau, Power BI, custom solutions), conducting prototype demos and presenting cost-benefit analysis with strategic tradeoff recommendations that saved $25K in platform costs"
              ]
            },
          ]
        },
        {
          "company": "Consulting Firm B",
          "title": "Jr. Developer → Developer",
          "dates": "October 2016 – April 2018",
          "projects": [
            {
              "name": "Healthcare Program (Healthcare Program)",
              "subtitle": "Oracle HCM Cloud Implementation Solutions",
              "bullets": [
                "Led requirements gathering and business analysis: Managing key stakeholders through fit/gap analysis and discovery sessions to convert 150+ PeopleSoft/SQR reports to Oracle Cloud, analyzing 20+ PeopleSoft app engines and SQR interfaces for system integration compatibility",
                "Architected and implemented data store solution: Researching optimal approaches, designing SQL Server database schema, developing stored procedures replicating PeopleSoft SQR logic, and implementing SQL Server Reporting Services frontend for HIPAA compliance reporting",
                "Delivered 50+ mission-critical compliance reports: Redeveloping legacy healthcare reports in both SQL Server solution and Oracle Cloud (OTBI/BI Publisher), implementing row-level security and PHI protection controls while conducting end-user training for clinical and administrative stakeholders"
              ]
            },
            {
              "name": "Financial Services (Financial Services Program)",
              "subtitle": "Oracle HCM Analytics Solutions",
              "bullets": [
                "Developed successful prototype securing contract extension: Creating proof-of-concept report using SQL and Oracle BI tools to integrate HCM data with external Excel sources, demonstrating 40% efficiency improvement in workforce analytics capabilities and securing $50K follow-on contract",
                "Built enterprise data model for consolidated reporting: Developing custom data model integrating disparate data sources across 20 banks, implementing PCI-DSS and SOX compliance controls for financial data handling with zero reporting interruption during cloud migration"
              ]
            }
          ]
        },
    ],
    "education": [
        {
            "school": "Oklahoma State University",
            "degree": "Bachelor of Science",
            "major": "Geology"
        }
    ],
    "certifications": [
        {"name": "[CLEARANCE_LEVEL]"},
        {"name": "AWS Certified Solutions Architect – Associate"},
        {"name": "AWS Certified Machine Learning Engineer – Associate"},
        {"name": "Oracle Cloud Infrastructure 2024 Architect Associate"},
        {"name": "Oracle Cloud Infrastructure 2024 Certified AI Foundations Associate"},
        {"name": "CompTIA Security+ ce"},
        {"name": "Oracle Financials Cloud ERP Certification"}
    ]
}


# --- API Endpoints ---

@app.get("/", response_model=models.HealthStatus)
def get_health_status():
    """
    Returns the health status and metadata of the API.
    """
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
            "/analytics/queries",
            "/analytics/top-domains",
            "/analytics/performance",
        ]
    }

@app.get("/resume", response_model=models.Resume)
def get_resume():
    """
    Returns the complete resume as a structured JSON object.
    """
    return RESUME_DATA


@app.get("/resume/experience", response_model=List[models.Experience])
def get_resume_experience(company: Optional[str] = None, after: Optional[int] = None):
    """
    Returns work experience, with optional filtering by company and start year.
    """
    experience = RESUME_DATA["experience"]
    
    if company:
        experience = [exp for exp in experience if company.lower() in exp['company'].lower()]

    if after:
        # A simple year extraction for demonstration
        experience = [exp for exp in experience if int(exp['dates'].split('–')[0].split()[-1]) >= after]
        
    if not experience:
        raise HTTPException(status_code=404, detail="No experience found matching the criteria.")
        
    return experience


@app.get("/resume/skills")
def get_resume_skills(category: Optional[str] = None, keyword: Optional[str] = None):
    """
    Returns skills, optionally filtered by category or a specific keyword.
    """
    skills = RESUME_DATA["skills"]

    if category:
        if category in skills:
            # Return as a plain dict (via JSONResponse) to bypass the response_model for filtered results.
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
        # Return as a plain dict (via JSONResponse) to bypass the response_model for filtered results.
        return JSONResponse(content=dict(filtered_skills))

    # For the unfiltered case, FastAPI will validate against the response_model
    return skills


@app.get("/resume/education", response_model=List[models.Education])
def get_resume_education():
    """
    Returns education history.
    """
    return RESUME_DATA["education"]


@app.get("/resume/certifications", response_model=List[models.Certification])
def get_resume_certifications():
    """
    Returns a list of certifications.
    """
    return RESUME_DATA["certifications"]


@app.get("/analytics/queries", response_model=List[models.AnalyticsQuery])
def get_analytics_queries(domain: Optional[str] = None, limit: int = 50, offset: int = 0):
    """
    Retrieves visitor query log data from the SQLite database with pagination.
    """
    conn = database.get_db_connection()
    
    query = "SELECT query_id as id, timestamp, recruiter_domain as domain, endpoint_hit as path FROM api_queries"
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
        
    # Manually add a placeholder for client_ip to match the Pydantic model
    results = []
    for q in queries:
        query_dict = dict(q)
        query_dict['client_ip'] = 'N/A'  # Placeholder value
        results.append(query_dict)

    return results


@app.get("/analytics/top-domains", response_model=models.TopDomains)
def get_top_domains(n: int = 10):
    """
    Returns the top N domains that have hit the API.
    """
    conn = database.get_db_connection()
    domains = [row['recruiter_domain'] for row in conn.execute("SELECT recruiter_domain FROM api_queries").fetchall()]
    conn.close()

    if not domains:
        return {"top_domains": {}}

    counter = collections.Counter(domains)
    top_domains_counter = dict(counter.most_common(n))

    return {"top_domains": top_domains_counter}


@app.get("/analytics/performance", response_model=models.Performance)
def get_performance_analytics():
    """
    Simulates API performance monitoring by returning response time percentiles.
    This is a simulation and does not reflect real performance metrics.
    """
    # In a real-world scenario, you would calculate these from logged response times.
    # Here, we are just returning static, simulated data.
    return {
        "p50": 50.0,
        "p95": 250.0,
        "p99": 750.0
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("api.main:app", host="0.0.0.0", port=port, reload=True)
