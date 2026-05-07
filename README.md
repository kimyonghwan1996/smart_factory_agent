# Logistics & Smart Factory Data Agent

A MVP for a natural-language data agent that provides operational analytics, KPI tracking, and root-cause analysis for logistics and smart factory environments.

## Architecture
- **Backend**: FastAPI + Python (Pandas, SQLAlchemy, OpenAI API)
- **Frontend**: Streamlit + Plotly
- **Database**: PostgreSQL

## Setup Instructions

### 1. Database Setup
Ensure you have PostgreSQL running. Create a database named `smart_factory` (or match the `DATABASE_URL` in `.env`).

### 2. Environment Variables
Copy `.env.example` to `.env` and fill in your details:
```bash
cp .env.example .env
```
Make sure to provide your `OPENAI_API_KEY` and the correct `DATABASE_URL`.

### 3. Install Dependencies
It's recommended to use a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Initialize Data
Generate the schema and seed the mock data:
```bash
python data/seed_data.py
```

### 5. Run the Application
Start the FastAPI Backend:
```bash
uvicorn backend.main:app --reload --port 8000
```

In a new terminal, start the Streamlit Frontend:
```bash
streamlit run frontend/app.py
```

## Features
- **KPI Analysis**: Calculates OEE, Delivery Delay, Picking Productivity, Defect Rate.
- **Natural Language Query**: Automatically translates questions into safe SELECT-only SQL queries.
- **Root Cause Analysis**: Diagnoses why KPIs drop.
- **Data Visualization**: Generates Plotly charts.
- **Daily Reporting**: Automatically summarizes daily operations.
