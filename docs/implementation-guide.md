# Resume API — Complete Implementation Guide
## Build a REST API on Google Cloud with Dual-Database Architecture

**Goal:** Build and deploy a REST API that serves structured resume data with analytics tracking, using a dual-database architecture (SQLite operational + BigQuery analytical) on Google Cloud infrastructure.  
**Total Cost:** $0.00 (Google Cloud free tier with billing safeguards)  
**Estimated Time:** 8-12 hours  
**Primary Tool:** Firebase Studio with Gemini AI-assisted development

---

## WHAT YOU'RE BUILDING

A portfolio-grade REST API that demonstrates:

| Skill Area | How It's Demonstrated |
|-----------|----------------------|
| API Design | 9 REST endpoints with proper resource modeling, query params, status codes, Swagger docs |
| Linux / CLI | Full terminal-based development and deployment using ps, grep, ss, kill, docker, gcloud |
| Python | Dictionary frequency maps, collections.Counter, Pydantic models, data generation |
| SQL / BigQuery | 3-tier query progression: naive → CTE/window functions → partitioned/clustered |
| Data Modeling | Schema mirrors digital advertising reporting patterns (advertiser, campaign, keyword) |
| Cloud Deployment | Docker containerization → Cloud Run serverless hosting |

---

## ARCHITECTURE OVERVIEW

```
┌─────────────────────────────────────────────────────┐
│  FIREBASE STUDIO (Development Environment)          │
│  ├── Write code with Gemini AI assistance           │
│  ├── Run Linux commands in terminal                 │
│  └── Test everything locally before deploying       │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│  GOOGLE CLOUD (Free Tier — Billing Account w/ Cap)  │
│                                                     │
│  ┌─────────────┐    ┌────────────────────┐          │
│  │ Cloud Run   │    │ BigQuery           │          │
│  │ (Your API)  │    │ (Analytical Data)  │          │
│  │ FastAPI +   │    │ 500K+ rows         │          │
│  │ SQLite      │    │ Partitioned tables │          │
│  └──────┬──────┘    └────────────────────┘          │
│         │                                           │
│         ▼                                           │
│  ┌─────────────┐                                    │
│  │ Public URL  │  ← https://resume-api-xxx.run.app  │
│  └─────────────┘                                    │
└─────────────────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│  GITHUB (Portfolio)                                 │
│  ├── All source code                                │
│  ├── README with design decisions & screenshots     │
│  └── SQL query comparisons with performance data    │
└─────────────────────────────────────────────────────┘
```

**The end result:** A fully deployed REST API on Google Cloud, backed by both a local SQLite database and BigQuery, with a data model inspired by ad tech reporting — and a README that explains every design decision.

---

## WHERE AM I? — LOCATION GUIDE

This guide moves between multiple environments. Every command and instruction is tagged with a location so you always know where to type or click.

| Tag | Where | What It Looks Like |
|-----|-------|-------------------|
| 📍 **GCP Console** | Google Cloud Console in your browser | `console.cloud.google.com` — clicking buttons, enabling APIs |
| 📍 **Firebase Terminal** | Terminal panel inside Firebase Studio | Black terminal at the bottom of the IDE — bash commands |
| 📍 **Firebase Editor** | Code editor inside Firebase Studio | The file tabs at the top — editing .py, .nix, .toml files |
| 📍 **Firebase Preview** | Web preview panel inside Firebase Studio | The "Web" tab — shows your running API |
| 📍 **BigQuery Console** | BigQuery UI in your browser | `console.cloud.google.com/bigquery` — running SQL queries |
| 📍 **Your Browser** | Your actual browser (Chrome/Firefox) | Visiting deployed URLs, downloading files |

> **Rule of thumb:** If you see `bash` code → it goes in **Firebase Terminal**. If you see `Go to: https://...` → it's in **your browser** (GCP Console or BigQuery Console). If you see `Open file...` or `Find the line...` → it's in the **Firebase Editor**.

---

## PRE-FLIGHT CHECKLIST

📍 **Firebase Terminal** (or any terminal with these tools installed)

Before starting, run this in any terminal to see what's available on your system:

```bash
python3 --version; uv --version; docker --version; gcloud --version; bq --version; git --version; curl --version
```

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Commands used:

| Command | What It Does |
|---------|-------------|
| `python3` | Runs the Python interpreter |
| `uv` | Fast Python package manager (replaces pip in Firebase Studio) |
| `docker` | Builds and runs containers |
| `gcloud` | Google Cloud CLI — manages GCP resources |
| `bq` | BigQuery CLI — runs queries and loads data |
| `git` | Version control — tracks code changes |
| `curl` | Makes HTTP requests from the terminal |
| `--version` | Flag that prints the installed version of any tool |
| `;` | Semicolon — runs the next command regardless of whether the previous succeeded |

</em></sub>


Note which commands succeed and which fail. You'll install anything missing during the appropriate phase.

---

## PHASE 0: ACCOUNT SETUP & BILLING SAFEGUARDS (30 minutes)

> **Do all of this BEFORE opening Firebase Studio. Build the safety net first.**
> 
> 📍 **All of Phase 0 happens in your browser (GCP Console) — you are NOT in Firebase Studio yet.**

### Step 0.1 — Create a Google Cloud Account (if you don't have one)
📍 **Your Browser**

1. Go to: `https://cloud.google.com`
2. Click **"Get started for free"**
3. Sign in with your Google account
4. You will get **$300 in free credits** for 90 days (separate from the Always Free tier)
5. Enter your credit card — **you will NOT be charged** unless you manually upgrade

> **Note:** Google requires a credit card like a hotel requires one at check-in. They place a $0 hold. No charges will be made unless you explicitly upgrade to a paid account. We're adding additional safeguards below.

### Step 0.2 — Create a New Project
📍 **GCP Console**

1. Go to: `https://console.cloud.google.com`
2. Click the project dropdown at the top (might say "My First Project")
3. Click **"New Project"**
4. Name it: `resume-api-portfolio`
5. Click **Create**
6. Make sure this project is selected in the dropdown

### Step 0.3 — Set Budget Alerts (YOUR SAFETY NET)
📍 **GCP Console → Billing**

> **Important:** Budget alerts are notifications only — they don't automatically stop charges. Your real kill switch is disabling billing (see Step 0.4).

1. Go to: `https://console.cloud.google.com/billing`
2. Click on your billing account
3. In the left sidebar, click **"Budgets & alerts"**
4. Click **"Create Budget"**
5. Set these values:
   - **Name:** `Portfolio Safety Cap`
   - **Projects:** Select `resume-api-portfolio`
   - **Time range:** Monthly
   - **Amount:** `$1.00` (yes, one dollar)
   - **Alert thresholds:** 50%, 90%, 100%
6. Click **"Finish"**

### Step 0.4 — Know Your Kill Switch
📍 **GCP Console → Billing**

If you ever get an alert email or want to stop all charges instantly:

1. Go to: `https://console.cloud.google.com/billing`
2. Click your billing account → **"Account Management"**
3. Click **"Disable billing"**

This immediately stops ALL charges. Cloud Run shuts down, BigQuery stops accepting queries. It's instant. Bookmark this page.

### Step 0.5 — Verify Free Trial Status
📍 **GCP Console → Billing**

1. Still in Billing, look for **"Account management"**
2. Verify it says **"Free trial"** or that your free credits are active
3. DO NOT click "Upgrade" anywhere

### Step 0.6 — Enable Required APIs
📍 **GCP Console → API Library**

Go to each of these links and click **"Enable"**:

1. BigQuery API: `https://console.cloud.google.com/apis/library/bigquery.googleapis.com`
2. Cloud Run API: `https://console.cloud.google.com/apis/library/run.googleapis.com`
3. Artifact Registry API: `https://console.cloud.google.com/apis/library/artifactregistry.googleapis.com`
4. Cloud Build API: `https://console.cloud.google.com/apis/library/cloudbuild.googleapis.com`

> **Why these?** BigQuery = analytical data layer. Cloud Run = hosts your API for free. Artifact Registry + Cloud Build = how your code gets packaged and deployed.

### Step 0.7 — Verify Your Permissions
📍 **GCP Console → IAM**

Since you created this project, you're automatically the **Owner** — which means you have all permissions needed. Verify this:

1. Go to: `https://console.cloud.google.com/iam-admin/iam`
2. Make sure `resume-api-portfolio` is selected in the project dropdown
3. You should see your Google account email with the **Owner** role

> **What you do NOT need to set up:**
> - **IAM roles:** You're already Owner. No additional roles needed.
> - **Service accounts:** Cloud Run automatically creates a default compute service account when you first deploy. You don't create one manually.
> - **Encryption keys:** Google manages encryption by default (Google-managed encryption keys). For a portfolio project with public resume data, this is appropriate. Custom KMS keys would be over-engineering.
> - **VPC / networking:** Cloud Run handles networking. Your API will get a public HTTPS URL automatically.
> - **API keys for your app:** Your API is intentionally public and read-only. No API key needed.

### Step 0.8 — Connect Firebase Studio to Your GCP Project
📍 **Firebase Terminal** ← first time using the terminal!

Firebase Studio needs to know which GCP project to use. When you first open a terminal in Firebase Studio, run:

```bash
gcloud auth list
```

If your Google account is listed with a `*` next to it, you're authenticated. If not:

```bash
gcloud auth login
```

Then set your default project:

```bash
gcloud config set project resume-api-portfolio
```

Verify everything is connected:

```bash
gcloud config get-value project
# Expected: resume-api-portfolio

bq ls
# Expected: empty (no datasets yet — you'll create one in Phase 3)
# If you get an error about permissions, your auth or project isn't set correctly
```

> **When does this need to happen again?** If Firebase Studio rebuilds your environment (workspace reset, dev.nix change), you may need to re-run `gcloud auth login` and `gcloud config set project`. Your code and git history survive rebuilds, but auth tokens may not.

---

## PHASE 1: FIREBASE STUDIO SETUP (15 minutes)

> 📍 **All of Phase 1 happens inside Firebase Studio (browser-based IDE).**

### Step 1.1 — Open Firebase Studio
📍 **Your Browser → Firebase Studio**

1. Go to: `https://studio.firebase.google.com`
2. Sign in with the same Google account
3. Click **"Create new workspace"**
4. Choose the **Python** template (bottom row — not Flask, not Django, not Node)
5. Name it: `resume-api`
6. Wait for it to spin up (takes 1-2 minutes)

> **What is Firebase Studio?** It's a browser-based development environment. It has a code editor on the left, a terminal at the bottom (this is your Linux environment), and Gemini AI in the right panel that can write code for you. Think of it as VS Code + a Linux server + an AI assistant, all in one browser tab.

> **Important:** Firebase Studio uses **`uv`** as its package manager, NOT pip. The Python template is a "Python UV Starter." All dependency management goes through `uv`.

### Step 1.2 — Verify Your Environment
📍 **Firebase Terminal**

Run this one-liner to capture everything in a single screenshot:

