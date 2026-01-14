"""preprocessing.py - Data cleaning and feature engineering pipeline"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import re

def extract_distance(ticket_name):
    """
    Extract distance value from ticketTypeName.
    Formats to look for: 3K, 5K, 10K, 21.1K, 24K, 42.2K, etc.
    Returns distance in format like '3K', '5K', '10K', '21.1K', '24K', '42.2K' or 'Other'
    """
    if pd.isna(ticket_name):
        return 'Other'
    
    ticket_str = str(ticket_name).upper()
    
    # Pattern to find distances: numbers followed by K or KM
    patterns = [
        r'(\d+\.?\d*)\s*(K|KM)',  # 3K, 5K, 10K, 21.1K, 24K, 42.2K, 5KM, 10KM, etc.
        r'(\d+)\s*(K|KM)',        # 3 K, 5 K, 10 K (with space)
    ]
    
    for pattern in patterns:
        match = re.search(pattern, ticket_str)
        if match:
            distance_num = match.group(1)
            # Convert to float and back to string to remove trailing .0
            try:
                distance_float = float(distance_num)
                if distance_float.is_integer():
                    distance_str = str(int(distance_float))
                else:
                    distance_str = str(distance_float)
                return f"{distance_str}K"
            except:
                return f"{distance_num}K"
    
    # If no distance pattern found, check for specific race types
    if 'MARATHON' in ticket_str:
        return '42.2K'
    elif 'HALF' in ticket_str and 'MARATHON' in ticket_str:
        return '21.1K'
    elif 'HALF' in ticket_str:
        return '21.1K'
    elif 'FULL' in ticket_str and 'MARATHON' in ticket_str:
        return '42.2K'
    elif '24K' in ticket_str or '24 KM' in ticket_str:
        return '24K'
    elif '21K' in ticket_str or '21.1K' in ticket_str or 'HALF' in ticket_str:
        return '21.1K'
    elif '10K' in ticket_str:
        return '10K'
    elif '5K' in ticket_str:
        return '5K'
    elif '3K' in ticket_str:
        return '3K'
    
    return 'Other'

def clean_event_data(df, verbose=True):
    """
    Comprehensive data cleaning pipeline for event registration data
    
    Args:
        df (pd.DataFrame): Raw event registration data
        verbose (bool): Whether to print progress messages
    
    Returns:
        pd.DataFrame: Cleaned and feature-engineered data with attributes
    """
    if verbose:
        print("🧹 Starting data cleaning pipeline...")
        print(f"📊 Raw data shape: {df.shape}")
    
    # Create a copy to avoid modifying original
    df_clean = df.copy()
    
    # Store ORIGINAL data for metrics calculation
    original_df = df.copy()
    
    # ========== 0. CHECK RAW DATA FIRST ==========
    if verbose and 'eventName' in df_clean.columns:
        print(f"\n🔍 CHECKING RAW DATA:")
        
        # Count events in raw data
        raw_event_count = df_clean['eventName'].nunique()
        print(f"   Raw unique events: {raw_event_count:,}")
        
        # Check for สุขเต็มสิบ in raw data
        event_counts = df_clean['eventName'].value_counts()
        found_suks = False
        for event, count in event_counts.head(20).items():
            if 'สุขเต็มสิบ' in str(event):
                print(f"   ✓ Found in raw data: '{event}' with {count:,} participants")
                found_suks = True
                break
        
        if not found_suks:
            print(f"   ❌ 'สุขเต็มสิบ' NOT FOUND in top 20 raw events!")
            # Search all events
            for event, count in event_counts.items():
                if 'สุขเต็มสิบ' in str(event):
                    print(f"   Found later: '{event}' with {count:,} participants (position {list(event_counts.index).index(event)+1})")
                    found_suks = True
                    break
    
    # ========== 1. MINIMAL EVENT NAME CLEANING ==========
    if 'eventName' in df_clean.columns:
        # Just basic cleaning - preserve original names
        df_clean['eventName'] = df_clean['eventName'].astype(str).str.strip()
        original_df['eventName'] = original_df['eventName'].astype(str).str.strip()
        
        if verbose:
            print(f"\n📊 After basic cleaning:")
            print(f"   Unique events: {df_clean['eventName'].nunique():,}")
            
            # Show top events
            event_counts = df_clean['eventName'].value_counts().head(10)
            for i, (event, count) in enumerate(event_counts.items(), 1):
                print(f"   {i:2}. '{event[:50]}': {count:,}")
    
    # ========== 2. PROCESS DATES ==========
    if 'registerDate' in df_clean.columns:
        df_clean['registerDate'] = pd.to_datetime(df_clean['registerDate'], errors='coerce')
        
        # Extract date features
        df_clean['registration_year'] = df_clean['registerDate'].dt.year
        df_clean['registration_month'] = df_clean['registerDate'].dt.month
        df_clean['registration_day'] = df_clean['registerDate'].dt.day
        df_clean['registration_weekday'] = df_clean['registerDate'].dt.day_name()
        df_clean['registration_week'] = df_clean['registerDate'].dt.isocalendar().week
    
    # ========== 3. PROCESS PRICES ==========
    if 'ticketTypePrice' in df_clean.columns:
        # Convert to numeric
        df_clean['ticketTypePrice'] = pd.to_numeric(df_clean['ticketTypePrice'], errors='coerce')
        original_df['ticketTypePrice'] = pd.to_numeric(original_df['ticketTypePrice'], errors='coerce')
        
        # Fill missing
        df_clean['ticketTypePrice'] = df_clean['ticketTypePrice'].fillna(0)
        original_df['ticketTypePrice'] = original_df['ticketTypePrice'].fillna(0)
        
        # Create price tiers
        def categorize_price(price):
            if pd.isna(price):
                return 'Unknown'
            elif price == 0:
                return 'Free'
            elif price <= 400:
                return 'Budget (≤400฿)'
            elif price <= 600:
                return 'Economy (401-600฿)'
            elif price <= 900:
                return 'Standard (601-900฿)'
            elif price <= 1200:
                return 'Premium (901-1200฿)'
            else:
                return 'VIP (>1200฿)'
        
        df_clean['price_tier'] = df_clean['ticketTypePrice'].apply(categorize_price)
    
    # ========== 4. CALCULATE METRICS FROM ORIGINAL DATA ==========
    # Calculate from ORIGINAL data (before any filtering/cleaning)
    total_registrations = len(original_df)
    
    if 'ID' in original_df.columns:
        unique_participants = original_df['ID'].nunique()
    else:
        unique_participants = total_registrations
    
    if 'ticketTypePrice' in original_df.columns:
        total_revenue = original_df['ticketTypePrice'].sum()
        avg_price_per_registration = total_revenue / total_registrations if total_registrations > 0 else 0
    else:
        total_revenue = 0
        avg_price_per_registration = 0
    
    if 'eventName' in original_df.columns:
        unique_events_all = original_df['eventName'].nunique()
        # Get top events from ALL data
        top_events_all = original_df['eventName'].value_counts().head(10)
    else:
        unique_events_all = 0
        top_events_all = pd.Series()
    
    if verbose:
        print(f"\n📈 METRICS FROM ALL DATA:")
        print(f"   Total Registrations: {total_registrations:,}")
        print(f"   Unique Participants: {unique_participants:,}")
        print(f"   Unique Events:       {unique_events_all:,}")
        print(f"   Total Revenue:       ฿{total_revenue:,.2f}")
        print(f"   Avg Price:           ฿{avg_price_per_registration:,.2f}")
        
        print(f"\n🏆 TOP EVENTS (FROM ALL DATA):")
        for i, (event, count) in enumerate(top_events_all.items(), 1):
            print(f"   {i:2}. '{event[:50]}': {count:,}")
            if 'สุขเต็มสิบ' in str(event):
                print(f"        ⭐ THIS SHOULD BE TOP EVENT")
    
    # ========== 5. PROCESS AGE ==========
    if 'birthDate' in df_clean.columns:
        df_clean['birthDate'] = pd.to_datetime(df_clean['birthDate'], errors='coerce')
        
        today = pd.Timestamp.now()
        df_clean['age'] = ((today - df_clean['birthDate']).dt.days / 365.25)
        
        # Convert to integer
        df_clean['age'] = df_clean['age'].apply(
            lambda x: int(x) if pd.notna(x) and 0 <= x <= 120 else np.nan
        )
        
        # Age groups
        def get_age_group(age):
            if pd.isna(age):
                return 'Unknown'
            if age < 18:
                return '<18'
            elif age < 25:
                return '18-24'
            elif age < 35:
                return '25-34'
            elif age < 45:
                return '35-44'
            elif age < 55:
                return '45-54'
            else:
                return '55+'
        
        df_clean['age_group'] = df_clean['age'].apply(get_age_group)
    
    # ========== 6. PROCESS GENDER ==========
    if 'gender' in df_clean.columns:
        df_clean['gender'] = df_clean['gender'].astype(str).str.lower().str.strip()
        
        gender_mapping = {
            'male': 'Male', 
            'm': 'Male',
            'female': 'Female', 
            'f': 'Female',
            'ชาย': 'Male', 
            'หญิง': 'Female',
            'unknown': 'LGBTQ',
            'other': 'LGBTQ',
            'lgbtq': 'LGBTQ',
            'lgbt': 'LGBTQ',
            'lgbtq+': 'LGBTQ',
            'queer': 'LGBTQ',
            'non-binary': 'LGBTQ',
            'nb': 'LGBTQ',
            'genderqueer': 'LGBTQ',
            'transgender': 'LGBTQ',
            'trans': 'LGBTQ'
        }
        
        df_clean['gender'] = df_clean['gender'].map(gender_mapping).fillna('LGBTQ')
    
    # ========== 7. EXTRACT EVENT CATEGORY ==========
    if 'eventName' in df_clean.columns:
        def extract_event_category(event_name):
            name_lower = str(event_name).lower()
            
            if 'สุขเต็มสิบ' in name_lower:
                return 'สุขเต็มสิบ'
            elif 'marathon' in name_lower and 'half' not in name_lower and 'mini' not in name_lower:
                return 'Marathon'
            elif 'half' in name_lower:
                return 'Half Marathon'
            elif 'mini' in name_lower:
                return 'Mini Marathon'
            elif '10k' in name_lower or '10 km' in name_lower:
                return '10K'
            elif '5k' in name_lower or '5 km' in name_lower:
                return '5K'
            elif 'fun run' in name_lower:
                return 'Fun Run'
            elif 'trail' in name_lower:
                return 'Trail Run'
            elif 'charity' in name_lower:
                return 'Charity Run'
            else:
                return 'Other'
        
        df_clean['event_category'] = df_clean['eventName'].apply(extract_event_category)
    
    # ========== 8. EXTRACT DISTANCE CATEGORY ==========
    if 'ticketTypeName' in df_clean.columns:
        # Apply distance extraction function
        df_clean['distance_category'] = df_clean['ticketTypeName'].apply(extract_distance)
        
        # Define the desired order for distances
        distance_order = ['5K', '10K', '21.1K', '42.2K', 'Other']
        
        # Convert to categorical with specified order
        df_clean['distance_category'] = pd.Categorical(
            df_clean['distance_category'], 
            categories=distance_order,
            ordered=True
        )
        
        if verbose:
            print(f"\n📏 DISTANCE CATEGORIES:")
            distance_counts = df_clean['distance_category'].value_counts().reindex(distance_order)
            for distance, count in distance_counts.items():
                print(f"   {distance}: {count:,} participants")
    
    # ========== 9. REMOVE DUPLICATES FOR DEMOGRAPHIC ANALYSIS ==========
    if verbose:
        print(f"\n✨ Creating deduplicated dataset for demographics...")
    
    rows_before = len(df_clean)
    
    if 'ID' in df_clean.columns:
        df_clean = df_clean.drop_duplicates(subset=['ID'])
        duplicates_removed = rows_before - len(df_clean)
        
        if verbose:
            print(f"   Removed {duplicates_removed:,} duplicate participant records")
            print(f"   Kept {len(df_clean):,} unique participants for analysis")
    else:
        # Fallback deduplication
        key_fields = ['eventName', 'registerDate']
        if 'gender' in df_clean.columns:
            key_fields.append('gender')
        if 'birthDate' in df_clean.columns:
            key_fields.append('birthDate')
        
        df_clean = df_clean.drop_duplicates(subset=key_fields)
    
    # Reset index
    df_clean = df_clean.reset_index(drop=True)
    
    # ========== 10. STORE ALL METRICS AS ATTRIBUTES ==========
    # Store the important metrics as dataframe attributes
    df_clean.attrs['total_registrations'] = total_registrations
    df_clean.attrs['unique_participants'] = unique_participants
    df_clean.attrs['total_revenue'] = total_revenue
    df_clean.attrs['avg_price_per_registration'] = avg_price_per_registration
    df_clean.attrs['unique_events_all'] = unique_events_all
    
    # Store top events from all data
    if len(top_events_all) > 0:
        df_clean.attrs['top_events_all'] = top_events_all.to_dict()
        df_clean.attrs['top_event_name'] = top_events_all.index[0]
        df_clean.attrs['top_event_count'] = int(top_events_all.iloc[0])
    
    # ========== 11. FINAL VERIFICATION ==========
    if verbose:
        print("\n" + "="*60)
        print("✅ DATA PROCESSING COMPLETE")
        print("="*60)
        
        # Expected values
        expected = {
            'registrations': 212522,
            'participants': 133908,
            'revenue': 150466762.99,
            'avg_price': 708,
            'events': 528,
            'top_event_count': 6135,
        }
        
        print(f"\n📊 FINAL METRICS (from ALL data):")
        print(f"   Total Registrations: {total_registrations:,} (expected: {expected['registrations']:,})")
        print(f"   Unique Participants: {unique_participants:,} (expected: {expected['participants']:,})")
        print(f"   Unique Events:       {unique_events_all:,} (expected: {expected['events']:,})")
        print(f"   Total Revenue:       ฿{total_revenue:,.2f} (expected: ฿{expected['revenue']:,.2f})")
        print(f"   Avg Price:           ฿{avg_price_per_registration:,.2f} (expected: ฿{expected['avg_price']:,.2f})")
        
        # Check differences
        diffs = {
            'registrations': total_registrations - expected['registrations'],
            'participants': unique_participants - expected['participants'],
            'events': unique_events_all - expected['events'],
            'revenue': total_revenue - expected['revenue'],
            'avg_price': avg_price_per_registration - expected['avg_price'],
        }
        
        print(f"\n🔍 DIFFERENCES:")
        for key, diff in diffs.items():
            if abs(diff) > {
                'registrations': 100,
                'participants': 100,
                'events': 10,
                'revenue': 1000,
                'avg_price': 10
            }.get(key, 0):
                print(f"   ⚠️  {key}: {diff:+,}")
        
        print("="*60)
    
    return df_clean

def calculate_kpis(df):
    """
    Calculate Key Performance Indicators
    
    Uses stored attributes from ALL data, not just deduplicated data
    
    Args:
        df (pd.DataFrame): Cleaned event data with attributes
    
    Returns:
        dict: Dictionary of KPI metrics
    """
    kpis = {}
    
    # ========== 1. GET METRICS FROM ATTRIBUTES ==========
    # These come from ALL data (212,522 registrations)
    if hasattr(df, 'attrs'):
        kpis['total_registrations'] = df.attrs.get('total_registrations', 0)
        kpis['total_participants'] = df.attrs.get('unique_participants', 0)  # 133,908 unique
        kpis['total_revenue'] = float(df.attrs.get('total_revenue', 0))  # ฿150,466,762.99
        kpis['avg_ticket_price'] = float(df.attrs.get('avg_price_per_registration', 0))  # ~฿708
        kpis['unique_events'] = df.attrs.get('unique_events_all', 0)  # 528
        
        # Get top event info from ALL data
        if 'top_event_name' in df.attrs:
            kpis['top_event'] = df.attrs['top_event_name']
            kpis['top_event_count'] = df.attrs['top_event_count']
        
        # Get top events dict
        if 'top_events_all' in df.attrs:
            kpis['top_events_dict'] = df.attrs['top_events_all']
    else:
        # Fallback (shouldn't happen)
        kpis['total_registrations'] = len(df)
        kpis['total_participants'] = len(df)
        kpis['total_revenue'] = float(df['ticketTypePrice'].sum()) if 'ticketTypePrice' in df.columns else 0
        kpis['avg_ticket_price'] = float(df['ticketTypePrice'].mean()) if 'ticketTypePrice' in df.columns else 0
        kpis['unique_events'] = df['eventName'].nunique() if 'eventName' in df.columns else 0
    
    # ========== 2. CALCULATE OTHER METRICS ==========
    # Median price from current (deduplicated) data
    if 'ticketTypePrice' in df.columns:
        kpis['median_ticket_price'] = float(df['ticketTypePrice'].median())
    else:
        kpis['median_ticket_price'] = 0
    
    # ========== 3. DEMOGRAPHIC METRICS ==========
    # These come from DEDUPLICATED data (133,908 rows)
    if 'gender' in df.columns:
        gender_counts = df['gender'].value_counts()
        kpis.update({
            'male_participants': int(gender_counts.get('Male', 0)),
            'female_participants': int(gender_counts.get('Female', 0)),
            'lgbtq_participants': int(gender_counts.get('LGBTQ', 0)),
        })
    
    # Age metrics from deduplicated data
    if 'age' in df.columns:
        kpis.update({
            'avg_age': float(df['age'].mean()),
            'median_age': float(df['age'].median()),
            'participants_with_age': int(df['age'].notna().sum()),
        })
    
    # Event category from deduplicated data
    if 'event_category' in df.columns:
        top_category = df['event_category'].mode()
        kpis['top_event_category'] = top_category[0] if not top_category.empty else 'N/A'
    
    # Distance category from deduplicated data
    if 'distance_category' in df.columns:
        top_distance = df['distance_category'].mode()
        kpis['top_distance_category'] = top_distance[0] if not top_category.empty else 'N/A'
    
    # Date metrics from deduplicated data
    if 'registerDate' in df.columns:
        kpis.update({
            'earliest_registration': df['registerDate'].min().strftime('%Y-%m-%d'),
            'latest_registration': df['registerDate'].max().strftime('%Y-%m-%d'),
        })
    
    # ========== 4. CALCULATE PERCENTAGES ==========
    if kpis['total_participants'] > 0:
        if 'male_participants' in kpis:
            kpis['male_percentage'] = (kpis['male_participants'] / kpis['total_participants'] * 100)
        if 'female_participants' in kpis:
            kpis['female_percentage'] = (kpis['female_participants'] / kpis['total_participants'] * 100)
        if 'lgbtq_participants' in kpis:
            kpis['lgbtq_percentage'] = (kpis['lgbtq_participants'] / kpis['total_participants'] * 100)
        if 'participants_with_age' in kpis:
            kpis['age_known_percentage'] = (kpis['participants_with_age'] / kpis['total_participants'] * 100)
    
    # ========== 5. DEBUG OUTPUT ==========
    print(f"\n🔍 KPI CALCULATION DEBUG:")
    print(f"   Total Participants (unique): {kpis['total_participants']:,}")
    print(f"   Total Registrations (all):   {kpis['total_registrations']:,}")
    print(f"   Unique Events:               {kpis['unique_events']:,}")
    print(f"   Total Revenue:               ฿{kpis['total_revenue']:,.2f}")
    print(f"   Avg Ticket Price:            ฿{kpis['avg_ticket_price']:,.2f}")
    
    if 'top_event' in kpis:
        print(f"\n🏆 TOP EVENT (from ALL data):")
        print(f"   '{kpis['top_event']}' with {kpis['top_event_count']:,} participants")
        
        # Check if it's สุขเต็มสิบ
        if 'สุขเต็มสิบ' in kpis['top_event']:
            print(f"   ✓ This is 'สุขเต็มสิบ'")
        else:
            print(f"   ⚠️  Top event is NOT 'สุขเต็มสิบ'")
            
            # Show top 5 events
            if 'top_events_dict' in kpis:
                print(f"\n   Top 5 events from ALL data:")
                for i, (event, count) in enumerate(list(kpis['top_events_dict'].items())[:5], 1):
                    print(f"   {i}. '{event[:50]}': {count:,}")
    
    # ========== 6. VERIFICATION ==========
    # Expected values
    expected = {
        'total_registrations': 212522,
        'total_participants': 133908,
        'total_revenue': 150466762.99,
        'avg_ticket_price': 708,
        'unique_events': 528,
        'top_event_count': 6135,
    }
    
    # Check differences
    warnings = []
    for key, expected_val in expected.items():
        if key in kpis:
            actual = kpis[key]
            diff = actual - expected_val
            
            if abs(diff) > {
                'total_registrations': 100,
                'total_participants': 100,
                'total_revenue': 1000,
                'avg_ticket_price': 10,
                'unique_events': 10,
                'top_event_count': 100
            }.get(key, 0):
                warnings.append(f"{key}: Expected {expected_val:,}, Got {actual:,}, Diff: {diff:+,}")
    
    if warnings:
        print(f"\n⚠️  WARNINGS:")
        for warning in warnings:
            print(f"   {warning}")
    
    return kpis

def get_top_categories(df, column, n=10):
    """
    Get top N categories for a column
    
    For events: Use stored top events from ALL data
    For demographics: Use current (deduplicated) data
    
    Args:
        df (pd.DataFrame): Data
        column (str): Column name
        n (int): Number of top items to return
    
    Returns:
        pd.DataFrame: Top N categories
    """
    if column not in df.columns:
        return pd.DataFrame()
    
    # Special handling for eventName - use stored top events from ALL data
    if column == 'eventName' and hasattr(df, 'attrs') and 'top_events_all' in df.attrs:
        # Get top events from ALL data (212,522 registrations)
        top_events_dict = df.attrs['top_events_all']
        top_df = pd.DataFrame(list(top_events_dict.items()), columns=['eventName', 'count'])
        return top_df.head(n)
    
    # For other columns, use current (deduplicated) data
    result = df[column].value_counts().head(n).reset_index()
    result.columns = [column, 'count']
    
    return result