"""
Love Island USA — Season 4 Vocabulary Analysis
===============================================
Runs end-to-end linguistic analysis on the scraped transcripts and
generates all figures and tables needed for the academic paper.

REQUIREMENTS:
    pip install pandas nltk matplotlib seaborn wordcloud textblob scipy

USAGE:
    python analyze_love_island.py

OUTPUTS (all saved to ./output/):
    figures/
        01_top50_words.png
        02_word_frequency_distribution.png
        03_lexical_diversity_per_episode.png
        04_wordcloud_all.png
        05_wordcloud_no_stopwords.png
        06_filler_words.png
        07_pos_distribution.png
        08_sentiment_per_episode.png
        09_word_length_distribution.png
        10_vocabulary_growth_curve.png
    tables/
        top100_words.csv
        filler_word_counts.csv
        lexical_diversity.csv
        sentiment_scores.csv
        pos_summary.csv
        summary_statistics.csv
"""

import os, re, sys, string, warnings

# Windows consoles default to cp1252, which crashes on the → and … characters
# printed below. Force UTF-8 output so the script runs anywhere.
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from collections import Counter
from wordcloud import WordCloud

import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.tag import pos_tag
from textblob import TextBlob
from scipy import stats

warnings.filterwarnings("ignore")

# ── Download NLTK data ────────────────────────────────────────────────────────
# NLTK ≥3.8.2 renamed the tagger to the language-suffixed package; older NLTK
# uses the un-suffixed name. Download both so it works across versions.
for pkg in ["punkt", "punkt_tab", "stopwords",
            "averaged_perceptron_tagger", "averaged_perceptron_tagger_eng"]:
    nltk.download(pkg, quiet=True)

# ── Paths ─────────────────────────────────────────────────────────────────────
# Resolve everything relative to the project root (this file lives in scripts/),
# so the script works no matter which directory it is launched from.
ROOT       = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH   = os.path.join(ROOT, "data", "love_island_s4_transcripts.csv")
# Output location is overridable so figures/tables can be written into a
# specific version folder, e.g.  LI_OUTPUT_DIR=<repo>/V4  python analyze_love_island.py
OUT_DIR    = os.environ.get("LI_OUTPUT_DIR") or os.path.join(ROOT, "output")
FIG_DIR    = os.path.join(OUT_DIR, "figures")
TAB_DIR    = os.path.join(OUT_DIR, "tables")
os.makedirs(FIG_DIR, exist_ok=True)
os.makedirs(TAB_DIR, exist_ok=True)

# ── Style ─────────────────────────────────────────────────────────────────────
sns.set_theme(style="whitegrid", palette="muted")
BRAND_COLOR = "#E8415A"   # Love Island pinkish-red
# High-resolution output (override with LI_FIG_DPI). 300 dpi = crisp at full
# page width / for print.
FIG_DPI = int(os.environ.get("LI_FIG_DPI", "400"))
plt.rcParams.update({
    "figure.dpi": FIG_DPI,
    "savefig.dpi": FIG_DPI,
    "savefig.bbox": "tight",
    "font.family": "DejaVu Sans",
    # Larger fonts so figures stay legible when scaled to page width in the PDF
    "font.size": 14,
    "axes.titlesize": 16,
    "axes.labelsize": 14,
    "xtick.labelsize": 12,
    "ytick.labelsize": 12,
    "legend.fontsize": 12,
})

STOP = set(stopwords.words("english"))

# Filler words commonly associated with reality TV / casual speech
FILLERS = [
    "like", "literally", "basically", "honestly", "actually",
    "obviously", "totally", "definitely", "absolutely", "seriously",
    "right", "okay", "yeah", "um", "uh", "kind", "sort",
    "mean", "know", "just", "really", "very", "stuff", "thing",
]

# POS tag groups (Penn Treebank).
# NOTE: each tag must map to exactly ONE category — a tag listed under two
# categories is silently overwritten by whichever appears last in this dict.
# The Penn "IN" tag covers prepositions and subordinating conjunctions; by
# convention it is counted as a preposition, while "CC" (coordinating
# conjunction: and/but/or) is the conjunction class.
POS_MAP = {
    "Noun":        ["NN", "NNS", "NNP", "NNPS"],
    "Verb":        ["VB", "VBD", "VBG", "VBN", "VBP", "VBZ", "MD"],
    "Adjective":   ["JJ", "JJR", "JJS"],
    "Adverb":      ["RB", "RBR", "RBS"],
    "Pronoun":     ["PRP", "PRP$", "WP", "WP$"],
    "Preposition": ["IN", "TO"],
    "Conjunction": ["CC"],
    "Interjection":["UH"],
    "Determiner":  ["DT", "PDT", "WDT"],
    "Other":       [],
}