```bash
python3 --version; uv --version; uname -a; echo $SHELL; pwd; ls -la
```

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Commands used:

| Command | Flag(s) | What It Does |
|---------|---------|-------------|
| `uname` | `-a` | Prints Linux kernel and OS info. `-a` = all info |
| `echo` | | Prints text or variable values to the terminal |
| `$SHELL` | | A variable that stores which shell you're using (e.g., /bin/bash) |
| `pwd` | | Print Working Directory — shows your current location in the filesystem |
| `ls` | `-la` | Lists files. `-l` = detailed view, `-a` = include hidden files |

</em></sub>


**Screenshot this output.** It shows Python version, package manager, Linux kernel info, shell type, working directory, and file listing.

Run these additional checks to see what's pre-installed:

```bash
docker --version; gcloud --version; bq --version; git --version
```

> **If `docker` is not found:** Don't worry — you may not need it. Cloud Run can build containers from source code directly. See Phase 4 for details.

> **If `gcloud` or `bq` is not found:** You'll need to install the Google Cloud SDK:
> ```bash
> curl https://sdk.cloud.google.com | bash
> exec -l $SHELL
> gcloud init
> ```
>
<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Commands used (if installing SDK):

| Command | Flag(s) | What It Does |
|---------|---------|-------------|
| `\|` (pipe) | | Sends the output of one command as input to the next |
| `bash` | | Runs a shell script (here: the gcloud installer) |
| `exec` | `-l` | Replaces current shell with a fresh one. `-l` = login shell (reloads config) |
| `gcloud init` | | Interactive setup: picks your Google account + default project |

</em></sub>


### Step 1.3 — Install Core Dependencies
📍 **Firebase Terminal**

```bash
uv add fastapi "uvicorn[standard]" google-cloud-bigquery faker pandas
```

After this finishes, verify the packages installed correctly:

```bash
uv pip list | grep -i "fastapi\|uvicorn\|bigquery\|faker\|pandas"
```

You should see all 5 packages listed with version numbers. If any are missing, re-run `uv add [package-name]`.

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Commands used:

| Command | What It Does |
|---------|-------------|
| `uv add` | Installs a Python package AND records it in `pyproject.toml` (like `npm install` for Python) |

</em></sub>


> **What each package does:**
> - `fastapi` — API framework (Python, fast, auto-generates Swagger documentation)
> - `uvicorn` — The ASGI server that runs FastAPI
> - `google-cloud-bigquery` — Python client for BigQuery
> - `faker` — Generates realistic fake data (names, emails, timestamps, domains)
> - `pandas` — Data manipulation library

### Step 1.4 — Configure Firebase Studio Preview
📍 **Firebase Editor** (editing `.idx/dev.nix`) then 📍 **Firebase Terminal** (git protect)

Firebase Studio uses `.idx/dev.nix` to auto-start your server when the workspace opens. Without this, the "Web Preview" panel won't work.

Open `.idx/dev.nix` and find the `previews` block. Replace the commented-out `web` section with:

```nix
    previews = {
      enable = true;
      previews = {
        web = {
          command = ["sh" "-c" "uv run -- python -m uvicorn api.main:app --reload --port 8000 --host 0.0.0.0"];
          manager = "web";
        };
      };
    };
```

Save the file. When prompted to **Rebuild Environment**, click yes.

> **Why this specific command format:**
> - We use `"sh" "-c" "..."` to run the full command through a shell
> - We use `uv run --` instead of bare `uvicorn` because Nix intercepts unrecognized commands and tries to install its own copy
> - Port is hardcoded to `8000` for simplicity — this matches your terminal curl commands
>
> **Common mistake:** Gemini will overwrite this file with `["uvicorn", "api.main:app", ...]` or `["python", "-m", "api.main"]`. Both will fail. See the git protection step below.

After rebuild, the preview panel should auto-start your server. If it shows "Starting server" but never loads, test from the terminal instead:
```bash
curl -s http://localhost:8000/ | python3 -m json.tool
```
If curl works, your API is fine — the preview panel is a nice-to-have, not a blocker.

**Git-protect dev.nix immediately** so you can restore it if Gemini overwrites it:

```bash
git add .idx/dev.nix
git commit -m "Lock dev.nix preview config - do not modify"
```

**If Gemini ever overwrites dev.nix**, restore it instantly:
```bash
git checkout .idx/dev.nix
```

**Also tell Gemini that dev.nix is off-limits.** In your GEMINI_CONTEXT.md, dev.nix is listed as a locked file. When referencing the context file, Gemini should not touch it. If Gemini suggests preview fixes, tell it: *"Do not modify dev.nix. Suggest changes for me to apply manually."*

> **Understanding the startup lifecycle:**
>
> | Environment | How Your Server Starts | Who Manages It |
> |---|---|---|
> | Firebase Studio | `dev.nix` preview command runs on workspace open | Automatic (Nix) |
> | Terminal (manual) | `uv run -- python -m uvicorn api.main:app --port 8000` | You |
> | Cloud Run (production) | Container starts on first HTTP request | Automatic (Google) |
>
> There is no persistent server to manage. You do NOT need systemctl, init.d, or startup scripts. Cloud Run is serverless — it scales to zero when idle and auto-starts on incoming requests.
>
> **If the preview and your manual terminal server conflict** ("Address already in use"), kill the other process:
> ```bash
> kill $(pgrep -f uvicorn)
> ```

### Step 1.5 — First Git Commit
📍 **Firebase Terminal**

Firebase Studio workspaces are **ephemeral** — they can reset without warning. Protect your work by committing early and often.

```bash
git add .
git commit -m "Initial workspace setup with dependencies"
```

If git asks you to configure your identity first, run these two commands (use your own name and email):

```bash
git config --global user.email "you@example.com"
git config --global user.name "Your Name"
```

Then re-run the `git add .` and `git commit` commands above.

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Commands used:

| Command | Flag(s) | What It Does |
|---------|---------|-------------|
| `git add` | `.` | Stages files for commit. `.` = stage everything in current directory |
| `git commit` | `-m` | Saves staged changes as a snapshot. `-m` = commit message inline |

</em></sub>


> **Rule of thumb:** Commit every 30 minutes or after every major step. If the workspace resets, you can `git clone` and be back up in 2 minutes.

---

## PHASE 2: BUILD THE API (2-3 hours)

> 📍 **All of Phase 2 happens inside Firebase Studio — terminal for commands, Gemini chat for code generation, editor for verification.**

> **This is where Gemini does the heavy lifting.** You'll give Gemini specific prompts in the right panel. Copy-paste these prompts, review what it generates, understand it, then tell it to adjust if needed.

### Step 2.1 — Create Project Structure
📍 **Firebase Terminal**

You're already inside the `resume-api` workspace. **Do NOT create a nested resume-api folder.** Just create the subdirectories:

```bash
pwd

mkdir -p api data sql screenshots
touch api/main.py api/models.py api/database.py
touch data/generate_data.py data/seed_bigquery.py
touch sql/tier1_naive.sql sql/tier2_optimized.sql sql/tier3_scale.sql
touch Dockerfile README.md .gitignore GEMINI_CONTEXT.md
```

> **GEMINI_CONTEXT.md** is a reference file for Firebase Studio's Gemini AI assistant. It contains your project structure, database schema, command patterns, and rules (like "always use `uv run --`" and "analytics endpoints read from `api_queries`, not `queries`"). At the start of every Gemini session, tell it: *"Read GEMINI_CONTEXT.md in the project root. Follow its rules for every task I give you."* This prevents Gemini from making conflicting decisions across prompts. Update this file as your project evolves — if you add new tables, endpoints, or change structure, add it here so Gemini stays current. A template is provided in the project files.

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Commands used:

| Command | Flag(s) | What It Does |
|---------|---------|-------------|
| `mkdir` | `-p` | Creates directories. `-p` = create parent directories too, no error if they exist |
| `touch` | | Creates an empty file (or updates timestamp if it already exists) |

</em></sub>


**Screenshot the terminal after this.** You've demonstrated `mkdir -p`, `touch`, and project organization.

Verify the structure:

```bash
find . -type f -not -path './.git/*' -not -path './.idx/*' -not -path './.venv/*' | sort
```

You should see your project files listed — `api/main.py`, `api/models.py`, `api/database.py`, `data/generate_data.py`, `sql/tier1_naive.sql`, `Dockerfile`, `README.md`, `.gitignore`, etc. If you see thousands of lines (pandas test files, etc.), you forgot to exclude `.venv` — add `-not -path './.venv/*'` to the command.

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Commands used:

| Command | Flag(s) | What It Does |
|---------|---------|-------------|
| `find` | `-type f` | Searches for files in a directory tree. `-type f` = files only (not folders) |
| | `-not -path` | Excludes matching paths from results |
| `sort` | | Sorts output alphabetically |

</em></sub>


### Step 2.2 — Prompt for Gemini: The Core API
📍 **Firebase Studio → Gemini Chat** (paste the prompt below into Gemini)

> **Before every Gemini prompt in this guide:** Run this command and paste the output at the top of your Gemini prompt, before the instructions. This gives Gemini visibility into what already exists so it doesn't create conflicting table names, duplicate imports, or wrong file paths:
> ```bash
> head -5 api/main.py api/models.py api/database.py data/generate_data.py 2>/dev/null && ls -la data/ 2>/dev/null
> ```
> For Step 2.2 (the first prompt), these files will be empty — that's fine. For every prompt after this one, the output shows Gemini what's already built.

Copy this prompt into the Gemini chat panel in Firebase Studio:

---

**PROMPT TO COPY:**

