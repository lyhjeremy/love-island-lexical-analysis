"""
Love Island USA S4 — Vocabulary-load & reading-level analysis (V2 add-on)
=========================================================================
Answers two questions for the V2 paper:
  Q1. How many words must you learn to follow daily conversation in the show,
      vs. the ~3,000 word-family benchmark for everyday English
      (Adolphs & Schmitt 2003; Nation 2006)?
  Q2. What reading/grade level is the show's language at, vs. the ~grade-5
      standard used for materials aimed at the general public?

Outputs:
  output/figures/11_vocabulary_coverage.png
  output/figures/12_reading_level.png
  output/tables/vocabulary_coverage.csv
  output/tables/reading_level.csv
"""
import os, re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from collections import Counter
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import textstat

for pkg in ["punkt", "punkt_tab", "wordnet", "omw-1.4"]:
    nltk.download(pkg, quiet=True)

sns.set_theme(style="whitegrid")
BRAND = "#E8415A"; BLUE = "#2A6F97"
FIG_DPI = int(os.environ.get("LI_FIG_DPI", "400"))
plt.rcParams.update({"figure.dpi": FIG_DPI, "savefig.dpi": FIG_DPI, "savefig.bbox": "tight",
                     "font.family": "DejaVu Sans",
                     "font.size": 14, "axes.titlesize": 16, "axes.labelsize": 14,
                     "xtick.labelsize": 12, "ytick.labelsize": 12})

# Paths resolved relative to the project root (this file lives in scripts/).
# Output dir overridable via LI_OUTPUT_DIR to target a version folder (e.g. V4).
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV = os.path.join(ROOT, "data", "love_island_s4_transcripts.csv")
_OUT = os.environ.get("LI_OUTPUT_DIR") or os.path.join(ROOT, "output")
FIG = os.path.join(_OUT, "figures"); TAB = os.path.join(_OUT, "tables")
os.makedirs(FIG, exist_ok=True); os.makedirs(TAB, exist_ok=True)

df = pd.read_csv(CSV)
df = df[df["word_count"] >= 50].sort_values("episode_num").reset_index(drop=True)

def clean(t):
    t = re.sub(r"\[.*?\]", " ", str(t)); t = re.sub(r"http\S+", " ", t); t = t.lower()
    t = re.sub(r"[^a-z\s'']", " ", t); return re.sub(r"\s+", " ", t).strip()

def tok(t):
    return [w for w in word_tokenize(clean(t)) if w.isalpha() and len(w) > 1]

all_tokens = [w for ep in df["transcript"].apply(tok) for w in ep]
N = len(all_tokens)

# ── Q1: vocabulary load (word-family coverage) ────────────────────────────────
lem = WordNetLemmatizer()
def family(w):                       # collapse inflections -> approx word family
    return lem.lemmatize(lem.lemmatize(w, "v"), "n")

fam_tokens = [family(w) for w in all_tokens]
fam_counts = Counter(fam_tokens)
type_counts = Counter(all_tokens)

def words_for(counter, target):
    cum = np.cumsum([c for _, c in counter.most_common()]) / sum(counter.values())
    return int(np.searchsorted(cum, target) + 1)

rows = []
for label, counter in [("Word families (lemmatised)", fam_counts),
                       ("Word types (raw forms)", type_counts)]:
    for tgt in (0.80, 0.90, 0.95, 0.98):
        rows.append({"unit": label, "coverage_target": f"{int(tgt*100)}%",
                     "words_needed": words_for(counter, tgt)})
cov_df = pd.DataFrame(rows)
cov_df.to_csv(os.path.join(TAB, "vocabulary_coverage.csv"), index=False)
print("Vocabulary load:\n", cov_df.to_string(index=False))
print(f"\nTotal word families (lemmas): {len(fam_counts):,}  |  raw types: {len(type_counts):,}")

fam95 = words_for(fam_counts, 0.95); fam98 = words_for(fam_counts, 0.98)
fam90 = words_for(fam_counts, 0.90)

# coverage curve
order = [c for _, c in fam_counts.most_common()]
cumcov = np.cumsum(order) / N * 100
x = np.arange(1, len(order) + 1)
fig, ax = plt.subplots(figsize=(11, 6))
ax.plot(x, cumcov, color=BRAND, lw=2.5)
for tgt, xv in [(95, fam95), (98, fam98)]:
    ax.axhline(tgt, ls=":", color="gray", lw=1)
    ax.plot([xv], [tgt], "o", color=BLUE, ms=8)
    ax.annotate(f"{xv:,} words → {tgt}%", (xv, tgt), textcoords="offset points",
                xytext=(12, -18), fontsize=12, color=BLUE, fontweight="bold")
