import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
DB_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/smart_factory")

def generate_mock_data():
    np.random.seed(42)
    random.seed(42)
    
    today = datetime.now().date()
    dates = [today - timedelta(days=i) for i in range(30, -1, -1)]
    
    # 1. Production Logs (for OEE)
    production_data = []
    for d in dates:
        for line in ['Line 1', 'Line 2']:
            for shift in ['Morning', 'Afternoon', 'Night']:
                product = random.choice(['Product A', 'Product B', 'Product C'])
                planned_time = 480 # 8 hours
                
                # Introduce an anomaly for yesterday on Line 2
                is_anomaly = (d == today - timedelta(days=1)) and (line == 'Line 2')
                
                downtime = random.randint(10, 40)
                if is_anomaly:
                    downtime = 126
                    downtime_reason = 'Equipment stop'
                else:
                    downtime_reason = random.choice(['Setup', 'Minor stop', 'Maintenance', None])
                
                operating_time = planned_time - downtime
                
                ideal_cycle_time = random.uniform(40, 50)
                if is_anomaly:
                    ideal_cycle_time = 47.0 # slower cycle
                
                max_possible = int((operating_time * 60) / ideal_cycle_time)
                total_count = int(max_possible * random.uniform(0.85, 0.98))
                
                defect_rate = random.uniform(0.01, 0.05)
                defect_count = int(total_count * defect_rate)
                good_count = total_count - defect_count
                
                production_data.append({
                    'log_date': d,
                    'line_id': line,
                    'shift': shift,
                    'product_id': product,
                    'planned_production_time': planned_time,
                    'operating_time': operating_time,
                    'ideal_cycle_time_sec': ideal_cycle_time,
                    'total_count': total_count,
                    'good_count': good_count,
                    'defect_count': defect_count,
                    'downtime_minutes': downtime,
                    'downtime_reason': downtime_reason
                })
    df_production = pd.DataFrame(production_data)
    
    # 2. Shipment Logs
    shipment_data = []
    for d in dates:
        num_shipments = random.randint(50, 100)
        for i in range(num_shipments):
            promised_date = d + timedelta(days=random.randint(1, 3))
            
            # Anomaly for current week
            is_anomaly = (d >= today - timedelta(days=5)) and random.random() < 0.2
            
            if is_anomaly:
                actual_date = promised_date + timedelta(days=random.randint(1, 4))
                status = 'DELAYED'
                reason = random.choice(['Carrier X pickup delay', 'Warehouse A picking backlog'])
            else:
                actual_date = promised_date
                status = 'DELIVERED'
                reason = None
                
            shipment_data.append({
                'shipment_id': f"SHP-{d.strftime('%Y%m%d')}-{i:04d}",
                'order_date': d,
                'promised_delivery_date': promised_date,
                'actual_delivery_date': actual_date,
                'carrier': random.choice(['Carrier X', 'Carrier Y', 'Carrier Z']),
                'warehouse_id': random.choice(['Warehouse A', 'Warehouse B']),
                'destination': f"Region {random.randint(1, 5)}",
                'status': status,
                'delayed_reason': reason
            })
    df_shipment = pd.DataFrame(shipment_data)
    
    # 3. Picking Logs
    picking_data = []
    for d in dates:
        for w in ['Warehouse A', 'Warehouse B']:
            for z in ['Zone 1', 'Zone 2', 'Zone 3']:
                labor_hours = random.uniform(7.5, 8.5)
                base_productivity = 150 # units per hour
                
                # Zone 3 anomaly in Warehouse A
                if w == 'Warehouse A' and z == 'Zone 3' and d >= today - timedelta(days=5):
                    base_productivity = 90
                
                picked_units = int(base_productivity * labor_hours * random.uniform(0.9, 1.1))
                picked_lines = int(picked_units * 0.4)
                
                picking_data.append({
                    'task_date': d,
                    'warehouse_id': w,
                    'zone_id': z,
                    'worker_id': f"WKR-{random.randint(100, 150)}",
                    'picked_lines': picked_lines,
                    'picked_units': picked_units,
                    'labor_hours': labor_hours
                })
    df_picking = pd.DataFrame(picking_data)
    
    # 4. Quality Inspections
    quality_data = []
    for d in dates:
        for line in ['Line 1', 'Line 2']:
            for product in ['Product A', 'Product B', 'Product C']:
                total_inspected = random.randint(500, 2000)
                defect_rate = random.uniform(0.01, 0.03)
                
                if d == today - timedelta(days=2) and product == 'Product C':
                    defect_rate = 0.08 # Defect spike
                
                defect_count = int(total_inspected * defect_rate)
                passed_count = total_inspected - defect_count
                
                quality_data.append({
                    'inspection_date': d,
                    'line_id': line,
                    'product_id': product,
                    'lot_number': f"LOT-{d.strftime('%m%d')}-{random.randint(10,99)}",
                    'total_inspected': total_inspected,
                    'passed_count': passed_count,
                    'defect_count': defect_count,
                    'defect_type': random.choice(['Scratch', 'Dimension Error', 'Color Mismatch', 'Packaging Error']) if defect_count > 0 else None
                })
    df_quality = pd.DataFrame(quality_data)
    
    return df_production, df_shipment, df_picking, df_quality

def seed_database():
    print(f"Connecting to database: {DB_URL}")
    engine = create_engine(DB_URL)
    
    # Read schema.sql and execute
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    
    from sqlalchemy import text
    with engine.connect() as conn:
        print("Executing schema.sql...")
        # Split by semicolon and execute
        for statement in schema_sql.split(';'):
            if statement.strip():
                conn.execute(text(statement))
        conn.commit()
        
    print("Generating mock data...")
    df_prod, df_ship, df_pick, df_qual = generate_mock_data()
    
    print("Inserting data into database...")
    df_prod.to_sql('production_logs', engine, if_exists='append', index=False)
    df_ship.to_sql('shipment_logs', engine, if_exists='append', index=False)
    df_pick.to_sql('picking_logs', engine, if_exists='append', index=False)
    df_qual.to_sql('quality_inspections', engine, if_exists='append', index=False)
    
    print("Database seeding completed successfully.")

if __name__ == "__main__":
    seed_database()
