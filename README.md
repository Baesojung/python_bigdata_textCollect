# OpenAI 뉴스 수집기 및 분석기

이 프로젝트는 OpenAI에 대한 최신 뉴스 및 리뷰를 수집, 분석 및 시각화하기 위한 Python 기반 파이프라인입니다. 다양한 RSS 피드에서 기사를 가져오고, 감성 분석을 수행하며, 핵심 주제를 강조하기 위해 워드 클라우드를 생성합니다.

## 프로젝트 구조

- `collect_openai_news.py`: OpenAI의 공식 RSS 피드에서 직접 뉴스를 가져오는 간단한 스크립트입니다.
- `collect_openai_open_reviews.py`: 검색 쿼리를 기반으로 여러 뉴스 소스(Google 뉴스, Bing 뉴스)에서 기사를 수집합니다.
- `analyze_openai_articles.py`: 수집된 기사를 분석하여 감성 분석을 수행하고 워드 클라우드를 생성합니다.
- `openai_articles.csv`: `collect_openai_open_reviews.py`의 기본 출력 파일로, 수집된 기사를 포함합니다.
- `openai_articles_with_sentiment.csv`: 감성 분석의 결과물로, 감성 점수에 대한 열이 추가되어 있습니다.
- `openai_wordcloud.png`: 기사 제목과 요약에서 생성된 워드 클라우드 이미지입니다.
- `sentiment_summary.json`: 감성 분석 요약이 포함된 JSON 파일입니다.
- `openai_insights.md`: 분석에 대한 인사이트와 요약이 포함된 마크다운 파일입니다.

## 작동 방식

프로세스는 두 가지 주요 단계로 나뉩니다:

1.  **수집**: `collect_openai_open_reviews.py` 스크립트는 지난 30일 동안의 기사를 다양한 뉴스 피드에서 가져옵니다. 쿼리(기본값: "OpenAI")로 필터링하고 CSV 파일(`openai_articles.csv`)에 저장합니다.

2.  **분석**: `analyze_openai_articles.py` 스크립트는 CSV 파일을 읽고 텍스트를 정리한 다음 다음을 수행합니다:
    -   기사 제목과 요약에서 워드 클라우드(`openai_wordcloud.png`)를 생성합니다.
    -   기사에 대한 감성 분석을 수행하여 긍정, 부정, 중립 및 복합 점수를 계산합니다.
    -   감성 점수와 함께 기사를 새 CSV 파일(`openai_articles_with_sentiment.csv`)에 저장합니다.
    -   감성 분포 요약이 포함된 JSON 파일(`sentiment_summary.json`)을 생성합니다.

## 설치

먼저 Python 3이 설치되어 있어야 합니다. 그런 다음 pip를 사용하여 필요한 라이브러리를 설치할 수 있습니다:

```bash
pip install requests feedparser pandas matplotlib wordcloud vaderSentiment
```

## 사용법

터미널에서 스크립트를 실행할 수 있습니다.

### 1. 기사 수집

OpenAI에 대한 최신 기사를 수집하려면 다음 명령을 실행하십시오:

```bash
python collect_openai_open_reviews.py
```

그러면 동일한 디렉토리에 `openai_articles.csv`라는 파일이 생성됩니다. 출력 파일 및 기타 옵션을 사용자 지정할 수 있습니다:

```bash
python collect_openai_open_reviews.py --output my_articles.csv --format json --days 15
```

### 2. 기사 분석

기사가 있으면 분석할 수 있습니다:

```bash
python analyze_openai_articles.py
```

그러면 `openai_articles.csv`를 입력으로 사용하고 분석 파일(`openai_wordcloud.png`, `openai_articles_with_sentiment.csv`, `sentiment_summary.json`)을 생성합니다. 다른 입력 및 출력 파일을 지정할 수도 있습니다:

```bash
python analyze_openai_articles.py --input my_articles.csv --wordcloud-output my_wordcloud.png
```

분석을 실행한 후 `openai_insights.md` 파일에서 결과 요약을 검토할 수 있습니다.