ax.axvline(3000, ls="--", color="black", lw=1.3)
ax.annotate("3,000 words\n(general English, 95%)", (3000, 40),
            textcoords="offset points", xytext=(8, 0), fontsize=11)
ax.set_xscale("log")
ax.set_xlabel("Number of word families known (most frequent first, log scale)")
ax.set_ylabel("% of all speech understood")
ax.set_title("How many words to follow Love Island USA S4?")
ax.set_ylim(0, 101)
plt.tight_layout(); plt.savefig(os.path.join(FIG, "11_vocabulary_coverage.png")); plt.close()
print("  -> 11_vocabulary_coverage.png")

# ── Q2: reading / grade level ─────────────────────────────────────────────────
def join_raw(t):
    t = re.sub(r"\[.*?\]", " ", str(t)); t = re.sub(r"http\S+", " ", t)
    return re.sub(r"[ \t]+", " ", t).strip()

corpus_text = "\n".join(join_raw(t) for t in df["transcript"])

overall = {
    "Flesch-Kincaid Grade": textstat.flesch_kincaid_grade(corpus_text),
    "Dale-Chall Grade (approx)": textstat.dale_chall_readability_score(corpus_text),
    "SMOG Index": textstat.smog_index(corpus_text),
    "Flesch Reading Ease": textstat.flesch_reading_ease(corpus_text),
    "Consensus (text_standard)": textstat.text_standard(corpus_text, float_output=True),
}
# % of words outside the Dale-Chall 3,000 familiar-words list (known by ~4th graders)
diff = textstat.difficult_words(corpus_text)
total_words_rt = len(re.findall(r"[A-Za-z']+", corpus_text))
pct_difficult = diff / max(total_words_rt, 1) * 100

# per-episode FK grade for stability
ep_fk = [textstat.flesch_kincaid_grade(join_raw(t)) for t in df["transcript"]]

read_rows = [{"metric": k, "value": round(v, 2)} for k, v in overall.items()]
read_rows.append({"metric": "% words outside 3,000 familiar list (Dale-Chall)",
                  "value": round(pct_difficult, 1)})
read_rows.append({"metric": "Mean per-episode Flesch-Kincaid Grade", "value": round(np.mean(ep_fk), 2)})
read_rows.append({"metric": "Per-episode FK Grade range",
                  "value": f"{min(ep_fk):.1f}-{max(ep_fk):.1f}"})
read_df = pd.DataFrame(read_rows)
read_df.to_csv(os.path.join(TAB, "reading_level.csv"), index=False)
print("\nReading level:\n", read_df.to_string(index=False))

# reading-level comparison figure
labels = ["Love Island\nUSA S4", "Grade-5\nstandard\n(general public)",
          "Typical\nnewspaper", "Academic\nprose"]
grades = [overall["Flesch-Kincaid Grade"], 5, 10, 14]
colors = [BRAND, "#4C9F70", "#9aa0a6", "#9aa0a6"]
fig, ax = plt.subplots(figsize=(11, 5.2))
bars = ax.bar(labels, grades, color=colors, alpha=0.9)
ax.axhline(5, ls="--", color="#4C9F70", lw=1.3)
for b, g in zip(bars, grades):
    ax.text(b.get_x()+b.get_width()/2, g+0.15, f"{g:.1f}", ha="center", fontsize=12, fontweight="bold")
ax.set_ylabel("U.S. school grade level")
ax.set_title("Reading level of Love Island USA S4 vs. common benchmarks")
plt.tight_layout(); plt.savefig(os.path.join(FIG, "12_reading_level.png")); plt.close()
print("  -> 12_reading_level.png")

print("\nHEADLINES:")
print(f"  ~{fam95:,} word families -> 95% of show ; ~{fam98:,} -> 98%  (vs ~3,000 / ~6,000-7,000 for general English)")
print(f"  Flesch-Kincaid grade: {overall['Flesch-Kincaid Grade']:.1f} ; Dale-Chall: {overall['Dale-Chall Grade (approx)']:.1f} ; consensus grade {overall['Consensus (text_standard)']:.0f}")
print(f"  {pct_difficult:.1f}% of words fall outside the 3,000 familiar-words list")
