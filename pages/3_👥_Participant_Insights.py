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
st.title("👥Participant Insights")
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

with st.spinner("Loading..."):
    df_raw, df = load_and_process_data()

# Create two clickable tabs/buttons
st.markdown("---")
col1, col2 = st.columns(2)

# Use session state to track which tab is active
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = 'Least Active'

if 'show_least_active_results' not in st.session_state:
    st.session_state.show_least_active_results = False

if 'show_least_registration_results' not in st.session_state:
    st.session_state.show_least_registration_results = False

# Store selected ID in session state
if 'selected_id' not in st.session_state:
    st.session_state.selected_id = None

# Tab 1: Least Active
with col1:
    if st.button("**Least Active**", use_container_width=True, 
                 type="primary" if st.session_state.active_tab == 'Least Active' else "secondary"):
        st.session_state.active_tab = 'Least Active'
        st.session_state.show_least_active_results = False
        st.session_state.selected_id = None
        st.rerun()

# Tab 2: Least Registration
with col2:
    if st.button("**Least Registration**", use_container_width=True, 
                 type="primary" if st.session_state.active_tab == 'Least Registration' else "secondary"):
        st.session_state.active_tab = 'Least Registration'
        st.session_state.show_least_registration_results = False
        st.session_state.selected_id = None
        st.rerun()

st.markdown("---")

# Function to show participant details
def show_participant_details(participant_id):
    """Display participant event details"""
    st.markdown(f"**ID**: {participant_id}")
    
    # Use the processed data (df) for consistency
    participant_data = df[df['ID'] == participant_id].copy()
    
    if len(participant_data) > 0:
        # Clean and sort data
        participant_data['registerDate'] = pd.to_datetime(participant_data['registerDate'], errors='coerce')
        participant_data = participant_data.sort_values('registerDate', ascending=True)
        
        # Define display columns - check what's available in the processed data
        possible_columns = ['eventName', 'registerDate', 'Distance (KM)', 'Price', 
                           'distance', 'price', 'event_name', 'distance_km', 'price_usd']
        
        # Find which columns actually exist in the data
        available_cols = []
        for col in possible_columns:
            if col in participant_data.columns:
                available_cols.append(col)
        
        # Always include ID and eventName if available
        for essential_col in ['eventName', 'ID']:
            if essential_col in participant_data.columns and essential_col not in available_cols:
                available_cols.insert(0, essential_col)
        
        if len(available_cols) == 0:
            st.info("No displayable columns found for this participant")
            return
        
        # Display as table
        display_data = participant_data[available_cols].copy()
        
        # Format dates if present
        if 'registerDate' in display_data.columns:
            display_data['registerDate'] = display_data['registerDate'].dt.strftime('%Y/%m/%d')
        
        # Reset index
        display_data = display_data.reset_index(drop=True)
        
        # Display as dataframe for better formatting
        st.dataframe(
            display_data,
            use_container_width=True,
            hide_index=True
        )
        
        # Optional: Show summary statistics
        st.markdown("#### Summary")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Events", len(participant_data))
        with col2:
            if 'registerDate' in participant_data.columns:
                first_event = participant_data['registerDate'].min()
                st.metric("First Event", first_event.strftime('%Y/%m/%d'))
        with col3:
            if 'registerDate' in participant_data.columns:
                last_event = participant_data['registerDate'].max()
                st.metric("Last Event", last_event.strftime('%Y/%m/%d'))
        
    else:
        st.info("No event data found for this participant")

