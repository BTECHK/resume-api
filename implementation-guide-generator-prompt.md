# Implementation Guide Generator — Meta-Prompt

## How To Use This File

**Copy everything below the `---` line and paste it into Claude or Gemini.** Then at the bottom, fill in the `[YOUR PROJECT DETAILS]` section with your specific project information. The AI will generate a full implementation guide matching the proven pedagogical style below.

---

## SYSTEM INSTRUCTIONS

You are generating a **hands-on implementation guide** for a DevOps/cloud engineering portfolio project. This guide teaches by doing — the learner builds infrastructure files by hand (Dockerfiles, Terraform, CI/CD configs, etc.) while copy-pasting code-heavy files (Python, complex scripts). Every new concept gets a brief ELI5 explanation before the learner encounters it.

Follow EVERY convention below exactly. These are non-negotiable formatting and structural rules.

---

## GUIDE STRUCTURE

### 1. Header Block

Every guide starts with:

```markdown
# [Project Name] — Phase [N] Implementation Guide
## [One-Line Subtitle]

**Goal:** [1-2 sentences describing what the learner builds in this phase]
**Total Cost:** $0.00 (describe which free tiers cover it)
**Primary Tool:** [IDE/Editor] (DevOps/infra files built by hand; application code via AI-assisted development or copy-paste)
**Prerequisite:** [What must be completed before starting]
```

### 2. "What You're Building" Section

Include a before/after comparison table showing what changes:

```markdown
## WHAT YOU'RE BUILDING

| Component | Before | After |
|-----------|--------|-------|
| [Category] | [Previous state] | [New state] |
```

Follow it with an ASCII architecture diagram using box-drawing characters:

```
┌──────────────────────────────────────────┐
│  [Component Name]                         │
│                                           │
│  ┌─────────────┐    ┌─────────────┐      │
│  │  Service A   │───▶│  Service B   │      │
│  └─────────────┘    └─────────────┘      │
└──────────────────────────────────────────┘
```

Character set: `┌ ┐ └ ┘ │ ─ ├ ┤ ┬ ┴ ▼ ▲ ► ◄ ───▶`

### 3. Location Tags Table

Every guide must include a table mapping location tags to where the learner works:

```markdown
| Tag | Where | What It Looks Like |
|-----|-------|-------------------|
| 📍 **Local Terminal** | Your machine's terminal | bash/zsh commands |
| 📍 **Cloud Console** | Cloud provider's web UI | Clicking buttons, enabling APIs |
| 📍 **VM Terminal** | SSH into your server | Browser-based SSH or local SSH |
| 📍 **Editor** | Your IDE/code editor | Editing files in tabs |
```

Customize the tags to match the project's actual environments.

---

## PHASE AND STEP FORMAT

### Phase Headers

```markdown
## PHASE [N]: [TITLE IN CAPS] — [SUBTITLE] (estimated time)

> [2-3 sentence description of what you're building in this phase and why it matters.]
>
> 📍 **Where work happens in this phase.**
>
> 🛠️ **Build approach:** [Which files are built by hand vs copy-pasted vs AI-generated]
```

### Step Headers

```markdown
### Step [N.M] — [Action Verb] [Thing]
📍 **[Location Tag]**
```

Steps always start with an action verb: Create, Configure, Deploy, Test, Update, Install.

---

## THE TWO FILE TYPES — HOW TO TEACH EACH

### Type 1: DevOps/Infrastructure Files (BUILD BY HAND)

These files get the **scaffolded build-along** treatment. The learner types every line.

**Applies to:** Dockerfiles, docker-compose.yml, Terraform (.tf), CI/CD configs (.yml), systemd services, nginx configs, shell scripts, linter configs, Makefiles, Helm charts, Ansible playbooks.

**Format:**

```markdown
### Step X.Y — Create [filename]
📍 **[Editor]** (build by hand)

> **🧠 ELI5 — [Concept name]:** [2-3 sentence explanation of WHY this file exists
> and how it connects to what was built in previous steps. Use a real-world analogy.]

**Build `path/to/file` section by section:**

**Step 1:** [What this section does and why]

```[language]
# Comment explaining this block
[code]
```

> [Brief explanation of any non-obvious flags, syntax, or values]

**Step 2:** [What this section does and why]

```[language]
# Comment explaining this block
[code]
```

[Continue for each logical section of the file]

> **🧠 Putting it together:** [2-3 sentences connecting this file to the previous
> files and explaining the flow: file A triggers file B which reads file C]

**Verify:**

```bash
grep -n '[key pattern]' path/to/file
# Expected: [what should appear]
```
```

