import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# 1. Page Configuration
st.set_page_config(
    page_title="Maharashtra Corporate Insights",
    page_icon="⚡",
    layout="wide"
)

# 2. Custom CSS for Neon Theme & Hover Effects
st.markdown("""
    <style>
    /* Main Background */
    .stApp {
        background-color: #0E1117;
        color: #E0E0E0;
    }
    
    /* Neon Glow for Metrics */
    div[data-testid="stMetric"] {
        background-color: #161B22;
        border: 1px solid #00F2FF;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 0 10px #00F2FF33;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    div[data-testid="stMetric"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 0 20px #00F2FF66;
    }

    /* Professional Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #0B0E14;
        border-right: 1px solid #00F2FF33;
    }

    /* Custom Footer Style */
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #0E1117;
        color: #00F2FF;
        text-align: center;
        padding: 10px;
        font-family: 'Courier New', Courier, monospace;
        border-top: 1px solid #00F2FF33;
    }
    
    /* Sleek Download Button */
    .stDownloadButton button {
        background-color: #00F2FF !important;
        color: #0E1117 !important;
        font-weight: bold !important;
        border-radius: 20px !important;
        border: none !important;
        transition: 0.3s !important;
    }
    
    .stDownloadButton button:hover {
        box-shadow: 0 0 15px #00F2FF !important;
        transform: scale(1.05);
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Data Loading
@st.cache_data
def load_combined_data():
    files = ['companies_part_1.parquet', 'companies_part_2.parquet', 'companies_part_3.parquet']
    df = pd.concat([pd.read_parquet(f) for f in files], ignore_index=True)
    df['CompanyRegistrationdate_date'] = pd.to_datetime(df['CompanyRegistrationdate_date'], errors='coerce')
    return df

df = load_combined_data()

# --- SIDEBAR & BRANDING ---
st.sidebar.title("⚡ MH Corp Engine")
st.sidebar.markdown("---")
st.sidebar.info("Created by: **CA Tanmay Rajendra Bhavar**")
st.sidebar.markdown("[Connect on LinkedIn](https://www.linkedin.com/in/tbhavar/)")

# Filters
st.sidebar.header("Global Filters")
status_list = df['CompanyStatus'].unique().tolist()
selected_status = st.sidebar.multiselect("Status", status_list, default="Active")

# --- MAIN DASHBOARD ---
st.title("🏙️ Maharashtra Corporate Insights")
st.caption("Real-time data visualization of regional company registrations.")

# Global Filter Application
filtered_df = df[df['CompanyStatus'].isin(selected_status)]

# --- SEARCH PANEL ---
with st.expander("🔍 Advanced Search (CIN / Company / City / Address)", expanded=True):
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        search_main = st.text_input("Search by Name or CIN", placeholder="e.g. TATA or U12345...")
    with col_s2:
        search_addr = st.text_input("Search by City or Locality (Address)", placeholder="e.g. Pune, Mumbai, Bandra...")

# Filtering logic
if search_main:
    filtered_df = filtered_df[
        (filtered_df['CompanyName'].str.contains(search_main, case=False, na=False)) |
        (filtered_df['CIN'].str.contains(search_main, case=False, na=False))
    ]
if search_addr:
    filtered_df = filtered_df[filtered_df['Registered_Office_Address'].str.contains(search_addr, case=False, na=False)]

# --- METRICS ---
kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric("Result Count", f"{len(filtered_df):,}")
kpi2.metric("Total Paid-up Capital", f"₹{filtered_df['PaidupCapital'].sum()/1e7:.2f} Cr")
kpi3.metric("Avg Auth. Capital", f"₹{filtered_df['AuthorizedCapital'].mean()/1e5:.1f} L")

# --- VISUALIZATIONS ---
c1, c2 = st.columns(2)
with c1:
    fig_ind = px.bar(filtered_df['CompanyIndustrialClassification'].value_counts().head(10), 
                     orientation='h', template="plotly_dark", color_discrete_sequence=['#00F2FF'])
    fig_ind.update_layout(title="Top 10 Sectors", showlegend=False)
    st.plotly_chart(fig_ind, use_container_width=True)

with c2:
    fig_pie = px.pie(filtered_df, names='CompanyClass', hole=0.5, template="plotly_dark")
    fig_pie.update_traces(marker=dict(colors=['#00F2FF', '#7000FF', '#00FF95']))
    st.plotly_chart(fig_pie, use_container_width=True)

# --- DOWNLOAD & DATA TABLE ---
st.divider()
col_d1, col_d2 = st.columns([3, 1])
with col_d1:
    st.subheader("Filtered Data Preview")
with col_d2:
    # CSV Download
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Export Report (CSV)",
        data=csv,
        file_name=f"MH_Companies_Report_{datetime.now().strftime('%Y%m%d')}.csv",
        mime='text/csv',
    )

st.dataframe(filtered_df.head(100), use_container_width=True)

# --- DISCLAIMER ---
st.markdown("---")
st.warning("""
**Disclaimer:** This dashboard is for informational purposes only. The data is sourced from public filings (ROC). 
While every effort is made to ensure accuracy, CA Tanmay Rajendra Bhavar assumes no liability for errors or 
decisions made based on this information.
""")

# Floating Footer
st.markdown('<div class="footer">Dashboard by CA Tanmay Rajendra Bhavar | <a href="https://www.linkedin.com/in/tbhavar/" style="color:#00F2FF">LinkedIn</a></div>', unsafe_allow_html=True)