# ── Load & clean ──────────────────────────────────────────────────────────────
def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = re.sub(r"\[.*?\]", " ", text)          # remove [FAILED] etc.
    text = re.sub(r"http\S+", " ", text)           # remove URLs
    text = text.lower()
    text = re.sub(r"[^a-z\s'']", " ", text)       # keep letters, apostrophes
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tokenize(text):
    return [w for w in word_tokenize(clean_text(text))
            if w.isalpha() and len(w) > 1]


def count_sentences(text):
    """Count sentences from the RAW transcript.

    clean_text() strips all .?! punctuation, so sentence boundaries must be
    measured before cleaning — otherwise each episode collapses to one
    'sentence'. Subtitle line breaks are flattened to spaces first so that a
    single sentence split across several subtitle lines isn't over-counted.
    """
    if not isinstance(text, str):
        return 0
    t = re.sub(r"\[.*?\]", " ", text)        # drop [CHALLENGE NOT PASSED] etc.
    t = re.sub(r"\s+", " ", t).strip()       # flatten subtitle line wrapping
    return len(sent_tokenize(t)) if t else 0


print("Loading transcripts…")
df = pd.read_csv(CSV_PATH)
df = df[df["word_count"] >= 50].copy()
df["clean"] = df["transcript"].apply(clean_text)
df["tokens"] = df["clean"].apply(tokenize)
df = df.sort_values("episode_num").reset_index(drop=True)

all_tokens   = [tok for ep in df["tokens"] for tok in ep]
content_toks = [w for w in all_tokens if w not in STOP]

print(f"  Episodes loaded : {len(df)}")
print(f"  Total tokens    : {len(all_tokens):,}")
print(f"  Unique words    : {len(set(all_tokens)):,}")
print(f"  Content words   : {len(content_toks):,}")


# ═══════════════════════════════════════════════════════════════════════════════
# 1. SUMMARY STATISTICS
# ═══════════════════════════════════════════════════════════════════════════════
print("\n[1/10] Summary statistics…")

total_words   = len(all_tokens)
unique_words  = len(set(all_tokens))
ttr_overall   = unique_words / total_words          # Type-Token Ratio
avg_word_len  = np.mean([len(w) for w in all_tokens])
total_sents   = sum(count_sentences(t) for t in df["transcript"])
avg_sent_len  = total_words / max(total_sents, 1)

summary = pd.DataFrame([{
    "Metric": "Total episodes",             "Value": len(df)},
    {"Metric": "Total word tokens",         "Value": f"{total_words:,}"},
    {"Metric": "Unique word types",         "Value": f"{unique_words:,}"},
    {"Metric": "Type-Token Ratio (TTR)",    "Value": f"{ttr_overall:.4f}"},
    {"Metric": "Average word length (chars)","Value": f"{avg_word_len:.2f}"},
    {"Metric": "Total sentences (est.)",    "Value": f"{total_sents:,}"},
    {"Metric": "Avg words per sentence",    "Value": f"{avg_sent_len:.1f}"},
])
summary.to_csv(os.path.join(TAB_DIR, "summary_statistics.csv"), index=False)
print(summary.to_string(index=False))


# ═══════════════════════════════════════════════════════════════════════════════
# 2. TOP 50 WORDS (all tokens, no stopword removal)
# ═══════════════════════════════════════════════════════════════════════════════
print("\n[2/10] Top 50 word frequency…")

freq_all = Counter(all_tokens)
top50 = freq_all.most_common(50)
top50_df = pd.DataFrame(top50, columns=["word", "count"])
top50_df["percent"] = top50_df["count"] / total_words * 100

# Save top 100
top100_df = pd.DataFrame(freq_all.most_common(100), columns=["word", "count"])
top100_df["percent"] = top100_df["count"] / total_words * 100
top100_df.to_csv(os.path.join(TAB_DIR, "top100_words.csv"), index=False)

fig, ax = plt.subplots(figsize=(12, 10))
bars = ax.barh(top50_df["word"][::-1], top50_df["count"][::-1], color=BRAND_COLOR, alpha=0.85)
ax.tick_params(axis="y", labelsize=10)
ax.set_xlabel("Frequency", fontsize=13)
ax.set_title("Top 50 Most Frequent Words — Love Island USA Season 4", fontsize=15, fontweight="bold")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, "01_top50_words.png"))
plt.close()
print("  → 01_top50_words.png saved")


