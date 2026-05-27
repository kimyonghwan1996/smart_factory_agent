import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

import os

# Constants
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api")

st.set_page_config(page_title="Smart Factory Agent", layout="wide", page_icon="🏭")

def fetch_kpi(kpi_name, date=None):
    url = f"{API_BASE_URL}/kpi/{kpi_name}"
    if date:
        url += f"?date={date}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to fetch KPI: {response.text}")
        return None

def fetch_daily_report():
    response = requests.get(f"{API_BASE_URL}/report/daily")
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to fetch daily report: {response.text}")
        return None

def ask_agent(question):
    response = requests.post(f"{API_BASE_URL}/chat", json={"question": question})
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to process query: {response.text}")
        return None

# Sidebar
st.sidebar.title("🏭 Smart Factory Agent")
mode = st.sidebar.radio("Navigation", ["Chat Analysis", "KPI Dashboard", "Daily Report"])

yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
st.sidebar.markdown(f"**Data Date (Default)**: {yesterday}")

if mode == "Chat Analysis":
    st.title("💬 Operational Data Agent")
    st.markdown("Ask natural language questions about logistics, production, quality, or inventory.")
    
    # Pre-defined questions
    st.markdown("**Try asking:**")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Why did Line 2 OEE drop yesterday?"):
            st.session_state.query = f"Show me downtime and production details for Line 2 on {yesterday}"
        if st.button("What caused this week's shipping delays?"):
            st.session_state.query = "Show me delayed shipments in the last 7 days by warehouse and reason."
    with col2:
        if st.button("Which picking zone has the lowest productivity?"):
            st.session_state.query = f"Show me picking productivity by zone for {yesterday}."
        if st.button("Show me defect rate by product."):
            st.session_state.query = f"Calculate defect rate by product for {yesterday}."

    query = st.text_area("Your question:", key="query", height=100)
    
    if st.button("Analyze", type="primary"):
        if query:
            with st.spinner("Analyzing data..."):
                result = ask_agent(query)
                
                if result:
                    st.markdown("### 📊 Analysis Summary")
                    st.markdown(result.get("answer", "No analysis provided."))
                    
                    if result.get("sql"):
                        with st.expander("Show Generated SQL"):
                            st.code(result.get("sql"), language="sql")
                            
                    if result.get("data"):
                        st.markdown("### 📋 Data Sample")
                        df = pd.DataFrame(result.get("data"))
                        st.dataframe(df)
                        
                        # Basic charting logic
                        if len(df.columns) >= 2:
                            # Try to plot if suitable data exists
                            try:
                                num_cols = df.select_dtypes(include=['number']).columns
                                cat_cols = df.select_dtypes(exclude=['number']).columns
                                
                                if len(num_cols) > 0 and len(cat_cols) > 0:
                                    x_col = cat_cols[0]
                                    y_col = num_cols[0]
                                    fig = px.bar(df, x=x_col, y=y_col, title=f"{y_col} by {x_col}")
                                    st.plotly_chart(fig, use_container_width=True)
                            except Exception as e:
                                pass # Ignore chart errors for generic data
                                
elif mode == "KPI Dashboard":
    st.title("📈 KPI Dashboard")
    selected_kpi = st.selectbox("Select KPI", ["OEE", "Delivery Delay Rate", "Picking Productivity", "Defect Rate"])
    
    kpi_map = {
        "OEE": "oee",
        "Delivery Delay Rate": "delivery_delay",
        "Picking Productivity": "picking_productivity",
        "Defect Rate": "defect_rate"
    }
    
    if st.button("Calculate KPI"):
        with st.spinner("Calculating..."):
            kpi_data = fetch_kpi(kpi_map[selected_kpi], yesterday)
            if kpi_data:
                st.json(kpi_data)
                if "error" not in kpi_data:
                    st.info(f"Formula: {kpi_data.get('formula')}")

elif mode == "Daily Report":
    st.title("📄 Daily Operations Report")
    
    if st.button("Generate Report for Yesterday", type="primary"):
        with st.spinner("Aggregating KPIs and generating report..."):
            report = fetch_daily_report()
            if report:
                st.subheader(f"Date: {report['date']}")
                st.markdown(f"**Summary:** {report['summary']}")
                
                kpis = report['kpis']
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    oee_data = kpis.get('oee', {})
                    if "error" not in oee_data:
                        st.metric("OEE", f"{oee_data.get('oee')}%")
                    else:
                        st.metric("OEE", "N/A")
                        
                with col2:
                    del_data = kpis.get('delivery_delay', {})
                    if "error" not in del_data:
                        st.metric("Delivery Delay Rate", f"{del_data.get('delay_rate')}%")
                    else:
                        st.metric("Delivery Delay Rate", "N/A")
                        
                with col3:
                    pick_data = kpis.get('picking_productivity', {})
                    if "error" not in pick_data:
                        st.metric("Picking Productivity", f"{pick_data.get('productivity_units_per_hour')} U/hr")
                    else:
                        st.metric("Picking Productivity", "N/A")
                        
                with col4:
                    def_data = kpis.get('defect_rate', {})
                    if "error" not in def_data:
                        st.metric("Defect Rate", f"{def_data.get('defect_rate')}%")
                    else:
                        st.metric("Defect Rate", "N/A")