```
Build me a FastAPI application in api/main.py with the following specifications:

CONTEXT: This is a portfolio project. The API serves resume data and includes
a simulated analytics tracking system. The data model mirrors digital advertising 
reporting patterns (advertisers, campaigns, performance metrics).

ENDPOINTS (REST design):

1. GET /
   - Returns API health status and metadata
   - Response: {"status": "healthy", "version": "1.0", "endpoints": [...]}

2. GET /resume
   - Returns complete resume as structured JSON
   - Response includes: summary, experience[], skills[], education[], certifications[]

3. GET /resume/experience
   - Returns only work experience
   - Query params: ?company=deloitte&after=2020
   - Shows filtering capability

4. GET /resume/skills
   - Returns skills grouped by category
   - Query params: ?category=databases or ?keyword=sql
   - When filtering by ?category=, return ONLY that category as a plain dict
     (do NOT validate against the full Skills Pydantic model, since filtered
     results won't have all fields)

5. GET /resume/education

6. GET /resume/certifications

7. GET /analytics/queries
   - Returns visitor query log data from SQLite
   - Query params: ?domain=google.com&limit=50&offset=0
   - Pagination support

8. GET /analytics/top-domains
   - Returns top N domains hitting the API
   - Query params: ?n=10
   - MUST use a Python dictionary as a frequency map AND collections.Counter, 
     showing both approaches in comments

9. GET /analytics/performance
   - Returns response time percentiles (p50, p95, p99)
   - Simulates API health monitoring

TECHNICAL REQUIREMENTS:
- Use ABSOLUTE imports (not relative) when importing between files in api/:
  Use `import models` and `import database`, NOT `from . import models`
  Reason: In Phase 2, Docker runs main.py as a standalone module via
  `uvicorn main:app`, and relative imports fail without a parent package.
- Use Pydantic models for all request/response schemas (in api/models.py)
- Use SQLite database for the analytics data (connection in api/database.py)
- The analytics endpoints (/analytics/queries, /analytics/top-domains, /analytics/performance)
  must read from a table called "api_queries" with these columns:
  query_id, timestamp, recruiter_domain, endpoint_hit, skill_searched,
  response_time_ms, http_status, user_agent, referer_url
  This table will be pre-populated by a separate data generation script.
  Do NOT create a different table for analytics data.
- Include proper HTTP status codes (200, 400, 404, 500)
- Include rate limiting headers in responses (X-RateLimit-Limit, X-RateLimit-Remaining)
- Add CORS middleware
- Add request logging middleware that logs: timestamp, endpoint, response_time_ms, client_ip
- Include docstrings explaining design decisions

========================================================
RESUME DATA — Hardcode all of this in a Python dictionary
========================================================

CONTACT:
- name: "[YOUR_NAME]"
- email: "[YOUR_EMAIL]"
- linkedin: "[YOUR_LINKEDIN_URL]"
- location: "[YOUR_CITY]"

PROFESSIONAL SUMMARY:
"[YOUR_PROFESSIONAL_SUMMARY — 2-4 sentences describing your experience, 
client types, technical skills, and measurable outcomes. Example: 
'Technical Solutions Consultant with 8+ years developing customized solutions 
for Fortune 500 enterprises and federal agencies. Combines hands-on programming 
expertise (Python, SQL, Bash) with proven ability to manage technical relationships. 
Demonstrated track record delivering end-to-end solutions serving 50,000+ users 
with measurable outcomes: 30% cost reduction and 100% regulatory compliance.']"

CORE COMPETENCIES (group as nested dict by category):
- technical_development: [
    "[YOUR_TECHNICAL_SKILLS — programming languages, frameworks, tools. Example:
    'Python scripting and automation', 'SQL (PostgreSQL, Oracle, T-SQL)', 
    'System architecture design', 'API integration', 'Git version control']"
  ]
- solutions_analytics: [
    "[YOUR_ANALYTICS_SKILLS — BI tools, data platforms, methodologies. Example:
    'Business analysis and requirements gathering',
    'Dashboard development (CloudWatch, MicroStrategy, custom analytics)',
    'Large volume data platform management']"
  ]
- client_partner_management: [
    "[YOUR_MANAGEMENT_SKILLS — leadership, communication, stakeholder skills. Example:
    'Technical relationship management',
    'Cross-functional team leadership (100+ engineers)',
    'Translating technical concepts to non-technical and executive audiences']"
  ]
- cloud_infrastructure: [
    "[YOUR_CLOUD_SKILLS — cloud platforms, IaC, CI/CD. Example:
    'AWS (EC2, S3, IAM, VPC, CloudWatch, Lambda, Fargate)',
    'Infrastructure as Code (Terraform, CloudFormation)',
    'Docker', 'CI/CD (GitLab)', 'FinOps and cost optimization']"
  ]

EXPERIENCE (list of dicts, each with company, title, dates, projects):

[YOUR_EXPERIENCE — Structure each company like this:]

Company 1: [Company Name]
  Title: "[Your Title]"
  Dates: "[Start Date – End Date]"
  Projects: [
    {
      name: "[Project Name]",
      subtitle: "[Brief project description]",
      bullets: [
        "[Achievement bullet 1 — start with action verb, include metrics]",
        "[Achievement bullet 2]",
        "[Achievement bullet 3]"
      ]
    },
    {
      name: "[Second Project Name]",
      subtitle: "[Brief project description]",
      bullets: [
        "[Achievement bullet 1]",
        "[Achievement bullet 2]"
      ]
    }
  ]

Company 2: [Second Company Name]
  Title: "[Your Title]"
  Dates: "[Start Date – End Date]"
  Projects: [
    {
      name: "[Project Name]",
      subtitle: "[Brief project description]",
      bullets: [
        "[Achievement bullet 1]",
        "[Achievement bullet 2]"
      ]
    }
  ]

[Add as many companies and projects as you have. Include ALL 
bullet points — Gemini will truncate if you leave them vague.]

CERTIFICATIONS (list):
- "[YOUR_CERTIFICATIONS — list each one. Example:
  'AWS Certified Solutions Architect – Associate',
  'CompTIA Security+ ce',
  'Oracle Cloud Infrastructure 2024 Architect Associate']"

EDUCATION:
- school: "[YOUR_UNIVERSITY]"
- degree: "[YOUR_DEGREE]"
- major: "[YOUR_MAJOR]"

========================================================
END RESUME DATA
========================================================

Also create api/models.py with all Pydantic models and api/database.py with SQLite setup.
```

> **Important:** Replace every `[PLACEHOLDER]` above with your actual information before pasting into Gemini. The more detail you provide (especially in experience bullets), the less Gemini will invent on its own. Include ALL bullet points from your resume — if you leave them vague, Gemini will generate generic filler.

---

**After Gemini generates the files, verify all three were created:**

```bash
ls -la api/main.py api/models.py api/database.py
```

You should see three files, all with non-zero file sizes (the second column should be hundreds or thousands of bytes, not 0).

**Check that the API code has all required features.** Run these `grep` commands — each one searches the code for a specific feature. If a command prints nothing, that feature is missing and you need to tell Gemini to add it:

```bash
# Check all 9 endpoints exist (each grep should print at least one line)
grep -n 'def.*resume'       api/main.py
grep -n 'def.*experience'   api/main.py
grep -n 'def.*skills'       api/main.py
grep -n 'def.*education'    api/main.py
grep -n 'def.*certification' api/main.py
grep -n 'def.*queries'      api/main.py
grep -n 'def.*top.domain'   api/main.py
grep -n 'def.*performance'  api/main.py

# Check query parameters exist
grep -n 'company'   api/main.py    # should appear in experience endpoint
grep -n 'category'  api/main.py    # should appear in skills endpoint
grep -n 'keyword'   api/main.py    # should appear in skills endpoint
grep -n 'limit'     api/main.py    # should appear in analytics/queries
grep -n 'offset'    api/main.py    # should appear in analytics/queries

# Check technical requirements
grep -n 'CORSMiddleware'       api/main.py    # CORS middleware
grep -n 'Counter'              api/main.py    # collections.Counter (for top-domains)
grep -n 'X-RateLimit'          api/main.py    # Rate limiting headers
grep -n 'response_time'        api/main.py    # Request logging middleware

# Check Pydantic models exist
grep -n 'class.*BaseModel'     api/models.py  # Should show multiple model classes

# Check database setup
grep -n 'sqlite'               api/database.py  # SQLite connection
```

**If any `grep` returns nothing,** tell Gemini what's missing. Be specific:

> *"The /resume/skills endpoint is missing the ?keyword= query parameter. Add it with case-insensitive matching across all skill categories."*

> *"api/main.py is missing CORS middleware. Add CORSMiddleware from starlette with allow_origins=['*']."*

> *"The /analytics/top-domains endpoint only uses collections.Counter. Also include a manual dictionary frequency map approach with comments comparing both."*

**Spot-check resume data accuracy** — open `api/main.py` and search for your resume data:

```bash
grep -c 'Deloitte'     api/main.py    # Should be at least 1
grep -c 'New Resources' api/main.py   # Should be at least 1
grep -c 'Meta'          api/main.py   # Should be at least 1 (Meta privacy project)
grep -c 'Oklahoma'      api/main.py   # Should be at least 1 (education)
```

If any of these return `0`, Gemini dropped that content. Tell it: *"The resume data is incomplete. You're missing [company name]. Add the full experience entry for [project name]."*

### Step 2.3 — Prompt for Gemini: Data Generation
📍 **Firebase Studio → Gemini Chat** (paste the prompt below into Gemini)

After the API is built, give Gemini this prompt:

---

**PROMPT TO COPY:**

```
Create data/generate_data.py that generates realistic analytics data.

This simulates a tracking system for the Resume API — like Google Analytics for an API.
The data model mirrors patterns you'd see in digital advertising reporting.

GENERATE TWO DATASETS:

1. SQLite dataset (10,000 rows) — saved to data/analytics.db
   Schema: api_queries table
   - query_id (INTEGER PRIMARY KEY)
   - timestamp (DATETIME) — random timestamps over the last 90 days
   - recruiter_domain (TEXT) — use realistic company domains like google.com, meta.com, 
     amazon.com, deloitte.com, mckinsey.com, walmart.com, target.com, nike.com
   - endpoint_hit (TEXT) — one of /resume, /resume/experience, /resume/skills, etc.
   - skill_searched (TEXT) — Python, SQL, BigQuery, API Design, Cloud, Agile, etc.
   - response_time_ms (INTEGER) — realistic range 12-850ms
   - http_status (INTEGER) — weighted: 200 (85%), 304 (5%), 400 (4%), 404 (4%), 500 (2%)
   - user_agent (TEXT)
   - referer_url (TEXT)

2. CSV file (500,000 rows) — saved to data/recruiter_queries.csv
   Same schema but 50x larger, for uploading to BigQuery
   This demonstrates the "why BigQuery" story — SQLite handles 10K fine, 
   but at 500K+ you need a columnar analytical engine

Use the Faker library for realistic timestamps (last 90 days),
and use Python's random with weighted choices for the distribution.

Print progress every 100K rows so I can see it working.
Include timing: print how long each dataset took to generate.
```

---

**After generation, verify both datasets were created:**

```bash
ls -la data/analytics.db
# Expected: a file around 500KB-2MB (the SQLite database with 10,000 rows)

wc -l data/recruiter_queries.csv
# Expected: 500001 (500,000 data rows + 1 header row)

head -3 data/recruiter_queries.csv
# Expected: first line is column headers, next 2 lines are sample data

tail -3 data/recruiter_queries.csv
# Expected: last 3 data rows — check that timestamps look realistic
```

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Commands used:

| Command | Flag(s) | What It Does |
|---------|---------|-------------|
| `wc` | `-l` | Word Count. `-l` = count lines only (tells you how many rows in the CSV) |
| `head` | `-3` | Shows the first N lines of a file |
| `tail` | `-3` | Shows the last N lines of a file |

</em></sub>


> **Note the date range in the CSV output.** You'll need to match these dates when writing SQL queries in Phase 3. If the data spans December 2025–February 2026, your SQL WHERE clauses need to reference those dates, not hardcoded values.

### Step 2.4 — Prompt for Gemini: Dockerfile
📍 **Firebase Studio → Gemini Chat** (paste the prompt below into Gemini)

