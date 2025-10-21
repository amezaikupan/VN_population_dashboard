import plotly.express as px 
import geopandas as gpd
import numpy as np
import os 
from sklearn.preprocessing import MinMaxScaler

BASE_DIR = os.path.dirname(__file__)
GEO_PATH = os.path.join(BASE_DIR, "vn_map.geojson")
vn_geo_json = gpd.read_file(GEO_PATH)
location = 'Province'

def draw_choropleth_map(data, value, color_theme, scale_data=False, normalize=False):
    """
    Draw Vietnam (map of 2010 - 2024) choropleth using plotly.

    Parameters: 
        name (pd.Dataframe): Data that need to be ploted. The data should have the format of [Province, value_need_to_plot]
            Accepted province names: ['An Giang', 'Bà Rịa -Vũng Tàu', 'Bắc Giang', 'Bắc Kạn', 'Bạc Liêu', 'Bắc Ninh', 
            'Bến Tre', 'Bình Định', 'Bình Dương', 'Bình Phước', 'Bình Thuận', 'Cà Mau', 'Cần Thơ', 'Cao Bằng', 'Đà Nẵng', 
            'Đắk Lắk', 'Đắk Nông', 'Điện Biên', 'Đồng Nai', 'Đồng Tháp', 'Gia Lai', 'Hà Giang', 'Hà Nam', 'Hà Nội', 
            'Hà Tĩnh', 'Hải Dương', 'Hải Phòng', 'Hậu Giang', 'Hòa Bình', 'Hưng Yên', 'Khánh Hòa', 'Kiên Giang', 
            'Kon Tum', 'Lai Châu', 'Lâm Đồng', 'Lạng Sơn', 'Lào Cai', 'Long An', 'Nam Định', 'Nghệ An', 'Ninh Bình', 
            'Ninh Thuận', 'Phú Thọ', 'Phú Yên', 'Quảng Bình', 'Quảng Nam', 'Quảng Ngãi', 'Quảng Ninh', 'Quảng Trị', 
            'Sóc Trăng', 'Sơn La', 'Tây Ninh', 'Thái Bình', 'Thái Nguyên', 'Thanh Hóa', 'Thừa Thiên Huế', 'Tiền Giang', 
            'TP.Hồ Chí Minh', 'Trà Vinh', 'Tuyên Quang', 'Vĩnh Long', 'Vĩnh Phúc', 'Yên Bái']
        value (str): Name of data column that need to plot 
        color_theme (str): String code for cmap theme 
        scale_data (bool): Apply square root transformation to values 
        normalize (bool): Normalize to range 0-1 for entire dataset 

    Returns: 
        Plotly choropleth object
    """

    _value = value
    if scale_data:
        _value = "_" + value
        data[_value] = np.log2(data[value])

    if normalize:
        scaler = MinMaxScaler()
        data[value] = scaler.fit_transform(data[[value]])
        

    choropleth = px.choropleth(data, geojson=vn_geo_json,
                               locations=location, color=_value, 
                               color_continuous_scale=color_theme,
                               featureidkey="properties.Province",
                               range_color=(min(data[_value]), max(data[_value])),
                               hover_name=location, 
                               hover_data={value: True, _value: False, location: False}, 
                            )

    choropleth.update_geos(
        projection_type="mercator",
        fitbounds="locations",
        # If zoom in to mainland
        # lataxis_range = [7.7, 23.5],
        # lonaxis_range = [102.0, 111],
        visible=False
    )
    
    choropleth.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=0, b=0), 
        width=600,
        height=560,
        autosize=False, 
        uirevision='constant', 
        coloraxis_colorbar=dict(
            title=None,        # remove legend title
            tickvals=[],   # removes tick marks
            ticktext=[],   # removes tick labels
            ticks="",      # removes tick lines
        )
    )

    return choropleth