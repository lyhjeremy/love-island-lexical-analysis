"""
Debug script — run this if the main scraper fails.
    python step1_debug.py
Paste the full output back to Claude.
"""
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://subslikescript.com/",
}

session = requests.Session()
session.headers.update(HEADERS)

# ── Test 1: Series index page ─────────────────────────────────────────────────
url = "https://subslikescript.com/series/Love_Island-8819906"
print(f"[TEST 1] Fetching index: {url}")
r = session.get(url, timeout=20)
print(f"  Status: {r.status_code}  |  Final URL: {r.url}")
soup = BeautifulSoup(r.text, "html.parser")
links = soup.find_all("a", href=True)
print(f"  Total <a> tags: {len(links)}")
print("  All hrefs:")
for a in links:
    print(f"    {a['href']!r:70}  text={a.get_text(strip=True)[:40]!r}")
print("\n  Page title:", soup.title.string if soup.title else "N/A")
print("  Headings:")
for h in soup.find_all(["h1","h2","h3","h4"])[:10]:
    print(f"    <{h.name}>: {h.get_text(strip=True)[:80]}")
print("\n  Raw HTML (first 4000 chars):")
print(r.text[:4000])

# ── Test 2: One known episode page ───────────────────────────────────────────
print("\n" + "="*70)
ep_url = "https://subslikescript.com/series/Love_Island-8819906/season-4/episode-1-Episode_41"
print(f"[TEST 2] Fetching episode: {ep_url}")
r2 = session.get(ep_url, timeout=20)
print(f"  Status: {r2.status_code}  |  Final URL: {r2.url}")
soup2 = BeautifulSoup(r2.text, "html.parser")
print("  Page title:", soup2.title.string if soup2.title else "N/A")
print("  <article> tags:", [(t.get("class"), len(t.get_text())) for t in soup2.find_all("article")])
print("  <div> classes (first 20):", [" ".join(d.get("class",[])) for d in soup2.find_all("div") if d.get("class")][:20])
print("  Raw HTML (first 3000 chars):")
print(r2.text[:3000])