# ═══════════════════════════════════════════════════════════════════════════════
# 3. WORD FREQUENCY DISTRIBUTION (Zipf's Law check)
# ═══════════════════════════════════════════════════════════════════════════════
print("\n[3/10] Frequency distribution (Zipf)…")

ranks  = np.arange(1, len(freq_all) + 1)
counts = np.array([c for _, c in freq_all.most_common()])

# Stacked (2 rows) rather than side-by-side, so each panel is full page width
# and remains legible in the PDF.
fig, axes = plt.subplots(2, 1, figsize=(12, 9))
axes[0].plot(ranks[:200], counts[:200], color=BRAND_COLOR, linewidth=2)
axes[0].set_title("Word Frequency (Top 200 Words)")
axes[0].set_xlabel("Rank"); axes[0].set_ylabel("Frequency")

axes[1].loglog(ranks, counts, color=BRAND_COLOR, alpha=0.85, linewidth=2)
axes[1].set_title("Log-Log Plot (Zipf's Law Check) — a straight line indicates Zipfian decay")
axes[1].set_xlabel("Rank (log scale)"); axes[1].set_ylabel("Frequency (log scale)")

plt.suptitle("Word Frequency Distribution — Love Island USA Season 4",
             fontsize=16, fontweight="bold")
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, "02_word_frequency_distribution.png"))
plt.close()
print("  → 02_word_frequency_distribution.png saved")


# ═══════════════════════════════════════════════════════════════════════════════
# 4. LEXICAL DIVERSITY PER EPISODE
# ═══════════════════════════════════════════════════════════════════════════════
print("\n[4/10] Lexical diversity per episode…")

def mtld(tokens, threshold=0.72):
    """Measure of Textual Lexical Diversity (MTLD)."""
    def _forward(toks):
        factor, types, tokens_seen = 0, set(), 0
        for w in toks:
            types.add(w); tokens_seen += 1
            ttr = len(types) / tokens_seen
            if ttr <= threshold:
                factor += 1; types, tokens_seen = set(), 0
        if tokens_seen > 0:
            factor += (1 - len(types)/max(tokens_seen,1)) / (1 - threshold)
        return len(toks) / max(factor, 1)
    if len(tokens) < 50:
        return np.nan
    return (_forward(tokens) + _forward(list(reversed(tokens)))) / 2

lex_rows = []
for _, row in df.iterrows():
    toks = row["tokens"]
    n    = len(toks)
    if n < 10:
        continue
    unique = len(set(toks))
    ttr    = unique / n
    # Root TTR (normalised for length)
    rttr   = unique / np.sqrt(n)
    mtld_v = mtld(toks)
    lex_rows.append({
        "episode_num":  row["episode_num"],
        "title":        row["title"],
        "total_tokens": n,
        "unique_types": unique,
        "TTR":          round(ttr, 4),
        "Root_TTR":     round(rttr, 3),
        "MTLD":         round(mtld_v, 2) if not np.isnan(mtld_v) else np.nan,
    })

lex_df = pd.DataFrame(lex_rows)
lex_df.to_csv(os.path.join(TAB_DIR, "lexical_diversity.csv"), index=False)

fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True)
metrics = [("TTR", "Type-Token Ratio"), ("Root_TTR", "Root TTR"), ("MTLD", "MTLD Score")]
for ax, (col, label) in zip(axes, metrics):
    ax.plot(lex_df["episode_num"], lex_df[col], marker="o", color=BRAND_COLOR,
            markersize=5, linewidth=1.5)
    ax.axhline(lex_df[col].mean(), linestyle="--", color="gray", alpha=0.6, label=f"Mean: {lex_df[col].mean():.2f}")
    ax.set_ylabel(label, fontsize=10)
    ax.legend(fontsize=9)
axes[-1].set_xlabel("Episode Number", fontsize=11)
plt.suptitle("Lexical Diversity Across Episodes — Love Island USA Season 4",
             fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, "03_lexical_diversity_per_episode.png"))
plt.close()
print("  → 03_lexical_diversity_per_episode.png saved")


# ═══════════════════════════════════════════════════════════════════════════════
# 5. WORD CLOUDS
# ═══════════════════════════════════════════════════════════════════════════════
print("\n[5/10] Word clouds…")

