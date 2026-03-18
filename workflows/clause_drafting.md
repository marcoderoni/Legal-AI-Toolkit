# Workflow: Clause Drafting

## Objective
Draft or redraft specific contract clauses based on context provided.
Output is ready-to-use language, aligned with the playbook and
standard positions. No need to start from a full contract.

## Required Input
- Clause type (e.g. liability cap, audit rights, IP ownership)
- Context: governing law, deal size if relevant, counterparty type
- Constraint or trigger: why is this clause needed or being redrafted?
- Mode: own paper (we draft) or response to customer paper (we counter)

## Step 1 — Check Playbook First
Check references/playbook.docx for pre-approved language for this
clause type. If found, use it as the base and adapt to context.
If not found, draft from scratch using standard market practice
for EMEA SaaS agreements.

## Step 2 — Draft the Clause
Produce:
- **Preferred version**: our ideal position
- **Fallback version**: acceptable compromise if counterparty pushes back
- **Red line**: what we will not accept, and why (one line)

## Step 3 — Output Format
```
CLAUSE: [clause name]
GOVERNING LAW CONTEXT: [jurisdiction]

--- PREFERRED ---
[clause text]

--- FALLBACK ---
[clause text]

--- RED LINE ---
[what is not acceptable and why]
```

## Standard Positions by Clause Type
<!--
ADD YOUR OWN STANDARD POSITIONS HERE AS YOU BUILD THEM
Example:
LIABILITY CAP:
- Preferred: 12 months fees
- Fallback: 24 months fees for data breach only
- Red line: uncapped liability under any circumstance

IP OWNERSHIP:
- Preferred: all IP remains with us, customer gets licence only
- Fallback: work product specifically commissioned may be assigned
- Red line: assignment of our core platform IP
-->

## Governing Law Preferences
<!--
ADD YOUR PREFERRED GOVERNING LAW POSITIONS HERE
Example:
- Preferred: Dutch law, Amsterdam courts
- Acceptable: English law, Irish law
- Push back on: Italian law, US state law (requires escalation)
-->

## Notes and Edge Cases
<!--
ADD ANY DRAFTING NOTES, QUIRKS, OR LESSONS LEARNED HERE
Example: For public sector customers, liability caps may need to
follow procurement rules — flag and escalate.
-->
