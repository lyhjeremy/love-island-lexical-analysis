# "Like, Literally, Love": A Lexical Analysis of Vocabulary Complexity in *Love Island USA* Season 4

**Author:** Jeremy Lee  
**Date:** June 2026  

---

## Abstract

This paper asks a simple question about a popular reality show: *how hard is its language?* Using the subtitle transcripts of all 38 episodes of *Love Island USA* Season 4 (2022) — a 224,815-word corpus of on-screen speech — we measure vocabulary richness, word frequency, reading level, and the size of vocabulary a viewer actually needs. The answer is consistent across every measure: the show's language is small, repetitive, and very easy. The 100 most common words make up 61% of everything said, and word frequency follows Zipf's Law almost perfectly (R² = 0.98). A viewer who knows only the **~1,250 most common word families understands 95% of the show** — less than half the ~3,000 word families normally needed for everyday English. By standard formulas the dialogue reads at roughly a **3rd–5th grade level**, and 98% of all words spoken come from the 3,000 most familiar words in English. The talk is emotional and opinion-heavy but lexically thin: adjectives make up only 8.4% of words, and a handful of discourse markers (*like*, *know*, *yeah*) do much of the work. The show presents its audience with a narrow, highly accessible slice of English.

**Keywords:** lexical diversity, reality television, vocabulary load, readability, corpus linguistics, *Love Island*

---

## Key Findings at a Glance

- **You need very few words to follow it.** Knowing the ~1,250 most frequent word families is enough to understand 95% of all speech in the show; ~2,550 gets you to 98%. For comparison, understanding everyday English normally takes about 3,000 word families for 95% coverage and 6,000–7,000 for 98%.
- **It reads at roughly a 3rd–5th grade level.** Flesch–Kincaid puts the dialogue at grade 2.8 and a reading-ease score of 90/100 ("very easy"). 97.9% of all words spoken are among the 3,000 most familiar English words — so the general public would have no trouble understanding it.
- **A tiny core of words dominates.** The top 10 words are 22.7% of all speech; the top 100 are 61%. Word frequencies follow Zipf's Law almost exactly (R² = 0.98).
- **Low lexical diversity.** Mean MTLD is 59.96, below the ~72 benchmark for ordinary spontaneous speech, and it does not change across the season.
- **Emotional but plain.** Speech is uniformly positive and highly subjective, yet adjectives are only 8.4% of words; meaning is carried by verbs and pronouns, not rich description.

---

## 1. Introduction

Reality television is one of the dominant media formats of the twenty-first century, and *Love Island* — a British format now franchised worldwide — is among the most-watched. Unlike scripted drama, it captures speech roughly as it happens: contestants live in a villa, are filmed continuously, and produce hours of unrehearsed conversation per episode. That makes it a useful, if unusual, window onto a particular register of casual spoken English.

The motivation is a well-known fact from applied linguistics. English has around 170,000 words in current use, an educated adult actively uses perhaps 20,000–35,000, and comfortable everyday conversation needs only about 3,000 high-frequency word families (Nation, 2001; Adolphs & Schmitt, 2003). If ordinary conversation already concentrates on so few words, informal television may narrow the range even further. This paper measures exactly how narrow.

**Research questions.**

1. How concentrated is word usage in *Love Island USA* Season 4, and how lexically diverse is the language overall?
2. How many words must a viewer know to follow the show, and how does that compare with the ~3,000-word benchmark for everyday English?
3. What reading/grade level is the dialogue, relative to the ~grade-5 standard used for materials aimed at the general public?
4. What kinds of words dominate (parts of speech, filler words), and what is the emotional tone across the season?

---

## 2. Background

**Measuring vocabulary diversity.** The simplest measure, the Type–Token Ratio (TTR) — unique words divided by total words — is intuitive but drops automatically as a text gets longer (Richards, 1987). Length-robust measures are preferred: Root TTR partly corrects for length, and the Measure of Textual Lexical Diversity (MTLD; McCarthy & Jarvis, 2010) tracks how long a stretch of text can run before its running TTR falls below a threshold. As a rule of thumb, spontaneous speech scores roughly 60–100 on MTLD.

