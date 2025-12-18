import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(
    page_title="Maharashtra Company Dashboard",
    page_icon="🏢",
    layout="wide"
)

# 2. Data Loading Function (Optimized for 3-part split)
@st.cache_data
def load_combined_data():
    files = [
        'companies_part_1.parquet',
        'companies_part_2.parquet',
        'companies_part_3.parquet'
    ]
    
    # Read and combine the three parts
    df_list = [pd.read_parquet(f) for f in files]
    combined_df = pd.concat(df_list, ignore_index=True)
    
    # Clean up dates and strings
    combined_df['CompanyRegistrationdate_date'] = pd.to_datetime(combined_df['CompanyRegistrationdate_date'], errors='coerce')
    return combined_df

# Load the data
try:
    df = load_combined_data()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# --- SIDEBAR FILTERS ---
st.sidebar.header("🔍 Filter Options")

# Filter by Company Status
status_list = df['CompanyStatus'].unique().tolist()
selected_status = st.sidebar.multiselect("Select Company Status", options=status_list, default=status_list[:3])

# Filter by Company Class
class_list = df['CompanyClass'].unique().tolist()
selected_class = st.sidebar.multiselect("Select Company Class", options=class_list, default=class_list)

# Filter by Year
min_year = int(df['CompanyRegistrationdate_date'].dt.year.min())
max_year = int(df['CompanyRegistrationdate_date'].dt.year.max())
year_range = st.sidebar.slider("Registration Year Range", min_year, max_year, (2000, max_year))

# Apply Filters to DataFrame
mask = (
    df['CompanyStatus'].isin(selected_status) & 
    df['CompanyClass'].isin(selected_class) &
    (df['CompanyRegistrationdate_date'].dt.year >= year_range[0]) &
    (df['CompanyRegistrationdate_date'].dt.year <= year_range[1])
)
filtered_df = df[mask]

# --- MAIN DASHBOARD ---
st.title("🏢 Maharashtra Company Database Insights")
st.markdown(f"Showing results for **{len(filtered_df):,}** companies out of {len(df):,} total.")

# Row 1: KPI Metrics
m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Companies", f"{len(filtered_df):,}")
m2.metric("Total Paid-up Capital", f"₹{filtered_df['PaidupCapital'].sum()/1e7:.2f} Cr")
m3.metric("Avg Auth. Capital", f"₹{filtered_df['AuthorizedCapital'].mean()/1e5:.2f} Lakh")
m4.metric("Active Companies", len(filtered_df[filtered_df['CompanyStatus'] == 'Active']))

st.divider()

# Row 2: Charts
col1, col2 = st.columns(2)

with col1:
    st.subheader("Top 10 Industrial Classifications")
    ind_counts = filtered_df['CompanyIndustrialClassification'].value_counts().head(10).reset_index()
    fig1 = px.bar(ind_counts, x='count', y='CompanyIndustrialClassification', 
                 orientation='h', color='count', color_continuous_scale='Viridis')
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("Company Class Distribution")
    fig2 = px.pie(filtered_df, names='CompanyClass', hole=0.4)
    st.plotly_chart(fig2, use_container_width=True)

# Row 3: Timeline and Search
st.subheader("Registration Growth Over Time")
# Group by year and count
timeline = filtered_df.resample('YE', on='CompanyRegistrationdate_date').size().reset_index(name='New Registrations')
fig3 = px.area(timeline, x='CompanyRegistrationdate_date', y='New Registrations', line_shape='spline')
st.plotly_chart(fig3, use_container_width=True)

st.divider()

# Row 4: Search & Raw Data
st.subheader("🔎 Individual Company Search")
search_query = st.text_input("Enter Company Name or CIN")

if search_query:
    search_results = filtered_df[
        (filtered_df['CompanyName'].str.contains(search_query, case=False, na=False)) |
        (filtered_df['CIN'].str.contains(search_query, case=False, na=False))
    ]
    st.dataframe(search_results)
else:
    st.info("Top 100 rows of filtered data:")
    st.dataframe(filtered_df.head(100))
