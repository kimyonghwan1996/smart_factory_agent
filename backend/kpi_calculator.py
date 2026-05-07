import pandas as pd
from datetime import datetime, timedelta
from .database import execute_read_only_query

def calculate_oee(date_str: str = None) -> dict:
    """Calculates Average OEE for a given date."""
    if not date_str:
        date_str = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
    query = f"""
        SELECT 
            SUM(planned_production_time) as total_planned,
            SUM(operating_time) as total_operating,
            SUM(ideal_cycle_time_sec * total_count / 60.0) as total_ideal_operating,
            SUM(good_count) as total_good,
            SUM(total_count) as total_produced
        FROM production_logs
        WHERE log_date = '{date_str}'
    """
    df = execute_read_only_query(query)
    if df.empty or pd.isna(df['total_planned'][0]):
        return {"error": "No data found for the given date."}
        
    row = df.iloc[0]
    availability = row['total_operating'] / row['total_planned'] if row['total_planned'] > 0 else 0
    performance = row['total_ideal_operating'] / row['total_operating'] if row['total_operating'] > 0 else 0
    quality = row['total_good'] / row['total_produced'] if row['total_produced'] > 0 else 0
    
    oee = availability * performance * quality
    
    return {
        "date": date_str,
        "availability": round(availability * 100, 2),
        "performance": round(performance * 100, 2),
        "quality": round(quality * 100, 2),
        "oee": round(oee * 100, 2),
        "formula": "OEE = Availability × Performance × Quality"
    }

def calculate_delivery_delay_rate(date_str: str = None) -> dict:
    """Calculates shipping delay rate for a given order date."""
    if not date_str:
        date_str = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
    query = f"""
        SELECT 
            COUNT(*) as total_shipments,
            SUM(CASE WHEN status = 'DELAYED' THEN 1 ELSE 0 END) as delayed_shipments
        FROM shipment_logs
        WHERE order_date = '{date_str}'
    """
    df = execute_read_only_query(query)
    if df.empty or pd.isna(df['total_shipments'][0]) or df['total_shipments'][0] == 0:
        return {"error": "No shipment data found for the given date."}
        
    total = int(df['total_shipments'][0])
    delayed = int(df['delayed_shipments'][0])
    delay_rate = delayed / total if total > 0 else 0
    
    return {
        "date": date_str,
        "total_shipments": total,
        "delayed_shipments": delayed,
        "delay_rate": round(delay_rate * 100, 2),
        "formula": "Shipping Delay Rate = Delayed Shipments / Total Shipments"
    }

def calculate_picking_productivity(date_str: str = None) -> dict:
    """Calculates overall picking productivity (units per labor hour)."""
    if not date_str:
        date_str = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
    query = f"""
        SELECT 
            SUM(picked_units) as total_units,
            SUM(labor_hours) as total_hours
        FROM picking_logs
        WHERE task_date = '{date_str}'
    """
    df = execute_read_only_query(query)
    if df.empty or pd.isna(df['total_units'][0]):
        return {"error": "No picking data found for the given date."}
        
    units = int(df['total_units'][0])
    hours = float(df['total_hours'][0])
    productivity = units / hours if hours > 0 else 0
    
    return {
        "date": date_str,
        "total_picked_units": units,
        "total_labor_hours": round(hours, 2),
        "productivity_units_per_hour": round(productivity, 2),
        "formula": "Picking Productivity = Picked Units / Labor Hours"
    }

def calculate_defect_rate(date_str: str = None) -> dict:
    """Calculates defect rate for quality inspections."""
    if not date_str:
        date_str = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
    query = f"""
        SELECT 
            SUM(defect_count) as total_defects,
            SUM(total_inspected) as total_inspected
        FROM quality_inspections
        WHERE inspection_date = '{date_str}'
    """
    df = execute_read_only_query(query)
    if df.empty or pd.isna(df['total_inspected'][0]) or df['total_inspected'][0] == 0:
        return {"error": "No inspection data found for the given date."}
        
    defects = int(df['total_defects'][0])
    inspected = int(df['total_inspected'][0])
    defect_rate = defects / inspected if inspected > 0 else 0
    
    return {
        "date": date_str,
        "total_defects": defects,
        "total_inspected": inspected,
        "defect_rate": round(defect_rate * 100, 2),
        "formula": "Defect Rate = Defective Units / Total Produced Units"
    }
