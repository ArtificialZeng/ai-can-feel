"""Build paper/rr_stage1.docx (the Stage 1 Registered Report for Nature Human Behaviour) from paper/rr_stage1.md.

Citations "[n]" become superscript numerals, as the journal's template asks. Styles can come from the journal's Stage 1
template (NHB_Template_RR_Stage1.docx, https://www.nature.com/documents/NHB_Template_RR_Stage1.docx), passed as the
reference document; the template itself is not included in this repository.
Usage: python paper/build_rr_docx.py [path/to/NHB_Template_RR_Stage1.docx]
Without the template, pandoc's default styles are used. The section order and the design table follow the template
either way, and the default styles render the design table more reliably (LibreOffice check, 2026-11-07).
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
CITE = re.compile(r"\s?\[(\d+(?:[–,]\d+)*)\]")
COLS = [1400, 1900, 2000, 1800, 1926]   # dxa; sums to the A4 text width with 1-inch margins (9,026)
BORDERS = ('<w:tblBorders>' + "".join(f'<w:{b} w:val="single" w:sz="4" w:space="0" w:color="808080"/>'
                                      for b in ("top", "left", "bottom", "right", "insideH", "insideV")) +
           '</w:tblBorders>')
PPR = '<w:pStyle w:val="Compact" /><w:spacing w:before="0" w:after="40" w:line="240" w:lineRule="auto"/>' \
      '<w:ind w:firstLine="0"/><w:jc w:val="left" />'


def fix_table(tbl):
    """Fixed column widths, borders, single spacing and 9-pt text, bold header row."""
    tbl = re.sub(r'<w:tblW [^>]*/>', f'<w:tblW w:type="dxa" w:w="{sum(COLS)}" />' + BORDERS, tbl, count=1)
    grid = "".join(f'<w:gridCol w:w="{w}" />' for w in COLS)
    tbl = re.sub(r"<w:tblGrid>.*?</w:tblGrid>", "<w:tblGrid>" + grid + "</w:tblGrid>", tbl, count=1, flags=re.S)
    rows = re.split(r"(?=<w:tr>)", tbl)
    out = []
    for i, row in enumerate(rows):
        if "<w:tr>" in row:
            cells = re.split(r"(?=<w:tc>)", row)
            for j in range(1, len(cells)):
                tcw = f'<w:tcW w:w="{COLS[(j - 1) % 5]}" w:type="dxa"/>'
                if cells[j].startswith("<w:tc><w:tcPr>"):
                    cells[j] = cells[j].replace("<w:tc><w:tcPr>", "<w:tc><w:tcPr>" + tcw, 1)
                else:
                    cells[j] = cells[j].replace("<w:tc>", "<w:tc><w:tcPr>" + tcw + "</w:tcPr>", 1)
            row = "".join(cells)
            extra = "<w:b/>" if i == 1 else ""
            row = re.sub(r"<w:r><w:rPr>(.*?)</w:rPr>", lambda m: f'<w:r><w:rPr>{extra}{m.group(1)}<w:sz w:val="18"/></w:rPr>',
                         row)
            row = row.replace("<w:r><w:t", f'<w:r><w:rPr>{extra}<w:sz w:val="18"/></w:rPr><w:t')
            row = row.replace('<w:pStyle w:val="Compact" /><w:jc w:val="left" />', PPR)
        out.append(row)
    return "".join(out)


def postprocess(path):
    tmp = tempfile.mkdtemp()
    with zipfile.ZipFile(path) as z:
        z.extractall(tmp)
        names = z.namelist()
    doc = os.path.join(tmp, "word", "document.xml")
    xml = open(doc, encoding="utf-8").read()
    xml = re.sub(r"<w:tbl>.*?</w:tbl>", lambda m: fix_table(m.group(0)), xml, flags=re.S)
    # schema order: pStyle comes before numPr (pandoc writes them the other way round in list items)
    xml = re.sub(r'<w:pPr><w:numPr>(.*?)</w:numPr><w:pStyle w:val="([^"]+)" />',
                 r'<w:pPr><w:pStyle w:val="\2" /><w:numPr>\1</w:numPr>', xml)
    open(doc, "w", encoding="utf-8").write(xml)
    # drop media inherited from the reference document that nothing references
    rels = open(os.path.join(tmp, "word", "_rels", "document.xml.rels"), encoding="utf-8").read()
    for n in [n for n in names if n.startswith("word/media/") and n[len("word/"):] not in rels]:
        os.remove(os.path.join(tmp, n))
        names.remove(n)
        ct_path = os.path.join(tmp, "[Content_Types].xml")
        ct = open(ct_path, encoding="utf-8").read()
        ct = re.sub(r'<Override PartName="/%s"[^>]*/>' % re.escape(n), "", ct)
        open(ct_path, "w", encoding="utf-8").write(ct)
    ct_path = os.path.join(tmp, "[Content_Types].xml")
    ct = open(ct_path, encoding="utf-8").read()
    if 'Extension="png"' not in ct:
        ct = ct.replace('<Default Extension="xml"', '<Default Extension="png" ContentType="image/png" /><Default Extension="xml"', 1)
        open(ct_path, "w", encoding="utf-8").write(ct)
    st_path = os.path.join(tmp, "word", "settings.xml")
    st = open(st_path, encoding="utf-8").read()
    st = re.sub(r"<w:doNotTrackMoves\s*/>", "", st)   # misplaced in the template
    # pandoc's merge with the template puts footnotePr too early and repeats proofState at the end
    fn = re.search(r"<w:footnotePr>.*?</w:footnotePr>", st, re.S)
    if fn and "<w:rsids>" in st:
        st = st.replace(fn.group(0), "", 1).replace("<w:rsids>", fn.group(0) + "<w:rsids>", 1)
    proofs = list(re.finditer(r"<w:proofState[^>]*/>", st))
    for m in reversed(proofs[1:]):
        st = st[:m.start()] + st[m.end():]
    open(st_path, "w", encoding="utf-8").write(st)
    os.remove(path)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for n in names:
            if not n.endswith("/"):
                z.write(os.path.join(tmp, n), n)
    shutil.rmtree(tmp)


def main(template=None):
    src = open(os.path.join(HERE, "rr_stage1.md"), encoding="utf-8").read()
    head, refs = src.split("## References", 1)
    head = CITE.sub(lambda m: "^" + m.group(1) + "^", head)
    # pandoc needs a blank line between a paragraph and the list that follows it
    head = re.sub(r"(?m)^((?![-\s]|\d+\. ).+)\n(?=(?:- |\d+\. ))", r"\1\n\n", head)
    refs = refs.replace("\n## Table 1. Design table\n", "\n```{=openxml}\n<w:p><w:r><w:br w:type=\"page\"/></w:r></w:p>\n```\n\n**Table 1. Design table**\n")
    md = os.path.join(HERE, "rr_stage1_docx.md")
    with open(md, "w", encoding="utf-8") as fh:
        fh.write(head + "## References" + refs)
    out = os.path.join(HERE, "rr_stage1.docx")
    cmd = ["pandoc", md, "-f", "markdown", "-o", out, "--resource-path", HERE]
    subprocess.run(cmd + (["--reference-doc", template] if template else []), check=True)
    os.remove(md)
    postprocess(out)
    print("wrote", out)


if __name__ == "__main__":
    main(*sys.argv[1:2])