full_text = " ".join(all_tokens)
content_text = " ".join(content_toks)

def make_wc(text, title, fname, stopword_set=None):
    wc = WordCloud(
        width=3200, height=1600,   # hi-res bitmap so it stays sharp at full page width
        background_color="white",
        colormap="RdPu",
        max_words=200,
        stopwords=stopword_set,
        collocations=False,
    ).generate(text)
    fig, ax = plt.subplots(figsize=(16, 8))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    ax.set_title(title, fontsize=16, fontweight="bold", pad=15)
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, fname))
    plt.close()

make_wc(full_text,    "Word Cloud — All Words (incl. stopwords)",   "04_wordcloud_all.png")
make_wc(content_text, "Word Cloud — Content Words (stopwords removed)", "05_wordcloud_no_stopwords.png")
print("  → 04_wordcloud_all.png saved")
print("  → 05_wordcloud_no_stopwords.png saved")


# ═══════════════════════════════════════════════════════════════════════════════
# 6. FILLER WORD ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════
print("\n[6/10] Filler word analysis…")

filler_counts = {w: freq_all.get(w, 0) for w in FILLERS}
filler_df = pd.DataFrame(
    sorted(filler_counts.items(), key=lambda x: x[1], reverse=True),
    columns=["filler_word", "count"]
)
filler_df["per_1000_words"] = filler_df["count"] / total_words * 1000
filler_df["pct_of_total"]   = filler_df["count"] / total_words * 100
filler_df.to_csv(os.path.join(TAB_DIR, "filler_word_counts.csv"), index=False)

top_fillers = filler_df[filler_df["count"] > 0].head(20)
fig, ax = plt.subplots(figsize=(12, 6))
ax.bar(top_fillers["filler_word"], top_fillers["per_1000_words"], color=BRAND_COLOR, alpha=0.85)
ax.set_xlabel("Filler / Hedge Word", fontsize=11)
ax.set_ylabel("Occurrences per 1,000 Words", fontsize=11)
ax.set_title("Filler & Hedge Word Usage — Love Island USA Season 4", fontsize=13, fontweight="bold")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, "06_filler_words.png"))
plt.close()
print("  → 06_filler_words.png saved")


# ═══════════════════════════════════════════════════════════════════════════════
# 7. PART-OF-SPEECH DISTRIBUTION
# ═══════════════════════════════════════════════════════════════════════════════
print("\n[7/10] POS tagging (this takes a few minutes)…")

# Sample up to 50k tokens for speed
sample = all_tokens[:50_000]
tagged = pos_tag(sample)

pos_category_counts = {cat: 0 for cat in POS_MAP}
pos_category_counts["Other"] = 0
tag_to_cat = {}
for cat, tags in POS_MAP.items():
    for t in tags:
        tag_to_cat[t] = cat

for word, tag in tagged:
    cat = tag_to_cat.get(tag, "Other")
    pos_category_counts[cat] = pos_category_counts.get(cat, 0) + 1

pos_df = pd.DataFrame(
    [(k, v, v/len(sample)*100) for k, v in pos_category_counts.items() if v > 0],
    columns=["POS_Category", "count", "percent"]
).sort_values("count", ascending=False)
pos_df.to_csv(os.path.join(TAB_DIR, "pos_summary.csv"), index=False)

fig, ax = plt.subplots(figsize=(10, 6))
ax.bar(pos_df["POS_Category"], pos_df["percent"], color=BRAND_COLOR, alpha=0.85)
ax.set_ylabel("Percentage of Tokens (%)", fontsize=11)
ax.set_title("Part-of-Speech Distribution — Love Island USA Season 4\n(sample: 50,000 tokens)",
             fontsize=12, fontweight="bold")
plt.xticks(rotation=30, ha="right")
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, "07_pos_distribution.png"))
plt.close()
print("  → 07_pos_distribution.png saved")


# ═══════════════════════════════════════════════════════════════════════════════
# 8. SENTIMENT ANALYSIS PER EPISODE
# ═══════════════════════════════════════════════════════════════════════════════
print("\n[8/10] Sentiment analysis…")

sent_rows = []
for _, row in df.iterrows():
    blob = TextBlob(row["clean"])  # full episode text (TextBlob handles this fine)
    sent_rows.append({
        "episode_num": row["episode_num"],
        "title":       row["title"],
        "polarity":    round(blob.sentiment.polarity, 4),
        "subjectivity":round(blob.sentiment.subjectivity, 4),
    })

