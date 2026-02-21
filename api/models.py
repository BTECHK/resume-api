from pydantic import BaseModel, Field
from typing import List, Dict

class Contact(BaseModel):
    name: str
    email: str
    linkedin: str
    location: str

class Project(BaseModel):
    name: str
    subtitle: str
    bullets: List[str]

class Experience(BaseModel):
    company: str
    title: str
    dates: str
    projects: List[Project]

class Skills(BaseModel):
    technical_development: List[str]
    solutions_analytics: List[str]
    client_partner_management: List[str]
    cloud_infrastructure: List[str]

class Education(BaseModel):
    school: str
    degree: str
    major: str

class Certification(BaseModel):
    name: str

class Resume(BaseModel):
    contact: Contact
    summary: str
    skills: Skills
    experience: List[Experience]
    education: List[Education]
    certifications: List[Certification]

class HealthStatus(BaseModel):
    status: str = "healthy"
    version: str = "1.0"
    endpoints: List[str]

class AnalyticsQuery(BaseModel):
    id: int
    timestamp: str
    domain: str
    path: str
    client_ip: str

class TopDomains(BaseModel):
    top_domains: Dict[str, int]

class Performance(BaseModel):
    p50: float
    p95: float
    p99: float
