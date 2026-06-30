"""
Tailored Markdown -> LaTeX converter for paper_template.md.
Not a general converter — it handles exactly the constructs used in this paper:
headings, bold/italic, inline code, pipe tables (-> longtable+booktabs),
the "**Figure N.** caption / `[path]`" figure idiom, and the unicode symbols
used in the results (−, ×, ², ₁₀, ρ, ≈, –, —, …, “”, ‘’, <, >).
"""
import re, os

# Converts a paper markdown file to LaTeX. Paths resolved from the project root
# (this file lives in scripts/). Change VERSION to target a different paper.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERSION = "V4"
NAME = "LoveIsland_LexicalAnalysis_" + VERSION
SRC = os.path.join(ROOT, VERSION, NAME + ".md")
OUT = os.path.join(ROOT, VERSION, NAME + ".tex")

# From V4 on, figures span the full text width at high resolution (no shrink
# cap); earlier versions used a height-capped 0.82-width layout.
try:
    _VN = int(VERSION.lstrip("Vv"))
except ValueError:
    _VN = 0
FIG_W = "width=\\linewidth" if _VN >= 4 else \
        "width=0.82\\linewidth,height=0.42\\textheight,keepaspectratio"

# ── character-level conversions ───────────────────────────────────────────────
UNICODE = [
    ("−", r"$-$"),     # minus sign
    ("—", r"---"),      # em dash
    ("–", r"--"),       # en dash
    ("²", r"\textsuperscript{2}"),
    ("₁₀", r"\textsubscript{10}"),
    ("≈", r"$\approx$"),
    ("×", r"$\times$"),
    ("ρ", r"$\rho$"),
    ("…", r"\ldots{}"),
    ("“", r"``"), ("”", r"''"),
    ("‘", r"`"),  ("’", r"'"),
    ("→", r"$\rightarrow$"),
    ("≤", r"$\le$"), ("≥", r"$\ge$"),
]

def esc(s):
    """Escape LaTeX specials in plain prose (no markdown markup left)."""
    s = s.replace("\\", r"\textbackslash{}")
    for a, b in [("&", r"\&"), ("%", r"\%"), ("#", r"\#"), ("_", r"\_"),
                 ("{", r"\{"), ("}", r"\}"), ("$", r"\$")]:
        s = s.replace(a, b)
    s = s.replace("<", r"$<$").replace(">", r"$>$")
    for a, b in UNICODE:
        s = s.replace(a, b)
    s = s.replace("~", r"$\sim$")
    s = s.replace("^", r"\textasciicircum{}")
    return s

def esc_code(s):
    """Escape inside \texttt{} (filenames, code)."""
    for a, b in [("\\", r"\textbackslash{}"), ("_", r"\_"), ("%", r"\%"),
                 ("#", r"\#"), ("&", r"\&"), ("{", r"\{"), ("}", r"\}"),
                 ("$", r"\$"), ("~", r"\textasciitilde{}"), ("^", r"\textasciicircum{}")]:
        s = s.replace(a, b)
    return s

