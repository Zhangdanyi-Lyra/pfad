import pandas as pd
from pathlib import Path
import sys

CSV = Path('city_weather_timeseries.csv')
if not CSV.exists():
    print('缺少 city_weather_timeseries.csv，请先运行 weather_timeseries_fetch.py')
    sys.exit(1)

df = pd.read_csv(CSV)
if df.empty:
    print('文件为空')
    sys.exit(0)

latest_ts = df['timestamp_unix'].max()
latest = df[df['timestamp_unix'] == latest_ts]
print(f'最新时间: {latest_ts} (共 {len(latest)} 条)')

print('\n最高温 Top5:')
print(latest.sort_values('temp', ascending=False)[['city','temp']].head().to_string(index=False))

print('\n最低温 Top5:')
print(latest.sort_values('temp', ascending=True)[['city','temp']].head().to_string(index=False))

print('\n最大风速 Top5:')
print(latest.sort_values('wind_speed', ascending=False)[['city','wind_speed']].head().to_string(index=False))

print('\n最低湿度 Top5:')
print(latest.sort_values('humidity', ascending=True)[['city','humidity']].head().to_string(index=False))

# 可扩展：温差、体感温度等
