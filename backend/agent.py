import openai
from .config import config
from .database import execute_read_only_query
from .sql_generator import get_sql_prompt
import json

openai.api_key = config.OPENAI_API_KEY

def generate_sql_from_question(question: str) -> str:
    prompt = get_sql_prompt(question)
    try:
        response = openai.chat.completions.create(
            model=config.OPENAI_MODEL,
            messages=[{"role": "system", "content": prompt}],
            temperature=0,
            max_tokens=300
        )
        sql_query = response.choices[0].message.content.strip()
        # Clean up if the model wrapped it in markdown
        if sql_query.startswith("```sql"):
            sql_query = sql_query[6:-3].strip()
        elif sql_query.startswith("```"):
            sql_query = sql_query[3:-3].strip()
        return sql_query
    except Exception as e:
        return f"Error generating SQL: {str(e)}"

def analyze_data_with_llm(question: str, data_str: str) -> str:
    prompt = f"""
You are an expert Smart Factory and Logistics Data Agent. 
You are given a user's question and the raw data results from the database.
Provide a concise, analytical response following these guidelines:
1. Summary: Main finding in 1-2 sentences.
2. Key Findings: Highlight the most important metrics.
3. Root-Cause Candidates: If applicable, what caused the change based on the data?
4. Recommended Actions: Suggest concrete next steps.

User Question: {question}
Data Results:
{data_str}

Format the response using Markdown.
"""
    try:
        response = openai.chat.completions.create(
            model=config.OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error analyzing data: {str(e)}"

def process_chat_query(question: str) -> dict:
    # 1. Generate SQL
    sql_query = generate_sql_from_question(question)
    
    if sql_query.startswith("Error"):
        return {"answer": sql_query, "sql": None, "data": None}
        
    # 2. Execute SQL
    try:
        df = execute_read_only_query(sql_query)
        data_preview = df.head(10).to_dict(orient="records")
        data_str = df.head(50).to_string() # send up to 50 rows to LLM
        
        # 3. Analyze Results
        if df.empty:
            answer = "No data found for the given query."
        else:
            answer = analyze_data_with_llm(question, data_str)
            
        return {
            "answer": answer,
            "sql": sql_query,
            "data": data_preview,
            "columns": df.columns.tolist() if not df.empty else []
        }
    except Exception as e:
        return {
            "answer": f"Error executing query: {str(e)}",
            "sql": sql_query,
            "data": None
        }