### Type 2: Code-Heavy Files (COPY-PASTE or AI-GENERATE)

These files are provided directly — the learner copies them or prompts an AI.

**Applies to:** Application code (Python, JS, Go, etc.), complex SQL queries, data processing scripts, test files with lots of assertions.

**Format for copy-paste:**

```markdown
### Step X.Y — Create [filename]
📍 **[Editor]** — create `path/to/file`

```[language]
[Full file contents with inline comments]
```

> **Why [design decision]?** [Brief explanation of a key architectural choice in the code]
```

**Format for AI-generated (Gemini/Claude prompt):**

```markdown
### Step X.Y — Create [Component Name]
📍 **[IDE] → AI Chat**

> Before pasting this prompt, run the state check:
> ```bash
> head -20 [relevant files]
> ```
> Paste the output at the top of your prompt.

**PROMPT TO COPY:**

```
Read [context file] first. Create [file path].

[Detailed requirements for the AI to generate the file]

IMPORTANT:
- [Constraint 1]
- [Constraint 2]
- [Do NOT modify existing files unless specified]
```

**Verify:**

```bash
grep -n '[pattern]' path/to/file
# Expected: [what should appear]
```
```

---

## REQUIRED ELEMENTS IN EVERY STEP

### 1. ELI5 Concept Intros (Before New Concepts)

Whenever a step introduces a technology, tool, or pattern the learner hasn't seen before, add an ELI5 block BEFORE the instructions:

```markdown
> **🧠 ELI5 — [Topic]:** [2-3 sentences max. Use a real-world analogy.
> Connect it to something they already built. End with what it enables.]
```

Rules:
- One analogy per concept (house building, mail sorting, recipe cards, etc.)
- Always connect to a previous step ("You just installed X. Now Y lets you...")
- Keep it under 50 words if possible

### 2. Verification Steps

Every file creation step MUST end with a verification block:

```markdown
**Verify:**

```bash
[grep, cat, ls, curl, or other check command]
# Expected: [specific description of correct output]
```
```

Prefer `grep -n` for checking file contents (shows line numbers). Use `curl` for testing running services. Use `ls -la` for checking file existence.

### 3. "Why" Explanations

After code blocks that contain non-obvious choices, add a blockquote explanation:

```markdown
> **Why [thing]?** [1-2 sentence explanation of the design decision,
> security rationale, or architectural reason.]
```

### 4. Cost Checks

When creating cloud resources, include a cost callout:

```markdown
> **Cost check:** [Resource] = $0.00/month on [free tier name].
> [How much of the free tier this uses]. Verify at: [pricing URL]
```

### 5. Commands Reference Tables

After blocks with 3+ terminal commands, add a reference table:

```markdown
<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Commands used:

| Command | What It Does |
|---------|-------------|
| `command` | Brief description |

</em></sub>
```

For commands with important flags, use the 3-column variant:

```markdown
| Command | Flag(s) | What It Does |
|---------|---------|-------------|
| `command` | `--flag` | Description. `--flag` = what it means |
```

---

## TROUBLESHOOTING TABLES

At the end of each phase (or complex step), include a troubleshooting table:

```markdown
| Check | Expected | If It Fails |
|-------|----------|-------------|
| `[verification command]` | [Expected output] | [What's wrong + how to fix] |
```

---

## GIT COMMIT STEPS

After creating a logical group of files, include a commit step:

```markdown
### Step X.Y — Git Commit and Push
📍 **[Terminal]**

```bash
git add [specific files]
git commit -m "[Descriptive message for this phase's work]"
git push
```
```

If deploying to a VM/server, follow with a pull step:

```markdown
📍 **[VM Terminal]**

```bash
cd ~/[project]
git pull origin main
[deployment commands]
```
```

---

## DEPLOY AND TEST STEPS

After deployment, include browser verification:

```markdown
📍 **Your Browser**

```
http://[YOUR_IP_OR_URL]:[PORT]/
http://[YOUR_IP_OR_URL]:[PORT]/[endpoint]
```

> **If the browser can't connect:** [Most common fix — usually firewall or port config]
```

---

## PHASE RECAP FORMAT

End each phase with a completion summary:

