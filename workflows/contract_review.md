# Workflow: Contract Review

**Version:** 1.0 | **Last updated:** 2026-03-16

---

## Objective

Perform a structured risk review of a SaaS, DPA, or enterprise contract and produce a
prioritised markup report saved to `.tmp/`.

---

## Required Inputs

| Input | How to get it |
|---|---|
| Contract file | PDF or DOCX dropped into the project root or a known path |
| Contract mode | **OWN PAPER** or **CUSTOMER PAPER** (ask if not provided) |
| Counterparty profile | Enterprise / Mid-market / Public sector / Startup (ask if not provided) |
| Deal context (optional) | ACV, product, renewal vs. new, any known constraints |

If mode or counterparty profile are missing, ask before proceeding.

---

## Steps

### Step 1 — Extract contract text

Run the parse tool on the uploaded file:

```bash
python tools/parse_contract.py <path_to_contract>
```

The tool writes extracted text to `.tmp/<filename>.txt` and prints the output path.
If extraction fails, check the error trace and fix before continuing (do not attempt
to review from a blank or partial extract).

---

### Step 2 — Clause-by-clause review

Work through the contract systematically. For each area below, compare against the
**reference positions** and classify every deviation as 🔴 / 🟡 / 🟢.

#### 3A — Liability

| Position | Reference (ServiceNow standard) |
|---|---|
| Cap | 12 months of fees paid in the period preceding the first event |
| Excluded damages | Indirect, consequential, punitive, special, exemplary (mutual) |
| Carve-outs from cap | Payment obligations, IP infringement/misappropriation, indemnification obligations, gross negligence / wilful misconduct in tort |

Red lines:
- 🔴 No liability cap on either party
- 🔴 Liability cap excludes customer but not vendor
- 🔴 Gross negligence / wilful misconduct NOT carved out
- 🟡 Cap below 12 months fees → push for 12 months
- 🟡 Consequential damages excluded for vendor but not customer → must be mutual

#### 3B — Intellectual Property

| Position | Reference |
|---|---|
| Platform / product IP | Vendor retains all rights |
| Customer data | Customer retains all rights; vendor licence limited to service delivery |
| Customer feedback | Vendor may use irrevocably — flag if scope is broader than improvements |
| Pro Services / custom deliverables | Newly Created IP assigned to customer on full payment; other deliverables: licence for use with the service only |

Red lines:
- 🔴 Any clause assigning customer's pre-existing IP to vendor
- 🔴 Vendor licence to use Customer Data extends beyond service delivery (e.g., model training)
- 🟡 No explicit assignment of Newly Created IP in PS → add "assigned upon full payment"
- 🟡 Feedback clause with no scope limit → narrow to product improvement only

#### 3C — Data Protection

| Position | Reference |
|---|---|
| DPA | Must be incorporated by reference or attached |
| Security programme | Industry-standard written programme required |
| Data residency | Flag if EU personal data processed outside EEA without SCCs |
| Sub-processors | Customer notification right required |

Red lines:
- 🔴 No DPA where personal data is processed
- 🔴 No data security obligations on vendor
- 🟡 DPA not updated for GDPR / Schrems II → require current version
- 🟡 No sub-processor list or notification right → negotiate in

#### 3D — Termination

| Position | Reference |
|---|---|
| Termination for breach | 30-day written cure period before termination right |
| Termination for convenience | Neither party should have unilateral T4C without notice (≥ 30 days) |
| Data return | Customer can export data during term; 10-day window post-termination, then deletion |
| Fees on termination | Termination for vendor breach → refund of prepaid fees for remainder of term |

Red lines:
- 🔴 Vendor can terminate for convenience with short / no notice and no fee refund
- 🔴 No data return right post-termination
- 🟡 Cure period < 30 days → push for 30
- 🟡 No refund of prepaid fees on termination for vendor breach

#### 3E — Payment & Auto-Renewal

- Flag any automatic price increase above CPI without consent (🟡)
- Flag auto-renewal with notice window < 60 days (🟡)
- Flag payment terms > 30 days net as risk if cash-flow sensitive (🟢)

#### 3F — Warranties & SLA

- Confirm warranty that the service will materially conform to Documentation (🔴 if absent)
- SLA and credits: confirm reference to CSA or equivalent; credits below 10% of monthly fees = 🟡
- Exclusive remedy clause: flag if it limits all warranty remedies to re-performance only with no termination right (🟡)

#### 3G — Confidentiality

- Standard mutual NDA provisions expected
- 🔴 if Customer Data not classified as Confidential Information
- 🟡 if survival period < 3 years post-termination

#### 3H — Assignment & Change of Control

- Reference: assignment requires consent; permitted exception for M&A
- 🟡 if vendor can assign freely without consent (especially to competitors)
- 🟡 if no customer termination right on vendor change of control

#### 3I — Governing Law

- EMEA-preferred: Ireland (EU), England & Wales (UK / Middle East)
- 🟡 if governing law is US (New York) for an EU-domiciled customer → request Irish or NL law
- 🔴 if governing law is outside EMEA entirely (see Escalation Triggers)

#### 3J — AI-Specific (if applicable)

If the contract involves AI products or services, check the AI Contract Watchlist
(see CLAUDE.md). Flag every item on the list.

---

### Step 4 — Escalation check

Before writing the report, check all Escalation Triggers from CLAUDE.md:
- Liability exposure > €1M
- New product category
- Governing law outside EMEA
- Regulated industry (finance, health, public sector)
- Data sovereignty / state security clause

If any trigger is met, add an **ESCALATION REQUIRED** banner at the top of the report.

---

### Step 5 — Write the review report

Save to `.tmp/<contract_filename>_review.md`.

**Report structure:**

```
# Contract Review: <Contract Name>
Date: YYYY-MM-DD
Mode: OWN PAPER / CUSTOMER PAPER
Counterparty: <name + profile>
Governing law: <jurisdiction>
GDPR exposure: Yes / No

---

## ESCALATION REQUIRED  ← include only if triggered
<reason>

---

## 🔴 BLOCKERS  (<n> items)
### [Clause X.X] — <Issue title>
**Issue:** <what the clause says>
**Risk:** <commercial/legal consequence>
**Redline:** <our proposed language>

---

## 🟡 NEGOTIATE  (<n> items)
(same structure)

---

## 🟢 ACCEPT / NOTE  (<n> items)
(same structure, briefer)

---

## Summary
<2–3 sentence executive summary: overall risk level, key blockers, recommended next step>
```

---

## Edge Cases

| Situation | Action |
|---|---|
| Contract in FR / DE / NL | Review in original, output report in English |
| No governing law clause | Flag as 🔴 BLOCKER — must be added before signing |
| DPA is a separate document | Note it, ask if it should be reviewed in the same session |
| File is image-based PDF (scanned) | pdfplumber will return empty text — inform user, request a text-based PDF or DOCX |
| Contract >100 pages | Process in sections; flag page ranges in the report |

---

## Output

File: `.tmp/<contract_filename>_review.md`

No contract content should appear outside `.tmp/`. Do not paste clause text into
chat history beyond what is needed to ask a clarifying question.
