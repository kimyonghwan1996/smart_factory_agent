from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from .config import config
from .database import execute_read_only_query
from .sql_generator import get_sql_prompt
import json

# Initialize LangChain LLM for deterministic SQL generation
llm = ChatOpenAI(
    model=config.OPENAI_MODEL,
    temperature=0,
    openai_api_key=config.OPENAI_API_KEY
)

# Initialize LangChain LLM for detailed analysis (slightly higher temperature)
analysis_llm = ChatOpenAI(
    model=config.OPENAI_MODEL,
    temperature=0.3,
    openai_api_key=config.OPENAI_API_KEY
)

def generate_sql_from_question(question: str) -> str:
    prompt_content = get_sql_prompt(question)
    
    # Wrap in ChatPromptTemplate
    prompt = ChatPromptTemplate.from_messages([
        ("system", prompt_content)
    ])
    
    # LCEL Chain: prompt -> llm -> output_parser
    chain = prompt | llm | StrOutputParser()
    
    try:
        sql_query = chain.invoke({})
        sql_query = sql_query.strip()
        
        # Clean up if the model wrapped it in markdown
        if sql_query.startswith("```sql"):
            sql_query = sql_query[6:-3].strip()
        elif sql_query.startswith("```"):
            sql_query = sql_query[3:-3].strip()
        return sql_query
    except Exception as e:
        return f"Error generating SQL: {str(e)}"

def analyze_data_with_llm(question: str, data_str: str) -> str:
    # Analytical prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert Smart Factory and Logistics Data Agent.\n"
                   "You are given a user's question and the raw data results from the database.\n"
                   "Provide a concise, analytical response following these guidelines:\n"
                   "1. Summary: Main finding in 1-2 sentences.\n"
                   "2. Key Findings: Highlight the most important metrics.\n"
                   "3. Root-Cause Candidates: If applicable, what caused the change based on the data?\n"
                   "4. Recommended Actions: Suggest concrete next steps.\n\n"
                   "Format the response using Markdown."),
        ("user", "User Question: {question}\nData Results:\n{data_str}")
    ])
    
    # LCEL Chain
    chain = prompt | analysis_llm | StrOutputParser()
    
    try:
        response = chain.invoke({
            "question": question,
            "data_str": data_str
        })
        return response.strip()
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