sent_df = pd.DataFrame(sent_rows)
sent_df.to_csv(os.path.join(TAB_DIR, "sentiment_scores.csv"), index=False)

fig, axes = plt.subplots(2, 1, figsize=(14, 8), sharex=True)
axes[0].plot(sent_df["episode_num"], sent_df["polarity"], marker="o",
             color=BRAND_COLOR, linewidth=1.5, markersize=5)
axes[0].axhline(0, linestyle="--", color="gray", alpha=0.5)
axes[0].axhline(sent_df["polarity"].mean(), linestyle=":", color="blue",
                alpha=0.6, label=f"Mean: {sent_df['polarity'].mean():.3f}")
axes[0].set_ylabel("Polarity\n(−1 = negative, +1 = positive)", fontsize=10)
axes[0].legend(fontsize=9)
axes[0].set_title("Sentiment Analysis Across Episodes — Love Island USA Season 4",
                  fontsize=12, fontweight="bold")

axes[1].plot(sent_df["episode_num"], sent_df["subjectivity"], marker="s",
             color="#F4A261", linewidth=1.5, markersize=5)
axes[1].axhline(sent_df["subjectivity"].mean(), linestyle=":", color="blue",
                alpha=0.6, label=f"Mean: {sent_df['subjectivity'].mean():.3f}")
axes[1].set_ylabel("Subjectivity\n(0 = objective, 1 = subjective)", fontsize=10)
axes[1].set_xlabel("Episode Number", fontsize=11)
axes[1].legend(fontsize=9)

plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, "08_sentiment_per_episode.png"))
plt.close()
print("  → 08_sentiment_per_episode.png saved")


# ═══════════════════════════════════════════════════════════════════════════════
# 9. WORD LENGTH DISTRIBUTION
# ═══════════════════════════════════════════════════════════════════════════════
print("\n[9/10] Word length distribution…")

lengths = [len(w) for w in all_tokens]
length_counter = Counter(lengths)
max_len = min(max(lengths), 15)

fig, ax = plt.subplots(figsize=(12, 5))
xs = range(1, max_len + 1)
ys = [length_counter.get(x, 0) / total_words * 100 for x in xs]
ax.bar(xs, ys, color=BRAND_COLOR, alpha=0.85)
ax.axvline(np.mean(lengths), linestyle="--", color="gray",
           label=f"Mean length: {np.mean(lengths):.2f} chars")
ax.set_xlabel("Word Length (characters)", fontsize=11)
ax.set_ylabel("Percentage of All Words (%)", fontsize=11)
ax.set_title("Word Length Distribution — Love Island USA Season 4",
             fontsize=12, fontweight="bold")
ax.set_xticks(list(xs))
ax.legend(fontsize=10)
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, "09_word_length_distribution.png"))
plt.close()
print("  → 09_word_length_distribution.png saved")


# ═══════════════════════════════════════════════════════════════════════════════
# 10. VOCABULARY GROWTH CURVE
# ═══════════════════════════════════════════════════════════════════════════════
print("\n[10/10] Vocabulary growth curve…")

seen, cumulative_unique, cumulative_total = set(), [], []
for ep_tokens in df["tokens"]:
    for tok in ep_tokens:
        seen.add(tok)
        cumulative_unique.append(len(seen))
    cumulative_total.append(sum(len(t) for t in df["tokens"][:df["tokens"].tolist().index(ep_tokens)+1]))

# Plot against cumulative token count
cum_tokens = list(range(1, len(all_tokens) + 1))
seen2 = set()
cum_unique = []
for w in all_tokens:
    seen2.add(w)
    cum_unique.append(len(seen2))

# Sample every 500 points for a clean plot
step = 500
xs = cum_tokens[::step]
ys = cum_unique[::step]

fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(xs, ys, color=BRAND_COLOR, linewidth=2)
ax.set_xlabel("Cumulative Token Count", fontsize=11)
ax.set_ylabel("Cumulative Unique Word Types", fontsize=11)
ax.set_title("Vocabulary Growth Curve — Love Island USA Season 4\n(flattening = vocabulary saturation)",
             fontsize=12, fontweight="bold")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x/1000)}k"))
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x/1000)}k"))
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, "10_vocabulary_growth_curve.png"))
plt.close()
print("  → 10_vocabulary_growth_curve.png saved")


# ═══════════════════════════════════════════════════════════════════════════════
# 11. STATISTICAL TESTS (top-N coverage, Zipf fit, across-season trends)
# ═══════════════════════════════════════════════════════════════════════════════
print("\n[11/11] Statistical tests…")

