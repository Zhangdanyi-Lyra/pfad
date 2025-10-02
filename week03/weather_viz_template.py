import pandas as pd
import pydeck as pdk
import streamlit as st
import os
from datetime import datetime

# 自动检测是否是时间序列文件
if os.path.exists('city_weather_timeseries.csv'):
    DATA_PATH = 'city_weather_timeseries.csv'
else:
    DATA_PATH = 'city_weather.csv'

@st.cache_data
def load_data(path: str):
    df_ = pd.read_csv(path)
    # 兼容单次与多次格式
    if 'timestamp_iso' in df_.columns:
        # 解析时间
        try:
            df_['timestamp'] = pd.to_datetime(df_['timestamp_iso'])
        except Exception:
            # 退化处理
            df_['timestamp'] = pd.to_datetime(df_['timestamp_unix'], unit='s')
    else:
        # 为旧格式构造一个统一时间戳列
        df_['timestamp'] = pd.Timestamp.utcnow()
    return df_

df = load_data(DATA_PATH)

# 可选：根据温度/湿度/风速等映射颜色和大小
COLOR_BINS = [0, 10, 20, 30, 40]
COLOR_RANGE = [
    [0, 0, 255],    # 蓝色（低温）
    [0, 255, 255],  # 青色
    [0, 255, 0],    # 绿色
    [255, 255, 0],  # 黄色
    [255, 0, 0],    # 红色（高温）
]
def get_color(temp):
    for i, t in enumerate(COLOR_BINS):
        if temp < t:
            return COLOR_RANGE[i]
    return COLOR_RANGE[-1]
temp_col = 'temp'
if temp_col not in df.columns:
    st.error('数据中缺少 temp 列，无法映射颜色。')
    st.stop()
df['color'] = df[temp_col].apply(get_color)

# pydeck 动态可视化
st.title('全球城市天气动态可视化（支持时间序列）')
st.write(f'数据来源：OpenWeatherMap | 数据文件: {DATA_PATH}')

# 时间序列支持
timestamps = sorted(df['timestamp'].unique())
if len(timestamps) > 1:
    st.sidebar.subheader('时间控制')
    idx = st.sidebar.slider('时间索引', 0, len(timestamps)-1, 0)
    current_ts = timestamps[idx]
    df_show = df[df['timestamp'] == current_ts]
    st.caption(f'当前时间：{pd.to_datetime(current_ts).isoformat()} | 样本数量：{len(df_show)} | 帧 {idx+1}/{len(timestamps)}')
    # 城市选择折线
    with st.expander('城市温度曲线（最近全部时间）'):
        city_sel = st.multiselect('选择城市', sorted(df['city'].unique()), default=sorted(df['city'].unique())[:5])
        if city_sel:
            line_df = df[df['city'].isin(city_sel)].copy().sort_values('timestamp')
            pivot_df = line_df.pivot_table(index='timestamp', columns='city', values='temp')
            st.line_chart(pivot_df)
else:
    df_show = df

layer = pdk.Layer(
    'ScatterplotLayer',
    data=df_show,
    get_position='[lon, lat]',
    get_color='color',
    get_radius=20000,
    pickable=True,
    auto_highlight=True,
)

view_state = pdk.ViewState(
    latitude=df_show['lat'].mean(),
    longitude=df_show['lon'].mean(),
    zoom=1.5,
    pitch=30,
)

tooltip = {
    'text': '{city}\n温度: {temp}°C\n湿度: {humidity}%\n风速: {wind_speed}m/s\n天气: {weather_main}'
}
r = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip=tooltip)
col_map, col_legend = st.columns([4,1])
with col_map:
    st.pydeck_chart(r)
with col_legend:
    st.markdown('**温度图例**')
    for i in range(len(COLOR_BINS)):
        if i == 0:
            rng = f'< {COLOR_BINS[i]}'
        elif i == len(COLOR_BINS)-1:
            rng = f'>= {COLOR_BINS[i-1]}'
        else:
            rng = f'{COLOR_BINS[i-1]}–{COLOR_BINS[i]}'
        c = COLOR_RANGE[i]
        st.markdown(f"<div style='display:flex;align-items:center; margin-bottom:4px;'>"
                    f"<div style='width:18px;height:18px;background:rgb({c[0]},{c[1]},{c[2]});margin-right:6px;'></div>"
                    f"<span style='font-size:12px;'>{rng}°C</span></div>", unsafe_allow_html=True)

# 已移除自动播放逻辑

# 可选：加时间轴动画（如有多时刻数据）
# 可用 st.slider 控制时间，筛选 df 后再渲染
