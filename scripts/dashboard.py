"""
QuantumTrader Advanced Dashboard
=================================
Professional monitoring dashboard for backtest results and live trading.

Features:
- 📊 Backtest Results Viewer with interactive charts
- 📈 Live Performance Monitoring
- 🔍 Strategy Comparison
- 📉 Advanced Analytics
- 🎯 Risk Metrics

Author: QuantumTrader Team
Date: November 2025
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from pathlib import Path
import json
from datetime import datetime, timedelta
import numpy as np

# Page config
st.set_page_config(
    page_title="QuantumTrader Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .positive {
        color: #10b981;
        font-weight: bold;
    }
    .negative {
        color: #ef4444;
        font-weight: bold;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 1.1rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">📊 QuantumTrader Dashboard</h1>', unsafe_allow_html=True)
st.markdown("**Professional Algorithmic Trading Analysis Platform**")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/200x60/667eea/ffffff?text=QuantumTrader", use_container_width=True)
    st.markdown("### 🎯 Navigation")
    
    # File uploader for backtest results
    st.markdown("### 📁 Load Backtest Results")
    reports_dir = Path("reports")
    
    if reports_dir.exists():
        excel_files = list(reports_dir.glob("*_backtest_*.xlsx"))
        if excel_files:
            selected_file = st.selectbox(
                "Select Report",
                excel_files,
                format_func=lambda x: x.name
            )
        else:
            st.warning("No backtest reports found in /reports")
            selected_file = None
    else:
        st.warning("Reports directory not found")
        selected_file = None
    
    uploaded_file = st.file_uploader("Or Upload Excel Report", type=['xlsx'])
    
    st.markdown("---")
    st.markdown("### ⚙️ Settings")
    show_costs = st.checkbox("Show Cost Breakdown", value=True)
    show_drawdown = st.checkbox("Show Drawdown Chart", value=True)
    chart_theme = st.selectbox("Chart Theme", ["plotly", "plotly_dark", "plotly_white"])
    
    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.markdown("""
    **Version**: 2.0.0  
    **Engine**: Advanced Backtest v2  
    **Database**: Supabase Cloud  
    **Status**: ✅ Production Ready
    """)

# Load data function
@st.cache_data
def load_backtest_data(file_path):
    """Load backtest Excel report"""
    try:
        # Load all sheets
        trades_df = pd.read_excel(file_path, sheet_name='Trades')
        metrics_df = pd.read_excel(file_path, sheet_name='Performance Metrics')
        monthly_df = pd.read_excel(file_path, sheet_name='Monthly Returns')
        
        # Parse metrics
        metrics = {}
        for _, row in metrics_df.iterrows():
            metrics[row['Metric']] = row['Value']
        
        return trades_df, metrics, monthly_df
    except Exception as e:
        st.error(f"Error loading file: {str(e)}")
        return None, None, None

# Main content
if selected_file or uploaded_file:
    file_to_load = uploaded_file if uploaded_file else selected_file
    
    trades_df, metrics, monthly_df = load_backtest_data(file_to_load)
    
    if trades_df is not None:
        # Create tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Overview", 
            "📈 Performance", 
            "💹 Trades", 
            "📉 Risk Analysis",
            "🔍 Advanced"
        ])
        
        # TAB 1: Overview
        with tab1:
            st.markdown("## 📊 Backtest Overview")
            
            # Key metrics in columns
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                initial_balance = metrics.get('Initial Balance', 10000)
                final_balance = metrics.get('Final Balance', 0)
                total_return = metrics.get('Total Return (%)', 0)
                
                st.metric(
                    "Final Balance",
                    f"${final_balance:,.2f}",
                    f"{total_return:.2f}%",
                    delta_color="normal"
                )
            
            with col2:
                total_trades = metrics.get('Total Trades', 0)
                win_rate = metrics.get('Win Rate (%)', 0)
                st.metric(
                    "Total Trades",
                    f"{int(total_trades):,}",
                    f"Win Rate: {win_rate:.1f}%"
                )
            
            with col3:
                profit_factor = metrics.get('Profit Factor', 0)
                st.metric(
                    "Profit Factor",
                    f"{profit_factor:.2f}",
                    "Good" if profit_factor > 1.5 else "Needs Improvement"
                )
            
            with col4:
                max_dd = metrics.get('Max Drawdown (%)', 0)
                st.metric(
                    "Max Drawdown",
                    f"{max_dd:.2f}%",
                    "High Risk" if abs(max_dd) > 30 else "Acceptable"
                )
            
            st.markdown("---")
            
            # Equity curve
            st.markdown("### 📈 Equity Curve")
            
            if 'Exit Time' in trades_df.columns and 'Net P&L' in trades_df.columns:
                # Calculate cumulative equity
                trades_df['Exit Time'] = pd.to_datetime(trades_df['Exit Time'])
                trades_df = trades_df.sort_values('Exit Time')
                trades_df['Cumulative P&L'] = trades_df['Net P&L'].cumsum()
                trades_df['Equity'] = initial_balance + trades_df['Cumulative P&L']
                
                # Create equity chart
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=trades_df['Exit Time'],
                    y=trades_df['Equity'],
                    mode='lines',
                    name='Equity',
                    line=dict(color='#667eea', width=2),
                    fill='tozeroy',
                    fillcolor='rgba(102, 126, 234, 0.1)'
                ))
                
                # Add initial balance line
                fig.add_hline(
                    y=initial_balance,
                    line_dash="dash",
                    line_color="gray",
                    annotation_text="Initial Balance"
                )
                
                fig.update_layout(
                    template=chart_theme,
                    height=400,
                    xaxis_title="Date",
                    yaxis_title="Equity ($)",
                    hovermode='x unified',
                    showlegend=True
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Stats cards
            st.markdown("### 📊 Detailed Statistics")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("#### 🎯 Trade Statistics")
                winning_trades = metrics.get('Winning Trades', 0)
                losing_trades = metrics.get('Losing Trades', 0)
                avg_win = metrics.get('Average Win ($)', 0)
                avg_loss = metrics.get('Average Loss ($)', 0)
                
                st.write(f"**Winning Trades**: {int(winning_trades)}")
                st.write(f"**Losing Trades**: {int(losing_trades)}")
                st.write(f"**Average Win**: ${avg_win:,.2f}")
                st.write(f"**Average Loss**: ${avg_loss:,.2f}")
            
            with col2:
                st.markdown("#### 📉 Risk Metrics")
                sharpe = metrics.get('Sharpe Ratio', 0)
                sortino = metrics.get('Sortino Ratio', 0)
                max_dd_dollar = metrics.get('Max Drawdown ($)', 0)
                
                st.write(f"**Sharpe Ratio**: {sharpe:.3f}")
                st.write(f"**Sortino Ratio**: {sortino:.3f}")
                st.write(f"**Max DD ($)**: ${max_dd_dollar:,.2f}")
            
            with col3:
                if show_costs:
                    st.markdown("#### 💸 Costs Breakdown")
                    total_costs = metrics.get('Total Costs ($)', 0)
                    commission = metrics.get('Total Commission ($)', 0)
                    spread = metrics.get('Total Spread ($)', 0)
                    
                    st.write(f"**Total Costs**: ${total_costs:,.2f}")
                    st.write(f"**Commission**: ${commission:,.2f}")
                    st.write(f"**Spread**: ${spread:,.2f}")
        
        # TAB 2: Performance
        with tab2:
            st.markdown("## 📈 Performance Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Win/Loss distribution
                st.markdown("### 🎯 Win/Loss Distribution")
                
                wins = trades_df[trades_df['Net P&L'] > 0]['Net P&L']
                losses = trades_df[trades_df['Net P&L'] <= 0]['Net P&L']
                
                fig = go.Figure()
                
                fig.add_trace(go.Histogram(
                    x=wins,
                    name='Wins',
                    marker_color='#10b981',
                    opacity=0.7,
                    nbinsx=30
                ))
                
                fig.add_trace(go.Histogram(
                    x=losses,
                    name='Losses',
                    marker_color='#ef4444',
                    opacity=0.7,
                    nbinsx=30
                ))
                
                fig.update_layout(
                    template=chart_theme,
                    height=350,
                    barmode='overlay',
                    xaxis_title='P&L ($)',
                    yaxis_title='Frequency'
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Monthly returns heatmap
                st.markdown("### 📅 Monthly Returns")
                
                if not monthly_df.empty and 'Month' in monthly_df.columns:
                    # Prepare data for heatmap
                    monthly_pivot = monthly_df.pivot_table(
                        values='Return (%)',
                        index='Year',
                        columns='Month',
                        aggfunc='sum'
                    )
                    
                    fig = go.Figure(data=go.Heatmap(
                        z=monthly_pivot.values,
                        x=monthly_pivot.columns,
                        y=monthly_pivot.index,
                        colorscale='RdYlGn',
                        text=monthly_pivot.values,
                        texttemplate='%{text:.1f}%',
                        textfont={"size": 10},
                        colorbar=dict(title="Return %")
                    ))
                    
                    fig.update_layout(
                        template=chart_theme,
                        height=350,
                        xaxis_title='Month',
                        yaxis_title='Year'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
            
            # Drawdown chart
            if show_drawdown:
                st.markdown("### 📉 Drawdown Analysis")
                
                if 'Cumulative P&L' in trades_df.columns:
                    # Calculate running drawdown
                    cumulative_max = trades_df['Equity'].cummax()
                    drawdown = trades_df['Equity'] - cumulative_max
                    drawdown_pct = (drawdown / cumulative_max) * 100
                    
                    fig = go.Figure()
                    
                    fig.add_trace(go.Scatter(
                        x=trades_df['Exit Time'],
                        y=drawdown_pct,
                        mode='lines',
                        name='Drawdown',
                        line=dict(color='#ef4444', width=2),
                        fill='tozeroy',
                        fillcolor='rgba(239, 68, 68, 0.1)'
                    ))
                    
                    fig.update_layout(
                        template=chart_theme,
                        height=300,
                        xaxis_title='Date',
                        yaxis_title='Drawdown (%)',
                        hovermode='x unified'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
        
        # TAB 3: Trades
        with tab3:
            st.markdown("## 💹 Trade Analysis")
            
            # Filters
            col1, col2, col3 = st.columns(3)
            
            with col1:
                trade_filter = st.selectbox(
                    "Filter Trades",
                    ["All Trades", "Winning Trades", "Losing Trades"]
                )
            
            with col2:
                if 'Direction' in trades_df.columns:
                    direction_filter = st.selectbox(
                        "Direction",
                        ["All", "BUY", "SELL"]
                    )
                else:
                    direction_filter = "All"
            
            with col3:
                sort_by = st.selectbox(
                    "Sort By",
                    ["Exit Time", "Net P&L", "Duration (hours)", "Return (%)"]
                )
            
            # Apply filters
            filtered_df = trades_df.copy()
            
            if trade_filter == "Winning Trades":
                filtered_df = filtered_df[filtered_df['Net P&L'] > 0]
            elif trade_filter == "Losing Trades":
                filtered_df = filtered_df[filtered_df['Net P&L'] <= 0]
            
            if direction_filter != "All" and 'Direction' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['Direction'] == direction_filter]
            
            # Sort
            if sort_by in filtered_df.columns:
                filtered_df = filtered_df.sort_values(sort_by, ascending=False)
            
            # Display stats
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Filtered Trades", len(filtered_df))
            with col2:
                avg_pnl = filtered_df['Net P&L'].mean()
                st.metric("Avg P&L", f"${avg_pnl:.2f}")
            with col3:
                total_pnl = filtered_df['Net P&L'].sum()
                st.metric("Total P&L", f"${total_pnl:.2f}")
            with col4:
                if len(filtered_df) > 0:
                    win_rate_filtered = (filtered_df['Net P&L'] > 0).sum() / len(filtered_df) * 100
                    st.metric("Win Rate", f"{win_rate_filtered:.1f}%")
            
            st.markdown("---")
            
            # Trade table
            st.markdown("### 📋 Trade History")
            
            # Format columns for display
            display_df = filtered_df.copy()
            
            # Color code P&L
            def color_pnl(val):
                color = 'green' if val > 0 else 'red'
                return f'color: {color}'
            
            if 'Net P&L' in display_df.columns:
                st.dataframe(
                    display_df.style.applymap(color_pnl, subset=['Net P&L']),
                    use_container_width=True,
                    height=400
                )
            else:
                st.dataframe(display_df, use_container_width=True, height=400)
            
            # Download button
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                "📥 Download Filtered Trades (CSV)",
                csv,
                "filtered_trades.csv",
                "text/csv"
            )
        
        # TAB 4: Risk Analysis
        with tab4:
            st.markdown("## 📉 Risk Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Risk metrics gauge
                st.markdown("### 🎯 Risk Score")
                
                # Calculate risk score (0-100)
                sharpe = metrics.get('Sharpe Ratio', 0)
                max_dd_pct = abs(metrics.get('Max Drawdown (%)', 0))
                win_rate = metrics.get('Win Rate (%)', 0)
                
                risk_score = min(100, max(0, (
                    (sharpe + 2) * 20 +  # Sharpe contribution
                    (1 - max_dd_pct/100) * 30 +  # Drawdown contribution
                    win_rate * 0.5  # Win rate contribution
                )))
                
                fig = go.Figure(go.Indicator(
                    mode="gauge+number+delta",
                    value=risk_score,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Risk Score"},
                    delta={'reference': 50},
                    gauge={
                        'axis': {'range': [None, 100]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': [0, 30], 'color': "#ef4444"},
                            {'range': [30, 70], 'color': "#f59e0b"},
                            {'range': [70, 100], 'color': "#10b981"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 90
                        }
                    }
                ))
                
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
                
                # Risk interpretation
                if risk_score >= 70:
                    st.success("✅ **Low Risk** - Strategy shows good risk management")
                elif risk_score >= 40:
                    st.warning("⚠️ **Medium Risk** - Consider optimizing parameters")
                else:
                    st.error("🔴 **High Risk** - Strategy needs significant improvements")
            
            with col2:
                # Consecutive wins/losses
                st.markdown("### 📊 Consecutive Trades")
                
                # Calculate streaks
                trades_df['Win'] = trades_df['Net P&L'] > 0
                trades_df['Streak'] = (trades_df['Win'] != trades_df['Win'].shift()).cumsum()
                
                win_streaks = trades_df[trades_df['Win']].groupby('Streak').size()
                loss_streaks = trades_df[~trades_df['Win']].groupby('Streak').size()
                
                max_win_streak = win_streaks.max() if len(win_streaks) > 0 else 0
                max_loss_streak = loss_streaks.max() if len(loss_streaks) > 0 else 0
                
                st.metric("Max Consecutive Wins", f"{max_win_streak}")
                st.metric("Max Consecutive Losses", f"{max_loss_streak}")
                
                # Risk-reward ratio
                if 'Return (%)' in trades_df.columns:
                    avg_win_pct = trades_df[trades_df['Net P&L'] > 0]['Return (%)'].mean()
                    avg_loss_pct = abs(trades_df[trades_df['Net P&L'] <= 0]['Return (%)'].mean())
                    
                    if avg_loss_pct > 0:
                        rr_ratio = avg_win_pct / avg_loss_pct
                        st.metric("Risk/Reward Ratio", f"1:{rr_ratio:.2f}")
            
            # Recovery factor
            st.markdown("### 📈 Recovery Analysis")
            
            total_profit = metrics.get('Total Net Profit ($)', 0)
            max_dd_dollar = abs(metrics.get('Max Drawdown ($)', 0))
            
            if max_dd_dollar > 0:
                recovery_factor = total_profit / max_dd_dollar
            else:
                recovery_factor = 0
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Profit", f"${total_profit:,.2f}")
            with col2:
                st.metric("Max Drawdown", f"${max_dd_dollar:,.2f}")
            with col3:
                st.metric("Recovery Factor", f"{recovery_factor:.2f}")
            
            if recovery_factor > 3:
                st.success("✅ Excellent recovery capability")
            elif recovery_factor > 1.5:
                st.info("ℹ️ Good recovery capability")
            else:
                st.warning("⚠️ Poor recovery capability - high drawdown relative to profit")
        
        # TAB 5: Advanced
        with tab5:
            st.markdown("## 🔍 Advanced Analytics")
            
            # Time-based analysis
            st.markdown("### ⏰ Performance by Time")
            
            if 'Entry Time' in trades_df.columns:
                trades_df['Entry Time'] = pd.to_datetime(trades_df['Entry Time'])
                trades_df['Hour'] = trades_df['Entry Time'].dt.hour
                trades_df['DayOfWeek'] = trades_df['Entry Time'].dt.day_name()
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Performance by hour
                    hourly_pnl = trades_df.groupby('Hour')['Net P&L'].sum()
                    
                    fig = go.Figure(data=[
                        go.Bar(
                            x=hourly_pnl.index,
                            y=hourly_pnl.values,
                            marker_color=['#10b981' if x > 0 else '#ef4444' for x in hourly_pnl.values]
                        )
                    ])
                    
                    fig.update_layout(
                        template=chart_theme,
                        title="P&L by Hour of Day",
                        xaxis_title="Hour",
                        yaxis_title="Total P&L ($)",
                        height=300,
                        showlegend=False
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Performance by day of week
                    daily_pnl = trades_df.groupby('DayOfWeek')['Net P&L'].sum()
                    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
                    daily_pnl = daily_pnl.reindex([d for d in day_order if d in daily_pnl.index])
                    
                    fig = go.Figure(data=[
                        go.Bar(
                            x=daily_pnl.index,
                            y=daily_pnl.values,
                            marker_color=['#10b981' if x > 0 else '#ef4444' for x in daily_pnl.values]
                        )
                    ])
                    
                    fig.update_layout(
                        template=chart_theme,
                        title="P&L by Day of Week",
                        xaxis_title="Day",
                        yaxis_title="Total P&L ($)",
                        height=300,
                        showlegend=False
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
            
            # Trade duration analysis
            st.markdown("### ⏱️ Trade Duration Analysis")
            
            if 'Duration (hours)' in trades_df.columns:
                col1, col2 = st.columns(2)
                
                with col1:
                    # Duration vs P&L scatter
                    fig = px.scatter(
                        trades_df,
                        x='Duration (hours)',
                        y='Net P&L',
                        color='Net P&L',
                        color_continuous_scale=['red', 'yellow', 'green'],
                        title="Trade Duration vs P&L"
                    )
                    
                    fig.update_layout(
                        template=chart_theme,
                        height=300
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Duration distribution
                    fig = go.Figure(data=[
                        go.Histogram(
                            x=trades_df['Duration (hours)'],
                            nbinsx=30,
                            marker_color='#667eea'
                        )
                    ])
                    
                    fig.update_layout(
                        template=chart_theme,
                        title="Trade Duration Distribution",
                        xaxis_title="Duration (hours)",
                        yaxis_title="Frequency",
                        height=300
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
            
            # Export all data
            st.markdown("### 📥 Export Data")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📊 Export Summary JSON"):
                    summary = {
                        "backtest_summary": {
                            "file": str(selected_file.name) if selected_file else "uploaded_file.xlsx",
                            "date": datetime.now().isoformat(),
                            "metrics": metrics,
                            "total_trades": len(trades_df)
                        }
                    }
                    
                    st.download_button(
                        "Download JSON",
                        json.dumps(summary, indent=2),
                        "backtest_summary.json",
                        "application/json"
                    )
            
            with col2:
                csv_all = trades_df.to_csv(index=False)
                st.download_button(
                    "📋 Export All Trades CSV",
                    csv_all,
                    "all_trades.csv",
                    "text/csv"
                )
            
            with col3:
                if not monthly_df.empty:
                    csv_monthly = monthly_df.to_csv(index=False)
                    st.download_button(
                        "📅 Export Monthly Returns",
                        csv_monthly,
                        "monthly_returns.csv",
                        "text/csv"
                    )

else:
    # Welcome screen
    st.markdown("""
    ## 👋 Welcome to QuantumTrader Dashboard!
    
    ### 🚀 Get Started:
    
    1. **Load a backtest report** from the sidebar
    2. **Explore interactive charts** and analytics
    3. **Analyze performance** across multiple dimensions
    4. **Export results** for further analysis
    
    ### 📊 Features:
    
    - **Overview**: Key metrics and equity curve
    - **Performance**: Win/loss distribution, monthly returns, drawdown analysis
    - **Trades**: Detailed trade history with filters
    - **Risk Analysis**: Risk score, streaks, recovery factor
    - **Advanced**: Time-based analysis, duration vs P&L
    
    ### 📁 Supported Files:
    
    - Excel backtest reports from QuantumTrader backtest engine
    - Reports located in `/reports` directory
    - Upload custom reports via file uploader
    
    ---
    
    **No backtest reports found?** Run a backtest first:
    
    ```bash
    python examples/working_backtest.py
    ```
    
    The report will be automatically saved to `/reports` directory.
    """)
    
    # Sample metrics display
    st.markdown("### 📈 Sample Dashboard Preview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Sample Balance", "$8,323.62", "-16.76%")
    with col2:
        st.metric("Sample Trades", "117", "Win Rate: 41.8%")
    with col3:
        st.metric("Sample PF", "0.84", "Needs Improvement")
    with col4:
        st.metric("Sample DD", "-83.11%", "High Risk")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>QuantumTrader Dashboard v2.0.0 | Built with ❤️ using Streamlit & Plotly</p>
    <p>Professional Algorithmic Trading Analysis Platform</p>
</div>
""", unsafe_allow_html=True)
