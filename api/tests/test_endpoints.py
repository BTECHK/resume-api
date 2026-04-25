"""Integration tests for all api/ REST endpoints."""


# ── Health check ─────────────────────────────────────────────────────

class TestHealthCheck:
    def test_health_status(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "healthy"
        assert body["version"] == "1.0"
        assert isinstance(body["endpoints"], list)
        assert "/resume" in body["endpoints"]
        assert len(body["endpoints"]) == 11


# ── GET /resume ──────────────────────────────────────────────────────

class TestGetResume:
    def test_full_resume(self, client):
        resp = client.get("/resume")
        assert resp.status_code == 200
        body = resp.json()
        # Top-level keys
        for key in ("contact", "summary", "skills", "experience", "education", "certifications"):
            assert key in body, f"Missing top-level key: {key}"
        # Contact shape
        assert body["contact"]["name"] == "The Candidate"
        assert "email" in body["contact"]
        # Non-empty collections
        assert len(body["experience"]) > 0
        assert len(body["education"]) > 0
        assert len(body["certifications"]) > 0


# ── GET /resume/experience ───────────────────────────────────────────

class TestGetExperience:
    def test_all_experience(self, client):
        resp = client.get("/resume/experience")
        assert resp.status_code == 200
        items = resp.json()
        assert isinstance(items, list)
        assert len(items) >= 2
        # Each item has required fields
        for item in items:
            assert "company" in item
            assert "title" in item
            assert "dates" in item
            assert "projects" in item

    def test_filter_by_company(self, client):
        resp = client.get("/resume/experience", params={"company": "Big Four"})
        assert resp.status_code == 200
        items = resp.json()
        assert len(items) >= 1
        for item in items:
            assert "big four" in item["company"].lower()

    def test_filter_by_after(self, client):
        resp = client.get("/resume/experience", params={"after": 2018})
        assert resp.status_code == 200
        items = resp.json()
        assert len(items) >= 1

    def test_company_filter_no_match(self, client):
        resp = client.get("/resume/experience", params={"company": "NonExistentCorp"})
        assert resp.status_code == 404

    def test_after_filter_no_match(self, client):
        resp = client.get("/resume/experience", params={"after": 2099})
        assert resp.status_code == 404


# ── GET /resume/skills ───────────────────────────────────────────────

class TestGetSkills:
    def test_all_skills(self, client):
        resp = client.get("/resume/skills")
        assert resp.status_code == 200
        body = resp.json()
        assert "technical_development" in body
        assert "cloud_infrastructure" in body
        assert isinstance(body["technical_development"], list)

    def test_filter_by_category(self, client):
        resp = client.get("/resume/skills", params={"category": "cloud_infrastructure"})
        assert resp.status_code == 200
        body = resp.json()
        assert "cloud_infrastructure" in body
        assert len(body) == 1  # only the requested category

    def test_category_not_found(self, client):
        resp = client.get("/resume/skills", params={"category": "nonexistent"})
        assert resp.status_code == 404

    def test_filter_by_keyword(self, client):
        resp = client.get("/resume/skills", params={"keyword": "Python"})
        assert resp.status_code == 200
        body = resp.json()
        # At least one category returned with a Python-matching skill
        assert len(body) >= 1
        found = False
        for skills in body.values():
            for skill in skills:
                if "python" in skill.lower():
                    found = True
        assert found

    def test_keyword_not_found(self, client):
        resp = client.get("/resume/skills", params={"keyword": "ZZZNOTASKILL"})
        assert resp.status_code == 404


# ── GET /resume/education ────────────────────────────────────────────

class TestGetEducation:
    def test_education(self, client):
        resp = client.get("/resume/education")
        assert resp.status_code == 200
        items = resp.json()
        assert isinstance(items, list)
        assert len(items) >= 1
        item = items[0]
        assert item["school"] == "Oklahoma State University"
        assert "degree" in item
        assert "major" in item


# ── GET /resume/certifications ───────────────────────────────────────

class TestGetCertifications:
    def test_certifications(self, client):
        resp = client.get("/resume/certifications")
        assert resp.status_code == 200
        items = resp.json()
        assert isinstance(items, list)
        assert len(items) >= 1
        for item in items:
            assert "name" in item


# ── POST /resume/contact ────────────────────────────────────────────

class TestPostContact:
    def test_contact_request(self, client):
        payload = {
            "recruiter_email": "recruiter@example.com",
            "company": "Acme Inc",
            "message": "We'd like to schedule an interview.",
            "role": "Senior Engineer",
        }
        resp = client.post("/resume/contact", json=payload)
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "received"
        assert body["confirmation_id"] is not None
        assert body["confirmation_id"].startswith("conf_")
        assert "message" in body

    def test_contact_missing_field(self, client):
        payload = {"recruiter_email": "a@b.com"}  # missing required fields
        resp = client.post("/resume/contact", json=payload)
        assert resp.status_code == 422  # Pydantic validation error


# ── POST /resume/shortlist ──────────────────────────────────────────

class TestPostShortlist:
    def test_shortlist(self, client):
        payload = {"list_name": "Top Picks", "priority": "high"}
        resp = client.post("/resume/shortlist", json=payload)
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "shortlisted"
        assert "message" in body

    def test_shortlist_missing_field(self, client):
        resp = client.post("/resume/shortlist", json={"list_name": "X"})
        assert resp.status_code == 422


# ── GET /analytics/queries ──────────────────────────────────────────

class TestAnalyticsQueries:
    def test_queries_empty_db(self, client):
        """Empty DB returns 404."""
        resp = client.get("/analytics/queries")
        assert resp.status_code == 404

    def test_queries_with_data(self, client, seeded_db):
        resp = client.get("/analytics/queries")
        assert resp.status_code == 200
        items = resp.json()
        assert isinstance(items, list)
        assert len(items) == 3
        for item in items:
            assert "id" in item
            assert "timestamp" in item
            assert "domain" in item
            assert "path" in item

    def test_queries_domain_filter(self, client, seeded_db):
        resp = client.get("/analytics/queries", params={"domain": "google.com"})
        assert resp.status_code == 200
        items = resp.json()
        assert len(items) == 2
        for item in items:
            assert item["domain"] == "google.com"

    def test_queries_domain_no_match(self, client, seeded_db):
        resp = client.get("/analytics/queries", params={"domain": "nope.org"})
        assert resp.status_code == 404

    def test_queries_limit_offset(self, client, seeded_db):
        resp = client.get("/analytics/queries", params={"limit": 1, "offset": 0})
        assert resp.status_code == 200
        assert len(resp.json()) == 1


# ── GET /analytics/top-domains ──────────────────────────────────────

class TestAnalyticsTopDomains:
    def test_top_domains_empty(self, client):
        resp = client.get("/analytics/top-domains")
        assert resp.status_code == 200
        assert resp.json()["top_domains"] == {}

    def test_top_domains_with_data(self, client, seeded_db):
        resp = client.get("/analytics/top-domains")
        assert resp.status_code == 200
        domains = resp.json()["top_domains"]
        assert isinstance(domains, dict)
        assert domains["google.com"] == 2
        assert domains["amazon.com"] == 1

    def test_top_domains_n_param(self, client, seeded_db):
        resp = client.get("/analytics/top-domains", params={"n": 1})
        assert resp.status_code == 200
        domains = resp.json()["top_domains"]
        assert len(domains) == 1
        assert "google.com" in domains


# ── GET /analytics/performance ──────────────────────────────────────

class TestAnalyticsPerformance:
    def test_performance(self, client):
        resp = client.get("/analytics/performance")
        assert resp.status_code == 200
        body = resp.json()
        assert body["p50"] == 50.0
        assert body["p95"] == 250.0
        assert body["p99"] == 750.0
