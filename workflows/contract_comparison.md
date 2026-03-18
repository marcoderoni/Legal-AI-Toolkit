# Workflow: Contract Version Comparison

## Objective
Perform a word-by-word cross-check between two versions of the same
contract. Identify only changes NOT marked with track changes —
both in the body text and in margin comments.
This is a fidelity check, not a risk analysis.

## Required Inputs
- **V1**: The earlier version (baseline)
- **V2**: The later version to compare against V1

## Step 1 — Parse Both Documents
Run tools/parse_contract.py on both files:
```
python3 tools/parse_contract.py [V1_filename]
python3 tools/parse_contract.py [V2_filename]
```

## Step 2 — Cross-Check for Hidden Changes
Compare V1 and V2 word by word. Ignore all changes already visible
via track changes. Flag only:
- Text added, removed, or substituted WITHOUT track changes
- Margin comments added or removed WITHOUT track changes

## Step 3 — Output
If hidden changes are found, produce a table:

| Location | V1 Text | V2 Text |
|---|---|---|
| Art. X | [original text] | [modified text] |

Flag each entry as:
⚠️ UNMARKED CHANGE — modified without track changes

If no hidden changes are found, confirm:
✅ No hidden changes detected. All modifications are
visible via track changes.

## Edge Cases
- Different document structure or numbering between versions:
  match clauses by content, not article number, and note the
  structural difference
- If V2 has no track changes at all: state prominently
  "⚠️ No track changes found in V2 — full manual comparison performed"
