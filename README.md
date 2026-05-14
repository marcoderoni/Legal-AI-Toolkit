# ⚖️ Legal AI Toolkit

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Claude Code](https://img.shields.io/badge/Built%20with-Claude%20Code-7B68EE?style=flat-square&logo=anthropic&logoColor=white)](https://anthropic.com)
[![Architecture](https://img.shields.io/badge/Architecture-WAT%20Framework-0ea5e9?style=flat-square)]()
[![Automation](https://img.shields.io/badge/Automation-Make%20%2F%20Integromat-6366f1?style=flat-square)](https://make.com)
[![Claude Skill](https://img.shields.io/badge/Claude-Skill%20Ready-7B68EE?style=flat-square&logo=anthropic&logoColor=white)](SKILL.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-22c55e?style=flat-square)](LICENSE)
[![Last Commit](https://img.shields.io/github/last-commit/marcoderoni/Legal-AI-Toolkit?style=flat-square)](https://github.com/marcoderoni/Legal-AI-Toolkit/commits/main)
[![Part of](https://img.shields.io/badge/portfolio-legal--tech-0ea5e9?style=flat-square&logo=github)](https://github.com/marcoderoni)

> **AI-assisted legal contract review framework for in-house counsel.** Covers SaaS, DPA, DSA and CSA contracts across EMEA. Built on the WAT architecture (Workflows, Agents, Tools) using Claude Code — no coding required to operate. Integrated with Make for automated email triage.

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Architecture](#-architecture)
- [Workflows](#-workflows)
- [Make Automation Pipeline](#-make-automation-pipeline)
- [Quick Start](#-quick-start)
- [Project Structure](#-project-structure)
- [Disclaimer](#-disclaimer)
- [Portfolio](#-portfolio)

---

## 🎯 Overview

In-house legal teams spend a disproportionate amount of time on repetitive contract review tasks — checking the same red lines, spotting the same risk patterns, drafting the same fallback language. This toolkit automates the pattern-matching while keeping the lawyer in control of every decision.

Built by a Senior Commercial Legal Counsel (EMEA) for real-world use across **SaaS agreements, DPAs, DSAs, and CSAs** — both own paper and customer paper negotiations.

**What it does:**
- Reviews contracts clause-by-clause against pre-defined playbooks
- Classifies risk as 🔴 Blocker / 🟡 Negotiate / 🟢 Accept
- Detects hidden changes between contract versions (unmarked redlines)
- Outputs annotated `.docx` files with inline Word comments
- Infers counterparty priorities from redlines and margin comments
- Suggests trade-offs grounded in a pre-approved fallback playbook
- Drafts clause language and email responses to counterparty objections
- Answers legal Q&A from colleagues across the business

---

## 🏗️ Architecture

Built on the **WAT Framework** (Workflows, Agents, Tools) — a structured approach to agentic AI systems where:

```
┌─────────────────────────────────────────────────────┐
│  W — WORKFLOWS   Natural language task instructions  │
│  A — AGENT       Claude Code reasoning engine        │
│  T — TOOLS       Python scripts for file I/O         │
└─────────────────────────────────────────────────────┘
```

The **CLAUDE.md** configuration file acts as the agent's persistent memory — defining role, decision framework, playbook references, and output standards. No prompt engineering required at runtime.

### Automation Pipeline

```
Gmail (incoming contract email)
        ↓
Make / Integromat
        ↓
Google Drive (retrieve playbook)
        ↓
Claude API (contract review)
        ↓
Gmail (draft response — human review before send)
```

Human-in-the-loop at every step: AI prepares, lawyer decides.

---

## 📂 Workflows

Five workflows cover the full commercial legal lifecycle. Claude selects the correct workflow automatically from natural language — no need to specify filenames.

| Workflow | File | Description |
|----------|------|-------------|
| **Contract Review** | `contract_review.md` | Clause-by-clause risk review with R/Y/G scoring against playbook |
| **Contract Comparison** | `contract_comparison.md` | Hidden change detection between two contract versions |
| **Clause Drafting** | `clause_drafting.md` | Draft or redraft specific clauses with fallback positions |
| **Email Response** | `email_response.md` | Draft responses to counterparty objections |
| **Legal Q&A** | `legal_qa.md` | Answer legal questions from business colleagues |

### Playbook Coverage

| Contract Type | Playbook | Key Red Lines |
|--------------|----------|---------------|
| SaaS / MSA / TCs | `playbook_tcs.docx` | Liability cap, IP ownership, auto-renewal notice |
| DPA | `playbook_dpa.docx` | Sub-processor consent, SCCs, 72h breach notification |
| DSA | `playbook_dsa.docx` | Purpose limitation, onward transfer restrictions |
| CSA | `playbook_csa.docx` | SLA minimums, data residency, exit/portability |

### R/Y/G Scoring

| Score | Meaning | Action |
|-------|---------|--------|
| 🔴 **RED** | High risk — reject or escalate | Must redline; flag for legal sign-off |
| 🟡 **YELLOW** | Medium risk — negotiate | Push back with alternative language |
| 🟢 **GREEN** | Acceptable | Note and move on |

---

## ⚡ Make Automation Pipeline

The toolkit integrates with **Make (Integromat)** for automated contract triage:

1. **Gmail** watches for incoming contract emails
2. **Google Drive** retrieves the relevant playbook based on contract type
3. **Claude API** reviews the contract against the playbook
4. **Gmail** creates a draft response — ready for lawyer review before sending

> **Human-in-the-loop principle**: AI prepares outputs, lawyer approves every action. No automated sending.

---

## 🚀 Quick Start

```bash
# 1. Clone
git clone https://github.com/marcoderoni/Legal-AI-Toolkit.git
cd Legal-AI-Toolkit

# 2. Install Claude Code (if not already installed)
npm install -g @anthropic-ai/claude-code

# 3. Open in VS Code and launch Claude Code
code .
# In terminal:
claude

# 4. Start reviewing — natural language, no commands needed
# "Review this SaaS agreement against our playbook"
# "Compare these two DPA versions and flag hidden changes"
# "Draft a liability cap clause for a €2M SaaS deal"
```

**No API key needed** — Claude Code uses your Anthropic subscription.

---

## 🏗️ Project Structure

```
Legal-AI-Toolkit/
├── CLAUDE.md                  # Agent configuration — role, playbook logic, output format
├── SKILL.md                   # Claude skill instructions (upload to Claude Skills)
├── workflows/
│   ├── contract_review.md     # Risk review workflow
│   ├── contract_comparison.md # Version comparison workflow
│   ├── clause_drafting.md     # Clause drafting workflow
│   ├── email_response.md      # Email response workflow
│   └── legal_qa.md            # Legal Q&A workflow
├── tools/
│   ├── parse_contract.py      # PDF/DOCX parser
│   ├── add_review_comments.py # Inline Word comment injector
│   └── compare_versions.py    # Contract diff tool
├── references/
│   ├── playbook_tcs.docx      # SaaS/TCs playbook (template — add your own)
│   ├── playbook_dpa.docx      # DPA playbook (template)
│   ├── playbook_dsa.docx      # DSA playbook (template)
│   └── playbook_csa.docx      # CSA playbook (template)
├── requirements.txt
├── .env.example
├── LICENSE
└── README.md
```

---

## ⚠️ Disclaimer

This toolkit provides **AI-assisted legal analysis** for productivity purposes only. It does **not** constitute legal advice. All outputs should be reviewed by a qualified legal professional before reliance. Do not use with confidential client data on public or unsecured systems.

The author is a practising in-house legal counsel, not acting in a legal advisory capacity through this tool.

---

## 🗂️ Portfolio

Part of the **Legal Tech GitHub Portfolio** by [Marco De Roni](https://github.com/marcoderoni) — Senior Commercial Legal Counsel (EMEA) building open-source tools at the intersection of law, AI, and compliance.

| Repo | Description |
|------|-------------|
| **Legal-AI-Toolkit** | **← You are here** |
| [legal-gpt-reviewer](https://github.com/marcoderoni/legal-gpt-reviewer) | Provider-agnostic AI contract reviewer (Groq + GPT-4o) |
| [contract-scanner](https://github.com/marcoderoni/contract-scanner) | Single-contract risk scanner with R/Y/G scoring |
| [contract-bulk-analyzer](https://github.com/marcoderoni/contract-bulk-analyzer) | Portfolio-level contract analysis |
| [legal-knowledge-wiki](https://github.com/marcoderoni/legal-knowledge-wiki) | D3.js knowledge graphs + ontology extraction |
| [eu-ai-act-classifier](https://github.com/marcoderoni/eu-ai-act-classifier) | EU AI Act risk classifier — Prohibited → Minimal Risk |

---

**Copyright (c) 2026 Marco De Roni. All rights reserved.**
Licensed under the [MIT License](LICENSE).

*Built with ⚖️ and 🐍 in Amsterdam.*
