import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from data_loader import load_data
from preprocessing import clean_event_data

# Page configuration
st.set_page_config(
    page_title="Participant Insights",
    page_icon="👥",
    layout="wide"
)

# Title
st.title("👥 Participant Insights")
st.markdown("Analyze participant registration patterns and identify inactive users")

# Load data
@st.cache_data
def load_and_process_data():
    try:
        df_raw = load_data(sample_mode=False)
    except:
        df_raw = load_data(sample_mode=True)
    
    df_processed = clean_event_data(df_raw, verbose=False)
    return df_raw, df_processed

with st.spinner("Loading data..."):
    df_raw, df = load_and_process_data()

# Controls
col1, col2 = st.columns(2)

with col1:
    inactivity_threshold = st.slider(
        "Inactive threshold (days):",
        min_value=30, max_value=365, value=180, step=30
    )

with col2:
    results_limit = st.selectbox(
        "Show first N results:",
        [100, 250, 500, 1000], index=2
    )

# Apply button
if st.button("Show Results", type="primary", use_container_width=True):
    
    if 'registerDate' not in df.columns or 'ID' not in df.columns:
        st.error("Required columns not found!")
        st.stop()
    
    df['registerDate'] = pd.to_datetime(df['registerDate'], errors='coerce')
    
    # Calculate participant stats
    participant_stats = df.groupby('ID').agg({
        'registerDate': 'max',
        'eventName': 'count'
    }).reset_index()
    
    participant_stats.columns = ['ID', 'last_reg_date', 'registration_count']
    
    current_date = datetime.now()
    participant_stats['days_since_last'] = (current_date - participant_stats['last_reg_date']).dt.days
    participant_stats['is_inactive'] = participant_stats['days_since_last'] > inactivity_threshold
    
    # Create two columns for both analyses
    col1, col2 = st.columns(2)
    
    # COLUMN 1: Inactive IDs
    with col1:
        st.header(f"IDs with no registration > {inactivity_threshold} days")
        
        inactive_ids = participant_stats[participant_stats['is_inactive'] == True].copy()
        inactive_ids = inactive_ids.sort_values('days_since_last', ascending=False)
        results = inactive_ids.head(results_limit)
        
        display_df = results.copy()
        display_df['last_reg_date'] = display_df['last_reg_date'].dt.strftime('%Y-%m-%d')
        
        st.dataframe(
            display_df[['ID', 'last_reg_date', 'days_since_last', 'registration_count']],
            use_container_width=True,
            height=600
        )
        
        csv_data = results[['ID', 'last_reg_date', 'days_since_last', 'registration_count']].to_csv(index=False)
        st.download_button(
            label=f"Download {len(results)} IDs",
            data=csv_data,
            file_name=f"inactive_ids.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    # COLUMN 2: IDs with least registrations
    with col2:
        st.header("IDs with least registrations")
        
        least_reg_ids = participant_stats.sort_values(['registration_count', 'days_since_last'], 
                                                     ascending=[True, False])
        results = least_reg_ids.head(results_limit)
        
        display_df = results.copy()
        display_df['last_reg_date'] = display_df['last_reg_date'].dt.strftime('%Y-%m-%d')
        
        st.dataframe(
            display_df[['ID', 'registration_count', 'last_reg_date', 'days_since_last']],
            use_container_width=True,
            height=600
        )
        
        csv_data = results[['ID', 'registration_count', 'last_reg_date', 'days_since_last']].to_csv(index=False)
        st.download_button(
            label=f"Download {len(results)} IDs",
            data=csv_data,
            file_name=f"least_registration_ids.csv",
            mime="text/csv",
            use_container_width=True
        )

else:
    st.info("Click 'Show Results' to see both analyses")

# Footer
st.markdown("---")
st.caption(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")