**How many words you need.** Vocabulary researchers express difficulty as *coverage*: the share of a text you understand if you know its most frequent words. Knowing about 3,000 word families gives roughly 95% coverage of everyday spoken English, and 6,000–7,000 families gives about 98% (Adolphs & Schmitt, 2003; Nation, 2006). Television sits in the same range: Webb and Rodgers (2009) found that ~3,000 families cover 95% of TV dialogue and ~7,000 cover 98%. These figures give us a yardstick to compare *Love Island* against.

**Reading level.** Readability formulas convert sentence length and word length/syllables into a U.S. school grade. Flesch–Kincaid (Kincaid et al., 1975) and the Dale–Chall familiar-word approach (Dale & Chall, 1948) are standard. Public-facing materials — surveys, health information, news — are typically written at a 5th–8th grade level so the general population can follow them, with grade 5 often cited as a conservative target.

**Reality TV talk.** Prior work finds reality contestants mix private conversation with performance, since they know they are filmed, which can push speech toward safe, broadly understood language (Thornborrow & Morris, 2004), and toward hedges and vague "approximators" such as *like* and *kind of* (Channell, 1994; Fleiss, 2018). No published study has examined *Love Island USA* specifically; this paper begins to fill that gap.

---

## 3. Methods

**Data.** Transcripts of all 38 Season 4 episodes (aired July–August 2022 on Peacock) were scraped from Subslikescript.com and stored as a CSV. After cleaning, the corpus is 224,815 word tokens.

**Scope.** The source is closed-caption subtitle text with no speaker labels, so it mixes contestant dialogue (the large majority) with host/narrator voiceover and occasional on-screen lyrics. Because the voices cannot be separated automatically, results describe *Love Island USA* speech as broadcast, not any one contestant. This is revisited in Limitations.

**Processing.** Text was lowercased, stripped of subtitle dashes, metadata, and non-letters (apostrophes kept), and tokenised with NLTK; single-character tokens (*I*, *a*) were removed. Sentence counts use the raw text, before punctuation was stripped.

**Measures.** Word frequency and cumulative top-*N* coverage; Zipf's Law via regression of log frequency on log rank; lexical diversity (TTR, Root TTR, MTLD per episode); part-of-speech tags (NLTK); sentiment (TextBlob). For the two new questions: **vocabulary load** was computed by lemmatising tokens to approximate word families and finding how many families are needed for 80/90/95/98% coverage; **reading level** was computed with `textstat` (Flesch–Kincaid grade, Flesch Reading Ease, SMOG, and the Dale–Chall familiar-word list). Analyses use Python 3.12 (`nltk`, `textblob`, `textstat`, `scipy`, `pandas`, `matplotlib`).

---

## 4. Results

### 4.1 A small, repetitive core vocabulary

The corpus contains 224,815 word tokens but only 7,856 distinct word types (about 5,900 word families). Usage is heavily concentrated on a few words. The ten most frequent tokens are *you, to, like, the, and, it, that, know, yeah,* and *do* (Figure 1).

**Figure 1.** Top 50 most frequent words.  
`[output/figures/01_top50_words.png]`

The top 10 words alone are 22.7% of all speech, the top 50 are 48.7%, and the top 100 are 61.0%; a mere 1,000 word types cover 91.1% of everything said. This is a textbook Zipf distribution: regressing log-frequency on log-rank gives a slope of −1.45 with R² = 0.98 (Figure 2). In plain terms, a small number of words are repeated constantly while the long tail of rarer words barely appears.

**Figure 2.** Word frequency distribution and Zipf's Law check.  
`[output/figures/02_word_frequency_distribution.png]`

### 4.2 How many words do you actually need? (RQ2)

Figure 3 turns frequency into a practical question: if you learned the show's most common words first, how much would you understand? The curve rises steeply and then flattens. Knowing just the **250 most common word families covers 80%** of all speech, **~590 covers 90%**, **~1,250 covers 95%**, and **~2,550 covers 98%**.

**Figure 3.** How many words you need to follow the show.  
`[output/figures/11_vocabulary_coverage.png]`

Set against the benchmarks, the show is markedly easier than general English. Everyday spoken English needs roughly 3,000 word families for 95% coverage and 6,000–7,000 for 98% (Adolphs & Schmitt, 2003; Nation, 2006; Webb & Rodgers, 2009). *Love Island* reaches 95% with **fewer than half** that vocabulary (~1,250), and even 98% of the show (~2,550 families) falls *below* the 3,000-word everyday-English threshold. A learner or younger viewer with a modest vocabulary could follow almost all of it.

### 4.3 What reading level is the show? (RQ3)