# Show content based on active tab
if st.session_state.active_tab == 'Least Active':
    st.markdown("### Least Active")
    
    # Create a horizontal layout with proper alignment
    st.markdown("""
    <style>
    .inline-container {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 1rem;
    }
    .inline-label {
        white-space: nowrap;
        font-weight: 600;
        padding-top: 8px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Create the inline layout
    st.markdown('<div class="inline-container">', unsafe_allow_html=True)
    
    # Label
    st.markdown('<div class="inline-label">Show first N results:</div>', unsafe_allow_html=True)
    
    # Dropdown
    results_limit = st.selectbox(
        "",
        [100, 250, 500, 1000], 
        index=2,
        label_visibility="collapsed",
        key="least_active_dropdown"
    )
    
    # Button
    if st.button("Show Results", 
               type="primary", 
               key="show_least_active_btn"):
        st.session_state.show_least_active_results = True
        st.session_state.show_least_registration_results = False
        st.session_state.selected_id = None
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.session_state.show_least_active_results:
        if 'registerDate' not in df.columns or 'ID' not in df.columns:
            st.error("Required columns 'registerDate' or 'ID' not found in processed data!")
            st.stop()
        
        df['registerDate'] = pd.to_datetime(df['registerDate'], errors='coerce')
        
        # Calculate stats
        participant_stats = df.groupby('ID').agg({
            'registerDate': 'max',
            'eventName': 'count'
        }).reset_index()
        
        participant_stats.columns = ['ID', 'last_reg_date', 'registration_count']
        
        current_date = datetime.now()
        participant_stats['days_since_last'] = (current_date - participant_stats['last_reg_date']).dt.days
        
        # Use fixed inactivity threshold (180 days)
        inactivity_threshold = 180
        participant_stats['is_inactive'] = participant_stats['days_since_last'] > inactivity_threshold
        
        # Filter inactive participants
        inactive_ids = participant_stats[participant_stats['is_inactive'] == True].copy()
        inactive_ids = inactive_ids.sort_values('days_since_last', ascending=False)
        results = inactive_ids.head(results_limit)
        
        # Display results section
        st.markdown("---")
        
        if len(results) == 0:
            st.info(f"No participants found inactive for more than {inactivity_threshold} days")
        else:
            # Display header
            st.markdown(f"**Showing first {len(results)} inactive IDs:**")
            
            # Create a list of IDs with selectable format
            for idx, row in results.iterrows():
                # Create a unique key for each button
                if st.button(f"{row['ID']} ({row['registration_count']} events, {row['days_since_last']} days inactive)", 
                            key=f"least_active_{row['ID']}",
                            use_container_width=True,
                            type="secondary"):
                    st.session_state.selected_id = row['ID']
                    st.rerun()
                
                # Show details immediately below the selected ID
                if st.session_state.selected_id == row['ID']:
                    show_participant_details(row['ID'])
            
            # Download button at the bottom
            st.markdown("---")
            csv_data = results[['ID', 'last_reg_date', 'days_since_last', 'registration_count']].to_csv(index=False)
            st.download_button(
                label=f"Download {len(results)} IDs",
                data=csv_data,
                file_name=f"least_active_ids.csv",
                mime="text/csv",
                use_container_width=True
            )

elif st.session_state.active_tab == 'Least Registration':
    st.markdown("### Least Registration")
    
    # Create a horizontal layout with proper alignment
    st.markdown("""
    <style>
    .inline-container {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 1rem;
    }
    .inline-label {
        white-space: nowrap;
        font-weight: 600;
        padding-top: 8px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Create the inline layout
    st.markdown('<div class="inline-container">', unsafe_allow_html=True)
    
    # Label
    st.markdown('<div class="inline-label">Show first N results:</div>', unsafe_allow_html=True)
    
    # Dropdown
    results_limit = st.selectbox(
        "",
        [100, 250, 500, 1000], 
        index=2,
        label_visibility="collapsed",
        key="least_reg_dropdown"
    )
    
    # Button
    if st.button("Show Results", 
               type="primary", 
               key="show_least_registration_btn"):
        st.session_state.show_least_registration_results = True
        st.session_state.show_least_active_results = False
        st.session_state.selected_id = None
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.session_state.show_least_registration_results:
        if 'registerDate' not in df.columns or 'ID' not in df.columns:
            st.error("Required columns 'registerDate' or 'ID' not found in processed data!")
            st.stop()
        
        df['registerDate'] = pd.to_datetime(df['registerDate'], errors='coerce')
        
        # Calculate stats
        participant_stats = df.groupby('ID').agg({
            'registerDate': 'max',
            'eventName': 'count'
        }).reset_index()
        
        participant_stats.columns = ['ID', 'last_reg_date', 'registration_count']
        
        current_date = datetime.now()
        participant_stats['days_since_last'] = (current_date - participant_stats['last_reg_date']).dt.days
        
        # Sort by registration count ONLY (not by inactivity)
        least_reg_ids = participant_stats.sort_values(['registration_count'], ascending=[True])
        results = least_reg_ids.head(results_limit)
        
        # Display results section
        st.markdown("---")
        
        if len(results) == 0:
            st.info("No participant data found")
        else:
            # Display header
            st.markdown(f"**Showing first {len(results)} IDs with fewest registrations:**")
            
            # Create a list of IDs with selectable format
            for idx, row in results.iterrows():
                # Create a unique key for each button
                if st.button(f"{row['ID']} ({row['registration_count']} events)", 
                            key=f"least_reg_{row['ID']}",
                            use_container_width=True,
                            type="secondary"):
                    st.session_state.selected_id = row['ID']
                    st.rerun()
                
                # Show details immediately below the selected ID
                if st.session_state.selected_id == row['ID']:
                    show_participant_details(row['ID'])
            
            # Download button at the bottom
            st.markdown("---")
            csv_data = results[['ID', 'registration_count', 'last_reg_date']].to_csv(index=False)
            st.download_button(
                label=f"Download {len(results)} IDs",
                data=csv_data,
                file_name=f"least_registration_ids.csv",
                mime="text/csv",
                use_container_width=True
            )

# Footer
st.markdown("---")
st.caption(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")