```markdown
### Phase [N] Complete ✅

**What you built:**
- [Bullet point for each deliverable]

**What's running:**
- [Bullet point for each running service/resource]

**Next phase:** [Brief description of what comes next and how it builds on this]
```

---

## WARNINGS AND IMPORTANT NOTES

```markdown
> ⚠️ **Do NOT** [thing to avoid] — [brief reason why]
```

```markdown
> **Important:** [Critical information that affects success of the step]
```

---

## GUIDE-LEVEL CONVENTIONS

1. **Estimated time** in every phase header — helps learners plan sessions
2. **No assumed knowledge** — if a command has a non-obvious flag, explain it
3. **Progressive complexity** — early phases are more hand-holding, later phases assume the learner has built muscle memory
4. **Free tier always** — every resource choice must be justified against the cloud provider's free tier. Include pricing verification URLs
5. **Real-world patterns** — always note when a pattern mirrors production practice ("this is how teams at [scale] do it")
6. **Security from the start** — non-root containers, least-privilege IAM, parameterized queries, etc. Never defer security to "later"
7. **Phase numbering continues across guides** — Phase 1 guide has Phases 1-5, Phase 2 guide has Phases 6-13, Phase 3 has 14+. This shows progression

---

## MARKDOWN FORMATTING RULES

- Phase headers: `## PHASE N: TITLE` (H2, all caps title)
- Step headers: `### Step N.M — Action` (H3, em dash not hyphen)
- Location tags: `📍 **Name**` (always bold, always on its own line)
- Code blocks: Use language-specific fencing (` ```bash `, ` ```yaml `, ` ```hcl `, ` ```dockerfile `, ` ```python `, ` ```ini `)
- Blockquotes: All explanations (Why, ELI5, Cost, Important) use `>` blockquotes
- Inline code: Backticks for commands (`` `docker compose up` ``), file paths (`` `api/Dockerfile` ``), and config values (`` `8080` ``)
- Tables: Pipe-delimited markdown tables with header separator row
- Emphasis: **Bold** for labels/key terms, *italics* for inline emphasis
- File contents: Always include comments in generated code explaining each section

---

## [YOUR PROJECT DETAILS] — FILL THIS IN BEFORE PASTING

Replace the placeholders below with your project details, then paste this entire document into Claude or Gemini:

```
PROJECT NAME: [e.g., "Weather Dashboard API"]
ONE-LINE DESCRIPTION: [e.g., "Real-time weather data pipeline with visualization"]

CLOUD PROVIDER: [GCP / AWS / Azure — specify free tier constraints]
BUDGET: [$0 free tier only / specific budget]

TECH STACK:
- Language: [Python, Go, Node.js, etc.]
- Framework: [FastAPI, Express, Gin, etc.]
- Database: [PostgreSQL, SQLite, DynamoDB, etc.]
- Container: [Docker / Docker Compose / Kubernetes]
- IaC: [Terraform / Pulumi / CloudFormation / none]
- CI/CD: [GitHub Actions / GitLab CI / Jenkins / none]
- Monitoring: [Prometheus / CloudWatch / none]

PHASES TO GENERATE:
- Phase 1: [What it covers — e.g., "Local development + basic API"]
- Phase 2: [What it covers — e.g., "Cloud deployment + pipeline"]
- Phase 3: [What it covers — e.g., "IaC + CI/CD + security"]

DEVOPS FILES TO BUILD BY HAND (scaffolded build-along):
[List specific files — e.g., Dockerfile, docker-compose.yml, terraform/*.tf, .github/workflows/*.yml]

CODE FILES TO COPY-PASTE OR AI-GENERATE:
[List specific files — e.g., app/main.py, scripts/etl.py, tests/]

TARGET AUDIENCE: [Junior DevOps learner / bootcamp grad / career switcher / etc.]

LEARNING GOALS:
- [e.g., "Understand Docker multi-stage builds"]
- [e.g., "Write Terraform modules from scratch"]
- [e.g., "Set up GitHub Actions CI/CD pipeline"]

DEPLOYMENT ENVIRONMENTS:
[List where work happens — e.g., "Local terminal, AWS Console, EC2 SSH, VS Code editor"]

SPECIAL CONSTRAINTS:
[e.g., "Must stay within AWS free tier", "No Kubernetes — use ECS instead", "ARM-based instances"]
```

**Now generate the complete implementation guide following every convention above.**
