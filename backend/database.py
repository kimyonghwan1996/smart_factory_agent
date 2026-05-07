from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from .config import config
import pandas as pd
import re

engine = create_engine(config.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def is_safe_query(query: str) -> bool:
    """Ensure the query is SELECT-only and does not contain dangerous keywords."""
    query_upper = query.upper()
    dangerous_keywords = ['INSERT', 'UPDATE', 'DELETE', 'DROP', 'ALTER', 'TRUNCATE', 'MERGE', 'GRANT', 'REVOKE']
    
    # Check if any dangerous keyword is present as an isolated word
    for keyword in dangerous_keywords:
        if re.search(r'\b' + keyword + r'\b', query_upper):
            return False
            
    if not query_upper.strip().startswith('SELECT'):
        return False
        
    return True

def execute_read_only_query(query: str):
    """Executes a SQL query safely and returns a pandas DataFrame."""
    if not is_safe_query(query):
        raise ValueError("Unsafe SQL query detected. Only SELECT statements are allowed.")
        
    try:
        df = pd.read_sql_query(text(query), engine.connect())
        return df
    except Exception as e:
        raise ValueError(f"Database error: {str(e)}")
