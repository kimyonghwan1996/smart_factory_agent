-- Logistics & Smart Factory Data Schema

CREATE TABLE IF NOT EXISTS production_logs (
    log_id SERIAL PRIMARY KEY,
    log_date DATE NOT NULL,
    line_id VARCHAR(50) NOT NULL,
    shift VARCHAR(10) NOT NULL,
    product_id VARCHAR(50),
    planned_production_time INT, -- in minutes
    operating_time INT, -- in minutes
    ideal_cycle_time_sec DECIMAL(5,2), -- in seconds
    total_count INT,
    good_count INT,
    defect_count INT,
    downtime_minutes INT,
    downtime_reason VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS shipment_logs (
    shipment_id VARCHAR(50) PRIMARY KEY,
    order_date DATE,
    promised_delivery_date DATE,
    actual_delivery_date DATE,
    carrier VARCHAR(100),
    warehouse_id VARCHAR(50),
    destination VARCHAR(100),
    status VARCHAR(20), -- 'DELIVERED', 'DELAYED', 'IN_TRANSIT'
    delayed_reason VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS picking_logs (
    task_id SERIAL PRIMARY KEY,
    task_date DATE NOT NULL,
    warehouse_id VARCHAR(50),
    zone_id VARCHAR(50),
    worker_id VARCHAR(50),
    picked_lines INT,
    picked_units INT,
    labor_hours DECIMAL(4,2)
);

CREATE TABLE IF NOT EXISTS quality_inspections (
    inspection_id SERIAL PRIMARY KEY,
    inspection_date DATE NOT NULL,
    line_id VARCHAR(50),
    product_id VARCHAR(50),
    lot_number VARCHAR(100),
    total_inspected INT,
    passed_count INT,
    defect_count INT,
    defect_type VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS inventory (
    inventory_id SERIAL PRIMARY KEY,
    warehouse_id VARCHAR(50),
    sku_id VARCHAR(50),
    on_hand_qty INT,
    allocated_qty INT,
    minimum_stock_level INT
);
