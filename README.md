# 물류 및 스마트 팩토리 데이터 에이전트

물류 및 스마트 팩토리 환경에서 운영 분석, KPI 추적 및 근본 원인 분석을 제공하는 자연어 기반 데이터 에이전트의 MVP입니다.

## 아키텍처
- **백엔드**: FastAPI + Python (Pandas, SQLAlchemy, OpenAI API)
- **프론트엔드**: Streamlit + Plotly
- **데이터베이스**: PostgreSQL

## 설치 및 설정 가이드

### 1. 데이터베이스 설정
PostgreSQL이 실행 중인지 확인하세요. `smart_factory`라는 데이터베이스를 생성하거나 `.env`의 `DATABASE_URL`에 맞게 설정하세요.

### 2. 환경 변수
`.env.example`을 `.env`로 복사한 후 내용을 채우세요:
```bash
cp .env.example .env
```
`OPENAI_API_KEY`와 올바른 `DATABASE_URL`을 반드시 입력하세요.

### 3. 의존성 설치
가상환경 사용을 권장합니다:
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 4. 데이터 초기화
스키마 생성 및 샘플(모의) 데이터 적재:
```bash
python data/seed_data.py
```

### 5. 애플리케이션 실행
FastAPI 백엔드를 시작합니다:
```bash
uvicorn backend.main:app --reload --port 8000
```

새 터미널에서 Streamlit 프론트엔드를 실행합니다:
```bash
streamlit run frontend/app.py
```

## 기능
- **KPI 분석**: OEE, 납기 지연(Delivery Delay), 피킹 생산성(Picking Productivity), 불량률(Defect Rate)을 계산합니다.
- **자연어 질의**: 사용자의 질문을 안전한 SELECT 전용 SQL 쿼리로 자동 변환합니다.
- **근본 원인 분석**: KPI 하락 원인을 진단합니다.
- **데이터 시각화**: Plotly 차트를 생성합니다.
- **일일 리포트**: 운영 요약을 자동으로 생성합니다.

