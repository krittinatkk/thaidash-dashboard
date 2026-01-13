# REPLACE the clean_data function with this FIXED version:

def clean_data(df):
    """Clean and preprocess the dataset - FIXED VERSION"""
    df_clean = df.copy()
    
    # ONLY fill columns that exist
    if 'city' in df_clean.columns:
        df_clean['city'] = df_clean['city'].fillna('Bangkok')
    
    if 'country' in df_clean.columns:  # Only if column exists
        df_clean['country'] = df_clean['country'].fillna('Thailand')
    
    # Create age from birthDate if column exists
    if 'birthDate' in df_clean.columns:
        try:
            df_clean['birthDate'] = pd.to_datetime(df_clean['birthDate'], errors='coerce')
            df_clean['age'] = (pd.Timestamp('2024-01-01') - df_clean['birthDate']).dt.days // 365
        except:
            df_clean['age'] = None
    
    # Parse dates if column exists
    if 'registerDate' in df_clean.columns:
        df_clean['registerDate'] = pd.to_datetime(df_clean['registerDate'], errors='coerce')
    
    # Create simple price categories if column exists
    if 'ticketTypePrice' in df_clean.columns:
        try:
            df_clean['price_category'] = pd.cut(
                df_clean['ticketTypePrice'],
                bins=[0, 500, 1000, 2000, 10000],
                labels=['Budget (<500)', 'Standard (500-1000)', 'Premium (1000-2000)', 'VIP (2000+)']
            )
        except:
            df_clean['price_category'] = 'Unknown'
    
    return df_clean

# ALSO update the create_sample_data function:
def create_sample_data():
    """Generate sample data - FIXED VERSION"""
    np.random.seed(42)
    n_samples = 500
    
    data = {
        'eventName': np.random.choice([
            'Bangkok Marathon 2024', 'Phuket Beach Run', 'Chiang Mai Trail',
            'Bangkok Midnight Run', 'Virtual 10K Challenge'
        ], n_samples),
        'ticketTypePrice': np.random.randint(300, 2500, n_samples),
        'gender': np.random.choice(['Male', 'Female', 'Other'], n_samples, p=[0.55, 0.42, 0.03]),
        'city': np.random.choice(['Bangkok', 'Phuket', 'Chiang Mai', 'Unknown'], n_samples),
        'registerDate': pd.date_range('2024-01-01', periods=n_samples, freq='h').tolist(),  # 'h' not 'H'
        'birthDate': pd.to_datetime(np.random.choice(
            pd.date_range('1970-01-01', '2005-12-31', freq='D'), n_samples
        ))
    }
    
    return pd.DataFrame(data)