import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from data_loader import load_data, save_processed_data
from preprocessing import clean_event_data, calculate_kpis, get_top_categories

# ========== PAGE CONFIGURATION ==========
st.set_page_config(
    page_title="Event Analytics - ThaiDash",
    page_icon="📊",
    layout="wide"
)

# ========== CUSTOM CSS ==========
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        color: #1e3a8a;
        margin-bottom: 0.5rem;
    }
    .section-title {
        font-size: 1.5rem;
        color: #3b82f6;
        margin-top: 2rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e5e7eb;
    }
    .insight-title {
        font-size: 1rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    .insight-value {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ========== SIDEBAR ==========
with st.sidebar:
    st.title("📊 Event Analytics")
    
    # Only keep a simple description in sidebar
    st.markdown("---")
    st.markdown("### About")
    st.markdown("""
    This dashboard provides analytics for event participation,
    revenue trends, and demographic insights.
    
    All data is from real event registrations.
    """)

# ========== MAIN CONTENT ==========
def main():
    # Page header
    st.markdown('<h1 class="main-title">📊 Event Analytics Dashboard</h1>', unsafe_allow_html=True)
    st.markdown("Deep dive into event performance, participant demographics, and revenue trends")
    
    # Load data
    with st.spinner("Loading data..."):
        # Always use real data (sample_mode=False)
        df_raw = load_data(sample_mode=False)
        
        if df_raw is not None:
            df_clean = clean_event_data(df_raw, verbose=False)
            kpis = calculate_kpis(df_clean)
        else:
            st.error("Failed to load data")
            return
    
    # ========== KEY INSIGHTS SECTION ==========
    st.markdown('<h2 class="section-title">🔑 Key Insights at a Glance</h2>', unsafe_allow_html=True)
    
    # Top insights in cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="insight-title">Total Revenue</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="insight-value">฿{kpis["total_revenue"]:,.0f}</div>', unsafe_allow_html=True)
        st.markdown('<div>All events combined</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="insight-title">Total Unique Participants</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="insight-value">{kpis["total_participants"]:,}</div>', unsafe_allow_html=True)
        st.markdown('<div>Across all events</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="insight-title">Avg. Ticket Price</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="insight-value">฿{kpis["avg_ticket_price"]:,.0f}</div>', unsafe_allow_html=True)
        st.markdown('<div>Per participant</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="insight-title">Unique Events</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="insight-value">{kpis["unique_events"]}</div>', unsafe_allow_html=True)
        st.markdown('<div>Different events</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ========== EVENT PERFORMANCE SECTION ==========
    st.markdown('<h2 class="section-title">🏆 Event Performance Analysis</h2>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📈 Popularity", "💰 Revenue", "📊 Comparisons"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown("**Top 15 Events by Participants**")
            
            # Top events by participants - sort by highest at the top
            top_events = get_top_categories(df_clean, 'eventName', 15)
            
            # Sort in descending order (highest at top for horizontal bar)
            top_events = top_events.sort_values('count', ascending=True)  # True for horizontal bars
            
            fig1 = px.bar(
                top_events,
                y='eventName',
                x='count',
                orientation='h',
                color='count',
                color_continuous_scale='plasma',
                title='',
                labels={'eventName': 'Event Name', 'count': 'Participants'}
            )
            
            # Add value labels on bars
            fig1.update_traces(
                texttemplate='%{x:,}',
                textposition='outside'
            )
            
            # Update layout
            fig1.update_layout(
                height=500,
                yaxis={'categoryorder': 'total ascending'},  # Highest at top
                coloraxis_showscale=True,
                coloraxis_colorbar=dict(
                    title="Participants",
                    thickness=20,
                    len=0.8
                )
            )
            st.plotly_chart(fig1, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown("**Distance (KM) Distribution**")
            
            # Distance categories pie/donut chart
            if 'distance_category' in df_clean.columns:
                # Define the distance order
                distance_order = ['5K', '10K', '21.1K', '42.2K', 'Other']
                
                # Get counts and reindex to maintain order
                distance_counts = df_clean['distance_category'].value_counts().reindex(distance_order).reset_index()
                distance_counts.columns = ['distance', 'count']
                
                # Create donut chart
                fig2 = px.pie(
                    distance_counts,
                    values='count',
                    names='distance',
                    hole=0.4,
                    color_discrete_sequence=px.colors.qualitative.Set3,
                    title='',
                    category_orders={"distance": distance_order}
                )
                
                # Add percentage labels
                fig2.update_traces(
                    textposition='inside',
                    textinfo='percent+label',
                    hovertemplate='Distance: %{label}<br>Participants: %{value}<br>Percentage: %{percent:.1%}<extra></extra>'
                )
                
                fig2.update_layout(
                    height=500,
                    showlegend=True,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.2,
                        xanchor="center",
                        x=0.5
                    )
                )
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("Distance data not available in the dataset")
            st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown("**Revenue Trend Over Time**")
            
            # Revenue over time (monthly)
            df_clean['registerMonth'] = pd.to_datetime(df_clean['registerDate']).dt.to_period('M')
            monthly_revenue = df_clean.groupby('registerMonth')['ticketTypePrice'].sum().reset_index()
            monthly_revenue['registerMonth'] = monthly_revenue['registerMonth'].dt.to_timestamp()
            monthly_revenue = monthly_revenue.sort_values('registerMonth')
            
            fig4 = px.line(
                monthly_revenue,
                x='registerMonth',
                y='ticketTypePrice',
                markers=True,
                title='',
                labels={'registerMonth': 'Month', 'ticketTypePrice': 'Monthly Revenue (฿)'}
            )
            fig4.update_layout(height=400)
            st.plotly_chart(fig4, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown("**Top 10 Revenue-Generating Events**")
            
            # Top revenue events
            revenue_by_event = df_clean.groupby('eventName')['ticketTypePrice'].sum().reset_index()
            revenue_by_event = revenue_by_event.sort_values('ticketTypePrice', ascending=False).head(10)
            revenue_by_event = revenue_by_event.sort_values('ticketTypePrice', ascending=True)  # For horizontal bars
            
            fig4 = px.bar(
                revenue_by_event,
                y='eventName',
                x='ticketTypePrice',
                orientation='h',
                color='ticketTypePrice',
                color_continuous_scale='Viridis',
                title='',
                labels={'eventName': 'Event', 'ticketTypePrice': 'Revenue (฿)'}
            )
            fig4.update_layout(height=400)
            st.plotly_chart(fig4, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown("**Avg. Price by Distance Category**")
            
            # Average price by distance category
            if 'distance_category' in df_clean.columns:
                avg_price_by_distance = df_clean.groupby('distance_category')['ticketTypePrice'].mean().reset_index()
                avg_price_by_distance = avg_price_by_distance.sort_values('distance_category')
                
                fig5 = px.bar(
                    avg_price_by_distance,
                    x='distance_category',
                    y='ticketTypePrice',
                    color='ticketTypePrice',
                    color_continuous_scale='Reds',
                    title='',
                    labels={'distance_category': 'Distance Category', 'ticketTypePrice': 'Average Price (฿)'}
                )
                fig5.update_layout(height=400)
                st.plotly_chart(fig5, use_container_width=True)
            else:
                # Fallback to event category
                avg_price_cat = df_clean.groupby('event_category')['ticketTypePrice'].mean().reset_index()
                avg_price_cat = avg_price_cat.sort_values('ticketTypePrice', ascending=False)
                
                fig5 = px.bar(
                    avg_price_cat,
                    x='event_category',
                    y='ticketTypePrice',
                    color='ticketTypePrice',
                    color_continuous_scale='Reds',
                    title='',
                    labels={'event_category': 'Event Category', 'ticketTypePrice': 'Average Price (฿)'}
                )
                fig5.update_layout(height=400)
                st.plotly_chart(fig5, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown("**Participants vs Revenue Scatter**")
            
            # Scatter plot: participants vs revenue
            event_stats = df_clean.groupby('eventName').agg(
                participants=('ID', 'count'),
                revenue=('ticketTypePrice', 'sum'),
                avg_price=('ticketTypePrice', 'mean')
            ).reset_index()
            
            fig6 = px.scatter(
                event_stats,
                x='participants',
                y='revenue',
                size='avg_price',
                color='avg_price',
                hover_name='eventName',
                size_max=60,
                color_continuous_scale='Rainbow',
                title='',
                labels={
                    'participants': 'Number of Participants',
                    'revenue': 'Total Revenue (฿)',
                    'avg_price': 'Average Price (฿)'
                }
            )
            fig6.update_layout(height=400)
            st.plotly_chart(fig6, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
    
    # ========== DEMOGRAPHICS SECTION ==========
    st.markdown('<h2 class="section-title">👥 Participant Demographics</h2>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("**Gender Distribution**")
        
        gender_data = df_clean['gender'].value_counts().reset_index()
        fig7 = px.pie(
            gender_data,
            values='count',
            names='gender',
            hole=0.3,
            color_discrete_map={
                'Male': '#2d5ad7', 
                'Female': '#ec4899', 
                'LGBTQ': '#24d754'  
            }
        )
        fig7.update_layout(height=350)
        st.plotly_chart(fig7, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("**Age Group Distribution**")
        
        # Filter out "Unknown" age groups
        age_data = df_clean[df_clean['age_group'] != 'Unknown']['age_group'].value_counts().reset_index()
        
        # Define the order for age groups
        age_order = ['<18', '18-24', '25-34', '35-44', '45-54', '55+']
        age_data['age_group'] = pd.Categorical(age_data['age_group'], categories=age_order, ordered=True)
        age_data = age_data.sort_values('age_group')
        
        fig8 = px.bar(
            age_data,
            x='age_group',
            y='count',
            color='age_group',
            color_discrete_sequence=px.colors.qualitative.Pastel,
            title='',
            labels={'age_group': 'Age Group', 'count': 'Participants'}
        )
        fig8.update_layout(
            height=350, 
            xaxis_title="Age Group", 
            yaxis_title="Participants",
            xaxis={'categoryorder': 'array', 'categoryarray': age_order}
        )
        st.plotly_chart(fig8, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("**Price Tier Preferences**")
        
        price_tier_data = df_clean['price_tier'].value_counts().reset_index()
        fig9 = px.bar(
            price_tier_data,
            x='price_tier',
            y='count',
            color='price_tier',
            color_discrete_sequence=px.colors.sequential.Viridis,
            title='',
            labels={'price_tier': 'Price Tier', 'count': 'Participants'}
        )
        fig9.update_layout(height=350, xaxis_title="Price Tier", yaxis_title="Participants")
        st.plotly_chart(fig9, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ========== TEMPORAL ANALYSIS SECTION ==========
    st.markdown('<h2 class="section-title">📅 Temporal Analysis</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("**Daily Registration Trend**")
        
        # Daily registrations - Use ALL registrations (raw data)
        df_raw['registerDate'] = pd.to_datetime(df_raw['registerDate'], errors='coerce')
        daily_reg = df_raw.groupby('registerDate').size().reset_index()
        daily_reg.columns = ['Date', 'Registrations']
        daily_reg = daily_reg.sort_values('Date')
        
        fig10 = px.line(
            daily_reg,
            x='Date',
            y='Registrations',
            markers=True,
            title='',
            labels={'Date': 'Date', 'Registrations': 'Daily Registrations'}
        )
        fig10.update_layout(height=350)
        st.plotly_chart(fig10, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("**Registration by Weekday**")
        
        # Registrations by weekday - Use ALL registrations (raw data)
        df_raw['registerDate'] = pd.to_datetime(df_raw['registerDate'], errors='coerce')
        df_raw['weekday'] = df_raw['registerDate'].dt.day_name()
        
        weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        weekday_data = df_raw['weekday'].value_counts().reindex(weekday_order).reset_index()
        weekday_data.columns = ['Weekday', 'Registrations']
        
        fig11 = px.bar(
            weekday_data,
            x='Weekday',
            y='Registrations',
            color='Registrations',
            color_continuous_scale='Sunset',
            title='',
            labels={'Weekday': 'Day of Week', 'Registrations': 'Number of Registrations'}
        )
        fig11.update_layout(height=350)
        st.plotly_chart(fig11, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ========== FOOTER ==========
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #6b7280; padding: 1rem;'>
        <p>📊 <strong>Event Analytics Dashboard</strong> • Part of ThaiDash Analytics Suite</p>
        <p>Data last updated: {}</p>
    </div>
    """.format(
        datetime.now().strftime("%Y-%m-%d %H:%M"),
        f"{len(df_clean):,}"
    ), unsafe_allow_html=True)

# ========== RUN THE APP ==========
if __name__ == "__main__":
    main()