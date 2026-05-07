from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

from .agent import process_chat_query
from .kpi_calculator import (
    calculate_oee,
    calculate_delivery_delay_rate,
    calculate_picking_productivity,
    calculate_defect_rate
)

app = FastAPI(title="Logistics & Smart Factory Data Agent MVP")

class ChatRequest(BaseModel):
    question: str

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    result = process_chat_query(request.question)
    return result

@app.get("/api/kpi/{kpi_name}")
async def get_kpi(kpi_name: str, date: Optional[str] = None):
    try:
        if kpi_name.lower() == "oee":
            return calculate_oee(date)
        elif kpi_name.lower() == "delivery_delay":
            return calculate_delivery_delay_rate(date)
        elif kpi_name.lower() == "picking_productivity":
            return calculate_picking_productivity(date)
        elif kpi_name.lower() == "defect_rate":
            return calculate_defect_rate(date)
        else:
            raise HTTPException(status_code=400, detail="Unknown KPI")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/report/daily")
async def get_daily_report():
    # Simple aggregation of KPIs for yesterday
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    try:
        oee = calculate_oee(yesterday)
        delivery = calculate_delivery_delay_rate(yesterday)
        picking = calculate_picking_productivity(yesterday)
        defect = calculate_defect_rate(yesterday)
        
        report = {
            "date": yesterday,
            "kpis": {
                "oee": oee,
                "delivery_delay": delivery,
                "picking_productivity": picking,
                "defect_rate": defect
            },
            "summary": "This is a consolidated view of yesterday's operations. Check the individual KPIs to spot any anomalies."
        }
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
