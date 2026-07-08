import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

# ==========================================
# 1. PAGE CONFIGURATION & SYSTEM THEME
# ==========================================
st.set_page_config(
    page_title="UAC Care Transition & Placement Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom enterprise styling for government/policy analytics dashboard
st.markdown("""
<style>
    .reportview-container { background: #f8f9fa; }
    .metric-box {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border-left: 5px solid #1f77b4;
    }
    .alert-container {
        background-color: #fff3cd;
        padding: 15px;
        border-radius: 6px;
        border-left: 5px solid #ffc107;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. DATA INGESTION & FEATURE ENGINEERING (FIXED)
# ==========================================
@st.cache_data
def load_and_preprocess_data(file_path):
    if not os.path.exists(file_path):
        st.error(f"Data file '{file_path}' not found. Please place it in the same directory.")
        st.stop()
        
    df = pd.read_csv(file_path)
    
    # Drop rows that are completely empty or missing dates
    df = df.dropna(subset=['Date'])
    
    # Strip any trailing/leading whitespaces from column headers
    df.columns = [c.strip() for c in df.columns]
    
    # --- BULLETPROOF NUMERIC CLEANING ---
    # List of all pipeline metric tracking columns that require conversion to float
    numeric_cols = [
        'Children apprehended and placed in CBP custody*',
        'Children in CBP custody',
        'Children transferred out of CBP custody',
        'Children in HHS Care',
        'Children discharged from HHS Care'
    ]
    
    for col in numeric_cols:
        if col in df.columns:
            # Step A: Convert to string, strip whitespace, and drop commas (e.g., '2,484' -> '2484')
            df[col] = df[col].astype(str).str.replace(',', '', regex=True).str.strip()
            # Step B: Coerce to actual float64, converting any broken values to NaN safely
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
    # Convert Date column to standard datetime and sort chronologically
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date').reset_index(drop=True)
    
    # --- METRICS CALCULATIONS ---
    # Using .replace(0, np.nan) on completely float64 series avoids type collision errors
    df['Transfer Efficiency Ratio'] = df['Children transferred out of CBP custody'] / df['Children in CBP custody'].replace(0, np.nan)
    df['Discharge Effectiveness'] = df['Children discharged from HHS Care'] / df['Children in HHS Care'].replace(0, np.nan)
    df['Pipeline Throughput Rate'] = df['Children discharged from HHS Care'] / df['Children apprehended and placed in CBP custody*'].replace(0, np.nan)
    df['Net Pipeline Accumulation'] = df['Children apprehended and placed in CBP custody*'] - df['Children discharged from HHS Care']
    
    # Temporal attributes for analysis
    df['Day of Week'] = df['Date'].dt.day_name()
    df['Month'] = df['Date'].dt.to_period('M').astype(str)
    
    return df

# Initialize real dataset tracking
FILE_NAME = "HHS_Unaccompanied_Alien_Children_Program.csv"
df_clean = load_and_preprocess_data(FILE_NAME)

# ==========================================
# 3. SIDEBAR / CONTROL PANEL INTERFACES
# ==========================================
st.sidebar.image("https://img.icons8.com/fluency/96/analytics.png", width=60)
st.sidebar.title("UAC Analytics Engine")
st.sidebar.markdown("*U.S. Department of Health and Human Services*")
st.sidebar.divider()

st.sidebar.header("Filter Adjustments")
min_date = df_clean['Date'].min().to_pydatetime()
max_date = df_clean['Date'].max().to_pydatetime()

# Date window selection widget
date_selection = st.sidebar.date_input(
    "Analysis Time Frame", 
    [min_date, max_date], 
    min_value=min_date, 
    max_value=max_date
)

# Guard logic for partial date inputs
if len(date_selection) == 2:
    start_date, end_date = pd.to_datetime(date_selection[0]), pd.to_datetime(date_selection[1])
    df_filtered = df_clean[(df_clean['Date'] >= start_date) & (df_clean['Date'] <= end_date)].copy()
else:
    df_filtered = df_clean.copy()

st.sidebar.header("Alert Settings")
alert_backlog_threshold = st.sidebar.slider(
    "Net Backlog Alert Threshold", 
    min_value=0, max_value=200, value=50, step=10,
    help="Triggers an alert when net intake exceeds discharges by this many children on a single day."
)

alert_throughput_threshold = st.sidebar.slider(
    "Throughput Deficit Warning", 
    min_value=0.2, max_value=1.5, value=0.8, step=0.05,
    help="Triggers a warning when the system exit rate falls below this proportion of arrivals."
)

# ==========================================
# 4. CALCULATION OF SYSTEM AGGREGATES
# ==========================================
avg_transfer_eff = df_filtered['Transfer Efficiency Ratio'].mean()
avg_discharge_eff = df_filtered['Discharge Effectiveness'].mean()
avg_throughput = df_filtered['Pipeline Throughput Rate'].mean()
total_net_backlog = df_filtered['Net Pipeline Accumulation'].sum()

# ==========================================
# 5. MAIN CORE MODULES AND DASHBOARD VISUALS
# ==========================================
st.title("Care Transition Efficiency & Placement Outcome Analytics")
st.markdown("Evaluating processing efficiency, pipeline bottlenecks, and sponsor placement outcomes within the operational care infrastructure.")

# --- SECTION 0: THRESHOLD-BASED VISUAL ALERTS ---
critical_backlog_days = df_filtered[df_filtered['Net Pipeline Accumulation'] >= alert_backlog_threshold]
low_throughput_days = df_filtered[df_filtered['Pipeline Throughput Rate'] < alert_throughput_threshold]

if not critical_backlog_days.empty or not low_throughput_days.empty:
    with st.expander("⚠️ System Operational Alerts & Bottlenecks Detected", expanded=True):
        col_alert_left, col_alert_right = st.columns(2)
        with col_alert_left:
            if not critical_backlog_days.empty:
                st.markdown(
                    f"🔴 **Sustained Imbalance:** `{len(critical_backlog_days)} day(s)` detected where "
                    f"the daily backlog accumulation surpassed **{alert_backlog_threshold}** children."
                )
        with col_alert_right:
            if not low_throughput_days.empty:
                st.markdown(
                    f"⚠️ **Throughput Deficit:** `{len(low_throughput_days)} day(s)` logged where "
                    f"total system exits failed to scale with baseline entry metrics (Exit/Entry < {alert_throughput_threshold:.2f})."
                )

st.divider()

# --- SECTION 1: EXECUTIVE PERFORMANCE KPI TILES ---
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(
        label="Transfer Efficiency Ratio", 
        value=f"{avg_transfer_eff:.2%}" if not np.isnan(avg_transfer_eff) else "N/A", 
        help="Measures CBP to HHS transition speed. Defined as: Transfers ÷ CBP Custody."
    )
with col2:
    st.metric(
        label="Discharge Effectiveness Index", 
        value=f"{avg_discharge_eff:.2%}" if not np.isnan(avg_discharge_eff) else "N/A", 
        help="Measures HHS to Sponsor placement effectiveness. Defined as: Discharges ÷ HHS Care."
    )
with col3:
    st.metric(
        label="Pipeline Throughput Rate", 
        value=f"{avg_throughput:.2%}" if not np.isnan(avg_throughput) else "N/A", 
        help="Measures overall system exit capabilities relative to raw intakes. Defined as: Total Exits ÷ Total Entries."
    )
with col4:
    backlog_color = "inverse" if total_net_backlog > 0 else "normal"
    st.metric(
        label="Net Care Stagnation Volume", 
        value=f"{total_net_backlog:+,g}" if not np.isnan(total_net_backlog) else "N/A", 
        delta="Cumulative Window Net Change", 
        delta_color=backlog_color,
        help="Sum of daily differences between intake volumes and successful sponsor exits."
    )

st.divider()

# --- SECTION 2: MODULE 1 - CARE PIPELINE FLOW VISUALIZATION ---
st.subheader("1. Care Pipeline Flow Visualization")
st.markdown("This Sankey diagram shows the normalized average daily fluid volume passing across key milestones in the care workflow.")

avg_apprehensions = df_filtered['Children apprehended and placed in CBP custody*'].mean()
avg_transfers = df_filtered['Children transferred out of CBP custody'].mean()
avg_discharges = df_filtered['Children discharged from HHS Care'].mean()

# Fill with 0 if values evaluate to NaN to avoid diagram failures
avg_apprehensions = 0 if np.isnan(avg_apprehensions) else avg_apprehensions
avg_transfers = 0 if np.isnan(avg_transfers) else avg_transfers
avg_discharges = 0 if np.isnan(avg_discharges) else avg_discharges

sankey_fig = go.Figure(data=[go.Sankey(
    node=dict(
        pad=20,
        thickness=25,
        line=dict(color="black", width=0.5),
        label=["CBP Apprehensions (Intake)", "Active CBP Custody Status", "Active HHS Care Capacity", "Sponsor Placement (Exits)"],
        color=["#2b5c8f", "#e06666", "#f6b26b", "#6aa84f"]
    ),
    link=dict(
        source=[0, 1, 2], 
        target=[1, 2, 3],
        value=[avg_apprehensions, avg_transfers, avg_discharges],
        color="rgba(211, 211, 211, 0.5)"
    )
)])
sankey_fig.update_layout(height=320, margin=dict(l=10, r=10, t=10, b=10))
st.plotly_chart(sankey_fig, use_container_width=True)


# --- SECTION 3: MODULE 2 - EFFICIENCY PANELS ---
st.subheader("2. Transfer & Discharge Efficiency Panels")
tab_ratios, tab_equilibrium = st.tabs(["Process Efficiency Ratios", "Intake vs. Exit Volume Tracking"])

with tab_ratios:
    fig_ratios = go.Figure()
    fig_ratios.add_trace(go.Scatter(x=df_filtered['Date'], y=df_filtered['Transfer Efficiency Ratio'], name='CBP → HHS Transfer Efficiency', line=dict(color='#1f77b4', width=2)))
    fig_ratios.add_trace(go.Scatter(x=df_filtered['Date'], y=df_filtered['Discharge Effectiveness'], name='HHS → Sponsor Discharge Effectiveness', line=dict(color='#ff7f0e', width=2)))
    fig_ratios.update_layout(title="Daily Conversion Efficiency Ratios Over Time", yaxis=dict(tickformat=".0%"), xaxis_title="Timeline Date", height=400, margin=dict(t=40, b=40))
    st.plotly_chart(fig_ratios, use_container_width=True)

with tab_equilibrium:
    fig_eq = go.Figure()
    fig_eq.add_trace(go.Bar(x=df_filtered['Date'], y=df_filtered['Children apprehended and placed in CBP custody*'], name='Daily Apprehensions (System Inflow)', marker_color='#9467bd', opacity=0.7))
    fig_eq.add_trace(go.Scatter(x=df_filtered['Date'], y=df_filtered['Children discharged from HHS Care'], name='Daily Placements (System Outflow)', line=dict(color='#2ca02c', width=2)))
    fig_eq.update_layout(title="System Equilibrium Tracking (Inflow Volumes vs. Output Discharges)", barmode='overlay', xaxis_title="Timeline Date", height=400, margin=dict(t=40, b=40))
    st.plotly_chart(fig_eq, use_container_width=True)


# --- SECTION 4: MODULES 3 & 4 - BOTTLENECK DETECTION & TEMPORAL PATTERNS ---
col_bottleneck, col_stability = st.columns(2)

with col_bottleneck:
    st.subheader("3. Weekday vs. Weekend Bottleneck Detection")
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    dow_analysis = df_filtered.groupby('Day of Week')[['Transfer Efficiency Ratio', 'Discharge Effectiveness']].mean().reindex(day_order)
    
    fig_dow = px.bar(
        dow_analysis, 
        barmode='group',
        title="Processing Efficiency Index by Day of Week",
        labels={'value': 'Calculated Operational Ratio', 'Day of Week': 'Day of Week'},
        color_discrete_sequence=['#1f77b4', '#ff7f0e']
    )
    fig_dow.update_layout(yaxis=dict(tickformat=".0%"), height=350, margin=dict(t=40, b=40))
    st.plotly_chart(fig_dow, use_container_width=True)
    st.caption("Lower operational index scores during weekends identify potential staffing imbalances or administrative constraints.")

with col_stability:
    st.subheader("4. Month-over-Month Outcome Stability")
    mom_analysis = df_filtered.groupby('Month')[['Pipeline Throughput Rate', 'Net Pipeline Accumulation']].agg(
        {'Pipeline Throughput Rate': 'mean', 'Net Pipeline Accumulation': 'sum'}
    ).reset_index()
    
    fig_mom = px.line(
        mom_analysis, x='Month', y='Pipeline Throughput Rate',
        title="Month-over-Month System Throughput Track",
        markers=True, line_shape="linear"
    )
    fig_mom.update_layout(yaxis=dict(tickformat=".0%"), height=350, margin=dict(t=40, b=40))
    st.plotly_chart(fig_mom, use_container_width=True)
    st.caption("Values consistently trailing below 100% identify prolonged periods of accelerating shelter capacity pressures.")

# --- SECTION 5: DATA EXPORT SECTION ---
st.divider()
st.subheader("Processed Analytics Dataset View")
st.markdown("Provides the underlying granular daily metric performance tables computed above.")
st.dataframe(df_filtered, use_container_width=True)