```
Create a Dockerfile for this FastAPI application that:
1. Uses python:3.11-slim as base image
2. Copies requirements.txt and installs dependencies with pip
3. Copies the api/ directory and data/analytics.db
4. Exposes port 8080 (Cloud Run requirement)
5. Runs uvicorn with host 0.0.0.0 and port 8080
6. Include comments explaining each Docker instruction

Note: My project uses uv for dependency management (pyproject.toml).
Before building the Docker image, I will generate requirements.txt with:
  uv pip compile pyproject.toml -o requirements.txt
Create the Dockerfile assuming requirements.txt will exist at build time.
The Dockerfile itself should use standard pip (not uv) to keep the image simple.
```

After Gemini generates the Dockerfile, verify it has the essential instructions:

```bash
grep -n 'FROM'   Dockerfile    # Should show python:3.11-slim (the base image)
grep -n 'COPY'   Dockerfile    # Should show at least 2 COPY lines (requirements + app code)
grep -n 'RUN'    Dockerfile    # Should show pip install
grep -n 'EXPOSE' Dockerfile    # Should show 8080 (Cloud Run's required port)
grep -n 'CMD'    Dockerfile    # Should show uvicorn startup command
```

Each `grep` should print at least one line. If any prints nothing, tell Gemini: *"The Dockerfile is missing a [FROM/COPY/EXPOSE/CMD] instruction. Add it."*

> **Understanding the SQLite lifecycle:** The `COPY ./data/analytics.db` line bakes your database into the Docker image at build time. Cloud Run containers are stateless — if the container restarts or is replaced, it reloads from the image. This is fine for a read-only resume API. But it means: if you regenerate data or change resume content, you must rebuild and redeploy for changes to appear in production.

### Step 2.5 — Run and Test Locally
📍 **Firebase Terminal** (run commands) + 📍 **Firebase Preview** (view results in Web tab)

After Gemini generates all the files:

```bash
cd ~/resume-api && uv run -- python data/generate_data.py

pwd

cd ~/resume-api && uv run -- python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload &

sleep 2
curl http://localhost:8000/ | python3 -m json.tool
# Expected: {"status": "healthy", "version": "1.0", "endpoints": [...]}

curl http://localhost:8000/resume | python3 -m json.tool
# Expected: Full resume JSON with summary, experience, skills, education, certifications

curl "http://localhost:8000/resume/experience?company=deloitte" | python3 -m json.tool
# Expected: Only Deloitte experience entries (not New Resources)

curl "http://localhost:8000/resume/skills?category=cloud_infrastructure" | python3 -m json.tool
# Expected: Only cloud/infra skills (AWS, Docker, Terraform, etc.)

curl "http://localhost:8000/analytics/top-domains?n=5" | python3 -m json.tool
# Expected: Top 5 domains with hit counts (google.com, amazon.com, etc.)
```

If any curl returns an error like `Connection refused`, the server didn't start. Check the terminal output above the curl commands for Python error messages — usually a missing import or syntax error in the generated code. Tell Gemini the exact error.

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Commands used:

| Command | Flag(s) | What It Does |
|---------|---------|-------------|
| `uv run -- python -m uvicorn` | `--host`, `--port`, `--reload` | Starts the FastAPI server through uv's virtual environment. `--host 0.0.0.0` = accept connections from anywhere. `--port 8000` = listen on port 8000. `--reload` = auto-restart when code changes. We use `uv run` because Firebase Studio's Nix system intercepts bare `uvicorn` and uses the wrong Python |
| `&` | | Runs the command in the background so you get your terminal back |
| `sleep` | `2` | Pauses for 2 seconds (gives the server time to start before testing) |
| `python3 -m json.tool` | | Formats raw JSON output into readable, indented JSON |

</em></sub>


**Screenshot the curl outputs.** This proves the API is working.

Now demonstrate Linux process management:

```bash
ps aux | grep uvicorn

ss -tlnp | grep 8000

top -bn1 | head -20

kill $(pgrep -f uvicorn)

ps aux | grep uvicorn
```

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Commands used:

| Command | Flag(s) | What It Does |
|---------|---------|-------------|
| `ps` | `aux` | Lists all running processes. `a` = all users, `u` = detailed format, `x` = include background processes |
| `grep` | | Filters output to only show lines matching a pattern (here: "uvicorn") |
| `ss` | `-tlnp` | Socket Statistics — shows network connections. `-t` = TCP, `-l` = listening, `-n` = numeric ports, `-p` = show process name |
| `top` | `-bn1` | Shows system resource usage. `-b` = batch mode (for screenshots), `-n1` = one snapshot only |
| `kill` | | Sends a signal to stop a process |
| `pgrep` | `-f` | Finds process IDs by name. `-f` = match against full command line |
| `$(...)` | | Command substitution — runs the inner command and passes its output to the outer command |

</em></sub>


**Screenshot ALL of these commands and their outputs.** This is your Linux CLI evidence.

### Step 2.6 — Test the Auto-Generated Docs
📍 **Firebase Preview** (Web tab → append `/docs` to the URL)

FastAPI automatically creates Swagger (OpenAPI) documentation:

```bash
# If the server is still running from Step 2.5, skip this command entirely.
# If you stopped it, or got "Address already in use", kill any leftover process first:
#   kill $(pgrep -f uvicorn)
# Then start fresh:
cd ~/resume-api && uv run -- python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 &
```

In Firebase Studio, open the preview browser (look for the globe/preview icon in the top bar, or click the port `8000` link if it appears). Navigate to:

```
http://localhost:8000/docs
```

You should see a page titled something like "Resume API" with all 9 endpoints listed. Each endpoint has a dropdown arrow — click one to expand it and see the parameters and response schema. You can also click **"Try it out"** to test an endpoint directly from the browser.

Verify in the Swagger UI:
- All 9 endpoints are listed (scroll through the page)
- Click on `GET /resume/experience` → click "Try it out" → enter `deloitte` in the `company` field → click "Execute" → you should see filtered results
- The response section shows the Pydantic model schema (field names and types)

**Screenshot the Swagger UI** showing all 9 endpoints with their schemas.

### Step 2.7 — Git Commit
📍 **Firebase Terminal**

```bash
git add .
git commit -m "Add API endpoints, data generation, and Dockerfile"
```

---

## PHASE 3: BIGQUERY SETUP & SQL DEMOS (2-3 hours)

> 📍 **Phase 3 switches between environments frequently.** Watch the location tags carefully.
> - Dataset creation: **GCP Console** or **Firebase Terminal** (your choice)
> - CSV upload: **Firebase Terminal** (preferred) or **GCP Console** (fallback)
> - SQL queries: **BigQuery Console** (in your browser)

### Step 3.1 — Create BigQuery Dataset
📍 **BigQuery Console** (steps 1-7) then 📍 **Firebase Terminal** (verification)

📍 **BigQuery Console:**

1. Go to: `https://console.cloud.google.com/bigquery`
2. Make sure your `resume-api-portfolio` project is selected
3. In the left panel, click the three dots next to your project name
4. Click **"Create dataset"**
5. Dataset ID: `resume_analytics`
6. Location: `US`
7. Click **"Create Dataset"**

📍 **Firebase Terminal** — verify the dataset was created:

```bash
bq ls
```

You should see `resume_analytics` in the output.

### Step 3.2 — Upload Your CSV to BigQuery
📍 **Firebase Terminal** (preferred) or 📍 **GCP Console** (fallback)

**Preferred method: CLI upload from Firebase Studio.** Your CSV is already in the container and `bq` is pre-installed — no reason to download to your laptop and re-upload through the browser.

📍 **Firebase Terminal** — pre-flight checks (do these first):

```bash
# 1. Verify you're authenticated and pointed at the right project
gcloud auth list
# Expected: your Google account with a * next to it
# If not: gcloud auth login

gcloud config get-value project
# Expected: resume-api-portfolio
# If not: gcloud config set project resume-api-portfolio

# 2. Verify the dataset exists (created in Step 3.1)
bq ls
# Expected: should list "resume_analytics"
# If not: bq mk resume_analytics

# 3. Verify your CSV exists and has data
ls -lh data/recruiter_queries.csv
# Expected: ~50MB file
# If missing: uv run -- python data/generate_data.py

# 4. Check the CSV header row (these become your column names)
head -1 data/recruiter_queries.csv
# Expected: query_id,timestamp,recruiter_domain,endpoint_hit,skill_searched,response_time_ms,http_status,user_agent,referer_url
```

> **If any pre-flight check fails, fix it before proceeding.** The most common issue is auth tokens getting wiped after a workspace rebuild — just re-run `gcloud auth login`.

**Upload the CSV:**

```bash
bq load \
  --source_format=CSV \
  --autodetect \
  --skip_leading_rows=1 \
  resume_analytics.recruiter_queries \
  data/recruiter_queries.csv
```

This should take 10-30 seconds. You'll see output ending in something like `Upload complete` or showing the job status as `DONE`.

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Commands and flags explained:

| Command / Flag | What It Does |
|---------|-------------|
| `bq load` | Uploads data into a BigQuery table |
| `--source_format=CSV` | Tells BigQuery the file is comma-separated values |
| `--autodetect` | Let BigQuery infer column types from the data |
| `--skip_leading_rows=1` | Skip the header row (column names) — without this, BigQuery treats headers as data |
| `resume_analytics.recruiter_queries` | Target: dataset.table_name |
| `data/recruiter_queries.csv` | Source: local file path (local to the container, not your laptop) |
| `\` | Line continuation — splits a long command across multiple lines for readability |

</em></sub>

**Post-upload verification (all three checks):**

```bash
# 1. Row count — should be exactly 500,000
bq query --use_legacy_sql=false \
  'SELECT COUNT(*) as total_rows FROM resume_analytics.recruiter_queries'

# 2. Schema check — verify column types (especially timestamp)
bq show --schema --format=prettyjson resume_analytics.recruiter_queries
# Look for: "name": "timestamp", "type": "TIMESTAMP" (not STRING)
# If timestamp shows as STRING, the data is still usable but you'll need
# PARSE_TIMESTAMP() in your SQL queries later. Not a blocker.

# 3. Sample rows — sanity check the data looks right
bq query --use_legacy_sql=false \
  'SELECT * FROM resume_analytics.recruiter_queries LIMIT 5'
