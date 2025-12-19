import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# 1. Page Configuration
st.set_page_config(
    page_title="Maharashtra Corporate Intelligence | CA Tanmay Bhavar",
    page_icon="⚡",
    layout="wide"
)

# 2. Custom CSS for Neon Theme, Hover Effects, and Styling
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #E0E0E0; }
    
    /* Neon Metric Cards with Hover Effect */
    div[data-testid="stMetric"] {
        background-color: #161B22;
        border: 1px solid #00F2FF;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 0 10px #00F2FF33;
        transition: all 0.3s ease-in-out;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 0 25px #00F2FF66;
        border: 1px solid #7000FF;
    }

    /* Professional Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0B0E14;
        border-right: 1px solid #00F2FF33;
    }

    /* Footer Style */
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #0E1117;
        color: #00F2FF;
        text-align: center;
        padding: 8px;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        border-top: 1px solid #00F2FF33;
        z-index: 100;
    }
    
    /* Sleek Download Button */
    .stDownloadButton button {
        background-color: #00F2FF !important;
        color: #0E1117 !important;
        font-weight: bold !important;
        border-radius: 30px !important;
        width: 100%;
        transition: 0.4s !important;
    }
    .stDownloadButton button:hover {
        box-shadow: 0 0 20px #00F2FF !important;
        background-color: #7000FF !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Optimized Data Loading
@st.cache_data
def load_data():
    files = ['companies_part_1.parquet', 'companies_part_2.parquet', 'companies_part_3.parquet']
    df = pd.concat([pd.read_parquet(f) for f in files], ignore_index=True)
    
    # Pre-processing
    df['CompanyRegistrationdate_date'] = pd.to_datetime(df['CompanyRegistrationdate_date'], errors='coerce')
    df['Year'] = df['CompanyRegistrationdate_date'].dt.year
    df['Age'] = datetime.now().year - df['Year']
    df['PaidupCapital_Cr'] = df['PaidupCapital'] / 1e7
    return df

df = load_data()

# --- SIDEBAR & PERSONAL BRANDING ---
st.sidebar.title("⚡ MH Corp Engine")
st.sidebar.markdown(f"Created by: **CA Tanmay Rajendra Bhavar**")
st.sidebar.markdown("[🔗 Connect on LinkedIn](https://www.linkedin.com/in/tbhavar/)")
st.sidebar.divider()

# --- 10 ADVANCED FILTERS & SLICERS ---
with st.sidebar.expander("💰 Financial Slicers", expanded=True):
    cap_range = st.slider("Paid-up Capital (INR Cr)", 0.0, float(df['PaidupCapital_Cr'].max()), (0.0, 10.0))
    hide_zero = st.checkbox("Hide Zero-Capital Companies", value=True)

with st.sidebar.expander("🏢 Industry & Category"):
    selected_ind = st.multiselect("Industrial Classification", options=df['CompanyIndustrialClassification'].unique()[:20])
    selected_sub = st.multiselect("Company Sub-Category", options=df['CompanySubCategory'].unique())
    selected_class = st.multiselect("Company Class", options=df['CompanyClass'].unique(), default=df['CompanyClass'].unique())

with st.sidebar.expander("⏳ Timeline & Age"):
    age_range = st.slider("Company Age (Years)", 0, int(df['Age'].max()), (0, 50))
    selected_status = st.multiselect("Company Status", options=df['CompanyStatus'].unique(), default="Active")

with st.sidebar.expander("📍 Regional & Type"):
    selected_roc = st.multiselect("ROC Code", options=df['CompanyROCcode'].unique())
    selected_type = st.radio("Entity Type", ["All", "Indian", "Foreign"])

# --- FILTER LOGIC ---
filtered_df = df.copy()

if hide_zero: filtered_df = filtered_df[filtered_df['PaidupCapital'] > 0]
filtered_df = filtered_df[(filtered_df['PaidupCapital_Cr'] >= cap_range[0]) & (filtered_df['PaidupCapital_Cr'] <= cap_range[1])]
filtered_df = filtered_df[(filtered_df['Age'] >= age_range[0]) & (filtered_df['Age'] <= age_range[1])]
if selected_ind: filtered_df = filtered_df[filtered_df['CompanyIndustrialClassification'].isin(selected_ind)]
if selected_sub: filtered_df = filtered_df[filtered_df['CompanySubCategory'].isin(selected_sub)]
if selected_class: filtered_df = filtered_df[filtered_df['CompanyClass'].isin(selected_class)]
if selected_status: filtered_df = filtered_df[filtered_df['CompanyStatus'].isin(selected_status)]
if selected_roc: filtered_df = filtered_df[filtered_df['CompanyROCcode'].isin(selected_roc)]
if selected_type != "All": filtered_df = filtered_df[filtered_df['CompanyIndian/Foreign Company'] == selected_type]

# --- MAIN DASHBOARD UI ---
st.title("🏙️ Maharashtra Corporate Insights")
st.markdown("---")

# Row 1: Advanced Search
with st.container():
    col_s1, col_s2, col_s3 = st.columns([2, 2, 1])
    with col_s1:
        search_main = st.text_input("🔍 Search Company Name / CIN", placeholder="e.g. TATA, RELIANCE...")
    with col_s2:
        search_addr = st.text_input("📍 Search City / Locality", placeholder="e.g. Pune, Bandra, Andheri...")
    with col_s3:
        top_n = st.number_input("Top 'N' by Capital", min_value=10, max_value=1000, value=100)

# Apply Text Search
if search_main:
    filtered_df = filtered_df[(filtered_df['CompanyName'].str.contains(search_main, case=False, na=False)) | (filtered_df['CIN'].str.contains(search_main, case=False, na=False))]
if search_addr:
    filtered_df = filtered_df[filtered_df['Registered_Office_Address'].str.contains(search_addr, case=False, na=False)]

# Sort by Top N
filtered_df = filtered_df.nlargest(top_n, 'PaidupCapital')

# Row 2: Metrics
m1, m2, m3, m4 = st.columns(4)
m1.metric("Companies Found", f"{len(filtered_df):,}")
m2.metric("Total Capital", f"₹{filtered_df['PaidupCapital_Cr'].sum():,.2f} Cr")
m3.metric("Avg Age", f"{filtered_df['Age'].mean():.1f} Years")
m4.metric("Foreign Entities", len(filtered_df[filtered_df['CompanyIndian/Foreign Company'] == 'Foreign']))

# Row 3: Visuals
col_left, col_right = st.columns(2)
with col_left:
    fig_bar = px.bar(filtered_df['CompanyIndustrialClassification'].value_counts().head(10), 
                     orientation='h', template="plotly_dark", color_discrete_sequence=['#00F2FF'])
    fig_bar.update_layout(title="Top 10 Industry Sectors (Hover for details)")
    st.plotly_chart(fig_bar, use_container_width=True)

with col_right:
    fig_trend = px.line(filtered_df.groupby('Year').size().reset_index(name='Count'), 
                        x='Year', y='Count', template="plotly_dark")
    fig_trend.update_traces(line_color='#7000FF', line_width=3)
    st.plotly_chart(fig_trend, use_container_width=True)

# Row 4: Data & Export
st.subheader("📋 Custom Generated Report")
csv_data = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Download Filtered Report as CSV",
    data=csv_data,
    file_name=f"CA_Tanmay_Bhavar_Report_{datetime.now().strftime('%Y%m%d')}.csv",
    mime='text/csv'
)
st.dataframe(filtered_df, use_container_width=True)

# --- DISCLAIMER ---
st.divider()
st.info("""
**Professional Disclaimer:** This data is compiled from public MCA records. While every effort is made to maintain 
accuracy, CA Tanmay Rajendra Bhavar is not responsible for any financial decisions made based on this dashboard. 
Users are advised to cross-verify sensitive data with official ROC filings. The data is updated on 3rd November 2023.
""")

# Floating Footer
st.markdown(f'<div class="footer">Dashboard created by CA Tanmay Rajendra Bhavar | <a href="https://www.linkedin.com/in/tbhavar/" style="color:#00F2FF">LinkedIn Connect</a></div>', unsafe_allow_html=True)
