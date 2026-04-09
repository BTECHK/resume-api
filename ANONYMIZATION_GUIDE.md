# Anonymization Guidelines

This document defines the anonymization rules for all resume data in this project.
These rules apply to every file that contains resume content: code, configs, docs, and prompts.

## Core Rule

**The candidate is never identified by real name.** Use "the candidate" or a generic placeholder.

## What to Anonymize

| Category | Rule | Example |
|----------|------|---------|
| **Name** | Never use real name | "The Candidate" |
| **Companies** | Describe by characteristics, not name | "a Big Four consulting firm" not "Deloitte" |
| **Clients** | Describe by sector + scale | "a top-3 social media conglomerate" not "Meta" |
| **Federal agencies** | Describe by mission area | "a federal defense intelligence agency" not "NGA" |
| **Email / phone** | Use placeholder or project-specific bot address | `resume-bot@project-domain.com` |
| **LinkedIn** | Omit or use placeholder | Do not link to real profile |
| **Location** | General region is OK | "Washington D.C. metro area" is acceptable |

## What NOT to Anonymize

| Category | Why |
|----------|-----|
| **Certifications** | Publicly verifiable, no PII risk (e.g., "AWS Solutions Architect – Associate") |
| **Skills & technologies** | Generic technical knowledge, not identifying |
| **Metrics & outcomes** | Percentages, dollar amounts, team sizes — keep them, they demonstrate impact |
| **Project descriptions** | Keep the work detail, just anonymize the who |
| **Education** | University name is OK (publicly listed on LinkedIn anyway) |

## Consulting-Style Descriptions

When anonymizing companies/clients, use this pattern:

> Worked at **[descriptor]** serving **[client descriptor]**

Examples:
- "Big Four professional services firm" (not Deloitte)
- "top-3 social media conglomerate" (not Meta)
- "Fortune 100 technology manufacturer" (not Dell)
- "top-5 US grocery retailer" (not Kroger)
- "federal justice agency supporting 50,000+ users"
- "federal defense intelligence agency"
- "regional healthcare system and academic medical center" (not Healthcare Program)
- "multi-state community banking group" (not Financial Services Program)

## Audit Checklist

Before any commit that touches resume data, verify:
- [ ] No real name appears anywhere in the diff
- [ ] No company names appear (use descriptors)
- [ ] No personal email or phone numbers
- [ ] No LinkedIn URL pointing to real profile
- [ ] Certifications, skills, and metrics are preserved
- [ ] Consulting-style descriptors follow the pattern above