```

> **What to look for in the schema check:**
>
> | Column | Expected Type | If Wrong |
> |--------|--------------|----------|
> | query_id | INTEGER or STRING | Either is fine |
> | timestamp | TIMESTAMP | If STRING, use `PARSE_TIMESTAMP()` in queries |
> | recruiter_domain | STRING | ✅ |
> | endpoint_hit | STRING | ✅ |
> | skill_searched | STRING | ✅ |
> | response_time_ms | FLOAT or INTEGER | Either is fine |
> | http_status | INTEGER | ✅ |
> | user_agent | STRING | ✅ |
> | referer_url | STRING | ✅ |

**If the upload fails:**

```bash
# Check the error message — common issues:
# "Not found: Dataset" → dataset doesn't exist: bq mk resume_analytics
# "Access Denied" → auth issue: gcloud auth login
# "Could not parse" → CSV formatting issue: head -5 data/recruiter_queries.csv
```

**Fallback — Option B: Console upload (if CLI doesn't work):**

📍 **Your Browser → GCP Console**

If `bq load` fails repeatedly and you need to move on:

1. In Firebase Studio's Explorer panel, right-click `data/recruiter_queries.csv` → **Download**
2. Go to: `https://console.cloud.google.com/bigquery`
3. Click on your `resume_analytics` dataset
4. Click **"Create Table"**
5. Source: **Upload** → select the downloaded CSV
6. Table name: `recruiter_queries`
7. Check **"Auto detect"** schema
8. Click **"Create Table"**

> **Note:** This downloads ~50MB to your laptop then re-uploads it to the same cloud. It works but it's inefficient — the CLI method above keeps everything in Google's infrastructure. Mention both approaches to show you understand the trade-off.

### Step 3.3 — Confirm Your Data's Date Range
📍 **BigQuery Console** (run SQL in the query editor)

Before writing queries, check what dates your generated data actually covers:

```bash
bq query --use_legacy_sql=false \
  'SELECT MIN(timestamp) as earliest, MAX(timestamp) as latest FROM resume_analytics.recruiter_queries'
```

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Commands used:

