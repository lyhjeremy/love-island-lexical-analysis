# Lexical Analysis of Vocabulary Complexity in *Love Island USA* Season 4

A corpus-based study of how simple/repetitive the show's spoken language is:
vocabulary richness, word-frequency (Zipf), filler words, part of speech,
sentiment, the vocabulary load needed to follow it, and its reading level.

## Folder structure

```
.
├── README.md
├── data/                                  Corpus (shared by all versions)
│   ├── love_island_s4_transcripts.csv         cleaned transcripts (one row per episode)
│   └── love_island_s4_txt/                     one .txt per episode
├── scripts/                               Code (shared by all versions)
│   ├── scrape_love_island_s4.py               scraper (Selenium) -> data/
│   ├── analyze_love_island.py                 main analysis -> figures 01–10 + tables
│   ├── analyze_vocab_level.py                 vocab-load + reading-level -> figures 11–12
│   ├── md2tex.py                              paper Markdown -> LaTeX converter
│   └── step1_debug.py                         scratch/debug helper
├── V1/ … V4/                              One self-contained folder per draft
│   ├── LoveIsland_LexicalAnalysis_V4.md        editable source
│   ├── LoveIsland_LexicalAnalysis_V4.tex       generated from the .md
│   ├── LoveIsland_LexicalAnalysis_V4.pdf       compiled result
│   ├── figures/                                the .png figures used by this version
│   └── tables/                                 the .csv tables used by this version
```

Each version folder is self-contained: its paper **and** the figures/tables it
uses live together. **V4 is the latest.**

### Version history
- **V1** — first full draft; all numeric results filled in.
- **V2** — shorter, less-technical rewrite; added the two questions ("how many
  words do you need" and "what reading level"); conclusions up front.
- **V3** — restored Top-100 / per-episode / sentiment tables and the
  vocabulary-growth figure; US Letter, 2 cm margins, no tables split across pages.
- **V4** — same content as V3, but **high-resolution (400 dpi) figures shown at
  full page width** for maximum readability, with figures floated and tightened
  spacing to minimise whitespace.

> Note: the V1 and V2 PDFs were compiled earlier with smaller versions of some
> figures; the `figures/` folders now hold the current (larger) renders, so those
> loose images may differ slightly from what is embedded in the older V1/V2 PDFs.

## How to rebuild

Dependencies (once):
```
pip install pandas numpy scipy nltk textblob textstat wordcloud matplotlib seaborn beautifulsoup4 selenium webdriver-manager
```
A LaTeX install (TeX Live) is needed to compile the PDF.

The analysis scripts resolve `data/` automatically and write figures/tables to
the folder given by the `LI_OUTPUT_DIR` environment variable (default: a top-level
`output/`). `LI_FIG_DPI` controls resolution (default 400). To (re)generate a
version's figures, e.g. V4:
```
LI_OUTPUT_DIR="$PWD/V4" python scripts/analyze_love_island.py
LI_OUTPUT_DIR="$PWD/V4" python scripts/analyze_vocab_level.py
```

Rebuild a paper after editing its `.md` (set `VERSION` near the top of
`scripts/md2tex.py`, then):
```
python scripts/md2tex.py                       # writes V4/LoveIsland_LexicalAnalysis_V4.tex
cd V4 && pdflatex LoveIsland_LexicalAnalysis_V4.tex && pdflatex LoveIsland_LexicalAnalysis_V4.tex
```
`md2tex.py` renders figures at full width from V4 onward; earlier versions use a
height-capped layout.

Start a new version (e.g. V5):
```
mkdir V5 && cp V4/LoveIsland_LexicalAnalysis_V4.md V5/LoveIsland_LexicalAnalysis_V5.md
# edit V5/...md, then set VERSION = "V5" in scripts/md2tex.py
LI_OUTPUT_DIR="$PWD/V5" python scripts/analyze_love_island.py
LI_OUTPUT_DIR="$PWD/V5" python scripts/analyze_vocab_level.py
python scripts/md2tex.py
cd V5 && pdflatex LoveIsland_LexicalAnalysis_V5.tex && pdflatex LoveIsland_LexicalAnalysis_V5.tex
```

## Headline findings
- The 100 most common words make up **61%** of all speech; word frequency is
  near-perfectly Zipfian (R² = 0.98).
- Knowing the **~1,250 most common word families covers 95%** of the show
  (vs ~3,000 for everyday English); ~2,550 covers 98%.
- Reads at roughly a **3rd–5th grade level**; **97.9%** of words are among the
  3,000 most familiar English words.
- Low lexical diversity (mean MTLD 59.96), no trend across the season; uniformly
  positive, highly subjective tone with few adjectives (8.4%).
