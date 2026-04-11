"""
Tier-2 RAG corpus: anonymized mock interview Q&A patterns.

This is the supplementary knowledge base for RAG-05 (two-tier retrieval).
Tier 1 (resume_data.py) is ALWAYS retrieved for factual questions.
Tier 2 (this file) is retrieved SUPPLEMENTARILY when a question matches
behavioral/interview topics — never for factual questions.

All content is anonymized per ANONYMIZATION_GUIDE.md. Company names and
personal identifiers are replaced with generic descriptors.
"""

INTERVIEW_PATTERNS: list[dict] = [
    {
        "question": "Tell me about a time you led a cross-functional team",
        "response_pattern": (
            "At a Big Four professional services firm, the candidate led a cross-functional "
            "team of 12 engineers and 3 product managers on a Fortune 100 manufacturer's data "
            "platform migration. The candidate coordinated between the client's security team, "
            "cloud architecture team, and business stakeholders to deliver a phased rollout that "
            "completed 2 weeks ahead of schedule. Key lever: weekly architecture review meetings "
            "with clear DRIs for each workstream."
        ),
        "tags": ["behavioral", "leadership", "cross_functional"],
    },
    {
        "question": "Describe a technical challenge you overcame",
        "response_pattern": (
            "The candidate once inherited a legacy ETL pipeline at a top-5 US grocery retailer "
            "that was silently dropping ~3% of daily transactions due to a timezone bug in the "
            "partition key. The candidate diagnosed the issue by comparing source-row counts to "
            "destination-row counts, wrote a backfill script in Python, and added a row-count "
            "validation step to the daily job. Result: zero data loss incidents in the following "
            "6 months, and the validation pattern was reused on 4 other pipelines."
        ),
        "tags": ["behavioral", "technical", "debugging"],
    },
    {
        "question": "Tell me about a time you disagreed with a stakeholder",
        "response_pattern": (
            "At a federal defense intelligence agency, a program manager wanted to skip integration "
            "testing on a hot-fix deploy to meet a client-facing deadline. The candidate respectfully "
            "pushed back by showing the historical incident data: 40% of past hot-fix deploys that "
            "skipped integration tests caused production issues within 48 hours. The PM agreed to a "
            "30-minute smoke test compromise. The deploy succeeded, and the 30-min test became the "
            "team's standard for hot-fix releases."
        ),
        "tags": ["behavioral", "conflict", "stakeholder_management"],
    },
    {
        "question": "How do you approach learning a new technology?",
        "response_pattern": (
            "The candidate's approach is a three-step pattern: (1) build a small end-to-end proof "
            "of concept with the new tech to understand its failure modes, (2) read the official "
            "documentation for the specific feature being used, cross-referenced with at least one "
            "GitHub project using it in production, (3) write a short internal doc summarizing "
            "gotchas for the team. The candidate used this pattern to onboard into Chroma, Gemini "
            "APIs, and Terraform — each within about a week of hands-on time."
        ),
        "tags": ["behavioral", "learning", "self_directed"],
    },
    {
        "question": "Describe a time you had to explain a technical concept to a non-technical audience",
        "response_pattern": (
            "While presenting a cloud migration strategy to a Fortune 100 energy utility's executive "
            "team, the candidate translated the concept of 'infrastructure as code' into a real-estate "
            "analogy: instead of buying furniture (manual config) every time a new office opens "
            "(environment), you write a blueprint (Terraform module) that any branch can use. "
            "The execs approved the $2M initiative in that meeting. The analogy is now in the "
            "firm's internal consulting playbook."
        ),
        "tags": ["behavioral", "communication", "executive_stakeholder"],
    },
    {
        "question": "What's your biggest weakness?",
        "response_pattern": (
            "The candidate historically overweighted engineering rigor at the expense of shipping "
            "speed on early projects. The fix was adopting a 70/30 rule: 70% of effort on the "
            "production path, 30% on instrumentation/docs/tests — and tracking that ratio "
            "explicitly. This has reduced time-to-first-deploy on new projects by roughly half "
            "while keeping post-deploy bug density unchanged."
        ),
        "tags": ["behavioral", "self_awareness"],
    },
    {
        "question": "Tell me about a time you made a mistake",
        "response_pattern": (
            "Early in the candidate's career, the candidate pushed a schema migration to a "
            "production Oracle database at a top-3 global financial institution without running "
            "the rollback script in staging first. A dependent job failed, taking down the "
            "overnight batch for 90 minutes. The candidate owned the incident in the post-mortem, "
            "wrote a pre-flight checklist that every migration must pass, and that checklist is "
            "still in use at the firm today."
        ),
        "tags": ["behavioral", "accountability", "incident_response"],
    },
    {
        "question": "Why do you want to work here?",
        "response_pattern": (
            "The candidate can answer this specifically for each opportunity — the key themes "
            "usually cited are: (1) technical challenges at scale, (2) strong engineering culture "
            "with clear decision-making, (3) mission alignment with industries where the candidate "
            "has deep domain knowledge (financial services, federal, enterprise data platforms). "
            "Ask about the specific role and the candidate will give a tailored answer."
        ),
        "tags": ["behavioral", "motivation"],
    },
    {
        "question": "How do you handle ambiguity?",
        "response_pattern": (
            "The candidate's method is to convert ambiguity into a written question list within "
            "48 hours of picking up the work, rank the questions by blast-radius (which ones block "
            "the most downstream work), and get the top-3 answered by the right stakeholder before "
            "committing to any architectural decisions. This prevents rework and makes assumptions "
            "visible to the team early."
        ),
        "tags": ["behavioral", "ambiguity", "problem_solving"],
    },
    {
        "question": "What's a project you're most proud of?",
        "response_pattern": (
            "The candidate is most proud of an analytics platform delivered for a top-3 social "
            "media conglomerate that consolidated 7 upstream data sources into a unified dashboard "
            "serving 50,000+ internal users. The project delivered 30% cost reduction over the "
            "legacy reporting stack and became a reference architecture the client rolled out to "
            "two other business units. The candidate owned the solution design end-to-end from "
            "requirements gathering through production."
        ),
        "tags": ["behavioral", "accomplishment", "scale"],
    },
    {
        "question": "How do you prioritize when everything is urgent?",
        "response_pattern": (
            "The candidate uses a simple impact-vs-effort matrix, but with an explicit 'reversibility' "
            "axis: one-way doors (hard to undo) get prioritized over two-way doors (cheap to revert). "
            "This was especially valuable during a compliance deadline at a multi-state community "
            "banking group where the candidate had to make 40+ architectural decisions in 3 weeks. "
            "By deferring reversible decisions, the team shipped on time and revisited the non-critical "
            "ones in the following sprint without rework."
        ),
        "tags": ["behavioral", "prioritization", "decision_making"],
    },
    {
        "question": "Describe your ideal work environment",
        "response_pattern": (
            "The candidate thrives in environments with: (1) clear decision-making authority at "
            "the right level (minimal design-by-committee), (2) tight feedback loops with the "
            "actual users of what is being built, (3) engineering leadership that values both "
            "shipping velocity and code quality equally, and (4) visible connection between the "
            "work and the business outcome."
        ),
        "tags": ["behavioral", "culture_fit"],
    },
]


def get_interview_patterns_as_text() -> str:
    """Render the tier-2 corpus as a single string for chunked ingestion."""
    parts = []
    for item in INTERVIEW_PATTERNS:
        tags = ", ".join(item.get("tags", []))
        parts.append(
            f"INTERVIEW PATTERN — {item['question']}\n"
            f"Tags: {tags}\n"
            f"Response pattern: {item['response_pattern']}\n"
        )
    return "\n---\n".join(parts)