By standard readability formulas the dialogue is very easy (Figure 4). Flesch–Kincaid places it at **grade 2.8** (per-episode range 2.3–3.7), the consensus grade estimate is **3.0**, and the Flesch Reading Ease score is **90.2 out of 100** — the "very easy" band, understandable by an average 11-year-old. Syllable-weighted formulas read slightly higher (SMOG ≈ 6.9), because the show does use the occasional long word (*relationship*, *definitely*), but every measure keeps the language at or near the grade-5 mark used for general-public materials — never in the difficult range.

**Figure 4.** Reading level (Flesch–Kincaid grade) vs. common benchmarks; other formulas place the show similarly low.  
`[output/figures/12_reading_level.png]`

The vocabulary evidence agrees: only **2.1% of all words spoken fall outside the 3,000 most familiar English words** (the Dale–Chall list known to fourth-graders). Put the other way, 97.9% of the show's words are among the most familiar in the language. Whether judged by sentence complexity or by word familiarity, *Love Island* is comfortably within reach of the general public.

### 4.4 Lexical diversity across the season

Per-episode MTLD averages 59.96 (range 40.42–81.93), below the ~72 benchmark for ordinary spontaneous speech — i.e., the show is *less* varied than normal conversation. Diversity does not drift over the season: neither MTLD nor TTR correlates with episode number (MTLD: r = −0.11, p = .52; TTR: r = 0.05, p = .78). Episode-to-episode bumps in Figure 5 track episode length and content (recaps, finales), not a trend.

**Figure 5.** Lexical diversity across episodes.  
`[output/figures/03_lexical_diversity_per_episode.png]`

### 4.5 Filler and hedge words

Filler and hedge words are pervasive (Figure 6). The most common are *like* (28.2 per 1,000 words), *know* (13.0), and *yeah* (12.5). *Like* alone is more than twice as frequent as any other filler and is the third most common word in the entire corpus. Across the 24 tracked filler/hedge words, these account for 9.3% of all tokens — roughly one word in eleven — doing social and discourse-organising work rather than conveying new information.

**Figure 6.** Filler and hedge word usage.  
`[output/figures/06_filler_words.png]`

### 4.6 What kinds of words: parts of speech

Verbs are the largest word class (24.5%), then nouns (17.9%), prepositions (15.4%), and pronouns (13.6%). Crucially, **adjectives are only 8.4%** of words (adverbs another 8.5%). Adjectives are the main carriers of description, so their scarcity — combined with heavy pronoun and verb use — marks a discourse built on relationships and actions ("I want to", "you said", "we talked") rather than vivid description.

**Figure 7.** Part-of-speech distribution.  
`[output/figures/07_pos_distribution.png]`

### 4.7 Emotional tone

Sentiment is uniformly positive: every one of the 38 episodes scores above zero on polarity (mean 0.174), with none near neutral. Subjectivity is high and stable (mean 0.556), confirming opinion- and feeling-heavy talk. There is no significant trend in tone across the season (r = −0.13, p = .44).

**Figure 8.** Sentiment across episodes.  
`[output/figures/08_sentiment_per_episode.png]`

Removing function words, the most frequent content words are *feel, love, good, think, want, going,* and *get* (Figure 9) — an emotion- and intention-focused vocabulary that fits the show's theme of romantic connection.

**Figure 9.** Word cloud of content words (function words removed).  
`[output/figures/05_wordcloud_no_stopwords.png]`

---

## 5. Discussion

Every measure points the same way: *Love Island USA* Season 4 runs on a small, familiar, repeated vocabulary. The headline numbers for a general reader are the two new ones. **You can follow 95% of the show on about 1,250 word families** — well under the ~3,000 needed for everyday English — and the dialogue reads at roughly a **third- to fifth-grade level**, with 98% of its words among the most familiar in English. This is a genuinely low-demand form of English.

That is unsurprising for spontaneous speech, which is always more restricted than writing, but the *degree* is striking, and the near-perfect Zipfian fit (R² = 0.98) shows the pattern is highly regular rather than a quirk of a few episodes. The texture of the talk explains the simplicity: it is emotional and personal (uniformly positive, highly subjective) but expressed through verbs, pronouns, intensifiers (*really*, *so*), and a thin band of evaluative adjectives (*good*, *amazing*, *crazy*) rather than descriptive variety. Discourse markers like *like* and *know* form a structural layer that organises talk and signals informality more than it adds content. This matches Biber et al.'s (1999) "involved production" — language under real-time pressure that foregrounds stance and connection over elaboration.

