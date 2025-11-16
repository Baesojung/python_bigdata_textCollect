# collect_openai_open_reviews.py 구성 설명

## 개요
- 스크립트 위치: `collect_openai/collect_openai_open_reviews.py`
- 역할: 최근 1개월 이내 OpenAI 관련 뉴스·리뷰 헤드라인을 RSS 피드에서 수집하고 CSV/JSON으로 저장
- 주요 의존성: `requests`, `feedparser`, `argparse`, `csv`, `json`

## 모듈 구성
1. **상수 정의 (`DEFAULT_FEEDS`)**
   - OpenAI 키워드를 포함하는 Google News, Bing News RSS URL을 기본으로 제공
   - 사용자가 `--feeds` 인자를 통해 덮어쓸 수 있어 확장성 확보

2. **`fetch_feed(url, timeout=15)` (`collect_openai_open_reviews.py:21`)**
   - `requests.get`으로 RSS 원문을 가져온 뒤 `feedparser.parse`로 파싱
   - HTTP 오류 발생 시 `raise_for_status()`로 즉시 예외 처리
   - 타임아웃 기본값 15초로 설정해 지연 시 무한 대기 방지

3. **`normalize_timestamp(entry)` (`collect_openai_open_reviews.py:28`)**
   - RSS 항목의 `published_parsed` 또는 `updated_parsed`를 읽어 `datetime` 객체로 변환
   - 타임스탬프가 없는 항목은 `None`을 반환해 이후 필터링에서 제외
   - 모든 날짜를 UTC 기준으로 통일

4. **`collect_entries(feeds, min_results, days, query)` (`collect_openai_open_reviews.py:37`)**
   - 핵심 수집 루프
   - `cutoff`: 현재 시각 - `days`일을 계산해 최신 항목만 유지
   - 각 RSS 피드를 순회하며
     - `normalize_timestamp`로 날짜 확인 후 기간 외 기사 제외
     - 제목과 요약에 `query`(대소문자 무시)가 포함되는 항목만 통과
     - `(제목, 링크)` 조합으로 중복 제거
     - 수집된 항목을 ISO 포맷 타임스탬프를 포함한 dict로 저장
   - 결과 리스트를 발행일 기준 내림차순 정렬
   - 수집 결과가 `min_results` 미만이면 `RuntimeError`로 실패 안내

5. **`save_results(results, output_path, fmt)` (`collect_openai_open_reviews.py:73`)**
   - `fmt`가 `json`일 경우 UTF-8 JSON 파일을 생성 (`ensure_ascii=False`로 비영어권 문자 지원)
   - 기본값 `csv`일 때는 `title`, `link`, `source`, `published`, `summary` 헤더를 포함하는 CSV 저장

6. **`parse_args()` (`collect_openai_open_reviews.py:87`)**
   - CLI 인자 정의
     - `--query`: 키워드 필터 (기본값 `OpenAI`)
     - `--min-results`: 필요한 최소 기사 수 (기본 20건)
     - `--days`: 수집 기간 (기본 30일)
     - `--format`: 출력 형식 (`csv` 또는 `json`)
     - `--output`: 저장 파일명 (기본 `openai_articles.csv`)
     - `--feeds`: RSS 리스트 덮어쓰기

7. **`main()` (`collect_openai_open_reviews.py:119`)**
   - 인자 파싱 → `collect_entries` 호출
   - 예외 발생 시 메시지를 포함하여 종료 (`SystemExit`)
   - 수집된 결과를 `save_results`로 저장 후 완료 메시지 출력

## 실행 예시
```bash
python collect_openai_open_reviews.py \
  --days 20 \
  --min-results 30 \
  --format json \
  --output openai_recent.json
```
- 위 명령은 최근 20일 자료 중 최소 30건을 확보할 때까지 수집하고 JSON으로 저장

## 활용 팁
- **피드 추가**: 특정 언론사의 RSS를 추가하려면 `--feeds https://example.com/rss ...`로 지정
- **중복 필터**: 제목과 링크를 동시에 비교해 비슷한 기사라도 URL이 다르면 별도 기사로 인정되므로 필요 시 후처리에서 추가 정제가 가능
- **에러 처리**: `RuntimeError`가 발생하면 `--feeds` 확대, `--days` 연장, `--min-results` 축소 등을 통해 수집 조건을 조정
