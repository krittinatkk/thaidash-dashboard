import streamlit as st
import pandas as pd
import plotly.express as px
from src.preprocessing import clean_data, create_sample_data

# ========== PAGE CONFIG ==========
st.set_page_config(
    page_title="ThaiDash - Event Dashboard",
    page_icon="🏃",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== CUSTOM CSS ==========
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #FF6B35;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-left: 5px solid #FF6B35;
    }
    .st-emotion-cache-1v0mbdj {
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ========== TITLE ==========
st.markdown('<h1 class="main-header">🏃 ThaiDash Event Analytics Dashboard</h1>', unsafe_allow_html=True)

# ========== SIDEBAR ==========
with st.sidebar:
    st.image("https://img.icons8.com/color/96/running--v1.png", width=80)
    st.title("🎯 Dashboard Controls")
    
    # Data source selection
    data_source = st.radio(
        "Choose data source:",
        ["Use Sample Data", "Upload CSV File"]
    )
    
    if data_source == "Upload CSV File":
        uploaded_file = st.file_uploader("Upload your event data (CSV)", type=['csv'])
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
        else:
            st.info("📁 No file uploaded. Using sample data.")
            df = create_sample_data()
    else:
        df = create_sample_data()
    
    # Clean the data
    df = clean_data(df)
    
    # Filters
    st.subheader("🔍 Filters")
    
    # Date filter
    if 'registerDate' in df.columns:
        min_date = df['registerDate'].min().date()
        max_date = df['registerDate'].max().date()
        date_range = st.date_input(
            "Select Date Range",
            value=[min_date, max_date],
            min_value=min_date,
            max_value=max_date
        )
    
    # Event filter
    if 'eventName' in df.columns:
        selected_events = st.multiselect(
            "Select Events",
            options=sorted(df['eventName'].unique()),
            default=sorted(df['eventName'].unique())[:3]
        )
        df = df[df['eventName'].isin(selected_events)] if selected_events else df

# ========== MAIN CONTENT ==========
# KPI Cards
st.subheader("📊 Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_events = df['eventName'].nunique() if 'eventName' in df.columns else 0
    st.metric("Total Events", f"{total_events:,}")

with col2:
    total_participants = len(df)
    st.metric("Total Participants", f"{total_participants:,}")

with col3:
    total_revenue = df['ticketTypePrice'].sum() if 'ticketTypePrice' in df.columns else 0
    st.metric("Total Revenue", f"฿{total_revenue:,.0f}")

with col4:
    avg_price = df['ticketTypePrice'].mean() if 'ticketTypePrice' in df.columns else 0
    st.metric("Avg Ticket Price", f"฿{avg_price:,.0f}")

# ========== VISUALIZATIONS ==========
st.subheader("📈 Visual Analytics")

tab1, tab2, tab3 = st.tabs(["Event Popularity", "Revenue Trend", "Demographics"])

with tab1:
    # Top events by participants
    if 'eventName' in df.columns:
        event_counts = df['eventName'].value_counts().head(10)
        fig1 = px.bar(
            x=event_counts.values,
            y=event_counts.index,
            orientation='h',
            title="Top 10 Events by Participants",
            labels={'x': 'Number of Participants', 'y': 'Event Name'},
            color=event_counts.values,
            color_continuous_scale='oranges'
        )
        st.plotly_chart(fig1, use_container_width=True)

with tab2:
    # Daily revenue trend
    if 'registerDate' in df.columns and 'ticketTypePrice' in df.columns:
        df['registerDate'] = pd.to_datetime(df['registerDate'])
        daily_revenue = df.groupby(df['registerDate'].dt.date)['ticketTypePrice'].sum().reset_index()
        daily_revenue.columns = ['Date', 'Revenue']
        
        fig2 = px.line(
            daily_revenue,
            x='Date',
            y='Revenue',
            title="Daily Revenue Trend",
            markers=True
        )
        fig2.update_traces(line=dict(color='#FF6B35', width=3))
        st.plotly_chart(fig2, use_container_width=True)

with tab3:
    col1, col2 = st.columns(2)
    
    with col1:
        # Gender distribution
        if 'gender' in df.columns:
            gender_counts = df['gender'].value_counts()
            fig3 = px.pie(
                values=gender_counts.values,
                names=gender_counts.index,
                title="Gender Distribution",
                color_discrete_sequence=px.colors.sequential.Oranges
            )
            st.plotly_chart(fig3, use_container_width=True)
    
    with col2:
        # Age distribution if available
        if 'age' in df.columns:
            fig4 = px.histogram(
                df, 
                x='age',
                nbins=20,
                title="Age Distribution",
                labels={'age': 'Age'},
                color_discrete_sequence=['#FF6B35']
            )
            st.plotly_chart(fig4, use_container_width=True)

# ========== DATA PREVIEW ==========
st.subheader("📋 Data Preview")

# Show dataframe
st.dataframe(
    df.head(50),
    use_container_width=True,
    hide_index=True
)

# Download button
csv = df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Download Filtered Data (CSV)",
    data=csv,
    file_name="thaidash_filtered_data.csv",
    mime="text/csv"
)

# ========== FOOTER ==========
st.markdown("---")
st.caption("ThaiDash Dashboard v1.0 • Built with Streamlit • Data refreshes automatically")