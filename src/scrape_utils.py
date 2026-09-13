"""Shared HTTP fetch + article-text extraction used by every scraper module."""
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from config import HEADERS, REQUEST_DELAY_SECONDS


def get(url: str) -> requests.Response | None:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        time.sleep(REQUEST_DELAY_SECONDS)
        if resp.status_code == 200:
            return resp
        return None
    except requests.RequestException as e:
        print(f"  ! request failed for {url}: {e}")
        return None


def cached_fetch_html(url: str, cache_path: Path) -> str | None:
    if cache_path.exists():
        return cache_path.read_text(encoding="utf-8")
    resp = get(url)
    if resp is None:
        return None
    cache_path.write_text(resp.text, encoding="utf-8")
    return resp.text


def cached_fetch_binary(url: str, cache_path: Path) -> bytes | None:
    if cache_path.exists():
        return cache_path.read_bytes()
    resp = get(url)
    if resp is None:
        return None
    cache_path.write_bytes(resp.content)
    return resp.content


def extract_article_text(html: str) -> str:
    """Extract body paragraphs from the div#article container (falls back to
    div#content), dropping known UI paragraph classes (release time, article
    date, share widgets). Same template holds for statements, minutes,
    speeches, and testimony across 2018-2026 (verified by direct inspection)."""
    soup = BeautifulSoup(html, "lxml")
    container = soup.find(id="article") or soup.find(id="content")
    if container is None:
        return ""
    parts = []
    for p in container.find_all("p"):
        classes = p.get("class") or []
        if any(c in ("releaseTime", "article__time") for c in classes):
            continue
        text = p.get_text(" ", strip=True)
        if text:
            parts.append(text)
    return "\n\n".join(parts)


def extract_release_time(html: str) -> str | None:
    soup = BeautifulSoup(html, "lxml")
    tag = soup.find("p", class_="releaseTime")
    if tag:
        return tag.get_text(" ", strip=True).replace("For release at", "").strip()
    return None


def extract_article_date(html: str) -> str | None:
    """The 'article__time' paragraph holds the human-readable date, e.g.
    'August 28, 2026' - present on speech/testimony pages."""
    soup = BeautifulSoup(html, "lxml")
    tag = soup.find("p", class_="article__time")
    if tag:
        return tag.get_text(" ", strip=True)
    return None
