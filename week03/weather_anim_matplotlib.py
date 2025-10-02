import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from pathlib import Path
from datetime import datetime, timezone
import shutil
import numpy as np
from matplotlib import cm, colors as mcolors
import argparse

CSV = Path('city_weather_timeseries.csv')
if not CSV.exists():
    raise SystemExit('缺少 city_weather_timeseries.csv')

df = pd.read_csv(CSV)
if df.empty:
    raise SystemExit('数据为空')

if 'timestamp_unix' not in df.columns:
    raise SystemExit('缺少 timestamp_unix')

# 排序并分组帧
df = df.sort_values('timestamp_unix')
frames = []
for ts, group in df.groupby('timestamp_unix'):
    frames.append((ts, group))

min_t = df['temp'].min(); max_t = df['temp'].max()

# 颜色映射与色标
cmap = plt.colormaps.get_cmap('turbo')
norm = mcolors.Normalize(vmin=min_t, vmax=max_t)

fig = plt.figure(figsize=(10,5))
ax = fig.add_subplot(111, projection='mollweide')  # 简单全球投影
# 全局色标（只绘制一次）
sm = cm.ScalarMappable(norm=norm, cmap=cmap)
cbar = fig.colorbar(sm, ax=ax, orientation='vertical', pad=0.08, fraction=0.05)
cbar.set_label('Temperature (°C)')
plt.subplots_adjust(top=0.9, bottom=0.05)
sc = None

# CLI 参数
parser = argparse.ArgumentParser(description='全球城市天气动画 (Matplotlib)')
parser.add_argument('--fps', type=int, default=1, help='输出视频帧率')
parser.add_argument('--trail', type=int, default=5, help='轨迹尾巴长度（含当前帧）')
parser.add_argument('--format', choices=['auto','mp4','gif'], default='auto', help='输出格式')
parser.add_argument('--outfile', type=str, default=None, help='输出文件名（自动加扩展名）')
args = parser.parse_args()

# 轨迹长度与帧率
TRAIL_LEN = max(1, args.trail)
FPS = max(1, args.fps)

# 将经纬度转换为弧度（mollweide需要）

def to_mollweide_lon(lon):
    # 转换范围 [-180,180] -> 弧度
    lon = ((lon + 180) % 360) - 180
    return np.radians(lon)

def init():
    ax.set_title('全球城市天气 (Matplotlib)')
    ax.grid(True, alpha=0.3)
    return []

def _plot_group(group, alpha=0.6, size_scale=8.0):
    lons = to_mollweide_lon(group['lon'].values)
    lats = np.radians(group['lat'].values)
    sizes = (group['wind_speed'].fillna(0)+1)*size_scale
    sc = ax.scatter(lons, lats, c=group['temp'].values, s=sizes, cmap=cmap, norm=norm, alpha=alpha, edgecolor='none')
    return sc


def update(i):
    ts, g = frames[i]
    ax.clear()
    ax.grid(True, alpha=0.3)
    ax.set_title(datetime.fromtimestamp(int(ts), tz=timezone.utc).strftime('%Y-%m-%d %H:%M UTC'))

    # 轨迹尾巴：画最近 TRAIL_LEN-1 帧（不含当前帧），由淡到浓
    start = max(0, i - TRAIL_LEN + 1)
    if start < i:
        steps = max(1, i - start)
        for j, idx in enumerate(range(start, i)):
            # 线性递增透明度 0.25 -> 0.65
            alpha = 0.25 + 0.4 * ((j + 1) / steps)
            _plot_group(frames[idx][1], alpha=alpha, size_scale=7.0)

    # 当前帧（最亮）
    scatter = _plot_group(g, alpha=0.9, size_scale=8.5)

    # 极值标注（当前帧）
    try:
        idx_min = g['temp'].idxmin()
        idx_max = g['temp'].idxmax()
        rmin = g.loc[idx_min]
        rmax = g.loc[idx_max]
        # 最低温
        ax.annotate(f"{rmin['city']} {rmin['temp']:.1f}°C",
                    xy=(to_mollweide_lon(rmin['lon']), np.radians(rmin['lat'])),
                    xytext=(3, -8), textcoords='offset points',
                    fontsize=8, color='white',
                    bbox=dict(boxstyle='round,pad=0.2', fc='black', alpha=0.4))
        # 最高温
        ax.annotate(f"{rmax['city']} {rmax['temp']:.1f}°C",
                    xy=(to_mollweide_lon(rmax['lon']), np.radians(rmax['lat'])),
                    xytext=(3, -8), textcoords='offset points',
                    fontsize=8, color='white',
                    bbox=dict(boxstyle='round,pad=0.2', fc='black', alpha=0.4))
    except Exception:
        pass

    return [scatter]

ani = animation.FuncAnimation(fig, update, init_func=init, frames=len(frames), interval=int(1000/FPS), blit=False)

# 优先尝试 mp4 (ffmpeg), 否则回退 GIF
ffmpeg_path = shutil.which('ffmpeg')
writers = animation.writers.list()
can_ffmpeg = ffmpeg_path is not None and 'ffmpeg' in writers

# 输出文件名
if args.outfile:
    base = Path(args.outfile).with_suffix('')
else:
    base = Path('weather_animation')

def save_mp4():
    out = str(base.with_suffix('.mp4'))
    ani.save(out, fps=FPS, writer='ffmpeg')
    print(f'已生成 {out} (使用 ffmpeg)')

def save_gif():
    out = str(base.with_suffix('.gif'))
    ani.save(out, writer='pillow', fps=FPS)
    print(f'已生成 {out}')

if args.format == 'mp4':
    if not can_ffmpeg:
        print('未检测到 ffmpeg，无法输出 mp4，建议: brew install ffmpeg')
        save_gif()
    else:
        try:
            save_mp4()
        except Exception as e:
            print('使用 ffmpeg 保存 mp4 失败:', e)
            print('回退到 GIF (pillow)')
            try:
                save_gif()
            except Exception as e2:
                print('保存 gif 失败:', e2)
elif args.format == 'gif':
    try:
        save_gif()
    except Exception as e:
        print('保存 gif 失败:', e)
else:  # auto
    if can_ffmpeg:
        try:
            save_mp4()
        except Exception as e:
            print('使用 ffmpeg 保存 mp4 失败:', e)
            print('回退到 GIF (pillow)')
            try:
                save_gif()
            except Exception as e2:
                print('保存 gif 失败:', e2)
    else:
        print('未检测到 ffmpeg, 直接生成 GIF')
        try:
            save_gif()
            print('若需 mp4 请安装 ffmpeg: brew install ffmpeg')
        except Exception as e:
            print('保存 gif 失败:', e)
