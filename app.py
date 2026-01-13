import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# Page setup
st.set_page_config(page_title="ThaiDash", layout="wide")

st.title("🏃‍♂️ ThaiDash - Event Analytics")
st.markdown("### Your dashboard is loading...")

# Check for data file
data_path = "data/raw/bkk_data_final.csv"

if os.path.exists(data_path):
    st.success(f"✅ Data found: {data_path}")
    
    # Load data
    with st.spinner("Loading data..."):
        df = pd.read_csv(data_path)
        
    # Show basic info
    st.subheader("📊 Data Overview")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Records", len(df))
    
    with col2:
        st.metric("Columns", len(df.columns))
    
    with col3:
        st.metric("Size", f"{df.memory_usage().sum() / 1024:.0f} KB")
    
    # Show data preview
    with st.expander("🔍 View Data (First 100 rows)"):
        st.dataframe(df.head(100))
    
    # Quick analysis
    st.subheader("📈 Quick Insights")
    
    # 1. Event popularity
    if 'eventName' in df.columns:
        top_events = df['eventName'].value_counts().head(10)
        fig1 = px.bar(
            x=top_events.values,
            y=top_events.index,
            orientation='h',
            title="Top 10 Events"
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    # 2. Price distribution
    if 'ticketTypePrice' in df.columns:
        col1, col2 = st.columns(2)
        with col1:
            avg_price = df['ticketTypePrice'].mean()
            st.metric("Average Price", f"฿{avg_price:,.0f}")
        
        with col2:
            total_revenue = df['ticketTypePrice'].sum()
            st.metric("Total Revenue", f"฿{total_revenue:,.0f}")
    
    # 3. Gender distribution (if available)
    if 'gender' in df.columns:
        gender_counts = df['gender'].value_counts()
        fig2 = px.pie(
            values=gender_counts.values,
            names=gender_counts.index,
            title="Gender Distribution"
        )
        st.plotly_chart(fig2, use_container_width=True)
        
else:
    st.error(f"❌ Data file not found at: {data_path}")
    st.info("Please ensure your CSV file is at: data/raw/bkk_data_final.csv")
    
    # Create sample data for testing
    if st.button("Generate Sample Data for Testing"):
        sample_data = {
            'eventName': ['Bangkok Marathon', 'Phuket Run', 'Chiang Mai Trail'] * 10,
            'ticketTypePrice': [500, 600, 700, 800, 900] * 6,
            'gender': ['Male', 'Female'] * 15,
            'registerDate': pd.date_range('2024-01-01', periods=30).tolist()
        }
        df_sample = pd.DataFrame(sample_data)
        st.dataframe(df_sample)
        st.success("Sample data created for testing!")

# Sidebar
with st.sidebar:
    st.title("⚙️ Controls")
    st.markdown("---")
    st.write("**Data Info**")
    if 'df' in locals():
        st.write(f"Rows: {len(df)}")
        st.write(f"Columns: {len(df.columns)}")
    st.markdown("---")
    st.write("**Version:** 1.0.0")
    st.write(f"**Last loaded:** {datetime.now().strftime('%H:%M')}")