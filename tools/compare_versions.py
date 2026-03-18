"""
compare_versions.py
Compares a REDLINE .docx (with track changes) against a CLEAN .docx and reports
any text differences that are NOT marked as tracked changes in the REDLINE.

How it works:
  - From the REDLINE, reconstruct the "before" state: normal text + deleted text (w:del),
    excluding inserted text (w:ins). This is what the document looked like before redlining.
  - Compare that "before" state against the CLEAN.
  - Differences = text that was silently changed (not tracked).

Usage:
    python tools/compare_versions.py <redline.docx> <clean.docx>

Output:
    .tmp/<redline_stem>_vs_<clean_stem>_hidden_changes.txt
    Prints output path on success.

Requirements:
    pip install python-docx lxml
"""

import sys
import re
from pathlib import Path
from lxml import etree

# Word XML namespaces
W  = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
W14 = "http://schemas.microsoft.com/office/word/2010/wordml"

def iter_paragraphs_xml(docx_path: Path):
    """Yield raw paragraph XML elements from document.xml inside a .docx."""
    import zipfile
    with zipfile.ZipFile(docx_path) as z:
        with z.open("word/document.xml") as f:
            tree = etree.parse(f)
    body = tree.find(f".//{{{W}}}body")
    for elem in body:
        tag = etree.QName(elem.tag).localname
        if tag == "p":
            yield elem
        elif tag == "tbl":
            # Tables: yield each cell's paragraphs
            for cell_p in elem.iter(f"{{{W}}}p"):
                yield cell_p


def extract_text_from_runs(para_elem, include_ins=True, include_del=False):
    """
    Extract text from a paragraph element, respecting track-change flags.

    include_ins=True,  include_del=False  → "after"  state (accepted redline)
    include_ins=False, include_del=True   → "before" state (original, pre-redline)
    include_ins=True,  include_del=True   → all text (for plain extraction)
    """
    parts = []

    def walk(node, in_ins=False, in_del=False):
        tag = etree.QName(node.tag).localname if node.tag != etree.Comment else None
        if tag is None:
            return

        # Track-change wrappers
        if tag == "ins":
            for child in node:
                walk(child, in_ins=True, in_del=in_del)
            return
        if tag == "del":
            for child in node:
                walk(child, in_ins=in_ins, in_del=True)
            return

        # Actual text nodes
        if tag == "t":
            text = node.text or ""
            if in_ins and not include_ins:
                return
            if in_del and not include_del:
                return
            parts.append(text)
            return
        if tag == "delText":
            text = node.text or ""
            if not in_del:
                in_del = True
            if not include_del:
                return
            parts.append(text)
            return

        # Tab / break
        if tag == "tab":
            parts.append("\t")
            return
        if tag == "br":
            parts.append("\n")
            return

        for child in node:
            walk(child, in_ins=in_ins, in_del=in_del)

    walk(para_elem)
    return "".join(parts).strip()


def extract_paragraphs(docx_path: Path, include_ins=True, include_del=False):
    """Return list of paragraph strings from a docx, filtered by track-change mode."""
    result = []
    for para in iter_paragraphs_xml(docx_path):
        text = extract_text_from_runs(para, include_ins=include_ins, include_del=include_del)
        result.append(text)
    return result


def has_tracked_changes(docx_path: Path) -> bool:
    """Return True if the document contains any w:ins or w:del elements."""
    import zipfile
    with zipfile.ZipFile(docx_path) as z:
        with z.open("word/document.xml") as f:
            content = f.read()
    return b"w:ins" in content or b"w:del" in content


def diff_paragraphs(before_paras, clean_paras):
    """
    Compare two paragraph lists and return a list of differences.
    Uses a simple line-diff; returns list of dicts with context.
    """
    import difflib
    matcher = difflib.SequenceMatcher(None, before_paras, clean_paras, autojunk=False)
    diffs = []
    for op, i1, i2, j1, j2 in matcher.get_opcodes():
        if op == "equal":
            continue
        diffs.append({
            "op": op,
            "redline_before": before_paras[i1:i2],
            "clean":          clean_paras[j1:j2],
            "redline_para_idx": (i1, i2),
            "clean_para_idx":   (j1, j2),
        })
    return diffs


def format_report(diffs, redline_path, clean_path):
    lines = [
        f"HIDDEN CHANGE REPORT",
        f"REDLINE : {redline_path.name}",
        f"CLEAN   : {clean_path.name}",
        f"",
        f"Methodology: reconstructed the pre-redline ('before') state from the REDLINE",
        f"by including deleted text and excluding inserted text, then diffed against CLEAN.",
        f"Any difference below was NOT marked as a tracked change.",
        f"{'='*72}",
        "",
    ]

    if not diffs:
        lines.append("✅ No hidden (untracked) changes found.")
        lines.append("Every difference between CLEAN and REDLINE is properly tracked.")
        return "\n".join(lines)

    lines.append(f"⚠️  {len(diffs)} block(s) of untracked differences found:\n")

    for i, d in enumerate(diffs, 1):
        op_label = {
            "replace": "REPLACED (silently)",
            "insert":  "INSERTED (silently, not in redline)",
            "delete":  "DELETED  (silently, not in redline)",
        }.get(d["op"], d["op"].upper())

        lines.append(f"--- [{i}] {op_label} ---")
        lines.append(f"  REDLINE 'before' (para {d['redline_para_idx'][0]+1}–{d['redline_para_idx'][1]}):")
        for p in d["redline_before"]:
            if p.strip():
                lines.append(f"    - {p[:300]}")
        lines.append(f"  CLEAN (para {d['clean_para_idx'][0]+1}–{d['clean_para_idx'][1]}):")
        for p in d["clean"]:
            if p.strip():
                lines.append(f"    + {p[:300]}")
        lines.append("")

    return "\n".join(lines)


def main():
    if len(sys.argv) != 3:
        sys.exit("Usage: python tools/compare_versions.py <redline.docx> <clean.docx>")

    redline_path = Path(sys.argv[1]).resolve()
    clean_path   = Path(sys.argv[2]).resolve()

    for p in [redline_path, clean_path]:
        if not p.exists():
            sys.exit(f"File not found: {p}")
        if p.suffix.lower() != ".docx":
            sys.exit(f"Only .docx files supported: {p}")

    if not has_tracked_changes(redline_path):
        print("⚠️  WARNING: No track changes (w:ins/w:del) found in REDLINE file.")
        print("   The file may be a clean document. Proceeding with plain text diff.")

    # "Before" state from REDLINE: normal text + deleted text, no inserted text
    redline_before = extract_paragraphs(redline_path, include_ins=False, include_del=True)
    # CLEAN text
    clean_paras    = extract_paragraphs(clean_path,   include_ins=True,  include_del=False)

    diffs = diff_paragraphs(redline_before, clean_paras)
    report = format_report(diffs, redline_path, clean_path)

    project_root = Path(__file__).resolve().parent.parent
    tmp_dir = project_root / ".tmp"
    tmp_dir.mkdir(exist_ok=True)

    out_name = f"{redline_path.stem}_vs_{clean_path.stem}_hidden_changes.txt"
    out_path = tmp_dir / out_name
    out_path.write_text(report, encoding="utf-8")

    print(report)
    print(f"\n→ Saved to: {out_path}")


if __name__ == "__main__":
    main()
