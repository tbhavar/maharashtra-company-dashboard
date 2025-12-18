import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide", page_title="Maharashtra Company Dashboard")

@st.cache_data
def load_data():
    # Use parquet for speed
    df = pd.read_parquet("companies_mh.parquet")
    df['CompanyRegistrationdate_date'] = pd.to_datetime(df['CompanyRegistrationdate_date'])
    return df

df = load_data()

# --- SIDEBAR FILTERS ---
st.sidebar.header("Filters")
status = st.sidebar.multiselect("Company Status", options=df["CompanyStatus"].unique())
category = st.sidebar.multiselect("Category", options=df["CompanyCategory"].unique())

# Filter data
filtered_df = df.copy()
if status:
    filtered_df = filtered_df[filtered_df["CompanyStatus"].isin(status)]
if category:
    filtered_df = filtered_df[filtered_df["CompanyCategory"].isin(category)]

# --- DASHBOARD LAYOUT ---
st.title("🏢 Maharashtra Company Insights")

# Key Metrics
col1, col2, col3 = st.columns(3)
col1.metric("Total Companies", len(filtered_df))
col2.metric("Total Paid-up Capital", f"₹{filtered_df['PaidupCapital'].sum():,.0f}")
col3.metric("Foreign Companies", len(filtered_df[filtered_df["CompanyIndian/Foreign Company"] == "Foreign"]))

# Charts
fig_col1, fig_col2 = st.columns(2)

with fig_col1:
    st.subheader("Distribution by Class")
    fig = px.pie(filtered_df, names='CompanyClass')
    st.plotly_chart(fig, use_container_width=True)

with fig_col2:
    st.subheader("Registration Trend")
    trend = filtered_df.resample('YE', on='CompanyRegistrationdate_date').size().reset_index(name='Counts')
    fig2 = px.line(trend, x='CompanyRegistrationdate_date', y='Counts')
    st.plotly_chart(fig2, use_container_width=True)

st.subheader("Data Preview")
st.dataframe(filtered_df.head(100))
