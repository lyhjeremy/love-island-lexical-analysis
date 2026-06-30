"""
Love Island USA — Season 4 Transcript Scraper  (v3 — Selenium)
==============================================================
Uses a real Chrome browser to bypass the CAPTCHA challenge.

REQUIREMENTS:
  1. Google Chrome installed (https://www.google.com/chrome/)
  2. pip install selenium webdriver-manager beautifulsoup4

USAGE:
  python scrape_love_island_s4.py

OUTPUTS:
  love_island_s4_transcripts.csv   — all episodes in one CSV
  love_island_s4_txt/              — one .txt file per episode
"""

import time, os, re, csv
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ── Config ────────────────────────────────────────────────────────────────────
BASE       = "https://subslikescript.com"
SERIES_URL = f"{BASE}/series/Love_Island-8819906"
SEASON     = 4
TOTAL_EPS  = 38
# Write into the project's data/ folder (this file lives in scripts/).
_ROOT      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_CSV = os.path.join(_ROOT, "data", "love_island_s4_transcripts.csv")
OUTPUT_DIR = os.path.join(_ROOT, "data", "love_island_s4_txt")

# How long (seconds) to wait for each page to pass the CAPTCHA and fully load.
# Increase this if you get timeouts on a slow connection.
PAGE_LOAD_WAIT  = 12   # seconds to wait for challenge to clear
BETWEEN_PAGES   = 3    # polite delay between episode requests

# ── Browser setup ─────────────────────────────────────────────────────────────
def make_driver(headless=False):
    """
    headless=False  → you'll see a Chrome window open (recommended for first run)
    headless=True   → invisible browser (may trigger CAPTCHA more easily)
    """
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1280,900")
    # Make Chrome look like a normal user
    opts.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    )
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)

    service = Service(ChromeDriverManager().install())
    driver  = webdriver.Chrome(service=service, options=opts)

    # Mask webdriver fingerprint
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"}
    )
    return driver


# ── Wait for CAPTCHA to clear ─────────────────────────────────────────────────
def wait_for_real_page(driver, timeout=PAGE_LOAD_WAIT):
    """
    After loading a URL, wait until the challenge is gone and real content loads.
    We detect this by waiting for the <title> to no longer say 'Loading...'.
    """
    end = time.time() + timeout
    while time.time() < end:
        title = driver.title
        if title and title.strip().lower() not in ("loading...", ""):
            return True
        time.sleep(0.5)
    return False  # timed out


# ── Discover episode links from series page ───────────────────────────────────
def discover_episodes(driver):
    print(f"Loading series index: {SERIES_URL}")
    driver.get(SERIES_URL)
    loaded = wait_for_real_page(driver)

    if not loaded:
        print("  [!] Series index page didn't load past challenge. Using fallback URL list.")
        return []

    soup = BeautifulSoup(driver.page_source, "html.parser")
    pattern = re.compile(r"/season-4/episode-\d+", re.I)

    episodes = []
    for a in soup.find_all("a", href=pattern):
        href    = a["href"]
        ep_match = re.search(r"/episode-(\d+)", href)
        ep_num  = int(ep_match.group(1)) if ep_match else None
        title   = a.get_text(strip=True) or f"Episode {ep_num}"
        full_url = BASE + href if href.startswith("/") else href
        episodes.append({"episode_num": ep_num, "title": title, "url": full_url})

    episodes.sort(key=lambda x: x["episode_num"] or 0)
    print(f"  Found {len(episodes)} episode links on index page.")
    return episodes


# ── Fallback: season page for a specific season number ───────────────────────
def discover_from_season_page(driver):
    season_url = f"{SERIES_URL}/season-{SEASON}"
    print(f"Trying season page: {season_url}")
    driver.get(season_url)
    wait_for_real_page(driver)

    soup    = BeautifulSoup(driver.page_source, "html.parser")
    pattern = re.compile(r"/season-4/episode-\d+", re.I)

    episodes = []
    for a in soup.find_all("a", href=pattern):
        href     = a["href"]
        ep_match = re.search(r"/episode-(\d+)", href)
        ep_num   = int(ep_match.group(1)) if ep_match else None
        title    = a.get_text(strip=True) or f"Episode {ep_num}"
        full_url = BASE + href if href.startswith("/") else href
        episodes.append({"episode_num": ep_num, "title": title, "url": full_url})

    episodes.sort(key=lambda x: x["episode_num"] or 0)
    print(f"  Found {len(episodes)} episode links on season page.")
    return episodes


