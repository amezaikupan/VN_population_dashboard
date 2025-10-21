import streamlit as st 
import pandas as pd 
import altair as alt 
import plotly.express as px 
import geopandas as gpd
import json
import numpy as np
from vis.draw_vn_choropleth_map import draw_choropleth_map

st.set_page_config(
    page_title="VN Population Dashboard", 
    page_icon=":)", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# Remove top padding/margin
st.markdown("""
    <style>
        .block-container {
            padding-top: 3rem;
            padding-bottom: 0rem;
        }
    </style>
    """, unsafe_allow_html=True)

alt.themes.enable("dark")
map_data = gpd.read_file("proc_data/vn_map_crs_0.geojson")

data = pd.read_csv("proc_data/vn_population.csv", index_col=False)
migration_data = pd.read_csv("proc_data/vn_migration.csv", index_col=False)
sex_ratio_data = pd.read_csv("proc_data/vn_sex_ratio.csv", index_col=False)
city_countryside_data = pd.read_csv('proc_data/vn_city_countryside_dist.csv', index_col=False)

color_theme = 'RdYlGn_r'
data_sources = {
    'Population': "proc_data/vn_population.csv", 
    'Population density': "proc_data/vn_population_density.csv"
}


title, year_select, map_mode = st.columns([2, 1, 1])
with map_mode:
    data_source = st.selectbox("Select data display on map", list(data_sources.keys()))
    data = pd.read_csv(data_sources[data_source], index_col=False)

with year_select:
    year_list = list(data['Year'].unique())[::-1]
    selected_year = st.selectbox("Select a year", year_list, index=len(year_list) - 1)
    data_selected_year = data[data['Year'] == selected_year]
    data_selected_year_sorted = data_selected_year.sort_values(by="Population", ascending=False)

with title:
    st.title("VN Population Dashboard")


def calculate_population_difference(input_df, input_year):
    data_selected_year = data[data['Year'] == selected_year].reset_index()
    data_previous_year =  data[data['Year'] == selected_year - 1].reset_index()
    data_selected_year['Population_difference'] = data_selected_year['Population'] - data_previous_year['Population']
    return data_selected_year[['Province', 'Population', 'Population_difference']].sort_values(by="Population_difference", ascending=False)


def make_donut(input_response, input_text, input_color):
    if input_color == 'blue':
        chart_color = ['#29b5e8', '#155F7A']
    if input_color == 'green':
        chart_color = ['#27AE60', '#12783D']
    if input_color == 'orange':
        chart_color = ['#F39C12', '#875A12']
    if input_color == 'red':
        chart_color = ['#E74C3C', '#781F16']

    source = pd.DataFrame(
        {
            "Topic": ['', input_text], 
            "% value": [100-input_response, input_response]
        }
    )

    source_bg = pd.DataFrame({
        "Topic": ["", input_text], 
        "% value": [100, 0]
    })

    plot = alt.Chart(source).mark_arc(innerRadius=45, cornerRadius=25).encode(
        theta="% value", 
        color=alt.Color("Topic:N", 
                        scale=alt.Scale(
                            domain=[input_text, ''], 
                            range=chart_color
                        ), 
                        legend=None)
    ).properties(width=130, height=130)

    text = plot.mark_text(align="center", color="#29b5e8", font="Lato", fontSize=32, fontWeight=700, fontStyle="italic").encode(text=alt.value(f"{input_response}"))
    plot_bg = alt.Chart(source_bg).mark_arc(innerRadius=45, cornerRadius=20).encode(
        theta="% value",
        color= alt.Color("Topic:N",
                        scale=alt.Scale(
                            domain=[input_text, ''],
                            range=chart_color),  # 31333F
                        legend=None),
    ).properties(width=130, height=130)

    return plot_bg + plot + text

def format_number(num):
    actual_num = num * 1000  # Convert back to real numbers

    if abs(actual_num) > 1000000:
        if not actual_num % 1000000:
            return f'{actual_num // 1000000} M'
        return f'{round(actual_num / 1000000, 1)} M'
    return f'{round(actual_num // 1000, 1)} K'

col = st.columns((2, 2, 3.5), gap='Medium')

with col[2]:
    # st.markdown(f'#### Total Population {selected_year}')
    choropleth = draw_choropleth_map(data_selected_year, "Population", color_theme, scale_data=True, normalize=False)
    st.plotly_chart(choropleth, use_container_width=True)

with col[1]:
    st.markdown("#### Statistics")

    total_population = format_number(int(data_selected_year['Population'].sum()))
    st.metric(label="Total Population", value=total_population, border=True)

    sex_ratio = sex_ratio_data[(sex_ratio_data['Year'] == selected_year) & (sex_ratio_data['Province'] == 'Country')]['Sex_ratio'].values[0]
    st.metric(label='Sex ratio', value=f'{round(float(sex_ratio), 1)} 👨 / 100 👩', border=True)

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
    st.markdown(f'#### {data_source} in {selected_year} (thoudsands) ')

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
                max_value=max(data_selected_year_sorted['Population'])
            )
        }
    )