| Command | Flag(s) | What It Does |
|---------|---------|-------------|
| `bq query` | `--use_legacy_sql=false` | Runs a SQL query in BigQuery from the terminal. The flag tells it to use standard SQL (not BigQuery's legacy dialect) |

</em></sub>


Or run this in the BigQuery console query editor. **Write down the date range.** You'll use it in Tier 3.

### Step 3.4 — SQL Queries: The Three-Tier Progression
📍 **BigQuery Console** (paste each query into the query editor, run, screenshot results)

This is the centerpiece of the BigQuery demonstration. Run each query in the BigQuery console, screenshot the results AND the performance stats (bytes processed, time elapsed).

---

**TIER 1: Naive Query (The baseline — show why this is problematic at scale)**

```sql
-- File: sql/tier1_naive.sql
-- PURPOSE: Full table scan with no optimization
-- At 500K rows this is fine, but at 500M+ this gets expensive fast

SELECT 
  recruiter_domain, 
  COUNT(*) as total_hits
FROM `resume-api-portfolio.resume_analytics.recruiter_queries`
GROUP BY recruiter_domain
ORDER BY total_hits DESC;

-- RECORD THESE METRICS:
-- Bytes processed: ___________
-- Elapsed time: ___________
```

**Screenshot the query, results, and performance stats.**

> **Where to find performance stats:** After running a query in the BigQuery console, look at the green bar below the results. It shows "This query will process X bytes" before running, and after running shows elapsed time and bytes billed. Write both numbers down — you'll compare them across all three tiers.

---

**TIER 2: Optimized with CTEs + Window Functions**

```sql
-- File: sql/tier2_optimized.sql
-- PURPOSE: Production-quality query using CTE, window functions, SAFE_DIVIDE
-- Mirrors the SQL patterns used in ad tech reporting

WITH recruiter_stats AS (
  SELECT
    recruiter_domain,
    COUNT(*) AS total_hits,
    COUNTIF(http_status = 200) AS successful_hits,
    ROUND(AVG(response_time_ms), 2) AS avg_response_ms,
    APPROX_TOP_COUNT(skill_searched, 1)[OFFSET(0)].value AS top_skill_searched,
    MIN(timestamp) AS first_visit,
    MAX(timestamp) AS last_visit
  FROM `resume-api-portfolio.resume_analytics.recruiter_queries`
  WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY)
  GROUP BY recruiter_domain
),

ranked AS (
  SELECT
    *,
    RANK() OVER (ORDER BY total_hits DESC) AS activity_rank,
    ROUND(SAFE_DIVIDE(successful_hits, total_hits) * 100, 1) AS success_rate_pct,
    DATE_DIFF(DATE(last_visit), DATE(first_visit), DAY) AS engagement_span_days
  FROM recruiter_stats
)

SELECT * FROM ranked
WHERE activity_rank <= 10
ORDER BY activity_rank;

-- WHAT THIS DEMONSTRATES:
-- CTE: Readable, maintainable multi-step logic
-- COUNTIF: Conditional aggregation (ads data has zeroes everywhere)
-- APPROX_TOP_COUNT: BigQuery-specific approximate function
-- RANK() OVER: Window function for ranking without self-join
-- SAFE_DIVIDE: Prevents division by zero
-- DATE_DIFF: Date arithmetic
-- TIMESTAMP_SUB: Partition-friendly date filtering

-- RECORD THESE METRICS:
-- Bytes processed: ___________
-- Elapsed time: ___________
-- Improvement vs Tier 1: ___________%
```

**Screenshot the query, results, and performance stats.**

---

**TIER 3: Partitioned & Clustered Table (Scale-aware optimization)**

> **Before running this:** Use the date range you captured in Step 3.3 to update the WHERE clause below. Replace the example dates with a 30-day window that falls within your actual data.

```sql
-- File: sql/tier3_scale.sql
-- PURPOSE: Create an optimized table structure and show the performance difference
-- This is what you'd recommend to clients processing billions of ad impressions

-- Step 1: Create optimized table
CREATE OR REPLACE TABLE `resume-api-portfolio.resume_analytics.recruiter_queries_optimized`
PARTITION BY DATE(timestamp)
CLUSTER BY recruiter_domain, endpoint_hit
AS SELECT * FROM `resume-api-portfolio.resume_analytics.recruiter_queries`;

-- Step 2: Run a query on the optimized table
-- ⚠️ UPDATE THESE DATES to match your actual data range from Step 3.3
SELECT
  recruiter_domain,
  endpoint_hit,
  COUNT(*) AS hits,
  APPROX_QUANTILES(response_time_ms, 100)[OFFSET(95)] AS p95_response_ms,
  APPROX_QUANTILES(response_time_ms, 100)[OFFSET(50)] AS p50_response_ms
FROM `resume-api-portfolio.resume_analytics.recruiter_queries_optimized`
WHERE DATE(timestamp) BETWEEN 
  DATE_SUB(CURRENT_DATE(), INTERVAL 60 DAY) AND DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
  AND recruiter_domain IN ('google.com', 'amazon.com')
GROUP BY 1, 2
ORDER BY hits DESC;

-- COMPARE: Bytes scanned on this vs Tier 1
-- Partition pruning + clustering should show dramatic reduction
-- At billions of rows, this is the difference between a $5 query and a $0.05 query

-- WHY PARTITIONING/CLUSTERING MATTERS:
-- Partition by DATE(timestamp): BigQuery skips entire date chunks not in the WHERE clause
-- Cluster by recruiter_domain: Within each partition, data is sorted for efficient filtering
-- APPROX_QUANTILES: BigQuery-native percentile calculations at scale

-- RECORD THESE METRICS:
-- Bytes processed: ___________
-- Elapsed time: ___________
-- Improvement vs Tier 1: ___________%
```

**Screenshot the query, results, and performance stats. Also screenshot the partitioned table details in the BigQuery console.**

---

### Step 3.5 — SQLite vs BigQuery Comparison (OPTIONAL — Cut if short on time)
📍 **Firebase Studio → Gemini Chat** (generate script) then 📍 **Firebase Terminal** (run it)

This shows the "when to use which" decision framework.

**Prompt for Gemini:**

```
Create a Python script at data/compare_engines.py that:

1. Runs a "top domains by hit count" query on SQLite (data/analytics.db, 10K rows)
2. Runs the equivalent query on BigQuery (500K rows)
3. Times both executions
4. Prints a comparison table showing:
   - Database engine
   - Row count
   - Query execution time
   - Result set

This demonstrates understanding of WHEN to use each tool:
- SQLite: Perfect for local/embedded, <100K rows, single-user
- BigQuery: Columnar analytical engine, millions/billions of rows, concurrent users

Use the google-cloud-bigquery Python client library.
Include comments explaining the architectural decision of when each is appropriate.
```

### Step 3.6 — Git Commit
📍 **Firebase Terminal**

```bash
git add sql/
git commit -m "Add 3-tier SQL progression queries"
```

---

## PHASE 4: DEPLOY TO CLOUD RUN (1-2 hours)

> 📍 **Mostly Firebase Terminal for commands, then Your Browser to verify the live deployment.**

### Step 4.1 — Generate requirements.txt for Docker
📍 **Firebase Terminal**

Since the project uses `uv` with `pyproject.toml`, generate a standard `requirements.txt` that Docker can use:

```bash
uv pip compile pyproject.toml -o requirements.txt

cat requirements.txt
```

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Commands used:

| Command | Flag(s) | What It Does |
|---------|---------|-------------|
| `uv pip compile` | `-o` | Reads `pyproject.toml` and generates a pinned `requirements.txt`. `-o` = output file |
| `cat` | | Prints the entire contents of a file to the terminal |

</em></sub>


### Step 4.2 — Local Docker Test (If Docker is Available)
📍 **Firebase Terminal**

```bash
docker --version
```

**If Docker IS available:**

> **Important:** The Docker image bakes in a copy of `data/analytics.db` at build time. If you changed your resume data in `api/main.py` or re-ran `data/generate_data.py` since your last build, you must rebuild the image to pick up those changes.

```bash
docker build -t resume-api .

docker run -p 8080:8080 resume-api &
sleep 3
curl http://localhost:8080/
curl http://localhost:8080/resume
curl "http://localhost:8080/analytics/top-domains?n=5"

docker stop $(docker ps -q)
```

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Commands used (if Docker is available):

| Command | Flag(s) | What It Does |
|---------|---------|-------------|
| `docker build` | `-t` | Builds a Docker image from a Dockerfile. `-t resume-api` = name/tag the image |
| `docker run` | `-p` | Runs a container from an image. `-p 8080:8080` = map host port to container port |
| `docker stop` | | Stops a running container |
| `docker ps` | `-q` | Lists running containers. `-q` = quiet mode (IDs only, useful for piping to `docker stop`) |

</em></sub>


**If Docker is NOT available:** Skip to Step 4.3. The `gcloud run deploy --source .` command builds the Docker image in the cloud — you don't need Docker installed locally.

### Step 4.3 — Deploy to Cloud Run
📍 **Firebase Terminal** (deploy commands)

First, verify you're authenticated and pointing at the right project (initially set up in Step 0.8 — re-verify here in case your workspace was rebuilt):

```bash
gcloud auth list
# Expected: your Google account should be listed with a * next to it
# If not, run: gcloud auth login

gcloud config set project resume-api-portfolio
```

Then deploy:

```bash
gcloud services enable run.googleapis.com

gcloud run deploy resume-api \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --memory 256Mi \
  --max-instances 1 \
  --set-env-vars "ENVIRONMENT=production"
```

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Commands used:

| Command | Flag(s) | What It Does |
|---------|---------|-------------|
| `gcloud services enable` | | Turns on a GCP API for your project |
| `gcloud run deploy` | | Builds and deploys your app to Cloud Run. Key flags: |
| | `--source .` | Build from current directory (no local Docker needed) |
| | `--region` | Which data center to deploy in |
| | `--allow-unauthenticated` | Anyone can access the API (no login required) |
| | `--port 8080` | Which port the container listens on |
| | `--memory 256Mi` | RAM allocated to each instance |
| | `--max-instances 1` | Only one copy runs at a time (free tier safe) |

</em></sub>


**The output will include a URL like: `https://resume-api-xxxxx-uc.a.run.app`**

**Screenshot the deploy output.**

### Step 4.4 — Verify Live Deployment
📍 **Firebase Terminal** (curl commands) + 📍 **Your Browser** (visit the Cloud Run URL)

```bash
export API_URL="https://resume-api-xxxxx-uc.a.run.app"

curl $API_URL/ | python3 -m json.tool
curl $API_URL/resume | python3 -m json.tool
curl "$API_URL/resume/experience?company=deloitte" | python3 -m json.tool
curl "$API_URL/resume/skills?keyword=sql" | python3 -m json.tool
curl "$API_URL/analytics/top-domains?n=5" | python3 -m json.tool
```

Each curl should return JSON (not an HTML error page). If you see `{"detail":"Not Found"}`, double-check the URL — Cloud Run URLs are case-sensitive.

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Commands used:

| Command | What It Does |
|---------|-------------|
| `export` | Creates an environment variable that persists for the session. `$API_URL` can now be used in any command |

</em></sub>


**Screenshot these live responses with the Cloud Run URL visible.**

### Step 4.5 — Verify Free Tier Usage
📍 **GCP Console → Billing**

1. Go to: `https://console.cloud.google.com/run`
2. Click on your `resume-api` service
3. Check the **"Metrics"** tab — you should see a small spike in request count from your curl tests
4. Click **"Revisions"** — it should show one active revision with `256Mi` memory and `1` max instances
5. Free tier: 2 million requests/month — your test curls used approximately 5

**Screenshot the Cloud Run dashboard** showing the service is running with the settings you specified.

### Step 4.6 — Git Commit
📍 **Firebase Terminal**

```bash
git add .
git commit -m "Add Dockerfile, requirements.txt, and deployment config"
```

---

## PHASE 5: GITHUB + README (2-3 hours — MOST IMPORTANT PHASE)

> 📍 **Firebase Editor for writing, Firebase Terminal for git commands, Your Browser for GitHub verification.**

> **The README is more important than the code.** A reader looks at the README before diving into source code. This is where you communicate systems thinking.

### Step 5.1 — Update the README
📍 **Firebase Editor** (write the README in the code editor)

Replace the placeholder `README.md` with your actual documentation. Structure it like this:

```
# Resume API — Technical Portfolio

## Overview
Brief description: REST API with dual-database architecture 
(SQLite operational + BigQuery analytical), deployed on Cloud Run.
Built entirely in Firebase Studio using AI-assisted development (Gemini).

## Architecture
- ASCII diagram of the system:
  [Client] → [Cloud Run] → [FastAPI] → [SQLite: 10K rows]
                                     → [BigQuery: 500K rows]
- Data pipeline:
  [generate_data.py] → [SQLite: api_queries 10K] + [CSV: 500K rows]
                                                        ↓
                                               [bq load via CLI]
                                                        ↓
                                              [BigQuery: 500K rows]
  Data flows from generation script to two destinations: SQLite for 
  low-latency API serving, BigQuery for analytical queries. The CSV 
  is uploaded directly from the development container using `bq load` — 
  no local download/re-upload required.
- Technology choices with trade-offs:
  - FastAPI vs Flask: auto-generated docs, Pydantic validation, async support
  - SQLite + BigQuery: operational vs analytical workloads
  - Cloud Run vs App Engine: serverless scaling, pay-per-request, stateless containers
  - uv vs pip: faster installs, lockfile reproducibility, required for Nix environments
  - bq CLI vs Console upload: keeps data in Google's infrastructure, demonstrates 
    CLI proficiency, avoids downloading 50MB CSV to laptop and re-uploading
- How the dual-database pattern works in practice:
  SQLite serves low-latency API reads (< 50ms), BigQuery handles 
  analytical queries over 500K rows (full table scans, aggregations, window functions)

## API Design Decisions
9 endpoints, all read-only. For each, explain:
- REST resource model: nouns, not verbs (/resume/skills, not /getSkills)
- Query parameters: filtering (company, category, keyword), pagination (limit, offset)
- HTTP status codes: 200, 400 (bad params), 404 (not found), 500 (server error)
- Rate limiting: X-RateLimit headers (cosmetic in portfolio; production would use Redis)
- CORS: enabled for all origins (appropriate for public read-only API)
- Trade-off: no authentication added intentionally — adding OAuth to a public 
  read-only resume API would be over-engineering

## Data Model
Schema: api_queries table (mirrors digital advertising reporting patterns)
- recruiter_domain ≈ advertiser (who's looking)
- endpoint_hit ≈ campaign (what they're looking at)
- skill_searched ≈ keyword (what they searched for)
- response_time_ms ≈ latency (system health)
- http_status ≈ conversion tracking (success/failure)

10,000 rows in SQLite for API serving, 500,000 rows in CSV for BigQuery analysis.
Data generated using Python's Faker library with weighted distributions 
(85% HTTP 200, 5% 304, 4% 400, 4% 404, 2% 500).

### Data Ingestion Pipeline
The same `generate_data.py` script produces both datasets simultaneously:
- SQLite (10K rows): written directly to `data/analytics.db` for API serving
- CSV (500K rows): written to `data/recruiter_queries.csv` for BigQuery upload

BigQuery ingestion uses the `bq load` CLI directly from the development 
container — the CSV never leaves Google's infrastructure. Schema is auto-detected 
on upload, with post-upload verification of column types (particularly ensuring 
`timestamp` is parsed as TIMESTAMP, not STRING).

Key design decision: the two datasets share the same schema but differ in volume. 
This mirrors real ad tech systems where operational databases hold recent/hot data 
and analytical warehouses hold complete historical data.

## SQL Query Progression
All queries run against `resume_analytics.recruiter_queries` (500K rows) in 
BigQuery, uploaded via `bq load` CLI from the development container. Each tier 
demonstrates progressively more sophisticated query optimization.

### Tier 1: Naive (Full Table Scan)
- Query + screenshot + bytes processed
- Why this is problematic at scale

### Tier 2: Optimized (CTEs + Window Functions)
- Query + screenshot + performance improvement
- Demonstrates: WITH clauses, RANK(), date partitioning

### Tier 3: Partitioned & Clustered
- Query + screenshot + dramatic performance improvement
- When to use partitioning vs clustering

### When to Leave BigQuery
- Streaming needs → Dataflow/Apache Beam
- Sub-10ms reads → Bigtable
- Global transactional → Spanner
- (Discussion only — shows architectural awareness beyond the tool)
- This project uses BigQuery because the workload is analytical (aggregations, 
  window functions, full table scans) and batch-oriented. The 500K-row dataset 
  fits comfortably in BigQuery's free tier (1TB/month queries, 10GB storage).

## SQLite vs BigQuery: When to Use Each
| Factor | SQLite | BigQuery |
|--------|--------|----------|
| Query volume | < 100K rows | Millions+ rows |
| Latency | < 50ms | 1-5 seconds |
| Cost | Free | Pay per bytes scanned (1TB/month free) |
| Concurrency | Single writer | Thousands of concurrent readers |
| Best for | Serving API responses | Analytics, reporting, ad-hoc exploration |
| Data ingestion | Written directly by Python script | CSV upload via `bq load` CLI |
| Deployment | Embedded in Docker image (baked at build time) | Persistent cloud service (survives redeploys) |
| Schema changes | Regenerate data + rebuild Docker image | Reload table or use DDL |
| Portability | File-based, zero config | Requires GCP project + BigQuery API enabled |

Key insight: SQLite data is a **snapshot** frozen into the Docker image. 
BigQuery data is **persistent** and survives container restarts and redeploys. 
This mirrors production patterns where operational stores are ephemeral/cached 
and analytical warehouses are the durable source of truth.

## Security Considerations
- Input validation: handled by FastAPI/Pydantic automatically
- SQL injection: parameterized queries (cursor.execute with ? placeholders)
- No authentication: intentional — public resume data, no secrets
- Rate limiting: headers present, not enforced (production: Redis + middleware)
- BigQuery access: controlled by GCP IAM. Only the project Owner can query 
  the dataset. No public access configured (appropriate for portfolio data).
- Data pipeline security: CSV uploaded via authenticated `bq` CLI session. 
  Data never leaves Google's infrastructure (container → BigQuery, no local download).
- Production additions: API key auth, enforced rate limits, HTTPS termination at LB, 
  BigQuery dataset-level ACLs for team access control

## Development Environment: Firebase Studio

### Why Firebase Studio
- Zero local setup: Python, uv, gcloud, Docker, git all pre-installed
- Native Google Cloud integration: authentication, BigQuery, Cloud Run deploy
- Gemini AI assistant: code generation, debugging, refactoring inside the IDE
- Web preview panel: live-reload testing without leaving the browser
- Nix-based reproducibility: environment defined in code (dev.nix)

### Challenges & Solutions

**Nix Package Interception**
The biggest friction point. Firebase Studio uses Nix, which intercepts bare commands 
like `uvicorn` or `python3` and tries to install system packages instead of using 
the project's virtual environment. 
Solution: Every Python command uses `uv run --` prefix.
Example: `uv run -- python -m uvicorn api.main:app` instead of `uvicorn api.main:app`

**Ephemeral Workspaces**
Firebase Studio workspaces can reset without warning, wiping installed packages 
and uncommitted changes. 
Solution: Git commit every 30 minutes. `uv sync` restores all dependencies 
from the lockfile in seconds after a reset.

**AI Context Loss Between Prompts**
Gemini (Firebase Studio's AI) has no memory between prompts. It generated conflicting 
table names across steps (analytics endpoints queried `queries` table instead of 
`api_queries`) because it couldn't see what previous prompts had created. It also 
added SQLAlchemy as an import when the project only uses sqlite3, because it didn't 
know the existing codebase's patterns.
Solution: Created a GEMINI_CONTEXT.md reference file with project structure, 
table names, and command patterns. Paste current file state before every prompt.
Best practice: Ask Gemini for a plan before code ("list what you'll do, don't write 
code yet"), review the plan, then approve. One task per prompt, verify before moving on.

**dev.nix Preview Configuration**
The web preview requires the server startup command in Nix syntax. Bare `uvicorn` 
in the preview command fails because Nix intercepts it. The AI assistant (Gemini) 
repeatedly overwrites this file with non-working commands because it has no 
persistent memory of the Nix constraint.
Solution: Git-protect dev.nix after initial configuration (`git commit`), 
restore with `git checkout .idx/dev.nix` when overwritten, and mark the file 
as off-limits in GEMINI_CONTEXT.md. The correct command format uses 
`["sh" "-c" "uv run -- python -m uvicorn ..."]`.

**Pydantic Validation on Filtered Responses**
Filtering a single skill category returned only that category, but the Pydantic 
response model required all four categories — causing a 500 error.
Solution: Return filtered results as plain dict, bypassing strict model validation.

**Database Path Mismatches**
Data generation script and API database config pointed to different files 
(data/analytics.db vs analytics.db in project root) causing empty analytics responses.
Solution: Standardized all paths to data/analytics.db, added verification 
commands to catch mismatches early.

**Gemini Overwriting Correct Configurations**
Gemini sometimes replaces working code with its own assumptions. Examples: 
overwriting the dev.nix `uv run` command with bare `uvicorn`, adding SQLAlchemy 
imports to a project that uses raw sqlite3, using `pip install` when the project 
uses uv. Because Gemini has no persistent memory, it defaults to "standard" patterns 
that don't account for environment-specific constraints. This happened even after 
providing a GEMINI_CONTEXT.md file — Gemini must be reminded to reference it 
in each prompt, and may still deviate for tasks it considers "fixes."
Solution: Git-protect critical config files (`git commit` immediately after 
getting them right, `git checkout` to restore when overwritten). Mark files as 
off-limits in GEMINI_CONTEXT.md. For dev.nix specifically, tell Gemini to 
"suggest changes for me to apply manually" rather than editing directly.

**Nix Variable Syntax in dev.nix**
Firebase Studio's preview system injects a `$PORT` environment variable that the 
server must use. Getting this right required understanding how Nix passes values 
to shell commands:
- `${PORT:-8000}` → Nix interprets `${}` as Nix interpolation → parse errors
- `\${PORT:-8000}` → Backslash escaping → still caused Nix parse errors
- `$PORT` → No curly braces → Nix passes it through to shell untouched → **works**

The lesson: inside `"sh" "-c" "..."` strings in Nix, use `$VAR` (no braces) for 
shell variables. Nix only intercepts the `${...}` pattern.

**uv sync Removing Manually Added Packages**
Running `uv sync` strictly follows pyproject.toml — if a package was installed 
manually but not listed in pyproject.toml, uv sync removes it. This caused 
SQLAlchemy to disappear mid-development.
Solution: Always use `uv add package-name` (which writes to pyproject.toml) 
instead of manual installation.

### Cloud Run: Serverless Lifecycle
Understanding Cloud Run's behavior is essential for this architecture:
- **No persistent server.** Containers start on demand when an HTTP request arrives
  and shut down after a period of inactivity. There is nothing to "keep running."
- **Stateless containers.** SQLite data is baked into the Docker image at build time.
  If you change resume content or regenerate analytics data, you must rebuild the 
  image and redeploy — the running container does not update in place.
- **Cold starts.** The first request after idle may take 1-3 seconds while the 
  container spins up. Subsequent requests are fast (< 100ms). This is acceptable 
  for a portfolio project.
- **No startup scripts needed.** Cloud Run handles process management, health checks,
  and scaling. The Dockerfile's CMD is the only startup configuration required.

### Key Takeaway
Firebase Studio is a powerful choice for Google Cloud portfolio projects — zero 
setup, native GCP integration, and AI assistance in the IDE. But it requires 
understanding three abstraction layers:

1. **Nix** sits between you and Python. The `uv run --` prefix is non-negotiable. 
   Shell variables in Nix config files use `$VAR` (no braces), not `${VAR}`.
2. **Gemini** is stateless. A context file with explicit role boundaries + 
   one-task-at-a-time prompting + verification after every edit eliminates 
   most AI-generated errors. Critical config files must be git-protected.
3. **Cloud Run** is ephemeral. Your database is frozen at Docker build time. 
   Changes require rebuild → redeploy. There is no persistent server to manage.

The combination of frequent git commits, GEMINI_CONTEXT.md as an operating 
agreement, git-protection for critical configs, and `grep`-based verification 
after every Gemini edit made the workflow reliable despite the ephemeral 
environment and stateless AI assistant.

### AI-Assisted Development: What Worked
- **Context file as operating agreement (GEMINI_CONTEXT.md):** Not just a reference 
  doc — an explicit contract defining roles, responsibilities, and boundaries. 
  Includes project purpose, what Gemini should and shouldn't do, which files are 
  off-limits, and the command patterns required by the environment. Referenced at 
  the start of every session.
- **Two-step prompting:** "Tell me your plan, don't write code yet" → review → 
  "Approved, now implement." Caught wrong assumptions before they became code.
- **One task per prompt:** Prevented cascading errors where one wrong assumption 
  in a multi-step prompt broke everything downstream.
- **Verification after every edit:** `grep` commands to confirm Gemini didn't 
  change things it shouldn't have (dev.nix, database paths, import statements).
- **Error logs as prompts:** Pasting exact error messages to Gemini ("NameError on 
  line 42, variable db_path undefined") produced better fixes than "it's broken."
- **Git as a safety net:** Committing working configurations immediately so 
  `git checkout` can undo AI-generated regressions in seconds.
- **External coach for debugging:** Using a separate AI assistant (Claude) for 
  architecture decisions, debugging strategy, and guide creation — while Gemini 
  handled code execution in the IDE. Separation of concerns prevented either tool 
  from overreaching.

### What Didn't Work (Lessons Learned)
- **Large multi-step prompts:** Asking Gemini to build multiple components in one 
  prompt caused cascading failures. If step 1 used the wrong table name, steps 2-5 
  all inherited the error. Smaller prompts with verification between each caught 
  errors early.
- **Assuming AI remembers context:** Even with a context file, Gemini doesn't 
  remember it between prompts. Every session requires re-referencing 
  GEMINI_CONTEXT.md explicitly. Phrases like "as we discussed" or "following our 
  earlier pattern" don't work — the AI has no "earlier."
- **Trusting AI fixes to config files:** Gemini's instinct when something breaks 
  is to rewrite configuration files. It overwrote dev.nix at least three times with 
  non-working commands. The fix wasn't better prompting — it was making the file 
  off-limits and git-protecting it.
- **Abstract verification ("does X work?"):** Early prompts asked Gemini to verify 
  things like "does CORS middleware exist?" without executable commands. This led 
  to false confidence. Switching to `grep` commands with expected output made 
  verification reliable and objective.
- **Letting the AI "investigate" freely:** Asking Gemini to "find the problem" 
  sometimes led to destructive exploration — reading and rewriting files 
  unnecessarily. More effective approach: provide the exact error, the exact file, 
  and ask for a targeted fix.

### Reflections on AI-Assisted Development
Building this project with an AI coding assistant was faster than from scratch 
but required a different kind of discipline. The productivity gain isn't in writing 
code — it's in generating boilerplate (data schemas, endpoint scaffolding, SQL 
templates) while you focus on architecture and design decisions.

The biggest misconception going in was that AI assistance means less work. In 
practice, it means different work: less typing, more reviewing. Every AI-generated 
file needs verification. Every "fix" needs to be checked against the existing 
codebase. The total effort is roughly: 30% prompting, 20% coding, 50% verifying 
and debugging.

The most valuable pattern was treating the AI as a junior developer with amnesia — 
capable but needing explicit instructions, a clear scope for each task, and 
immediate review of every output. The GEMINI_CONTEXT.md file evolved from a simple 
reference document into an operating agreement that defined not just technical 
constraints, but roles, responsibilities, and boundaries.

For anyone attempting a similar project: start with the context file before writing 
any code. Define your environment constraints, your file structure, and your rules 
up front. It's much harder to retrofit boundaries after the AI has already started 
making assumptions.

## Digital Marketing Ecosystem Connection
How this project's patterns map to real ad tech workflows:
- API query tracking ≈ ad impression/click logging
- Recruiter domain analytics ≈ advertiser performance reporting
- Endpoint hit frequency ≈ campaign delivery metrics
- Response time monitoring ≈ ad latency SLAs
- SQLite → BigQuery pipeline ≈ real-time serving → offline analytics pattern
- `bq load` CSV ingestion ≈ batch ETL from ad servers to data warehouse
- Schema autodetect + validation ≈ data quality checks on ingestion pipelines
- 10K (operational) vs 500K (analytical) split ≈ hot/warm data tiering
- Tier 1→3 SQL progression ≈ query optimization for cost control on 
  pay-per-scan warehouses (directly relevant to Google Ads reporting infrastructure)

## Running Locally
Prerequisites: Python 3.11+, uv, git

```bash
git clone <repo>
cd resume-api
uv sync
uv run -- python data/generate_data.py
uv run -- python -m uvicorn api.main:app --host 0.0.0.0 --port 8000
```

Open http://localhost:8000/docs for interactive API documentation.

Note: If developing in Firebase Studio, read GEMINI_CONTEXT.md for 
environment-specific patterns before making changes.

### BigQuery Setup (optional — for analytical queries)
Requires: Google Cloud account, `gcloud` CLI, `bq` CLI

```bash
gcloud auth login
gcloud config set project resume-api-portfolio
bq mk resume_analytics
bq load --source_format=CSV --autodetect --skip_leading_rows=1 \
  resume_analytics.recruiter_queries data/recruiter_queries.csv
bq query --use_legacy_sql=false \
  'SELECT COUNT(*) FROM resume_analytics.recruiter_queries'
# Expected: 500000
```

The API endpoints work without BigQuery — it's only needed for the 
analytical SQL queries in the `sql/` directory.

## Live Demo
Link to deployed Cloud Run URL

## Technologies Used
| Technology | Role | Why This Choice |
|-----------|------|----------------|
| FastAPI | API framework | Auto-generated docs, Pydantic validation, async |
| Python 3.11 | Runtime | Stable, broad library support |
| SQLite | Operational database | Zero-config, < 50ms reads, embedded |
| BigQuery | Analytical database | Columnar storage, handles 500K+ rows |
| Docker | Containerization | Reproducible builds, Cloud Run requirement |
| Cloud Run | Hosting | Serverless, scales to zero, pay-per-request |
| Firebase Studio | Development IDE | Zero setup, GCP integration, AI assistant |
| uv | Package management | Fast installs, lockfile, Nix-compatible |
| Pydantic v2 | Data validation | Type safety, automatic request/response validation |
| Faker | Test data generation | Realistic timestamps, domains, user agents |
```

### Step 5.2 — Create .gitignore
📍 **Firebase Editor** or 📍 **Firebase Terminal**

```bash
cat > .gitignore << 'EOF'
__pycache__/
*.pyc
*.db
*.csv
.venv/
gcp-key.json
.env
.idx/
TRACKER.md
screenshots/
EOF
```

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Commands used:

| Syntax | What It Does |
|--------|-------------|
| `cat >` | Writes text into a file (overwrites if file exists) |
| `<< 'EOF'` | Heredoc — lets you type multiple lines. Everything until `EOF` goes into the file |

</em></sub>


> **Why exclude .db and .csv?** The data is generated by the script — anyone who clones the repo can run `uv run -- python data/generate_data.py` to recreate it. No need to store 500K rows in Git.

### Step 5.3 — Push to GitHub
📍 **Firebase Terminal** (git commands) then 📍 **Your Browser** (verify on github.com)

1. Go to `https://github.com` → Create new repository → Name: `resume-api`
2. Set to **Public**
3. DO NOT initialize with README (you already have one)
4. Follow GitHub's instructions to push:

```bash
git add .
git commit -m "Complete README with design decisions and screenshots"
git remote add origin https://github.com/YOUR-USERNAME/resume-api.git
git branch -M main
git push -u origin main
```

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Commands used:

| Command | Flag(s) | What It Does |
|---------|---------|-------------|
| `git remote add` | `origin` | Connects your local repo to a remote GitHub URL. `origin` = conventional name for the primary remote |
| `git branch` | `-M` | Renames the current branch. `-M main` = rename to `main` (GitHub's default branch name) |
| `git push` | `-u origin main` | Uploads commits to GitHub. `-u` = set upstream (so future `git push` doesn't need extra args) |

</em></sub>


5. Visit your repo URL and verify:
   - The README renders with proper formatting (headers, code blocks, tables)
   - The architecture diagram displays correctly (the ASCII art box)
   - SQL code blocks have syntax highlighting
   - Screenshots appear inline (if you've added them)
   - The `api/`, `data/`, and `sql/` folders are visible in the file tree
   - `.db` and `.csv` files are NOT in the repo (your `.gitignore` should exclude them)

---

## PHASE 6: SCREENSHOT CHECKLIST

> 📍 **Screenshots come from multiple environments — see the "Where" column below.**

Take and organize screenshots for the README. These are your evidence:

| # | Screenshot | Where to Take It | What It Demonstrates |
|---|-----------|------------------|---------------------|
| 1 | Terminal: `python3 --version`, `uv --version`, `uname -a` | 📍 Firebase Terminal | Environment familiarity |
| 2 | Terminal: `mkdir -p`, project structure (`find`) | 📍 Firebase Terminal | File system navigation |
| 3 | Terminal: `ps aux \| grep uvicorn` | 📍 Firebase Terminal | Process management |
| 4 | Terminal: `ss -tlnp \| grep 8000` | 📍 Firebase Terminal | Network diagnostics |
| 5 | Terminal: `docker build` output (if available) | 📍 Firebase Terminal | Container knowledge |
| 6 | Terminal: `gcloud run deploy` output | 📍 Firebase Terminal | Cloud deployment |
| 7 | Browser: FastAPI Swagger /docs page | 📍 Firebase Preview (Web tab) | API documentation |
| 8 | Terminal: curl responses with JSON | 📍 Firebase Terminal | API design validation |
| 9 | BigQuery: Tier 1 query + bytes scanned | 📍 BigQuery Console | Naive SQL baseline |
| 10 | BigQuery: Tier 2 query + bytes scanned | 📍 BigQuery Console | Optimized SQL skills |
| 11 | BigQuery: Tier 3 query + bytes scanned | 📍 BigQuery Console | Scale architecture |
| 12 | BigQuery: Partitioned table details | 📍 BigQuery Console | BigQuery-specific knowledge |
| 13 | Cloud Run: Deployed service dashboard | 📍 GCP Console → Cloud Run | Production deployment |
| 14 | Python: `compare_engines.py` output (if built) | 📍 Firebase Terminal | SQLite vs BigQuery comparison |

### Final Polish

```bash
git add screenshots/
git commit -m "Add evidence screenshots"
git push
```

Visit the GitHub repo one more time — README looks clean, links work, screenshots display.

---

## CLEANUP: After You're Done

To ensure zero ongoing charges:

```bash
gcloud run services delete resume-api --region us-central1

bq rm -t resume_analytics.recruiter_queries
bq rm -t resume_analytics.recruiter_queries_optimized
bq rm -r -d resume_analytics

gcloud run services list
```

That last command should return an empty list — confirming nothing is still running and incurring charges.

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Commands used:

| Command | Flag(s) | What It Does |
|---------|---------|-------------|
| `gcloud run services delete` | `--region` | Deletes a deployed Cloud Run service |
| `bq rm` | `-t` | Removes a BigQuery table. `-t` = table |
| `bq rm` | `-r -d` | Removes a BigQuery dataset. `-r` = recursive (delete all tables inside), `-d` = dataset |
| `gcloud run services list` | | Lists all deployed Cloud Run services — verify nothing is still running |

</em></sub>


Or the nuclear option — disable billing entirely:
1. Go to: `https://console.cloud.google.com/billing`
2. Click **"Account Management"**
3. Click **"Disable Billing"**

---

## QUICK REFERENCE: Free Tier Limits

| Service | Free Tier | Your Usage | Safe? |
|---------|-----------|------------|-------|
| Cloud Run | 2M requests/month, 360K vCPU-sec | ~100 requests | ✅ Way under |
| BigQuery Queries | 1 TB/month | ~2 GB | ✅ Way under |
| BigQuery Storage | 10 GB | ~500 MB | ✅ Way under |
| Artifact Registry | 500 MB | ~200 MB | ✅ Way under |
| Cloud Build | 120 build-min/day | ~5 minutes | ✅ Way under |
| Firebase Studio | Free (preview) | Unlimited | ✅ Free |

---

## TROUBLESHOOTING

> 📍 **All troubleshooting commands run in Firebase Terminal** unless noted otherwise.

**"uv: command not found"**
→ You may have selected the wrong template. Create a new workspace using the **Python** (UV Starter) template.

**"pip3 is not installed"**
→ Don't install pip3. Use `uv add` for packages and `uv pip compile` to generate requirements.txt.

**"gcloud command not found"**
→ Install the Google Cloud SDK:
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud init
```

**"docker: command not found"**
→ Skip local Docker testing. Use `gcloud run deploy --source .` which builds the container in the cloud.

**"Docker build failed"**
→ Run `uv pip compile pyproject.toml -o requirements.txt` first, then check that requirements.txt has all packages listed. Check Dockerfile paths.

**"Cloud Run deploy failed"**
→ Check that all required APIs are enabled (Phase 0, Step 0.6). Verify your project: `gcloud config get-value project`

**"BigQuery upload failed"**
→ Make sure the dataset exists first. Check CSV encoding: `head -5 data/recruiter_queries.csv`

**Analytics endpoints return empty results or errors**
→ Check that `api/database.py` points to the right file. Run:
```bash
grep DATABASE_FILE api/database.py
ls -la data/analytics.db
```
The path in `database.py` must match where the file actually exists. If `database.py` says `analytics.db` but the file is at `data/analytics.db`, update the path. Also check for stale copies in the project root:
```bash
ls -la analytics.db
# If this exists, delete it: rm analytics.db
```

**"BigQuery query returns 0 rows"**
→ Check your WHERE clause dates against the actual data range. Run: `SELECT MIN(timestamp), MAX(timestamp) FROM resume_analytics.recruiter_queries`

**"Firebase Studio workspace reset"**
→ This is why you commit to Git every 30 minutes. Clone your repo and reinstall dependencies:
```bash
git clone https://github.com/YOUR-USERNAME/resume-api.git
cd resume-api
uv sync
```

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Commands used:

| Command | What It Does |
|---------|-------------|
| `git clone` | Downloads a remote repository to your local machine |
| `cd` | Change Directory — navigate into a folder |
| `uv sync` | Reads `pyproject.toml` and installs all listed dependencies |

</em></sub>


**"Gemini generated code that doesn't work"**
→ Tell Gemini specifically what's wrong: "That generated a NameError on line 42. The variable `db_path` isn't defined. Please fix." Specific error messages get better results than "it's broken."

**"uvicorn: ModuleNotFoundError: No module named 'fastapi'" (or similar)**
→ Firebase Studio's Nix system intercepted the `uvicorn` command and used the system Python (3.12) instead of your virtual environment. Always run uvicorn through uv:
```bash
cd ~/resume-api && uv run -- python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```
Also make sure you're in your project directory (`~/resume-api`), not the root (`/`).

**"Address already in use" (or "[Errno 98]")**
→ A previous server is still running on that port. Kill it first:
```bash
kill $(pgrep -f uvicorn)
sleep 1
```
Then restart. If that doesn't work, find what's using the port and kill it directly:
```bash
ss -tlnp | grep 8000
# Look for the PID number, then:
kill <PID>
```

**Web preview panel shows "Starting server" but never loads**
→ The server is running but the preview can't connect. First verify the API works:
```bash
curl -s http://localhost:8000/ | python3 -m json.tool
```
If curl returns JSON, your API is fine — the preview is a port mismatch issue. You can proceed using curl and Swagger docs (`http://localhost:8000/docs`) for all testing. The preview panel is a nice-to-have, not a requirement.
If curl also fails, check if the server is actually running: `ps aux | grep uvicorn`

**"uvicorn is not installed" (Nix offers python312Packages.uvicorn)**
→ This means you typed bare `uvicorn` in the terminal. Nix doesn't know about your venv packages. Always use:
```bash
cd ~/resume-api && uv run -- python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

**Gemini overwrote dev.nix with bare `uvicorn` or `python` command**
→ This will keep happening — Gemini has no persistent memory of the Nix constraint. Restore instantly:
```bash
git checkout .idx/dev.nix
```
Then tell Gemini: *"dev.nix is off-limits. Do not modify it. This is documented in GEMINI_CONTEXT.md."*
To prevent this, GEMINI_CONTEXT.md marks dev.nix as a locked file. Always reference the context file at the start of a Gemini session.

---

## TIMELINE SUMMARY

| Phase | Time | Priority | Can Be Cut? |
|-------|------|----------|-------------|
| Phase 0: Account setup + billing safeguards | 30 min | Required | No |
| Phase 1: Firebase Studio setup | 15 min | Required | No |
| Phase 2: Build API (Gemini does heavy lifting) | 2-3 hrs | Required | No |
| Phase 3: BigQuery setup + SQL demos | 2-3 hrs | Required | No |
| Phase 4: Deploy to Cloud Run | 1-2 hrs | Recommended | Yes — demo locally instead |
| Phase 5: GitHub + README | 2-3 hrs | **Most Important** | **Never** |
| Phase 6: Screenshots | 30 min | Required | No |
| **Total** | **8-12 hrs** | | |

**If running out of time, cut in this order:**
1. Cut `compare_engines.py` (SQLite vs BQ comparison) → mention in README instead
2. Cut Tier 3 SQL → mention in README as "next step"
3. Cut Cloud Run deployment → demo locally with screenshots
4. **NEVER cut the README** — the design thinking is more valuable than the code
5. **NEVER cut Tier 1 + Tier 2 SQL** — this is the BigQuery centerpiece
6. **NEVER cut the API endpoints** — this is the API design centerpiece