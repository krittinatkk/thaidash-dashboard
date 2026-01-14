import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# Page setup
st.set_page_config(page_title="ThaiDash", layout="wide")

# Header with company logo and title - centered and closer together
st.markdown("""
    <style>
    .centered-header {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
        margin-bottom: 20px;
    }
    .header-title {
        text-align: left;
    }
    </style>
""", unsafe_allow_html=True)

# Create a centered header with logo and title
st.markdown('<div class="centered-header">', unsafe_allow_html=True)

# Image column
col1, col2 = st.columns([1, 3])
with col1:
    st.image("https://pbs.twimg.com/profile_images/807822247264014336/0wmn4ZjP_400x400.jpg", width=200)

with col2:
    st.markdown('<div class="header-title">', unsafe_allow_html=True)
    st.title("ThaiDash - Event Analytics")
    st.markdown("**Extended Digital Engineering Training Project**")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Company Background Section
with st.expander("🏢 **About Thaidotrun Co., Ltd.**", expanded=False):
    st.markdown("""
    ### Company Overview
    **Thaidotrun Co., Ltd.** is a leading event management and data analytics company based in Bangkok, Thailand. 
    We specialize in organizing and analyzing running events across the country, providing comprehensive insights 
    to event organizers, sponsors, and participants.
    
    ### Our Mission
    To promote health and wellness through organized sporting events while leveraging data analytics to 
    enhance participant experience and optimize event operations.
    
    ### Core Services:
    - 📊 Event Management & Organization
    - 🎯 Participant Analytics & Insights
    - 📈 Revenue Optimization Strategies
    - 🏆 Sponsorship & Partnership Management
    - 📱 Digital Registration Platforms
    """)

# Project Description Section
with st.expander("🎯 **Project Objectives**", expanded=False):
    st.markdown("""
    ### ThaiDash Analytics Platform
    This dashboard is designed to provide real-time insights into running event registrations across Thailand.
    
    ### Key Objectives:
    1. **Participant Analysis**: Understand demographic trends and registration patterns
    2. **Event Performance**: Track popularity and revenue metrics for each event
    3. **Operational Insights**: Optimize event planning and resource allocation
    4. **Revenue Tracking**: Monitor financial performance across all events
    5. **Market Intelligence**: Identify trends in the Thai running event industry
    
    ### Data Sources:
    - Event registration databases
    - Participant demographic information
    - Ticket sales and pricing data
    - Geographic distribution data
    """)

# Check for data file
data_path = "data/raw/bkk_data_final.csv"

if os.path.exists(data_path):
    st.success(f"✅ Data loaded successfully: {data_path}")
    
    # Load data
    with st.spinner("Loading data..."):
        df = pd.read_csv(data_path)
    
    # Dashboard Statistics
    st.subheader("📊 Dashboard Statistics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_records = len(df)
        st.metric("Total Registrations", f"{total_records:,}")
    
    with col2:
        unique_participants = df['ID'].nunique() if 'ID' in df.columns else "N/A"
        st.metric("Unique Participants", f"{unique_participants:,}")
    
    with col3:
        total_revenue = df['ticketTypePrice'].sum() if 'ticketTypePrice' in df.columns else 0
        st.metric("Total Revenue", f"฿{total_revenue:,.0f}")
    
    with col4:
        avg_price = df['ticketTypePrice'].mean() if 'ticketTypePrice' in df.columns else 0
        st.metric("Average Ticket Price", f"฿{avg_price:,.0f}")
    
    # Show data preview
    with st.expander("🔍 **View Raw Data**", expanded=False):
        st.dataframe(df.head(100))
        st.caption(f"Showing first 100 of {len(df):,} records")
        
else:
    st.error(f"❌ Data file not found at: {data_path}")
    st.info("Please ensure your CSV file is at: data/raw/bkk_data_final.csv")
    
    # Create sample data for testing
    if st.button("Generate Sample Data for Testing"):
        sample_data = {
            'ID': [f'ID_{i}' for i in range(1, 31)],  # 30 unique IDs
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
    
    st.write("### About")
    st.write("""
    **Thaidotrun Co., Ltd.**
    
    📍 Bangkok, Thailand
    
    📧 contact@thaidotrun.com
    
    🌐 www.thai.run
    """)
    
    st.caption("""
    **Version:** 1.0.0
    **Last Updated:** """ + datetime.now().strftime('%Y-%m-%d %H:%M'))