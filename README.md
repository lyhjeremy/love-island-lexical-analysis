# Lexical Analysis of Vocabulary Complexity in *Love Island USA* Season 4

A corpus-based study of how simple/repetitive the show's spoken language is:
vocabulary richness, word-frequency (Zipf), filler words, part of speech,
sentiment, the vocabulary load needed to follow it, and its reading level.

> 📄 **[Read the full paper (PDF)](V4/LoveIsland_LexicalAnalysis_V4.pdf)** &nbsp;·&nbsp;
> 🌐 **[Plain-English summary](https://lyhjeremy.github.io/love-island-lexical-analysis/)**

## Folder structure

```
.
├── index.html                              Plain-English showcase page (GitHub Pages)
├── data/                                    Corpus
│   ├── love_island_s4_transcripts.csv          cleaned transcripts (one row per episode)
│   └── love_island_s4_txt/                      one .txt per episode
├── scripts/                                 Analysis code
│   ├── scrape_love_island_s4.py                scraper (Selenium) -> data/
│   ├── analyze_love_island.py                  main analysis -> figures 01–10 + tables
│   ├── analyze_vocab_level.py                  vocab-load + reading-level -> figures 11–12
│   └── md2tex.py                               paper Markdown -> LaTeX converter
└── V4/                                      The paper (latest version)
    ├── LoveIsland_LexicalAnalysis_V4.md        editable source
    ├── LoveIsland_LexicalAnalysis_V4.tex       generated from the .md
    ├── LoveIsland_LexicalAnalysis_V4.pdf       compiled result
    ├── figures/                                the .png figures used by the paper
    └── tables/                                 the .csv tables used by the paper
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

## How to rebuild

Dependencies (once):
```
pip install pandas numpy scipy nltk textblob textstat wordcloud matplotlib seaborn beautifulsoup4 selenium webdriver-manager
```
A LaTeX install (TeX Live) is needed to compile the PDF.

The analysis scripts resolve `data/` automatically and write figures/tables to
the folder given by the `LI_OUTPUT_DIR` environment variable. `LI_FIG_DPI`
controls resolution (default 400). To (re)generate the paper's figures:
```
LI_OUTPUT_DIR="$PWD/V4" python scripts/analyze_love_island.py
LI_OUTPUT_DIR="$PWD/V4" python scripts/analyze_vocab_level.py
```

Rebuild the paper after editing `V4/LoveIsland_LexicalAnalysis_V4.md`:
```
python scripts/md2tex.py            # writes V4/LoveIsland_LexicalAnalysis_V4.tex
cd V4 && pdflatex LoveIsland_LexicalAnalysis_V4.tex && pdflatex LoveIsland_LexicalAnalysis_V4.tex
```

## License
[MIT](LICENSE) © 2026 Jeremy Lee
