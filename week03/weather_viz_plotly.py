import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime, timezone
import argparse

CSV = Path('city_weather_timeseries.csv')
if not CSV.exists():
    raise SystemExit('缺少 city_weather_timeseries.csv，请先运行采集脚本。')

df = pd.read_csv(CSV)
if df.empty:
    raise SystemExit('数据文件为空。')

# 确保时间序列排序
if 'timestamp_unix' not in df.columns:
    raise SystemExit('缺少 timestamp_unix 列。')
df = df.sort_values('timestamp_unix')

# 解析人类可读时间列
df['ts_iso'] = df['timestamp_unix'].apply(lambda x: datetime.fromtimestamp(int(x), tz=timezone.utc).strftime('%Y-%m-%d %H:%M UTC'))

# 温度取值范围
min_temp = df['temp'].min()
max_temp = df['temp'].max()

# 将每个时间戳作为一帧
frames = []
unique_ts = sorted(df['timestamp_unix'].unique())
iso_map = {ts: df[df['timestamp_unix']==ts]['ts_iso'].iloc[0] for ts in unique_ts}

def make_extreme_trace(sub):
    if sub.empty:
        return None
    try:
        idx_min = sub['temp'].idxmin()
        idx_max = sub['temp'].idxmax()
        rmin = sub.loc[idx_min]
        rmax = sub.loc[idx_max]
        lons = [rmin['lon'], rmax['lon']]
        lats = [rmin['lat'], rmax['lat']]
        texts = [f"MIN {rmin['city']} {rmin['temp']:.1f}°C", f"MAX {rmax['city']} {rmax['temp']:.1f}°C"]
        colors = ['#2e7ae6', '#d62728']
        return go.Scattergeo(
            lon=lons, lat=lats,
            mode='markers+text',
            marker=dict(size=6, color=colors, symbol='x'),
            text=texts,
            textposition='top right',
            textfont=dict(size=10, color='#111'),
            name='Extremes',
            showlegend=False,
            hoverinfo='skip'
        )
    except Exception:
        return None

# 颜色映射使用内置颜色尺度（可自定义）
for ts in unique_ts:
    sub = df[df['timestamp_unix'] == ts]
    traces = [go.Scattergeo(
        lon=sub['lon'], lat=sub['lat'],
        mode='markers',
        marker=dict(
            size=(sub['wind_speed'].fillna(0)+1)*3,  # 风速影响点大小
            color=sub['temp'],
            cmin=min_temp,
            cmax=max_temp,
            colorscale='Turbo',
            colorbar=dict(title='温度 (°C)')
        ),
        text=[f"{row.city}<br>温度:{row.temp}°C<br>湿度:{row.humidity}%<br>风速:{row.wind_speed}m/s<br>{row.weather_main}" for row in sub.itertuples()],
        hoverinfo='text'
    )]
    # 极值标注 trace 可选添加（先占位，稍后根据参数决定是否启用）
    extreme_trace = make_extreme_trace(sub)
    if extreme_trace is not None:
        traces.append(extreme_trace)
    frames.append(go.Frame(data=traces, name=str(ts)))

# 初始帧使用第一组数据
t0 = df[df['timestamp_unix'] == unique_ts[0]]

fig = go.Figure(
    data=[
        go.Scattergeo(
            lon=t0['lon'], lat=t0['lat'], mode='markers',
            marker=dict(
                size=(t0['wind_speed'].fillna(0)+1)*3,
                color=t0['temp'],
                cmin=min_temp,
                cmax=max_temp,
                colorscale='Turbo',
                colorbar=dict(title='温度 (°C)')
            ),
            text=[f"{row.city}<br>温度:{row.temp}°C<br>湿度:{row.humidity}%<br>风速:{row.wind_speed}m/s<br>{row.weather_main}" for row in t0.itertuples()],
            hoverinfo='text'
        ),
        # 先添加一个占位的极值 trace（可在渲染前按参数决定是否保留）
        make_extreme_trace(t0)
    ],
    frames=frames
)

parser = argparse.ArgumentParser(description='生成 Plotly 天气动画 HTML')
parser.add_argument('--speed', choices=['slow','normal','fast'], default='normal', help='播放速度')
parser.add_argument('--outfile', type=str, default=None, help='输出 HTML 文件名（可不带 .html）')
parser.add_argument('--annotate-extremes', action='store_true', help='为每帧标注最高/最低温城市')
args = parser.parse_args()
speed_map = {'slow': 1200, 'normal': 700, 'fast': 300}
frame_duration = speed_map[args.speed]

fig.update_layout(
    title=f'全球城市天气时间序列 (Plotly) | 温度范围 {min_temp:.1f}~{max_temp:.1f}°C',
    geo=dict(
        projection_type='natural earth',
        showland=True,
        landcolor='rgb(230,230,230)',
        showcountries=True,
        countrycolor='rgb(200,200,200)'
    ),
    updatemenus=[{
        'type': 'buttons',
        'showactive': False,
        'x': 0.05,
        'y': 0,
        'buttons': [
            {'label': '播放', 'method': 'animate', 'args': [None, {'frame': {'duration': frame_duration, 'redraw': True}, 'fromcurrent': True, 'transition': {'duration': int(frame_duration/2)}}]},
            {'label': '暂停', 'method': 'animate', 'args': [[None], {'frame': {'duration': 0}, 'mode': 'immediate'}]}
        ]
    }],
    sliders=[{
        'steps': [
            {
                'args': [[str(ts)], {'frame': {'duration': 0, 'redraw': True}, 'mode': 'immediate'}],
                'label': iso_map[ts],
                'method': 'animate'
            } for ts in unique_ts
        ],
        'x': 0.05,
        'y': -0.05,
        'len': 0.9
    }]
)
# 根据参数移除或保留极值标注 trace
if not args.annotate_extremes:
    # 初始 data 移除第 2 个 trace
    if len(fig.data) > 1:
        fig.data = (fig.data[0],)
    # 帧中移除第 2 个 trace
    new_frames = []
    for fr in fig.frames:
        if len(fr.data) > 1:
            new_frames.append(go.Frame(data=[fr.data[0]], name=fr.name))
        else:
            new_frames.append(fr)
    fig.frames = tuple(new_frames)

# 输出文件名
if args.outfile:
    out_path = Path(args.outfile)
    if out_path.suffix.lower() != '.html':
        out_path = out_path.with_suffix('.html')
else:
    suffix = '_annotated' if args.annotate_extremes else ''
    out_path = Path(f'weather_animation_{args.speed}{suffix}.html')

fig.write_html(str(out_path), include_plotlyjs='cdn')
print(f'已生成 {out_path.name}，可在浏览器打开。 播放速度: {args.speed} 标注: {"开" if args.annotate_extremes else "关"}')
