"""YAML-backed content loader with caching.

Single source of truth for resume, interview Q&A, and ADR data.
"""

from functools import lru_cache
from pathlib import Path

import yaml

_DATA_DIR = Path(__file__).parent / "data"


@lru_cache(maxsize=8)
def _load_yaml(name: str):
    with open(_DATA_DIR / f"{name}.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_resume_dict() -> dict:
    return _load_yaml("resume")


def get_resume_as_text() -> str:
    data = _load_yaml("resume")
    sections = []

    sections.append(f"# Professional Summary\n{data['summary']}")

    skills_text = "# Skills\n"
    for category, skill_list in data["skills"].items():
        category_label = category.replace("_", " ").title()
        skills_text += f"\n## {category_label}\n"
        skills_text += "\n".join(f"- {skill}" for skill in skill_list)
    sections.append(skills_text)

    for job in data["experience"]:
        job_text = f"# {job['company']} \u2014 {job['title']} ({job['dates']})\n"
        for project in job["projects"]:
            job_text += f"\n## {project['name']}: {project['subtitle']}\n"
            job_text += "\n".join(f"- {bullet}" for bullet in project["bullets"])
        sections.append(job_text)

    edu = data["education"][0]
    sections.append(f"# Education\n{edu['degree']} in {edu['major']}, {edu['school']}")

    cert_text = "# Certifications\n"
    cert_text += "\n".join(f"- {cert}" for cert in data["certifications"])
    sections.append(cert_text)

    portfolio_text = "# Portfolio Projects\n"
    for project in data["portfolio_projects"]:
        portfolio_text += f"\n## {project['name']}\n{project['description']}\n"
    sections.append(portfolio_text)

    return "\n\n".join(sections)


def get_interview_patterns_as_text() -> str:
    data = _load_yaml("interview_qa")
    parts = []
    for item in data:
        tags = ", ".join(item.get("tags", []))
        parts.append(
            f"INTERVIEW PATTERN \u2014 {item['question']}\n"
            f"Tags: {tags}\n"
            f"Response pattern: {item['response_pattern']}\n"
        )
    return "\n---\n".join(parts)


def get_adr_content_as_text() -> str:
    data = _load_yaml("adr")
    parts = []
    for item in data:
        parts.append(
            f"ARCHITECTURE DECISION \u2014 {item['decision']}\n"
            f"Phase: {item.get('phase', 'n/a')}\n"
            f"{item['content']}\n"
        )
    return "\n---\n".join(parts)
