r"""Build the arXiv source (paper/arxiv/main.tex + figures/) and paper/paper.pdf from paper/draft.md.

pdflatex only, since arXiv compiles with it: Chinese runs are wrapped in CJKutf8 (\zh{...}) and the remaining
non-ASCII symbols are declared in the header. Needs pandoc and a TeX Live with the cjk and newunicodechar packages.
Usage: python paper/build_arxiv.py
"""
import os
import re
import shutil
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "arxiv")
AUTHOR = "Zijian Zeng (UCSI University)"
HEADER = r"""
\usepackage{CJKutf8}
\newcommand{\zh}[1]{\begin{CJK*}{UTF8}{gbsn}#1\end{CJK*}}
\usepackage{newunicodechar}
\newunicodechar{−}{\ensuremath{-}}
\newunicodechar{→}{\ensuremath{\rightarrow}}
\newunicodechar{×}{\ensuremath{\times}}
\newunicodechar{≥}{\ensuremath{\geq}}
\newunicodechar{≤}{\ensuremath{\leq}}
\newunicodechar{Δ}{\ensuremath{\Delta}}
\newunicodechar{κ}{\ensuremath{\kappa}}
"""
CJK_CHARS = "　-〿一-鿿＀-￯"   # CJK punctuation, ideographs, full-width forms
CJK = re.compile(f"[{CJK_CHARS}]+")
CJK_BREAK = re.compile(f"(?<=[{CJK_CHARS}])\n(?=[{CJK_CHARS}])")   # a line break inside Chinese is not a space
STAR = re.compile(r"(?<=[0-9\])])\*(?!\*)")   # significance stars after a number, not emphasis
FIGURE = re.compile(r"!\[\]\((figures/[^)]+)\)\n\n\*Figure \d+\.\* (.+?)(?=\n\n|\Z)", re.S)   # -> floating figure


def main():
    src = open(os.path.join(HERE, "draft.md"), encoding="utf-8").read()
    title = src.split("\n", 1)[0].lstrip("# ").strip()
    abstract = src.split("## Abstract", 1)[1].split("\n## ", 1)[0].strip()
    body = "## 1. " + src.split("\n## 1. ", 1)[1]
    body = body.replace("](../figures/", "](figures/")
    body = FIGURE.sub(lambda m: "![" + m.group(2).replace("\n", " ") + "](" + m.group(1) + ")", body)
    body = STAR.sub(r"\\*", CJK_BREAK.sub("", body))
    body = CJK.sub(lambda m: "\\zh{" + m.group(0) + "}", body)
    meta = "---\ntitle: '%s'\nauthor: '%s'\nabstract: |\n%s\n---\n\n" % (
        title.replace("'", "''"), AUTHOR, "\n".join("  " + l for l in abstract.split("\n")))
    os.makedirs(os.path.join(OUT, "figures"), exist_ok=True)
    for f in re.findall(r"\]\(figures/([^)]+)\)", body):
        shutil.copy(os.path.join(HERE, "..", "figures", f), os.path.join(OUT, "figures", f))
    with open(os.path.join(OUT, "header.tex"), "w", encoding="utf-8") as h:
        h.write(HEADER.lstrip())
    md = os.path.join(OUT, "main.md")
    with open(md, "w", encoding="utf-8") as m:
        m.write(meta + body)
    subprocess.run(["pandoc", md, "-s", "-o", os.path.join(OUT, "main.tex"), "-H", os.path.join(OUT, "header.tex"),
                    "-V", "geometry:margin=1in", "-V", "fontsize=11pt", "-V", "colorlinks=true"], check=True)
    os.remove(md)
    for _ in range(2):
        subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"], cwd=OUT, check=True,
                       stdout=subprocess.DEVNULL)
    shutil.copy(os.path.join(OUT, "main.pdf"), os.path.join(HERE, "paper.pdf"))
    for ext in ("aux", "log", "out", "pdf"):
        p = os.path.join(OUT, "main." + ext)
        if os.path.exists(p):
            os.remove(p)
    print("wrote", os.path.join(OUT, "main.tex"), "and", os.path.join(HERE, "paper.pdf"))


if __name__ == "__main__":
    main()
