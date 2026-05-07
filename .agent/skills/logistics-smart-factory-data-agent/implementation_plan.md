# Logistics & Smart Factory Data Agent MVP Implementation Plan

This plan details the architecture, directory structure, and implementation steps to build the Logistics & Smart Factory Data Agent MVP.

## User Review Required

> [!IMPORTANT]
> Please review the proposed architecture, feature scope, and data models below. Once approved, I will begin implementing the project structure and code.

## Open Questions

> [!WARNING]
> 1. Do you have a preferred OpenAI model (e.g., `gpt-4o`, `gpt-4-turbo`) you want to use? I'll set it as an environment variable in `.env.example`.
> 2. Are you using Docker for PostgreSQL, or do you have a local instance running? (I'll provide setup instructions assuming local/docker PostgreSQL).
> 3. Should the daily report be generated on-demand via Streamlit, or as a scheduled background task? I'll implement it as an on-demand feature in Streamlit for the MVP.

## Proposed Architecture

- **Frontend**: Streamlit for a chat-based interface with dynamic chart rendering (Plotly) and KPI selection.
- **Backend**: FastAPI for handling requests, communicating with the LLM (OpenAI API), executing safe queries, and calculating KPIs.
- **Database**: PostgreSQL storing mock operational data (logistics, production, quality).
- **Agent**: An OpenAI function-calling / custom Python orchestration that:
  - Classifies intent (query vs. report vs. KPI).
  - Generates SELECT-only SQL against a predefined schema.
  - Queries DB and analyzes data using Pandas.
  - Computes KPIs (OEE, 출고 지연률, 피킹 생산성, 불량률) and generates root-cause analysis.
  - Generates Plotly charts.

## Directory Structure

We will create the following structure in `c:\Users\PC\PycharmProjects\smart_factory_agent`:

```text
smart_factory_agent/
├── .env.example                # Example environment variables
├── requirements.txt            # Python dependencies
├── README.md                   # Setup and execution instructions
├── data/
│   ├── schema.sql              # PostgreSQL tables creation
│   └── seed_data.py            # Script to generate sample CSV/SQL data
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── database.py             # DB connection and safe query execution
│   ├── agent.py                # LLM agent orchestration (OpenAI API)
│   ├── kpi_calculator.py       # Functions for OEE, Defect Rate, etc.
│   ├── sql_generator.py        # Logic for creating SELECT-only SQL
│   └── config.py               # Settings management
└── frontend/
    └── app.py                  # Streamlit application UI
```

## Proposed Changes

### Database Setup
#### [NEW] [schema.sql](file:///c:/Users/PC/PycharmProjects/smart_factory_agent/data/schema.sql)
Tables for `production_logs`, `shipment_logs`, `picking_logs`, and `quality_inspections` containing necessary columns for KPI calculation (e.g., planned_time, operating_time, total_count, good_count, defect_count, shipment_status, picking_time, worker_id).

#### [NEW] [seed_data.py](file:///c:/Users/PC/PycharmProjects/smart_factory_agent/data/seed_data.py)
A Python script using pandas to generate mock data and populate the database or create CSV files.

### Backend implementation
#### [NEW] [main.py](file:///c:/Users/PC/PycharmProjects/smart_factory_agent/backend/main.py)
FastAPI endpoints:
- `POST /api/chat`: Receives natural language questions and returns analysis/SQL/data.
- `GET /api/kpi/{kpi_name}`: Returns calculated KPI value for a given metric.
- `GET /api/report/daily`: Generates the daily operations report.

#### [NEW] [database.py](file:///c:/Users/PC/PycharmProjects/smart_factory_agent/backend/database.py)
Manages the SQLAlchemy/psycopg2 connection to PostgreSQL. Enforces read-only execution by rejecting `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, etc.

#### [NEW] [agent.py](file:///c:/Users/PC/PycharmProjects/smart_factory_agent/backend/agent.py)
The core OpenAI agent that coordinates intent classification, SQL generation, execution, and summarization.

#### [NEW] [kpi_calculator.py](file:///c:/Users/PC/PycharmProjects/smart_factory_agent/backend/kpi_calculator.py)
Implements formulas for:
- OEE (Availability * Performance * Quality)
- 출고 지연률 (Delayed / Total Shipments)
- 피킹 생산성 (Picks / Labor Hours)
- 불량률 (Defective / Total Units)

#### [NEW] [sql_generator.py](file:///c:/Users/PC/PycharmProjects/smart_factory_agent/backend/sql_generator.py)
System prompts and definitions passed to OpenAI for converting natural language to `SELECT` SQL statements based on the known DB schema.

### Frontend implementation
#### [NEW] [app.py](file:///c:/Users/PC/PycharmProjects/smart_factory_agent/frontend/app.py)
Streamlit UI to allow users to interact with the agent. Features:
- Chat interface.
- Sidebar for KPI selection and Daily Report generation.
- Display of generated SQL, data tables, and Plotly charts.

### Configuration
#### [NEW] [.env.example](file:///c:/Users/PC/PycharmProjects/smart_factory_agent/.env.example)
Database connection strings and OpenAI API Key template.

#### [NEW] [requirements.txt](file:///c:/Users/PC/PycharmProjects/smart_factory_agent/requirements.txt)
Dependencies: `fastapi`, `uvicorn`, `streamlit`, `pandas`, `plotly`, `openai`, `psycopg2-binary`, `sqlalchemy`, `python-dotenv`.

#### [NEW] [README.md](file:///c:/Users/PC/PycharmProjects/smart_factory_agent/README.md)
Instructions on how to install requirements, set up the DB, run the seed script, start FastAPI, and start Streamlit.

## Verification Plan

### Automated Tests
(None initially for MVP, focus on manual verification of core workflows)

### Manual Verification
1. Setup DB and verify sample data is populated successfully using `seed_data.py`.
2. Start FastAPI and test the API endpoints using Swagger UI (`/docs`).
3. Start Streamlit and run the following scenarios:
   - Ask "What was the OEE for yesterday?" and verify the result, SQL used, and chart.
   - Ask "Why did the defect rate increase?" and verify the root-cause analysis logic.
   - Try to ask "Delete the production logs table" and verify the safe-query constraints block it.
   - Generate the daily operations report and verify its structure.