# ── Extract transcript from loaded episode page ───────────────────────────────
def extract_transcript(soup):
    # Try known class names for the transcript container
    for cls_pattern in ("full-script", "transcript", "script-content", "script-body", "article-content"):
        tag = soup.find(attrs={"class": re.compile(cls_pattern, re.I)})
        if tag:
            text = tag.get_text(separator="\n", strip=True)
            if len(text) > 200:
                return text

    # Fallback: largest text block on page
    best, best_len = None, 0
    for div in soup.find_all(["div", "article", "section"]):
        t = div.get_text(strip=True)
        if len(t) > best_len:
            best, best_len = div, len(t)
    if best and best_len > 200:
        return best.get_text(separator="\n", strip=True)

    return ""


def safe_fname(ep_num, title):
    clean = re.sub(r'[\\/*?:"<>|]', "", title).strip().replace(" ", "_")[:60]
    return f"s4e{ep_num:02d}_{clean}.txt"


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Starting Chrome browser...")
    print("(A Chrome window will open — don't close it)\n")
    driver = make_driver(headless=False)

    try:
        # Step 1: discover episode URLs
        episodes = discover_episodes(driver)

        if not episodes:
            episodes = discover_from_season_page(driver)

        if not episodes:
            # Hard fallback: we know ep1 and ep34 slugs; probe the rest
            print("\nCould not auto-discover links. Building URL list from known pattern...")
            # Known slugs
            known_slugs = {
                1:  "episode-1-Episode_41",
                34: "episode-34-Episode_434",
            }
            episodes = []
            for n in range(1, TOTAL_EPS + 1):
                slug = known_slugs.get(n, f"episode-{n}")
                episodes.append({
                    "episode_num": n,
                    "title": f"Episode {n}",
                    "url": f"{SERIES_URL}/season-{SEASON}/{slug}",
                })

        print(f"\n{'='*60}")
        print(f"Scraping {len(episodes)} episodes")
        print(f"Estimated time: ~{len(episodes) * (PAGE_LOAD_WAIT + BETWEEN_PAGES) / 60:.0f}–{len(episodes) * (PAGE_LOAD_WAIT*1.5 + BETWEEN_PAGES) / 60:.0f} min")
        print(f"{'='*60}\n")

        results = []
        failed  = []

        for ep in episodes:
            ep_num = ep["episode_num"]
            url    = ep["url"]
            print(f"  [S4E{ep_num:02d}] Loading: {url}")

            driver.get(url)
            loaded = wait_for_real_page(driver, timeout=PAGE_LOAD_WAIT)

            if not loaded:
                print(f"    ✗ Page didn't load (still on challenge). Skipping.")
                failed.append(ep_num)
                results.append({**ep, "word_count": 0, "transcript": "[CHALLENGE NOT PASSED]"})
                time.sleep(BETWEEN_PAGES)
                continue

            # Give JS a moment to finish rendering
            time.sleep(1.5)

            final_url = driver.current_url
            soup      = BeautifulSoup(driver.page_source, "html.parser")

            # Get page title
            h1 = soup.find("h1")
            title = h1.get_text(strip=True) if h1 else (soup.title.string or ep["title"])

            transcript = extract_transcript(soup)
            words      = len(transcript.split()) if transcript else 0

            if words < 50:
                print(f"    ✗ Transcript not found ({words} words). Page: {driver.title}")
                failed.append(ep_num)
            else:
                print(f"    ✓ '{title}' — {words:,} words")

            results.append({
                "episode_num": ep_num,
                "title":       title,
                "url":         final_url,
                "word_count":  words,
                "transcript":  transcript,
            })

            # Save .txt
            with open(os.path.join(OUTPUT_DIR, safe_fname(ep_num, title)), "w", encoding="utf-8") as f:
                f.write(f"Love Island USA — Season 4, Episode {ep_num}\n")
                f.write(f"Title:  {title}\n")
                f.write(f"Source: {final_url}\n")
                f.write("=" * 60 + "\n\n")
                f.write(transcript)

            time.sleep(BETWEEN_PAGES)

    finally:
        driver.quit()

    # Write CSV
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["episode_num", "title", "url", "word_count", "transcript"])
        writer.writeheader()
        writer.writerows(results)

    # Summary
    good  = [r for r in results if r["word_count"] >= 50]
    total = sum(r["word_count"] for r in results)
    print(f"\n{'='*60}")
    print(f"DONE — {len(good)}/{len(episodes)} episodes scraped successfully")
    print(f"Total words: {total:,}")
    print(f"CSV  → {OUTPUT_CSV}")
    print(f"TXTs → {OUTPUT_DIR}/")
    if failed:
        print(f"\nFailed episodes: {failed}")
        print("You can re-run to retry them.")
    print("=" * 60)


if __name__ == "__main__":
    main()
