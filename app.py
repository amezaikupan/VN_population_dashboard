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
data = pd.read_csv("proc_data/vn_population.csv", index_col=False)
map_data = gpd.read_file("proc_data/vn_map_crs_0.geojson")
migration_data = pd.read_csv("proc_data/vn_migration.csv", index_col=False)

color_theme = 'viridis'
data_sources = {
    'Population': "proc_data/vn_population.csv", 
    'Population density': "proc_data/vn_population_density.csv"
}

with st.sidebar:
    st.title('VN Population Dashboard')
    data_source = st.selectbox("Select data", list(data_sources.keys()))
    data = pd.read_csv(data_sources[data_source], index_col=False)

    year_list = list(data['Year'].unique())[::-1]
    selected_year = st.selectbox("Select a year", year_list, index=len(year_list) - 1)
    data_selected_year = data[data['Year'] == selected_year]
    data_selected_year_sorted = data_selected_year.sort_values(by="Population", ascending=False)

    color_theme_list = ['RdYlGn_r', 'blues', 'cividis', 'greens', 'inferno', 'magma', 'plasma', 'reds', 'rainbow', 'turbo', 'viridis']
    color_theme = st.selectbox('Select a color theme', color_theme_list)

    with st.expander("About", expanded=True):
        st.write('''
        Data: [National Statistics Office of Vietnam](https://www.nso.gov.vn/px-web-2/?pxid=V0201&theme=D%C3%A2n%20s%E1%BB%91%20v%C3%A0%20lao%20%C4%91%E1%BB%99ng)    
                 
        - :orange[**Gains/Losses**]: states with high inbound/ outbound migration for selected year
        - :orange[**States Migration**]: percentage of states with annual inbound/ outbound migration > 50,000                         
        ''')

def make_heatmap(input_df, input_y, input_x, input_color, input_color_theme):
    heatmap = alt.Chart(input_df).mark_rect().encode(
        y = alt.Y(f'{input_y}:O', axis=alt.Axis(title="Year", titleFontSize=18, titlePadding=15, titleFontWeight=900, labelAngle=0)), 
        x = alt.X(f'{input_x}:O', axis=alt.Axis(title="", titleFontSize=12, titlePadding=15, titleFontWeight=900, labelOverlap=False)), 
        color = alt.Color(
            f'max({input_color}):Q', 
            legend=None, 
            scale=alt.Scale(scheme=input_color_theme)
        ),
        stroke = alt.value('black'), 
        strokeWidth = alt.value(0.25),
    ).properties(width=900).configure_axis(
        labelFontSize=12,
        titleFontSize=12
    )

    return heatmap

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

col = st.columns((1.5, 3, 2), gap='Medium')

with col[1]:
    # st.markdown(f'#### Total Population {selected_year}')
    choropleth = draw_choropleth_map(data_selected_year, "Population", color_theme, scale_data=True, normalize=False)
    st.plotly_chart(choropleth, use_container_width=True)

with col[0]:
    st.markdown("#### Gains/Losses")

    metric_col_1, metric_col_2 = st.columns(2, gap='small')
    population_difference_sorted = calculate_population_difference(data, selected_year)
    with metric_col_1:
        if selected_year > 2011:
            first_province_name = population_difference_sorted['Province'].iloc[0]
            first_province_population = format_number(population_difference_sorted['Population'].iloc[0])
            first_province_delta = format_number(population_difference_sorted['Population_difference'].iloc[0])
        else:
            first_province_name = '_'
            first_province_population = '_'
            first_province_delta = ''
        
        st.metric(label=first_province_name, value=first_province_population, delta=first_province_delta)

    with metric_col_2:
        if selected_year > 2010:
            last_province_name = population_difference_sorted['Province'].iloc[-1]
            last_province_population = format_number(population_difference_sorted['Population'].iloc[-1])
            last_province_delta = format_number(population_difference_sorted['Population_difference'].iloc[-1])
        else:
            last_province_name = '_'
            last_province_population = '_'
            last_province_delta = ''
        
        st.metric(label=last_province_name, value=last_province_population, delta=last_province_delta)

    st.markdown("#### Province migration")
    migration_data_copy = migration_data[migration_data['Year'] == selected_year]
    pos_net_migration = migration_data_copy[migration_data_copy['Net_Migration_Rate'] > 0]
    neg_net_mirgration = migration_data_copy[migration_data_copy['Net_Migration_Rate'] < 0]

    pos_net_migration_rate = round((len(pos_net_migration) / migration_data['Province'].nunique()) * 100)
    neg_net_mirgration_rate = round((len(neg_net_mirgration) / migration_data['Province'].nunique()) * 100)
    
    print(pos_net_migration_rate)
    donut_chart_greater = make_donut(pos_net_migration_rate, "Inbound Migration", 'green')
    donut_chart_less = make_donut(neg_net_mirgration_rate, 'Outbound Migration', 'red')

    migration_cols = st.columns((0.45, 0.1, 0.45))
    with migration_cols[0]:
        st.write('Inbound')
        st.altair_chart(donut_chart_greater, use_container_width=True)

    with migration_cols[2]:
        st.write('Outbound')
        st.altair_chart(donut_chart_less, use_container_width=True)
     
with col[2]: 
    st.markdown('#### Top 10 provinces')

    st.dataframe(
        data_selected_year_sorted,#.head(10), 
        column_order = ("Province", "Population"), 
        hide_index=True, 
        # width=None, 
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
