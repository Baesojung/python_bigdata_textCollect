#!/usr/bin/env python3
"""Collect recent online articles or reviews about OpenAI."""

from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timedelta, timezone
from typing import Dict, Iterable, List, Optional

import feedparser
import requests

# RSS feeds tuned for OpenAI coverage in the last month.
DEFAULT_FEEDS: List[str] = [
    "https://news.google.com/rss/search?q=%22OpenAI%22+when:1m&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=%22OpenAI%22+review&hl=en-US&gl=US&ceid=US:en",
    "https://www.bing.com/news/search?q=\"OpenAI\"&format=RSS",
]


def fetch_feed(url: str, timeout: int = 15) -> feedparser.FeedParserDict:
    """Return the parsed feed for the supplied URL."""
    response = requests.get(url, timeout=timeout, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()
    return feedparser.parse(response.content)


def normalize_timestamp(entry: feedparser.FeedParserDict) -> Optional[datetime]:
    """Extract the publication datetime for a feed entry if available."""
    struct = entry.get("published_parsed") or entry.get("updated_parsed")
    if struct is None:
        return None
    return datetime(*struct[:6], tzinfo=timezone.utc)


def collect_entries(
    feeds: Iterable[str],
    min_results: int,
    days: int,
    query: str,
) -> List[Dict[str, str]]:
    """Gather entries across feeds, keeping only recent, unique items."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    unique: Dict[str, Dict[str, str]] = {}

    for feed_url in feeds:
        parsed = fetch_feed(feed_url)
        source = parsed.feed.get("title", feed_url)

        for entry in parsed.entries:
            published = normalize_timestamp(entry)
            if published is None or published < cutoff:
                continue
            title = entry.get("title", "").strip()
            summary = entry.get("summary", "").strip()
            link = entry.get("link", "").strip()
            if query.lower() not in title.lower() and query.lower() not in summary.lower():
                continue
            if not title:
                continue
            key = (title.lower(), link.lower())
            if key in unique:
                continue
            unique[key] = {
                "title": title,
                "link": link,
                "source": source,
                "published": published.isoformat(),
                "summary": summary,
            }

    results = list(unique.values())
    results.sort(key=lambda item: item["published"], reverse=True)

    if len(results) < min_results:
        raise RuntimeError(
            f"Only {len(results)} unique results collected (min required: {min_results}). "
            "Consider adding more feeds or adjusting filters."
        )
    return results


def save_results(results: List[Dict[str, str]], output_path: str, fmt: str) -> None:
    """Persist results to the chosen format."""
    if fmt == "json":
        with open(output_path, "w", encoding="utf-8") as handle:
            json.dump(results, handle, ensure_ascii=False, indent=2)
    else:
        fieldnames = ["title", "link", "source", "published", "summary"]
        with open(output_path, "w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Collect recent OpenAI-related news headlines or reviews."
    )
    parser.add_argument(
        "--query",
        default="OpenAI",
        help="Keyword filter applied to titles and summaries (default: %(default)s).",
    )
    parser.add_argument(
        "--min-results",
        type=int,
        default=20,
        help="Minimum number of unique items to gather before succeeding (default: %(default)s).",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Look back window in days (default: %(default)s).",
    )
    parser.add_argument(
        "--format",
        choices=("csv", "json"),
        default="csv",
        help="File format for saved results (default: %(default)s).",
    )
    parser.add_argument(
        "--output",
        default="openai_articles.csv",
        help="Path to save collected results (default: %(default)s).",
    )
    parser.add_argument(
        "--feeds",
        nargs="*",
        default=DEFAULT_FEEDS,
        help="Override the feed list; default sources target OpenAI coverage.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        entries = collect_entries(
            feeds=args.feeds,
            min_results=args.min_results,
            days=args.days,
            query=args.query,
        )
    except Exception as exc:  # pragma: no cover - CLI surface
        raise SystemExit(f"Collection failed: {exc}") from exc

    save_results(entries, args.output, args.format)
    print(f"Collected {len(entries)} items. Saved to {args.output}.")


if __name__ == "__main__":
    main()