stat_rows = []

# --- High-frequency concentration: cumulative coverage of the top-N words ------
sorted_counts = np.array([c for _, c in freq_all.most_common()])
cum_pct = np.cumsum(sorted_counts) / total_words * 100
coverage = {}
for n in (10, 50, 100, 1000):
    pct = cum_pct[min(n, len(cum_pct)) - 1]
    coverage[n] = pct
    stat_rows.append({"test": f"Cumulative % of tokens — top {n} words",
                      "statistic": f"{pct:.2f}%", "p_value": ""})

# --- Zipf's Law: log-log linear regression of frequency on rank ----------------
log_rank = np.log10(np.arange(1, len(sorted_counts) + 1))
log_freq = np.log10(sorted_counts)
zipf = stats.linregress(log_rank, log_freq)
stat_rows.append({"test": "Zipf regression slope (log freq ~ log rank)",
                  "statistic": f"{zipf.slope:.3f}", "p_value": f"{zipf.pvalue:.2e}"})
stat_rows.append({"test": "Zipf regression R²",
                  "statistic": f"{zipf.rvalue**2:.3f}", "p_value": ""})

# --- Across-season trends: does diversity / sentiment change over episodes? -----
def trend(x, y, label):
    x, y = np.asarray(x, float), np.asarray(y, float)
    mask = ~np.isnan(y)
    r, p = stats.pearsonr(x[mask], y[mask])
    rho, p_s = stats.spearmanr(x[mask], y[mask])
    stat_rows.append({"test": f"{label} vs episode — Pearson r",
                      "statistic": f"{r:.3f}", "p_value": f"{p:.3f}"})
    stat_rows.append({"test": f"{label} vs episode — Spearman rho",
                      "statistic": f"{rho:.3f}", "p_value": f"{p_s:.3f}"})
    return r, p

mtld_r,  mtld_p  = trend(lex_df["episode_num"],  lex_df["MTLD"],          "MTLD")
ttr_r,   ttr_p   = trend(lex_df["episode_num"],  lex_df["TTR"],           "TTR")
sent_r,  sent_p  = trend(sent_df["episode_num"], sent_df["polarity"],     "Sentiment polarity")

stats_df = pd.DataFrame(stat_rows)
stats_df.to_csv(os.path.join(TAB_DIR, "statistical_tests.csv"), index=False)
print(stats_df.to_string(index=False))


# ═══════════════════════════════════════════════════════════════════════════════
# FINAL SUMMARY PRINT
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("ANALYSIS COMPLETE")
print("="*60)
print(f"\nKey findings:")
print(f"  Total tokens          : {total_words:,}")
print(f"  Unique word types     : {unique_words:,}")
print(f"  Type-Token Ratio      : {ttr_overall:.4f}  (lower = more repetitive)")
print(f"  Avg word length       : {avg_word_len:.2f} characters")
print(f"  Avg MTLD              : {lex_df['MTLD'].mean():.2f}")
print(f"  Avg sentiment polarity: {sent_df['polarity'].mean():.3f}")
print(f"  Avg subjectivity      : {sent_df['subjectivity'].mean():.3f}")
print(f"  Top-10 word coverage  : {coverage[10]:.1f}% of all tokens")
print(f"  Top-100 word coverage : {coverage[100]:.1f}% of all tokens")
print(f"  Zipf slope / R²       : {zipf.slope:.3f} / {zipf.rvalue**2:.3f}")
print(f"  MTLD vs episode       : r={mtld_r:.3f}, p={mtld_p:.3f}  ({'sig.' if mtld_p < 0.05 else 'n.s.'})")
print(f"  Polarity vs episode   : r={sent_r:.3f}, p={sent_p:.3f}  ({'sig.' if sent_p < 0.05 else 'n.s.'})")
print(f"\nTop 10 most frequent words:")
for word, count in freq_all.most_common(10):
    print(f"  {word:<15} {count:>6,}  ({count/total_words*100:.2f}%)")
top_fillers_found = filler_df[filler_df["count"]>0].head(5)
print(f"\nTop 5 filler words (per 1,000 words):")
for _, r in top_fillers_found.iterrows():
    print(f"  {r['filler_word']:<15} {r['per_1000_words']:>6.1f}/1k")
print(f"\nAll figures → {FIG_DIR}/")
print(f"All tables  → {TAB_DIR}/")
print("="*60)
print("\nCopy these numbers into your paper template (paper_template.md).")
