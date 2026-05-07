SCHEMA_DEFINITION = """
The database is PostgreSQL. You must generate valid, SELECT-only PostgreSQL queries.

TABLE: production_logs
- log_id (SERIAL PRIMARY KEY)
- log_date (DATE)
- line_id (VARCHAR: 'Line 1', 'Line 2')
- shift (VARCHAR: 'Morning', 'Afternoon', 'Night')
- product_id (VARCHAR)
- planned_production_time (INT, minutes)
- operating_time (INT, minutes)
- ideal_cycle_time_sec (DECIMAL, seconds)
- total_count (INT)
- good_count (INT)
- defect_count (INT)
- downtime_minutes (INT)
- downtime_reason (VARCHAR)

TABLE: shipment_logs
- shipment_id (VARCHAR PRIMARY KEY)
- order_date (DATE)
- promised_delivery_date (DATE)
- actual_delivery_date (DATE)
- carrier (VARCHAR)
- warehouse_id (VARCHAR)
- destination (VARCHAR)
- status (VARCHAR: 'DELIVERED', 'DELAYED', 'IN_TRANSIT')
- delayed_reason (VARCHAR)

TABLE: picking_logs
- task_id (SERIAL PRIMARY KEY)
- task_date (DATE)
- warehouse_id (VARCHAR)
- zone_id (VARCHAR)
- worker_id (VARCHAR)
- picked_lines (INT)
- picked_units (INT)
- labor_hours (DECIMAL)

TABLE: quality_inspections
- inspection_id (SERIAL PRIMARY KEY)
- inspection_date (DATE)
- line_id (VARCHAR)
- product_id (VARCHAR)
- lot_number (VARCHAR)
- total_inspected (INT)
- passed_count (INT)
- defect_count (INT)
- defect_type (VARCHAR)

TABLE: inventory
- inventory_id (SERIAL PRIMARY KEY)
- warehouse_id (VARCHAR)
- sku_id (VARCHAR)
- on_hand_qty (INT)
- allocated_qty (INT)
- minimum_stock_level (INT)
"""

def get_sql_prompt(user_question: str) -> str:
    prompt = f"""
You are an expert data analyst for a Logistics and Smart Factory. 
Your task is to translate the user's natural language question into a safe, SELECT-only SQL query based on the following schema:

{SCHEMA_DEFINITION}

IMPORTANT RULES:
1. ONLY return the SQL query, nothing else (no markdown tags, no explanation).
2. The query MUST be read-only (SELECT only).
3. If the user asks for data "yesterday" or "recently", use appropriate date filtering or order by date descending and limit. Assume the current date is the most recent date in the tables. 

User Question: {user_question}
SQL Query:
"""
    return prompt