The implications cut two ways. For accessibility, the show is easy: learners of English, younger viewers, and the broad public can follow it almost completely, which is part of its mass appeal. For language exposure, that same narrowness means heavy viewing offers a repetitive linguistic diet — a useful point for anyone weighing such content as "language input." A natural next step is a controlled comparison with scripted television of similar theme to isolate how much scripting widens vocabulary.

---

## 6. Limitations

- **No speaker labels.** The subtitles mix contestant, host, and voiceover speech and many different contestants, so results describe the broadcast as a whole, not individuals. Speaker-diarised transcripts would be needed for person-level analysis.
- **Approximations.** "Word families" were approximated by automatic lemmatisation, and reading-level/POS/sentiment tools are imperfect on informal, punctuation-stripped speech; figures are best read as robust *relative* indicators rather than exact values. Readability formulas in particular disagree on the exact grade (≈3 to ≈7), though all place the show low.
- **Transcription quirks.** Captions can mis-hear names and slang, and contractions such as *gonna* split into fragments (*gon*/*na*); single-letter words (*I*, *a*) were removed in preprocessing.
- **Spread, not depth.** Coverage and diversity measure how *many* words appear, not how precisely or creatively they are used.

---

## 7. Conclusion

*Love Island USA* Season 4 is, linguistically, a small and welcoming world. Across 224,815 words we find a tiny high-frequency core (top 100 words = 61% of speech), low lexical diversity (MTLD 59.96), and a strongly positive, subjective tone carried by verbs rather than description. Most concretely: a viewer needs only about **1,250 common word families to understand 95%** of the show, and the dialogue sits at roughly a **third- to fifth-grade reading level**, with 98% of its words among the 3,000 most familiar in English. Whether that reflects the nature of unscripted emotional speech, the cast, or the demands of being on camera is a question for future work — but the language of the villa, for all its drama, asks very little of its audience.

---

## References

Adolphs, S., & Schmitt, N. (2003). Lexical coverage of spoken discourse. *Applied Linguistics, 24*(4), 425–438.

Biber, D., Johansson, S., Leech, G., Conrad, S., & Finegan, E. (1999). *Longman grammar of spoken and written English*. Pearson.

Channell, J. (1994). *Vague language*. Oxford University Press.

Dale, E., & Chall, J. S. (1948). A formula for predicting readability. *Educational Research Bulletin, 27*(1), 11–28.

Fleiss, R. (2018). Vague language in reality television: Hedging as social performance. *Journal of Sociolinguistics, 22*(3), 301–324.

Kincaid, J. P., Fishburne, R. P., Rogers, R. L., & Chissom, B. S. (1975). *Derivation of new readability formulas for Navy enlisted personnel*. Naval Technical Training Command.

McCarthy, P. M., & Jarvis, S. (2010). MTLD, vocd-D, and HD-D: A validation study of sophisticated approaches to lexical diversity assessment. *Behavior Research Methods, 42*(2), 381–392.

Nation, I. S. P. (2001). *Learning vocabulary in another language*. Cambridge University Press.

Nation, I. S. P. (2006). How large a vocabulary is needed for reading and listening? *Canadian Modern Language Review, 63*(1), 59–82.

Richards, B. (1987). Type/token ratios: What do they really tell us? *Journal of Child Language, 14*(2), 201–209.

Thornborrow, J., & Morris, D. (2004). Gossip as strategy: The management of talk about others on reality TV show *Big Brother*. *Journal of Sociolinguistics, 8*(2), 246–271.

Webb, S., & Rodgers, M. P. H. (2009). The vocabulary demands of television programs. *Language Learning, 59*(2), 335–366.

---

## Appendix A — Vocabulary Load and Reading Level

*Vocabulary load: word families needed for each coverage level (lemmatised); raw word types shown for comparison.*

| Coverage of show | Word families needed | Raw word types needed |
|---|---|---|
| 80% | 250 | 326 |
| 90% | 592 | 860 |
| 95% | 1,249 | 1,902 |
| 98% | 2,554 | 3,911 |

*Benchmark for everyday/spoken English: ~3,000 families for 95%, ~6,000–7,000 for 98% (Adolphs & Schmitt, 2003; Nation, 2006; Webb & Rodgers, 2009).*

*Reading level of the full corpus:*

| Measure | Value | Interpretation |
|---|---|---|
| Flesch–Kincaid Grade | 2.8 | ~3rd grade |
| Consensus grade (textstat) | 3.0 | ~3rd grade |
| Flesch Reading Ease | 90.2 | "very easy" (90–100) |
| SMOG Index | 6.9 | ~7th grade (syllable-weighted) |
| % words outside 3,000 familiar list | 2.1% | 97.9% of words are highly familiar |
| Per-episode FK grade range | 2.3–3.7 | consistently easy |

## Appendix B — Corpus Statistics by Episode

*Tokens = post-cleaning token count; Types = unique word types.*

| Ep | Tokens | Types | TTR | MTLD | | Ep | Tokens | Types | TTR | MTLD |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 8650 | 1273 | 0.147 | 59.21 |  | 20 | 5973 | 1076 | 0.180 | 60.86 |
| 2 | 7062 | 1108 | 0.157 | 43.24 |  | 21 | 6031 | 961 | 0.159 | 59.93 |
| 3 | 5930 | 995 | 0.168 | 61.90 |  | 22 | 8294 | 1130 | 0.136 | 55.45 |
| 4 | 5722 | 936 | 0.164 | 53.98 |  | 23 | 5656 | 910 | 0.161 | 64.50 |
| 5 | 5415 | 1158 | 0.214 | 81.93 |  | 24 | 6174 | 1227 | 0.199 | 60.16 |
| 6 | 5317 | 920 | 0.173 | 62.15 |  | 25 | 5171 | 947 | 0.183 | 58.74 |
| 7 | 5447 | 953 | 0.175 | 59.85 |  | 26 | 5617 | 979 | 0.174 | 64.88 |
| 8 | 6468 | 950 | 0.147 | 56.49 |  | 27 | 6337 | 1032 | 0.163 | 53.28 |
| 9 | 5038 | 956 | 0.190 | 67.12 |  | 28 | 4675 | 896 | 0.192 | 67.98 |
| 10 | 6087 | 1009 | 0.166 | 55.08 |  | 29 | 4883 | 909 | 0.186 | 56.19 |
| 11 | 5961 | 1259 | 0.211 | 62.39 |  | 30 | 5244 | 1286 | 0.245 | 55.98 |
| 12 | 5009 | 998 | 0.199 | 65.01 |  | 31 | 5959 | 970 | 0.163 | 55.62 |
| 13 | 5411 | 887 | 0.164 | 54.69 |  | 32 | 5167 | 983 | 0.190 | 61.26 |
| 14 | 4750 | 918 | 0.193 | 63.41 |  | 33 | 4790 | 920 | 0.192 | 54.69 |
| 15 | 5368 | 922 | 0.172 | 51.89 |  | 34 | 4763 | 923 | 0.194 | 61.50 |
| 16 | 5275 | 997 | 0.189 | 54.35 |  | 35 | 7932 | 1044 | 0.132 | 43.82 |
| 17 | 5407 | 1276 | 0.236 | 64.92 |  | 36 | 6007 | 1240 | 0.206 | 40.42 |
| 18 | 5249 | 910 | 0.173 | 76.77 |  | 37 | 6034 | 1068 | 0.177 | 67.58 |
| 19 | 5176 | 996 | 0.192 | 71.49 |  | 38 | 11366 | 1415 | 0.125 | 69.80 |

## Appendix C — Statistical Tests

*Trend correlations are across the 38 episodes (n = 38); Zipf regression is over all ranked word types. Full per-row data (top-100 words, per-episode sentiment, filler counts) available on request.*

| Test | Statistic | p-value |
|---|---|---|
| Top 10 / 50 / 100 / 1,000 words — % of all tokens | 22.7% / 48.7% / 61.0% / 91.1% | — |
| Zipf regression slope (log freq ~ log rank) | −1.453 | < .001 |
| Zipf regression R² | 0.981 | — |
| MTLD vs. episode — Pearson r | −0.107 | .521 |
| TTR vs. episode — Pearson r | 0.048 | .775 |
| Sentiment polarity vs. episode — Pearson r | −0.129 | .441 |

---

*Analysis performed using Python 3.12. Scripts (`analyze_love_island.py`, `analyze_vocab_level.py`), the cleaned corpus, and all output tables/figures are available on request.*
