import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os
from datetime import datetime, timedelta
import json

# Set page configuration
st.set_page_config(
    page_title="COVID-19 Dashboard",
    page_icon="🦠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for theming
def local_css():
    st.markdown("""
    <style>
        .main {
            background-color: #f5f5f5;
        }
        .stApp {
            max-width: 1200px;
            margin: 0 auto;
        }
        h1, h2, h3 {
            color: #1E3A8A;
        }
        .stMetric {
            background-color: #ffffff;
            border-radius: 5px;
            padding: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .stPlotlyChart {
            background-color: white;
            border-radius: 5px;
            padding: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .sidebar .sidebar-content {
            background-color: #1E3A8A;
            color: white;
        }
        .sidebar .sidebar-content .stRadio label {
            color: white;
        }
    </style>
    """, unsafe_allow_html=True)

local_css()

# Load data function
@st.cache_data(ttl=3600)
def load_data():
    try:
        df = pd.read_csv('data/processed_covid_data.csv')
        df['date'] = pd.to_datetime(df['date'])
        with open('data/last_updated.txt', 'r') as f:
            last_updated = f.read().strip()
        return df, last_updated
    except FileNotFoundError:
        st.error("Data files not found. Please run the data pipeline notebook first.")
        st.stop()

# Main function
def main():
    # Header
    st.title("🦠 COVID-19 Trends Dashboard")
    
    # Load data
    data, last_updated = load_data()
    
    # Last updated info
    st.markdown(f"*Last updated: {last_updated}*")
    
    # Sidebar for filtering
    st.sidebar.title("Filters")
    
    # Country filter
    countries = sorted(data['country'].unique())
    selected_countries = st.sidebar.multiselect(
        "Select Countries",
        options=countries,
        default=["United States", "India", "Brazil", "United Kingdom"]
    )
    
    # Date filter
    date_range = st.sidebar.date_input(
        "Date Range",
        value=(data['date'].min().date(), data['date'].max().date()),
        min_value=data['date'].min().date(),
        max_value=data['date'].max().date()
    )
    
    # Metric filter
    metric_options = ["new_cases", "new_deaths", "total_cases", "total_deaths", 
                     "new_vaccinations", "people_fully_vaccinated"]
    selected_metric = st.sidebar.selectbox(
        "Select Metric",
        options=metric_options,
        format_func=lambda x: x.replace('_', ' ').title()
    )
    
    # View options
    view_options = ["Overview", "Time Series Analysis", "Country Comparison", "Vaccination Progress"]
    selected_view = st.sidebar.radio("Select View", view_options)
    
    # Filter data
    if selected_countries:
        filtered_data = data[data['country'].isin(selected_countries)]
    else:
        filtered_data = data
    
    # Date range filter
    start_date = pd.Timestamp(date_range[0])
    end_date = pd.Timestamp(date_range[1])
    filtered_data = filtered_data[(filtered_data['date'] >= start_date) & 
                                 (filtered_data['date'] <= end_date)]
    
    # Show selected view
    if selected_view == "Overview":
        display_overview(filtered_data)
    elif selected_view == "Time Series Analysis":
        display_time_series(filtered_data, selected_metric, selected_countries)
    elif selected_view == "Country Comparison":
        display_country_comparison(filtered_data, selected_metric)
    elif selected_view == "Vaccination Progress":
        display_vaccination_progress(filtered_data)

def display_overview(data):
    st.header("Global COVID-19 Overview")
    
    # Calculate summary stats
    latest_date = data['date'].max()
    latest_data = data[data['date'] == latest_date]
    
    total_cases = latest_data['total_cases'].sum()
    total_deaths = latest_data['total_deaths'].sum()
    avg_mortality = (total_deaths / total_cases) * 100 if total_cases > 0 else 0
    
    # Create columns for metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Confirmed Cases", f"{total_cases:,.0f}")
    
    with col2:
        st.metric("Total Deaths", f"{total_deaths:,.0f}")
    
    with col3:
        st.metric("Average Mortality Rate", f"{avg_mortality:.2f}%")
    
    # Create a world map of cases
    st.subheader("Global Distribution of Cases")
    fig = px.choropleth(
        latest_data,
        locations="iso_code",
        color="total_cases",
        hover_name="country",
        color_continuous_scale="Viridis",
        title="Total Confirmed Cases by Country",
        projection="natural earth"
    )
    fig.update_layout(margin=dict(l=0, r=0, b=0, t=30), height=500)
    st.plotly_chart(fig, use_container_width=True)
    
    # Top countries table
    st.subheader("Top 10 Countries by Confirmed Cases")
    top_countries = latest_data.sort_values('total_cases', ascending=False).head(10)
    top_countries = top_countries[['country', 'total_cases', 'total_deaths', 'people_fully_vaccinated']]
    top_countries.columns = ['Country', 'Total Cases', 'Total Deaths', 'Fully Vaccinated']
    top_countries = top_countries.reset_index(drop=True)
    st.dataframe(top_countries.style.format({
        'Total Cases': '{:,.0f}', 
        'Total Deaths': '{:,.0f}',
        'Fully Vaccinated': '{:,.0f}'
    }), use_container_width=True)

def display_time_series(data, metric, countries):
    st.header(f"Time Series Analysis: {metric.replace('_', ' ').title()}")
    
    if not countries:
        st.warning("Please select at least one country from the sidebar.")
        return
    
    # Prepare time series data
    pivot_data = data.pivot(index='date', columns='country', values=metric)
    
    # Create line chart
    fig = px.line(
        pivot_data,
        x=pivot_data.index,
        y=countries,
        title=f"{metric.replace('_', ' ').title()} Over Time",
        labels={'date': 'Date', 'value': metric.replace('_', ' ').title()}
    )
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title=metric.replace('_', ' ').title(),
        legend_title="Country",
        hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Add moving averages
    st.subheader("Moving Averages")
    window_size = st.slider("Select Moving Average Window (days)", 1, 30, 7)
    
    # Calculate moving averages for selected countries
    ma_fig = go.Figure()
    for country in countries:
        if country in pivot_data.columns:
            ma_data = pivot_data[country].rolling(window=window_size).mean()
            ma_fig.add_trace(go.Scatter(
                x=pivot_data.index,
                y=ma_data,
                mode='lines',
                name=f"{country} ({window_size}-day MA)"
            ))
    
    ma_fig.update_layout(
        title=f"{window_size}-Day Moving Average of {metric.replace('_', ' ').title()}",
        xaxis_title="Date",
        yaxis_title=f"{metric.replace('_', ' ').title()} (Moving Average)",
        hovermode="x unified"
    )
    st.plotly_chart(ma_fig, use_container_width=True)

def display_country_comparison(data, metric):
    st.header(f"Country Comparison: {metric.replace('_', ' ').title()}")
    
    # Get latest data for comparison
    latest_date = data['date'].max()
    latest_data = data[data['date'] == latest_date]
    
    # Sort countries by the selected metric
    sorted_data = latest_data.sort_values(by=metric, ascending=False).head(20)
    
    # Create bar chart
    fig = px.bar(
        sorted_data,
        x='country',
        y=metric,
        title=f"Top 20 Countries by {metric.replace('_', ' ').title()}",
        color=metric,
        labels={metric: metric.replace('_', ' ').title(), 'country': 'Country'}
    )
    fig.update_layout(
        xaxis_title="Country",
        yaxis_title=metric.replace('_', ' ').title(),
        xaxis={'categoryorder':'total descending'}
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Per capita analysis
    st.subheader("Per Capita Analysis")
    per_capita_options = {
        "new_cases": "New Cases per Million",
        "new_deaths": "New Deaths per Million",
        "total_cases": "Total Cases per Million",
        "total_deaths": "Total Deaths per Million",
    }
    
    if metric in per_capita_options:
        per_capita_metric = metric + "_per_million"
        per_capita_title = per_capita_options[metric]
        
        # Sort countries by the per capita metric
        per_capita_data = latest_data.sort_values(by=per_capita_metric, ascending=False).head(20)
        
        # Create per capita bar chart
        per_capita_fig = px.bar(
            per_capita_data,
            x='country',
            y=per_capita_metric,
            title=f"Top 20 Countries by {per_capita_title}",
            color=per_capita_metric,
            labels={per_capita_metric: per_capita_title, 'country': 'Country'}
        )
        per_capita_fig.update_layout(
            xaxis_title="Country",
            yaxis_title=per_capita_title,
            xaxis={'categoryorder':'total descending'}
        )
        st.plotly_chart(per_capita_fig, use_container_width=True)

def display_vaccination_progress(data):
    st.header("Vaccination Progress")
    
    # Latest vaccination data
    latest_date = data['date'].max()
    latest_data = data[data['date'] == latest_date]
    
    # Metrics for vaccination
    col1, col2 = st.columns(2)
    
    with col1:
        total_vaccinated = latest_data['people_fully_vaccinated'].sum()
        st.metric("Total People Fully Vaccinated", f"{total_vaccinated:,.0f}")
    
    with col2:
        world_population = 7900000000  # Approximate world population
        global_vaccination_rate = (total_vaccinated / world_population) * 100
        st.metric("Global Vaccination Rate", f"{global_vaccination_rate:.2f}%")
    
    # Top countries by vaccination rate
    st.subheader("Top Countries by Vaccination Rate")
    
    # Calculate vaccination rate
    latest_data['vaccination_rate'] = latest_data['people_fully_vaccinated'] / latest_data['population'] * 100
    top_vaccinated = latest_data.dropna(subset=['vaccination_rate']).sort_values('vaccination_rate', ascending=False).head(20)
    
    # Create bar chart for vaccination rate
    vax_fig = px.bar(
        top_vaccinated,
        x='country',
        y='vaccination_rate',
        title="Top 20 Countries by Vaccination Rate (%)",
        color='vaccination_rate',
        labels={'vaccination_rate': 'Vaccination Rate (%)', 'country': 'Country'}
    )
    vax_fig.update_layout(
        xaxis_title="Country",
        yaxis_title="Vaccination Rate (%)",
        xaxis={'categoryorder':'total descending'}
    )
    st.plotly_chart(vax_fig, use_container_width=True)
    
    # Vaccination progress over time for selected countries
    st.subheader("Vaccination Progress Over Time")
    
    # Country selector for vaccination trends
    countries = sorted(data['country'].unique())
    selected_countries = st.multiselect(
        "Select Countries for Vaccination Trends",
        options=countries,
        default=["United States", "United Kingdom", "Israel", "Canada"]
    )
    
    if selected_countries:
        # Filter data for selected countries
        vax_data = data[data['country'].isin(selected_countries)]
        
        # Pivot data for plotting
        pivot_vax_data = vax_data.pivot(index='date', columns='country', values='people_fully_vaccinated_per_hundred')
        
        # Create line chart
        vax_trend_fig = px.line(
            pivot_vax_data,
            x=pivot_vax_data.index,
            y=selected_countries,
            title="Vaccination Rate Over Time (% of Population)",
            labels={'date': 'Date', 'value': 'Fully Vaccinated (%)'}
        )
        vax_trend_fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Fully Vaccinated (%)",
            legend_title="Country",
            hovermode="x unified"
        )
        st.plotly_chart(vax_trend_fig, use_container_width=True)

if __name__ == "__main__":
    main()