
"""
data_loader.py - Handles data loading and basic operations
"""
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
import streamlit as st

def load_data(filepath='data/raw/bkk_data_final.csv', sample_mode=False):
    """
    Load event registration data from CSV file
    
    Args:
        filepath (str): Path to CSV file
        sample_mode (bool): If True, creates sample data for testing
    
    Returns:
        pd.DataFrame: Loaded data
    """
    try:
        if sample_mode:
            st.info("🔧 Using sample data for testing")
            return create_sample_data()
        
        # Check if file exists
        if not os.path.exists(filepath):
            st.error(f"❌ Data file not found: {filepath}")
            st.info("Switching to sample data mode")
            return create_sample_data()
        
        # Load CSV with proper encoding
        st.info(f"📂 Loading data from: {filepath}")
        
        # Try different encodings if needed
        try:
            df = pd.read_csv(filepath, encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(filepath, encoding='latin-1')
        
        # Basic validation
        st.success(f"✅ Loaded {len(df):,} rows with {len(df.columns)} columns")
        
        return df
        
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        st.info("Creating sample data for testing...")
        return create_sample_data()

def create_sample_data(num_rows=500):
    """
    Create realistic sample data for testing
    
    Args:
        num_rows (int): Number of rows to generate
    
    Returns:
        pd.DataFrame: Generated sample data
    """
    np.random.seed(42)  # For reproducibility
    
    # Generate realistic Thai event names
    thai_events = [
        "RECYCLE for LIFE WE CAN RUN FUND FOR LEGS",
        "วิ่งให้โอกาส 2024 สร้างหัวใจให้มีรอยยิ้ม",
        "TMC RUN FOR CHILDREN",
        "Black&White and Run 2024",
        "The Bridge Family Run @ มินิมาราธอน",
        "LAGUNA PHUKET MARATHON 2024",
        "65 ปี UNT ROCK AND RUN 2024",
        "Coffee Run 2024",
        "SAMSEN SPACE RUN 2024",
        "Run for the Ocean by KUFA #3"
    ]
    
    # Generate dates from Jan-Mar 2024
    start_date = datetime(2024, 1, 1)
    dates = [start_date + timedelta(days=np.random.randint(0, 90)) for _ in range(num_rows)]
    
    # Generate birth dates (ages 18-70)
    birth_dates = [datetime(2024 - np.random.randint(18, 70), 
                           np.random.randint(1, 13), 
                           np.random.randint(1, 28)) for _ in range(num_rows)]
    
    data = {
        'ID': [f'ID_{i:06d}' for i in range(num_rows)],
        'registrationId': [f'REG_{np.random.randint(10000, 99999)}' for _ in range(num_rows)],
        'gender': np.random.choice(['male', 'female'], num_rows, p=[0.55, 0.45]),
        'birthDate': [bd.strftime('%Y-%m-%d') for bd in birth_dates],
        'eventName': np.random.choice(thai_events, num_rows),
        'isVirtual': np.random.choice([True, False], num_rows, p=[0.15, 0.85]),
        'ticketTypeName': np.random.choice(['Early Bird', 'Regular', 'VIP', 'Student', 'Mini Marathon', 'Super Half Marathon'], num_rows),
        'ticketTypePrice': np.random.choice([400, 500, 600, 700, 800, 1000, 1200, 1500, 2000], num_rows, p=[0.1, 0.2, 0.15, 0.15, 0.1, 0.1, 0.1, 0.05, 0.05]),
        'province': np.random.choice(['Bangkok', 'Phuket', 'Chiang Mai', 'Khon Kaen', 'Surat Thani', 'Chonburi', 'Nonthaburi'], num_rows, p=[0.6, 0.1, 0.1, 0.05, 0.05, 0.05, 0.05]),
        'registerDate': [d.strftime('%Y/%m/%d') for d in dates],
        'shirtType': np.random.choice(['Short Sleeves', 'Sleeveless', 'Tech Tee', 'Short Sleeves (Black)', 'Adult\'s short sleeve shirt'], num_rows),
        'shirtSize': np.random.choice(['S : chest 36"', 'M : chest 38"', 'L : chest 40"', 'XL : chest 42"', '2XL : chest 44"', '3XL : chest 46"'], num_rows),
        'country': ['Thailand'] * num_rows,
        'city': np.random.choice(['Bangkok', 'Phuket City', 'Chiang Mai', 'Hat Yai', 'Pattaya', 'Khon Kaen'], num_rows),
        'postalCode': [str(np.random.randint(10000, 11000)) for _ in range(num_rows)]
    }
    
    df = pd.DataFrame(data)
    
    # Add some missing values (realistic)
    mask = np.random.random(num_rows) < 0.1
    df.loc[mask, 'city'] = np.nan
    df.loc[mask, 'postalCode'] = np.nan
    
    return df

def save_processed_data(df, filepath='data/processed/cleaned_data.csv'):
    """
    Save processed data to CSV file
    
    Args:
        df (pd.DataFrame): Data to save
        filepath (str): Path to save the file
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Save to CSV
        df.to_csv(filepath, index=False)
        return True, f"💾 Data saved to: {filepath}"
        
    except Exception as e:
        return False, f"❌ Error saving data: {str(e)}"

def get_data_summary(df):
    """
    Get comprehensive data summary
    
    Args:
        df (pd.DataFrame): Data to summarize
    
    Returns:
        dict: Summary statistics
    """
    summary = {
        'shape': df.shape,
        'columns': list(df.columns),
        'data_types': {col: str(dtype) for col, dtype in df.dtypes.items()},
        'missing_values': df.isnull().sum().to_dict(),
        'missing_percentage': {col: f"{(df[col].isnull().sum() / len(df)) * 100:.1f}%" for col in df.columns},
        'unique_counts': {col: df[col].nunique() for col in df.columns},
        'numeric_stats': {}
    }
    
    # Add numeric column statistics
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        summary['numeric_stats'][col] = {
            'min': float(df[col].min()),
            'max': float(df[col].max()),
            'mean': float(df[col].mean()),
            'median': float(df[col].median()),
            'std': float(df[col].std())
        }
    
    return summary