def inline(s):
    """Convert a line of markdown prose to LaTeX (code spans, bold, italic)."""
    # protect inline code first
    codes = []
    def stash(m):
        codes.append(esc_code(m.group(1)))
        return f"\x00{len(codes)-1}\x00"
    s = re.sub(r"`([^`]+)`", stash, s)
    s = esc(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", s)
    s = re.sub(r"\*(.+?)\*", r"\\emph{\1}", s)
    # restore code
    s = re.sub(r"\x00(\d+)\x00", lambda m: r"\texttt{" + codes[int(m.group(1))] + "}", s)
    return s

def cell(s):
    return inline(s.strip())

# ── table conversion ──────────────────────────────────────────────────────────
def convert_table(rows):
    header = [c for c in rows[0].strip().strip("|").split("|")]
    ncol = len(header)
    body = rows[2:]  # skip the |---| separator

    # measure raw (pre-LaTeX) max width per column
    allrows = [header] + [r.strip().strip("|").split("|") for r in body if r.strip()]
    maxlen = [0] * ncol
    for r in allrows:
        for c in range(min(ncol, len(r))):
            maxlen[c] = max(maxlen[c], len(r[c].strip()))

    body_rows = [r for r in body if r.strip()]
    nrow = len(body_rows)

    wide = [c for c in range(ncol) if maxlen[c] > 22]
    if not wide:
        spec = "l" * ncol
    else:
        # text-heavy table: wrap wide columns as p{} proportional to content
        budget = max(0.92 - 0.07 * (ncol - len(wide)), 0.40)
        wsum = sum(maxlen[c] for c in wide)
        spec = "".join(
            ("p{%s\\linewidth}" % round(budget * maxlen[c] / wsum, 3)) if c in wide else "l"
            for c in range(ncol))

    # Font size by row count so tall tables still fit on a single page.
    # A plain tabular is an unbreakable box: it will never split across pages
    # and TeX pushes it whole to the next page if it doesn't fit.
    size = "\\footnotesize" if nrow > 28 else ("\\small" if nrow > 14 else "")
    out = [r"\begin{center}"]
    if size:
        out.append(size + r"\setlength{\tabcolsep}{4pt}")
    out.append(r"\begin{tabular}{" + spec + "}")
    out.append(r"\toprule")
    out.append(" & ".join(cell(h) for h in header) + r" \\")
    out.append(r"\midrule")
    for r in body_rows:
        cells = r.strip().strip("|").split("|")
        cells += [""] * (ncol - len(cells))
        out.append(" & ".join(cell(c) for c in cells[:ncol]) + r" \\")
    out.append(r"\bottomrule")
    out.append(r"\end{tabular}")
    out.append(r"\end{center}")
    return "\n".join(out)

# ── main pass ─────────────────────────────────────────────────────────────────
with open(SRC, encoding="utf-8") as f:
    lines = f.read().split("\n")

# title
title = ""
for ln in lines:
    if ln.startswith("# "):
        title = inline(ln[2:].strip())
        break

# find body start (Abstract)
start = next(i for i, ln in enumerate(lines) if ln.strip() == "## Abstract")

body = []
i = start
in_abstract = False
while i < len(lines):
    ln = lines[i]
    stripped = ln.strip()

    # tables
    if stripped.startswith("|") and i + 1 < len(lines) and re.match(r"^\|[\s:|-]+\|?$", lines[i+1].strip()):
        tbl = [lines[i]]
        i += 1
        while i < len(lines) and lines[i].strip().startswith("|"):
            tbl.append(lines[i]); i += 1
        body.append(convert_table(tbl))
        continue

    # figure idiom: **Figure N.** caption  /  `[path]`
    mfig = re.match(r"^\*\*Figure\s+(\d+)\.\*\*\s*(.*)$", stripped)
    if mfig and i + 1 < len(lines):
        nxt = lines[i+1].strip()
        mpath = re.match(r"^`\[(.+?)\]`$", nxt)
        if mpath:
            cap = inline((mfig.group(2)).strip())
            fname = os.path.basename(mpath.group(1))
            body.append(
                "\\begin{figure}[htbp]\n\\centering\n"
                f"\\includegraphics[{FIG_W}]{{{fname}}}\n"
                f"\\caption*{{\\textbf{{Figure {mfig.group(1)}.}} {cap}}}\n"
                "\\end{figure}")
            i += 2
            continue

    # headings
    if stripped == "## Abstract":
        body.append(r"\begin{abstract}"); in_abstract = True; i += 1; continue
    if stripped.startswith("**Keywords:**"):
        if in_abstract:
            body.append(r"\end{abstract}"); in_abstract = False
        kw = inline(stripped.replace("**Keywords:**", "").strip())
        body.append(r"\smallskip\noindent\textbf{Keywords:} " + kw); i += 1; continue
    if stripped.startswith("## "):
        if in_abstract:
            body.append(r"\end{abstract}"); in_abstract = False
        htext = stripped[3:].strip()
        # Flush pending floats only at the References/Appendix boundary, so body
        # figures can't drift into the back matter but still pack naturally
        # within the body (avoids near-blank figure pages).
        if htext.startswith("References") or htext.startswith("Appendix"):
            body.append(r"\FloatBarrier")
        # For appendices, reserve vertical space for the upcoming table so the
        # heading stays with its (unbreakable) table: small tables can still
        # share a page, large ones move together to the next page. Avoids both
        # orphaned headings and wasted near-blank pages.
        if htext.startswith("Appendix"):
            rows = 0
            for j in range(i + 1, min(i + 80, len(lines))):
                s = lines[j].strip()
                if s.startswith("## "):
                    break
                if s.startswith("|") and j + 1 < len(lines) and re.match(r"^\|[\s:|-]+\|?$", lines[j + 1].strip()):
                    k = j + 2
                    while k < len(lines) and lines[k].strip().startswith("|"):
                        rows += 1; k += 1
                    break
            if rows:
                need = min(0.9, 0.10 + rows * 0.019)
                body.append(r"\needspace{%s\textheight}" % round(need, 2))
        body.append(r"\section*{" + inline(htext) + "}"); i += 1; continue
    if stripped.startswith("### "):
        body.append(r"\subsection*{" + inline(stripped[4:].strip()) + "}"); i += 1; continue

    # horizontal rule
    if stripped == "---":
        i += 1; continue

    # blockquote (italic source notes)
    if stripped.startswith(">"):
        body.append(r"{\small\itshape " + inline(stripped.lstrip("> ").strip()) + "}"); i += 1; continue

    # blank line
    if stripped == "":
        body.append(""); i += 1; continue

    # list: gather consecutive bulleted ("- ") or numbered ("N. ") items
    mlist = re.match(r"^(?:-|\*|\d+\.)\s+(.*)$", stripped)
    if mlist:
        ordered = bool(re.match(r"^\d+\.\s", stripped))
        env = "enumerate" if ordered else "itemize"
        items = []
        while i < len(lines):
            s2 = lines[i].strip()
            m2 = re.match(r"^(?:-|\*|\d+\.)\s+(.*)$", s2)
            if not m2:
                break
            if bool(re.match(r"^\d+\.\s", s2)) != ordered:
                break
            items.append(r"\item " + inline(m2.group(1)))
            i += 1
        body.append(r"\begin{%s}" % env)
        body.extend(items)
        body.append(r"\end{%s}" % env)
        continue

    # ordinary paragraph line
    body.append(inline(stripped)); i += 1

PREAMBLE = r"""\documentclass[11pt]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage[letterpaper,margin=2cm]{geometry}
\usepackage{graphicx}
\usepackage{float}
\usepackage{placeins}
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{array}
\usepackage{amssymb}
\usepackage{amsmath}
\usepackage[font=small]{caption}
\usepackage{microtype}
\usepackage{setspace}
\usepackage{needspace}
\usepackage[hidelinks]{hyperref}
\graphicspath{{figures/}}
\setlength{\parskip}{0.45em}
\setlength{\parindent}{0pt}
\renewcommand{\topfraction}{0.95}
\renewcommand{\bottomfraction}{0.95}
\renewcommand{\textfraction}{0.05}
\renewcommand{\floatpagefraction}{0.85}
\setcounter{topnumber}{4}
\setcounter{bottomnumber}{4}
\setcounter{totalnumber}{6}
\title{%s}
\author{Jeremy Lee}
\date{June 2026}
\begin{document}
\maketitle
""" % title

with open(OUT, "w", encoding="utf-8") as f:
    f.write(PREAMBLE)
    f.write("\n".join(body))
    f.write("\n\\end{document}\n")

print("wrote", OUT)
