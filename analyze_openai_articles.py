#!/usr/bin/env python3
"""Generate a word cloud and run sentiment analysis for OpenAI-related articles."""

from __future__ import annotations

import argparse
import html
import re
from pathlib import Path
from typing import Dict, Tuple

import matplotlib
import pandas as pd
from matplotlib import font_manager
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from wordcloud import STOPWORDS, WordCloud

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402  (Agg backend 설정 후 import)


def find_korean_font() -> str | None:
    """Return the path to a font that supports Korean characters if available."""
    preferred = [
        "AppleSDGothicNeo",
        "AppleGothic",
        "NanumGothic",
        "Malgun Gothic",
        "Noto Sans CJK KR",
    ]
    ttf_fonts = font_manager.findSystemFonts(fontpaths=None, fontext="ttf")
    ttc_fonts = font_manager.findSystemFonts(fontpaths=None, fontext="ttc")
    all_fonts = ttf_fonts + ttc_fonts

    for font_name in preferred:
        lower_target = font_name.lower()
        for path in all_fonts:
            if lower_target in Path(path).stem.lower():
                return path
    return None


def clean_text(text: str) -> str:
    """Remove HTML tags and decode entities for cleaner text."""
    no_html = re.sub(r"<[^>]+>", " ", text)
    return html.unescape(no_html)


def load_articles(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    df["combined_text"] = (df["title"].fillna("") + " " + df["summary"].fillna("")).map(
        clean_text
    )
    return df


def build_wordcloud(text: str, output_path: Path, font_path: str | None) -> None:
    stopwords = STOPWORDS.union({"OpenAI", "ChatGPT", "openai"})
    wc = WordCloud(
        width=1600,
        height=1000,
        background_color="white",
        stopwords=stopwords,
        font_path=font_path,
        collocations=False,
    ).generate(text)

    plt.figure(figsize=(12, 7))
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.tight_layout(pad=0)
    plt.savefig(output_path, dpi=300)
    plt.close()


def analyze_sentiment(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, float]]:
    analyzer = SentimentIntensityAnalyzer()
    scores = df["combined_text"].map(analyzer.polarity_scores)
    df = df.assign(
        compound=[score["compound"] for score in scores],
        positive=[score["pos"] for score in scores],
        neutral=[score["neu"] for score in scores],
        negative=[score["neg"] for score in scores],
    )
    df["sentiment_label"] = pd.cut(
        df["compound"],
        bins=[-1.0, -0.05, 0.05, 1.0],
        labels=["negative", "neutral", "positive"],
    )
    sentiment_counts = df["sentiment_label"].value_counts(normalize=True).to_dict()
    sentiment_counts["average_compound"] = df["compound"].mean()
    return df, sentiment_counts


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a word cloud and sentiment summary from OpenAI article data."
    )
    parser.add_argument(
        "--input",
        default="openai_articles.csv",
        help="CSV 파일 경로 (기본값: %(default)s)",
    )
    parser.add_argument(
        "--wordcloud-output",
        default="openai_wordcloud.png",
        help="워드클라우드 이미지 저장 경로 (기본값: %(default)s)",
    )
    parser.add_argument(
        "--sentiment-output",
        default="openai_articles_with_sentiment.csv",
        help="감성점수 컬럼이 포함된 CSV 출력 경로 (기본값: %(default)s)",
    )
    parser.add_argument(
        "--summary-output",
        default="sentiment_summary.json",
        help="감성 통계 요약을 저장할 JSON 경로 (기본값: %(default)s)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    if not input_path.exists():
        raise SystemExit(f"입력 파일을 찾을 수 없습니다: {input_path}")

    df = load_articles(input_path)

    font_path = find_korean_font()
    if font_path is None:
        print("경고: 한글 폰트를 찾지 못해 기본 폰트를 사용합니다. 일부 문자가 깨질 수 있습니다.")

    combined_text = " ".join(df["combined_text"].tolist())
    build_wordcloud(combined_text, Path(args.wordcloud_output), font_path)

    df_with_scores, summary = analyze_sentiment(df)
    df_with_scores.to_csv(args.sentiment_output, index=False)
    pd.Series(summary).to_json(args.summary_output, force_ascii=False, indent=2)

    print(
        "워드클라우드와 감성 분석이 완료되었습니다.\n"
        f"- 워드클라우드: {args.wordcloud_output}\n"
        f"- 감성 분석 CSV: {args.sentiment_output}\n"
        f"- 감성 요약 JSON: {args.summary_output}"
    )


if __name__ == "__main__":
    main()
