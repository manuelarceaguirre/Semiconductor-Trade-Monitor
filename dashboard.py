#!/usr/bin/env python3
"""
Streamlit Dashboard for Semiconductor Trade Monitor MVP
Interactive visualizations for semiconductor trade flows
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
import json
from datetime import datetime

class SemiconductorDashboard:
    def __init__(self, db_path="semiconductor_trade.db"):
        self.db_path = db_path
    
    def load_data_from_db(self):
        """Load trade data from SQLite database"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            query = """
                SELECT 
                    tf.period,
                    c1.name as reporter,
                    c2.name as partner,
                    hs.description as commodity,
                    tf.hs6,
                    tf.value_usd,
                    tf.quantity,
                    tf.unit
                FROM trade_flows tf
                JOIN countries c1 ON tf.reporter_iso = c1.iso3
                JOIN countries c2 ON tf.partner_iso = c2.iso3
                JOIN hs_codes hs ON tf.hs6 = hs.hs6
                ORDER BY tf.period DESC, tf.value_usd DESC
            """
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            return df
            
        except Exception as e:
            st.error(f"Database connection error: {e}")
            return pd.DataFrame()
    
    def create_value_trend_chart(self, df, selected_commodity=None):
        """Create line chart showing trade value trends"""
        
        if df.empty:
            return None
            
        # Filter by commodity if selected
        if selected_commodity and selected_commodity != "All":
            df_filtered = df[df['commodity'] == selected_commodity]
        else:
            df_filtered = df
        
        if df_filtered.empty:
            return None
        
        # Group by period and sum values
        trend_data = df_filtered.groupby(['period', 'commodity'])['value_usd'].sum().reset_index()
        
        fig = px.line(
            trend_data, 
            x='period', 
            y='value_usd',
            color='commodity',
            title='Semiconductor Trade Value Trends',
            labels={'value_usd': 'Trade Value (USD)', 'period': 'Year'}
        )
        
        fig.update_layout(
            xaxis_title="Year",
            yaxis_title="Trade Value (USD)",
            yaxis_tickformat="$,.0f"
        )
        
        return fig
    
    def create_country_flow_chart(self, df):
        """Create bar chart showing trade flows between countries"""
        
        if df.empty:
            return None
        
        # Create trade route labels
        df['trade_route'] = df['reporter'] + ' → ' + df['partner']
        
        # Group by trade route and sum values
        flow_data = df.groupby('trade_route')['value_usd'].sum().reset_index()
        flow_data = flow_data.sort_values('value_usd', ascending=True)
        
        fig = px.bar(
            flow_data,
            x='value_usd',
            y='trade_route',
            orientation='h',
            title='Top Semiconductor Trade Routes',
            labels={'value_usd': 'Trade Value (USD)', 'trade_route': 'Trade Route'}
        )
        
        fig.update_layout(
            xaxis_tickformat="$,.0f",
            height=400
        )
        
        return fig
    
    def create_commodity_pie_chart(self, df):
        """Create pie chart showing commodity breakdown"""
        
        if df.empty:
            return None
        
        commodity_data = df.groupby('commodity')['value_usd'].sum().reset_index()
        
        fig = px.pie(
            commodity_data,
            values='value_usd',
            names='commodity',
            title='Trade Value by Semiconductor Category'
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        
        return fig
    
    def display_summary_metrics(self, df):
        """Display key summary metrics"""
        
        if df.empty:
            st.warning("No data available")
            return
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_value = df['value_usd'].sum()
            st.metric("Total Trade Value", f"${total_value/1e9:.1f}B")
        
        with col2:
            unique_routes = len(df[['reporter', 'partner']].drop_duplicates())
            st.metric("Trade Routes", unique_routes)
        
        with col3:
            unique_commodities = df['commodity'].nunique()
            st.metric("Commodities", unique_commodities)
        
        with col4:
            latest_period = df['period'].max()
            st.metric("Latest Data", latest_period)
    
    def display_data_table(self, df):
        """Display detailed data table"""
        
        if df.empty:
            return
        
        # Format the dataframe for display
        display_df = df.copy()
        display_df['value_usd'] = display_df['value_usd'].apply(lambda x: f"${x:,.0f}")
        display_df['quantity'] = display_df['quantity'].apply(lambda x: f"{x:,.0f}")
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
    
    def run_dashboard(self):
        """Main dashboard application"""
        
        # Page configuration
        st.set_page_config(
            page_title="Semiconductor Trade Monitor",
            page_icon="🔬",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Header
        st.title("🔬 Semiconductor Trade Monitor")
        st.markdown("*Real-time insights into global semiconductor trade flows*")
        
        # Load data
        df = self.load_data_from_db()
        
        if df.empty:
            st.error("No data found. Please run the ETL pipeline first.")
            st.code("python3 etl_pipeline.py")
            return
        
        # Sidebar filters
        st.sidebar.header("Filters")
        
        # Commodity filter
        commodities = ["All"] + list(df['commodity'].unique())
        selected_commodity = st.sidebar.selectbox("Select Commodity", commodities)
        
        # Period filter
        periods = sorted(df['period'].unique(), reverse=True)
        selected_periods = st.sidebar.multiselect(
            "Select Periods", 
            periods, 
            default=periods
        )
        
        # Filter data
        if selected_periods:
            df_filtered = df[df['period'].isin(selected_periods)]
        else:
            df_filtered = df
        
        # Summary metrics
        st.header("📊 Overview")
        self.display_summary_metrics(df_filtered)
        
        # Charts
        st.header("📈 Visualizations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Trend chart
            trend_fig = self.create_value_trend_chart(df_filtered, selected_commodity)
            if trend_fig:
                st.plotly_chart(trend_fig, use_container_width=True)
        
        with col2:
            # Pie chart
            pie_fig = self.create_commodity_pie_chart(df_filtered)
            if pie_fig:
                st.plotly_chart(pie_fig, use_container_width=True)
        
        # Country flows chart
        flow_fig = self.create_country_flow_chart(df_filtered)
        if flow_fig:
            st.plotly_chart(flow_fig, use_container_width=True)
        
        # Data table
        st.header("📋 Detailed Data")
        
        if st.checkbox("Show raw data"):
            self.display_data_table(df_filtered)
        
        # Footer
        st.markdown("---")
        st.markdown("*MVP Dashboard - Sample Data*")
        
        # Development info in sidebar
        st.sidebar.markdown("---")
        st.sidebar.header("Development Status")
        st.sidebar.success("✅ ETL Pipeline")
        st.sidebar.success("✅ SQLite Database") 
        st.sidebar.success("✅ Dashboard UI")
        st.sidebar.warning("⏳ API Integration")
        st.sidebar.warning("⏳ Real-time Alerts")

if __name__ == "__main__":
    dashboard = SemiconductorDashboard()
    dashboard.run_dashboard()