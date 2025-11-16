# analyze_openai_articles.py 구성 설명

## 개요
- 스크립트 위치: `collect_openai/analyze_openai_articles.py`
- 역할: `openai_articles.csv`를 읽어 텍스트 정제 → 워드클라우드 이미지 생성 → VADER 기반 감성 분석 → 결과 CSV/JSON 저장
- 주요 의존성: `pandas`, `matplotlib`, `wordcloud`, `vaderSentiment`

## 주요 처리 흐름
1. **백엔드 설정 (`matplotlib.use("Agg")`)**
   - GUI 환경이 아닐 때도 이미지 저장이 가능하도록 Agg 백엔드로 강제 설정

2. **한글 폰트 검색 (`find_korean_font`)**
   - 시스템 폰트 중 AppleSDGothicNeo, NanumGothic 등 선호 목록을 탐색
   - `ttf`, `ttc` 폰트 파일 경로를 순회하며 매칭, 없으면 `None`
   - 결과는 워드클라우드 생성 시 `font_path`로 전달되어 한글 깨짐 방지

3. **텍스트 정제 (`clean_text`, `load_articles`)**
   - HTML 태그 제거, 엔티티 디코딩
   - CSV 파일의 `title`, `summary`를 결합한 `combined_text` 컬럼 생성
   - 경로는 `--input` 인자로 제어하며 기본값은 `openai_articles.csv`

4. **워드클라우드 생성 (`build_wordcloud`)**
   - 기본 스톱워드에 `OpenAI`, `ChatGPT` 등을 추가해 불필요한 단어 제거
   - `WordCloud` 객체를 이용해 1600×1000 이미지 생성 후 저장
   - 결과 경로는 `--wordcloud-output` 인자로 조정 (기본 `openai_wordcloud.png`)

5. **감성 분석 (`analyze_sentiment`)**
   - `SentimentIntensityAnalyzer` 로 문서별 감성 점수 계산 (pos/neu/neg/compound)
   - `compound` 값을 기준으로 부정(-1 ~ -0.05), 중립(-0.05 ~ 0.05), 긍정(0.05 ~ 1) 레이블 부여
   - 비율 계산 후 `average_compound`를 포함한 요약 dict 반환
   - 확장된 DataFrame은 `--sentiment-output`(기본 `openai_articles_with_sentiment.csv`)에 저장
   - 요약 dict는 JSON으로 직렬화 (`--summary-output`, 기본 `sentiment_summary.json`)

6. **명령줄 인자 (`parse_args`)**
   - `--input`, `--wordcloud-output`, `--sentiment-output`, `--summary-output` 네 인자를 제공
   - 사용자 지정 경로를 통해 다양한 입력/출력을 쉽게 제어 가능

7. **엔트리 포인트 (`main`)**
   - 인자 파싱 → 입력 파일 존재 여부 검사 → DataFrame 로드
   - 한글 폰트 미탐색 시 경고 출력 후 기본 폰트로 진행
   - 워드클라우드 생성 → 감성 분석 실행 → 결과 저장
   - 완료 메시지를 출력해 생성된 파일 경로 안내

## 실행 예시
```bash
python analyze_openai_articles.py \
  --input my_articles.csv \
  --wordcloud-output my_wordcloud.png \
  --sentiment-output sentiment_scored.csv \
  --summary-output sentiment_summary.json
```
- 위 명령은 사용자 정의 CSV를 분석해 맞춤 경로로 이미지와 결과 파일을 저장

## 활용 팁
- **폰트 문제 해결**: 한글 폰트가 없을 경우 `font_path`가 `None`이 되므로 워드클라우드 한글이 깨질 수 있다. 시스템에 한글 폰트를 설치하거나 `--wordcloud-output` 생성 후 별도 시각화 도구로 확인
- **감성 분석 미세 조정**: VADER는 영문에 최적화되어 있으므로 필요 시 한국어 감성 사전을 추가하거나 다른 라이브러리(KoNLPy 등)로 확장 가능
- **분석 재활용**: `sentiment_summary.json`과 `openai_articles_with_sentiment.csv`를 기반으로 BI 도구, 대시보드 등에 연동해 감성 추이를 모니터링할 수 있음
