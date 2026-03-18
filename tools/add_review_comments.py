"""
add_review_comments.py
Adds inline Word comments to a DOCX file and saves as _review.docx in .tmp/

Usage:
    python tools/add_review_comments.py <input.docx> <comments.json>

comments.json format:
    [
        {
            "search_text": "exact text to anchor the comment to",
            "comment": "comment body",
            "label": "🔴 BLOCKER | 🟡 NEGOTIATE | 🟢 NOTE"
        },
        ...
    ]

Requirements:
    pip install python-docx lxml
"""

import sys
import json
import copy
import zipfile
import shutil
from pathlib import Path
from datetime import datetime
from lxml import etree

AUTHOR = "Marco De Roni's AI Agent"
DATE   = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

W_NS  = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
W14_NS = "http://schemas.microsoft.com/office/word/2010/wordml"
W     = f"{{{W_NS}}}"

COMMENTS_XML_TEMPLATE = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:comments xmlns:wpc="http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas"
  xmlns:cx="http://schemas.microsoft.com/office/drawing/2014/chartex"
  xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"
  xmlns:o="urn:schemas-microsoft-com:office:office"
  xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
  xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"
  xmlns:v="urn:schemas-microsoft-com:vml"
  xmlns:wp14="http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing"
  xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
  xmlns:w10="urn:schemas-microsoft-com:office:word"
  xmlns:w="{W_NS}"
  xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml"
  xmlns:w15="http://schemas.microsoft.com/office/word/2012/wordml"
  xmlns:w16cex="http://schemas.microsoft.com/office/word/2018/wordml/cex"
  xmlns:w16cid="http://schemas.microsoft.com/office/word/2016/wordml/cid"
  xmlns:w16="http://schemas.microsoft.com/office/word/2018/wordml"
  xmlns:w16sdtdh="http://schemas.microsoft.com/office/word/2020/wordml/sdtdatahash"
  xmlns:w16se="http://schemas.microsoft.com/office/word/2015/wordml/symex"
  xmlns:wpg="http://schemas.microsoft.com/office/word/2010/wordprocessingGroup"
  xmlns:wpi="http://schemas.microsoft.com/office/word/2010/wordprocessingInk"
  xmlns:wne="http://schemas.microsoft.com/office/word/2006/wordml"
  xmlns:wps="http://schemas.microsoft.com/office/word/2010/wordprocessingShape"
  mc:Ignorable="w14 w15 w16se w16cid w16 w16cex w16sdtdh wp14">
