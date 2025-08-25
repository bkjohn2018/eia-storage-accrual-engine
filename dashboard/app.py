"""Streamlit dashboard for EIA Storage Accrual Engine."""

import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="EIA Storage Accrual Engine",
    page_icon="🔋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .status-good { color: #28a745; }
    .status-warning { color: #ffc107; }
    .status-error { color: #dc3545; }
</style>
""", unsafe_allow_html=True)

def main():
    """Main dashboard function."""
    
    # Header
    st.markdown('<h1 class="main-header">🔋 EIA Storage Accrual Engine</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("📊 Dashboard Controls")
        
        # Date selection
        st.subheader("📅 Date Range")
        end_date = st.date_input(
            "As-of Date",
            value=datetime.now().date(),
            max_value=datetime.now().date()
        )
        
        # Region selection
        st.subheader("🌍 Region")
        regions = ["US", "R10", "R20", "R30", "R40", "R50"]
        selected_region = st.selectbox("Select Region", regions, index=0)
        
        # Stratum selection
        st.subheader("🏗️ Storage Type")
        strata = ["All", "Salt", "Non-Salt", "None"]
        selected_stratum = st.selectbox("Select Stratum", strata, index=0)
        
        # Scenario selection
        st.subheader("📈 Scenario")
        scenarios = ["Base", "Low", "High"]
        selected_scenario = st.selectbox("Select Scenario", scenarios, index=0)
        
        # Refresh button
        if st.button("🔄 Refresh Data", type="primary"):
            st.rerun()
    
    # Main content
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="End Working Gas",
            value="2,847 BCF",
            delta="+45 BCF"
        )
    
    with col2:
        st.metric(
            label="% of Capacity",
            value="78.2%",
            delta="-2.1%"
        )
    
    with col3:
        st.metric(
            label="Z-Score vs 5Y",
            value="-0.3",
            delta="+0.1"
        )
    
    with col4:
        st.metric(
            label="Total Accrual",
            value="$1.2M",
            delta="+$45K"
        )
    
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📈 Rollforward", "💰 Accruals", "📋 KPIs"])
    
    with tab1:
        st.header("📊 Storage Overview")
        
        # Placeholder for storage chart
        st.info("📈 Storage trend chart will be displayed here")
        
        # Sample data for demonstration
        dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='W')
        sample_data = pd.DataFrame({
            'date': dates,
            'working_gas_bcf': [2000 + i*10 + (i % 52)*5 for i in range(len(dates))],
            'five_year_avg': [2100 + i*8 for i in range(len(dates))],
            'capacity': [3000] * len(dates)
        })
        
        # Create storage chart
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=sample_data['date'],
            y=sample_data['working_gas_bcf'],
            mode='lines+markers',
            name='Working Gas',
            line=dict(color='#1f77b4', width=2)
        ))
        
        fig.add_trace(go.Scatter(
            x=sample_data['date'],
            y=sample_data['five_year_avg'],
            mode='lines',
            name='5-Year Average',
            line=dict(color='#ff7f0e', width=2, dash='dash')
        ))
        
        fig.add_trace(go.Scatter(
            x=sample_data['date'],
            y=sample_data['capacity'],
            mode='lines',
            name='Working Capacity',
            line=dict(color='#d62728', width=2, dash='dot')
        ))
        
        fig.update_layout(
            title="Natural Gas Storage Trend",
            xaxis_title="Date",
            yaxis_title="BCF",
            hovermode='x unified',
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.header("📈 Monthly Rollforward")
        
        # Placeholder for rollforward table
        st.info("📋 Monthly rollforward data will be displayed here")
        
        # Sample rollforward data
        sample_rollforward = pd.DataFrame({
            'Month End': ['2024-01-31', '2024-02-29', '2024-03-31'],
            'Region': ['US', 'US', 'US'],
            'Stratum': ['All', 'All', 'All'],
            'Beg Working Gas (BCF)': [2500, 2400, 2300],
            'Est Injections (BCF)': [100, 80, 120],
            'Est Withdrawals (BCF)': [200, 180, 250],
            'End Working Gas (BCF)': [2400, 2300, 2170],
            'Gap Days': [3, 2, 4],
            'Estimation Method': ['Blended', 'Blended', 'Blended']
        })
        
        st.dataframe(sample_rollforward, use_container_width=True)
    
    with tab3:
        st.header("💰 Accrual Calculations")
        
        # Placeholder for accruals table
        st.info("💰 Accrual calculations will be displayed here")
        
        # Sample accrual data
        sample_accruals = pd.DataFrame({
            'Month End': ['2024-01-31', '2024-02-29', '2024-03-31'],
            'Region': ['US', 'US', 'US'],
            'Stratum': ['All', 'All', 'All'],
            'Scenario': ['Base', 'Base', 'Base'],
            'Inventory Accrual': [850000, 800000, 750000],
            'Variable Fees': [150000, 140000, 180000],
            'Fixed Demand': [120000, 120000, 120000],
            'Total Accrual': [1120000, 1060000, 1050000],
            'WACOG ($/MMBtu)': [3.25, 3.25, 3.25]
        })
        
        st.dataframe(sample_accruals, use_container_width=True)
        
        # Download button
        csv = sample_accruals.to_csv(index=False)
        st.download_button(
            label="📥 Download Accruals CSV",
            data=csv,
            file_name=f"accruals_{selected_region}_{end_date.strftime('%Y%m')}.csv",
            mime="text/csv"
        )
    
    with tab4:
        st.header("📋 Key Performance Indicators")
        
        # Placeholder for KPIs
        st.info("📊 KPI metrics will be displayed here")
        
        # Sample KPI data
        sample_kpis = pd.DataFrame({
            'Month End': ['2024-01-31', '2024-02-29', '2024-03-31'],
            'Region': ['US', 'US', 'US'],
            'Stratum': ['All', 'All', 'All'],
            'Working Gas (BCF)': [2400, 2300, 2170],
            'Working Capacity (BCF)': [3000, 3000, 3000],
            '% of Working Capacity': [80.0, 76.7, 72.3],
            'Z-Score vs 5Y': [-0.2, -0.5, -0.8],
            'Days of Cover': [45, 43, 41]
        })
        
        st.dataframe(sample_kpis, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>🔋 EIA Storage Accrual Engine | Built for the Energy Industry</p>
        <p>Last updated: {}</p>
    </div>
    """.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
