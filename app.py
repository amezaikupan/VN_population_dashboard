import streamlit as st 
import pandas as pd 
import altair as alt 
import plotly.express as px 
import geopandas as gpd
import json
import numpy as np
from vis.draw_vn_choropleth_map import draw_choropleth_map
from utils import calculate_population_difference, format_number

st.set_page_config(
    page_title="VN Population Dashboard", 
    page_icon=":)", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
        .block-container {
            padding-top: 3rem;
            padding-bottom: 0rem;
        }
    </style>
    """, unsafe_allow_html=True)

data = pd.read_csv("data/vn_population.csv", index_col=False)
density_data = pd.read_csv("data/vn_population_density.csv", index_col=False)
migration_data = pd.read_csv("data/vn_migration.csv", index_col=False)
sex_ratio_data = pd.read_csv("data/vn_sex_ratio.csv", index_col=False)
city_countryside_data = pd.read_csv('data/vn_city_countryside_dist.csv', index_col=False)

color_theme = 'RdYlGn_r'
data_sources = {
    'Population': data, 
    'Population density': density_data
}

# ____HEADER____
title, year_select, map_mode = st.columns([4, 1.75, 1.75])
with map_mode:
    data_source = st.selectbox("Select data display on map", list(data_sources.keys()))
    map_display_data = data_sources[data_source]

with year_select:
    year_list = list(data['Year'].unique())[::-1]
    selected_year = st.selectbox("Select a year", year_list, index=len(year_list) - 1)
    data_selected_year = data[data['Year'] == selected_year]
    map_display_data = map_display_data[map_display_data['Year'] == selected_year]
    data_selected_year_sorted = data_selected_year.sort_values(by="Population", ascending=False)

with title:
    st.title("VN Population Dashboard")

# ____DATA VIS____
col = st.columns((2, 2, 3.5), gap='Medium')

with col[2]:
    choropleth = draw_choropleth_map(map_display_data, "Population", color_theme, scale_data=True, normalize=False)
    st.plotly_chart(choropleth, use_container_width=True)

with col[1]:
    st.markdown("#### Statistics")

    total_population = format_number(int(data_selected_year['Population'].sum()))
    st.metric(label="Total Population", value=total_population, border=True)

    sex_ratio = sex_ratio_data[(sex_ratio_data['Year'] == selected_year) & (sex_ratio_data['Province'] == 'Country')]['Sex_ratio'].values[0]
    st.metric(label='Sex ratio in population', value=f'{round(float(sex_ratio), 1)} 👨 / 100 👩', border=True)

    # city_population = float(city_countryside_data[(city_countryside_data['Year'] == selected_year) & (city_countryside_data['Province'] == 'Country') & (city_countryside_data['Location'] == 'City')]['Value'].values[0])
    # countryside_population = float(city_countryside_data[(city_countryside_data['Year'] == selected_year) & (city_countryside_data['Province'] == 'Country') & (city_countryside_data['Location'] == 'Countryside')]['Value'].values[0])
    # city_ratio = city_population / (countryside_population + city_population)
    # countryside_ratio = countryside_population / (countryside_population + city_population)
    # st.metric(label="City to countryside ratio", value=f'{round(float(city_ratio), 1)} 🏙️ / {round(float(countryside_ratio), 1)} 🏠', border=True)

    metric_col_1, metric_col_2 = st.columns(2, gap='small')
    population_difference_sorted = calculate_population_difference(data, selected_year)
    with metric_col_1:
        if selected_year > 2011:
            first_province_name = population_difference_sorted['Province'].iloc[0]
            first_province_population = format_number(population_difference_sorted['Population'].iloc[0])
            first_province_delta = format_number(population_difference_sorted['Population_difference'].iloc[0])
        else:
            first_province_name = 'No data'
            first_province_population = None
            first_province_delta = '0'
        
        st.metric(label=first_province_name, value=first_province_population, delta=first_province_delta, border=True)

    with metric_col_2:
        if selected_year > 2010:
            last_province_name = population_difference_sorted['Province'].iloc[-1]
            last_province_population = format_number(population_difference_sorted['Population'].iloc[-1])
            last_province_delta = format_number(population_difference_sorted['Population_difference'].iloc[-1])
        else:
            last_province_name = 'No data'
            last_province_population = None
            last_province_delta = '0'
        
        st.metric(label=last_province_name, value=last_province_population, delta=last_province_delta, border=True)

with col[0]: 
    st.markdown(f'#### Population in {selected_year} (thoudsands) ')
    st.dataframe(
        data_selected_year_sorted,#.head(10), 
        column_order = ("Province", "Population"), 
        hide_index=True, 
        # width=None,
        height=380, 
        column_config={
            "Province": st.column_config.TextColumn(
                "Provinces",
            ), 
            "Population": st.column_config.ProgressColumn(
                "Population", 
                format="%f", 
                min_value=0, 
                max_value=max(data['Population'])
            )
        }
    )