</w:comments>"""


def build_comment_element(comment_id: int, label: str, body: str) -> etree._Element:
    """Build a <w:comment> XML element."""
    ns = W_NS
    comment = etree.Element(f"{{{ns}}}comment")
    comment.set(f"{{{ns}}}id", str(comment_id))
    comment.set(f"{{{ns}}}author", AUTHOR)
    comment.set(f"{{{ns}}}date", DATE)
    comment.set(f"{{{ns}}}initials", "AI")

    para = etree.SubElement(comment, f"{{{ns}}}p")
    ppr  = etree.SubElement(para, f"{{{ns}}}pPr")
    ps   = etree.SubElement(ppr, f"{{{ns}}}pStyle")
    ps.set(f"{{{ns}}}val", "CommentText")

    # annotation ref run
    r1   = etree.SubElement(para, f"{{{ns}}}r")
    rpr1 = etree.SubElement(r1, f"{{{ns}}}rPr")
    rs1  = etree.SubElement(rpr1, f"{{{ns}}}rStyle")
    rs1.set(f"{{{ns}}}val", "CommentReference")
    etree.SubElement(r1, f"{{{ns}}}annotationRef")

    # label run (bold)
    if label:
        rl   = etree.SubElement(para, f"{{{ns}}}r")
        rprl = etree.SubElement(rl, f"{{{ns}}}rPr")
        etree.SubElement(rprl, f"{{{ns}}}b")
        tl   = etree.SubElement(rl, f"{{{ns}}}t")
        tl.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
        tl.text = label + "  "

    # body run
    rb   = etree.SubElement(para, f"{{{ns}}}r")
    tb   = etree.SubElement(rb, f"{{{ns}}}t")
    tb.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    tb.text = body

    return comment


def _normalize(s: str) -> str:
    """Lowercase, collapse whitespace, replace smart quotes/dashes with ASCII."""
    import unicodedata, re
    s = unicodedata.normalize("NFKD", s)
    s = s.replace("\u2019", "'").replace("\u2018", "'")
    s = s.replace("\u201c", '"').replace("\u201d", '"')
    s = s.replace("\u2013", "-").replace("\u2014", "-")
    s = re.sub(r"\s+", " ", s).strip().lower()
    return s


def find_paragraph_with_text(body_root, search_text: str):
    """Return first <w:p> whose concatenated text contains search_text (fuzzy)."""
    needle = _normalize(search_text)
    for para in body_root.iter(f"{W}p"):
        texts = []
        for t in para.iter(f"{W}t"):
            texts.append(t.text or "")
        for t in para.iter(f"{W}delText"):
            texts.append(t.text or "")
        full = _normalize("".join(texts))
        if needle in full:
            return para
    # Second pass: try first 40 chars of needle (handles cross-run splits)
    short = needle[:40]
    if len(short) < 10:
        return None
    for para in body_root.iter(f"{W}p"):
        texts = []
        for t in para.iter(f"{W}t"):
            texts.append(t.text or "")
        for t in para.iter(f"{W}delText"):
            texts.append(t.text or "")
        full = _normalize("".join(texts))
        if short in full:
            return para
    return None


def insert_comment_markers(para, comment_id: int):
    """
    Wrap the entire paragraph's runs with comment range markers.
    Inserts <w:commentRangeStart> before the first run and
    <w:commentRangeEnd> + <w:commentReference> after the last run.
    """
    ns = W_NS

    start = etree.Element(f"{{{ns}}}commentRangeStart")
    start.set(f"{{{ns}}}id", str(comment_id))

    end = etree.Element(f"{{{ns}}}commentRangeEnd")
    end.set(f"{{{ns}}}id", str(comment_id))

    ref_run = etree.Element(f"{{{ns}}}r")
    ref_rpr = etree.SubElement(ref_run, f"{{{ns}}}rPr")
    ref_rs  = etree.SubElement(ref_rpr, f"{{{ns}}}rStyle")
    ref_rs.set(f"{{{ns}}}val", "CommentReference")
    ref_ref = etree.SubElement(ref_run, f"{{{ns}}}commentReference")
    ref_ref.set(f"{{{ns}}}id", str(comment_id))

    # find position of first and last run-like child
    children = list(para)
    # insert start before pPr or at position 0
    insert_pos = 0
    for i, child in enumerate(children):
        tag = etree.QName(child.tag).localname
        if tag == "pPr":
            insert_pos = i + 1
            break
    para.insert(insert_pos, start)

    # append end and ref at tail
    para.append(end)
    para.append(ref_run)


def process(input_path: Path, comments: list) -> Path:
    # Work on a copy
    project_root = Path(__file__).resolve().parent.parent
    tmp_dir = project_root / ".tmp"
    tmp_dir.mkdir(exist_ok=True)
    out_path = tmp_dir / (input_path.stem + "_review.docx")
    shutil.copy2(input_path, out_path)

    # Read the zip
    with zipfile.ZipFile(out_path, "r") as z:
        doc_xml  = z.read("word/document.xml")
        try:
            existing_comments_xml = z.read("word/comments.xml")
        except KeyError:
            existing_comments_xml = COMMENTS_XML_TEMPLATE.encode("utf-8")
        names = z.namelist()

    doc_tree      = etree.fromstring(doc_xml)
    comments_tree = etree.fromstring(existing_comments_xml)

    body = doc_tree.find(f".//{W}body")

    # Determine starting comment id
    existing_ids = [
        int(c.get(f"{W}id", 0))
        for c in comments_tree.findall(f"{W}comment")
    ]
    next_id = max(existing_ids, default=-1) + 1

    added = 0
    skipped = []
    for item in comments:
        search = item.get("search_text", "").strip()
        label  = item.get("label", "")
        body_text = item.get("comment", "")

        if not search:
            continue

        para = find_paragraph_with_text(body, search)
        if para is None:
            skipped.append(search[:60])
            continue

        cid = next_id
        next_id += 1

        # Add to comments.xml
        c_elem = build_comment_element(cid, label, body_text)
        comments_tree.append(c_elem)

        # Insert markers in document.xml
        insert_comment_markers(para, cid)
        added += 1

    # Write back
    doc_xml_out      = etree.tostring(doc_tree,      xml_declaration=True, encoding="UTF-8", standalone=True)
    comments_xml_out = etree.tostring(comments_tree, xml_declaration=True, encoding="UTF-8", standalone=True)

    # Rebuild zip
    import io
    buf = io.BytesIO()
    with zipfile.ZipFile(out_path, "r") as zin:
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zout:
            for item_name in zin.namelist():
                if item_name == "word/document.xml":
                    zout.writestr(item_name, doc_xml_out)
                elif item_name == "word/comments.xml":
                    zout.writestr(item_name, comments_xml_out)
                else:
                    zout.writestr(item_name, zin.read(item_name))
            # Add comments.xml if it didn't exist
            if "word/comments.xml" not in names:
                zout.writestr("word/comments.xml", comments_xml_out)

    out_path.write_bytes(buf.getvalue())

    print(f"✅ {added} comment(s) added → {out_path}")
    if skipped:
        print(f"⚠️  {len(skipped)} anchor(s) not found (text may span multiple runs):")
        for s in skipped:
            print(f"   - '{s}...'")
    return out_path


def main():
    if len(sys.argv) != 3:
        sys.exit("Usage: python tools/add_review_comments.py <input.docx> <comments.json>")

    input_path    = Path(sys.argv[1]).resolve()
    comments_path = Path(sys.argv[2]).resolve()

    if not input_path.exists():
        sys.exit(f"File not found: {input_path}")
    if not comments_path.exists():
        sys.exit(f"Comments file not found: {comments_path}")

    with open(comments_path, encoding="utf-8") as f:
        comments = json.load(f)

    process(input_path, comments)


if __name__ == "__main__":
    main()
