# --- Mandelbrot set 动画 ---
def mandelbrot_animation():
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation
    import numpy as np
    fig, ax = plt.subplots(figsize=(8,8))
    ax.axis('off')
    def mandelbrot(xmin, xmax, ymin, ymax, width, height, max_iter):
        x = np.linspace(xmin, xmax, width)
        y = np.linspace(ymin, ymax, height)
        X, Y = np.meshgrid(x, y)
        C = X + 1j * Y
        Z = np.zeros_like(C)
        img = np.zeros(C.shape, dtype=float)
        for i in range(max_iter):
            mask = np.abs(Z) <= 2
            Z[mask] = Z[mask] ** 2 + C[mask]
            img[mask & (img==0)] = i
        img[img==0] = max_iter
        return img
    ims = []
    # 动画参数：逐步缩放到细节区域
    zooms = np.linspace(1, 0.1, 60)
    for z in zooms:
        xmin, xmax = -2*z, 1.2*z
        ymin, ymax = -1.5*z, 1.5*z
        img = mandelbrot(xmin, xmax, ymin, ymax, 400, 400, 50)
        im = ax.imshow(img, cmap='twilight', extent=[xmin, xmax, ymin, ymax], animated=True)
        ims.append([im])
    ani = animation.ArtistAnimation(fig, ims, interval=100, blit=True, repeat_delay=1000)
    plt.show()
# --- 分形神经元/树状动画粒子系统 ---

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from matplotlib.patches import FancyArrowPatch
from matplotlib import colors as mcolors

def draw_branch(ax, x, y, angle, depth, max_depth, branch_length, branch_angle, color_map, lines, dots, color_idx):
    if depth > max_depth:
        dots.append((x, y, color_idx, depth))
        return
    n_branches = np.random.randint(2, 4)
    for i in range(n_branches):
        theta = angle + np.random.uniform(-branch_angle, branch_angle)
        length = branch_length * np.random.uniform(0.7, 1.1)
        # 贝塞尔曲线控制点
        ctrl_angle = angle + np.random.uniform(-0.5, 0.5)
        ctrl_len = length * np.random.uniform(0.3, 0.7)
        cx = x + ctrl_len * np.cos(ctrl_angle)
        cy = y + ctrl_len * np.sin(ctrl_angle)
        x2 = x + length * np.cos(theta)
        y2 = y + length * np.sin(theta)
        lines.append(((x, y), (cx, cy), (x2, y2), color_idx, depth))
        draw_branch(ax, x2, y2, theta, depth+1, max_depth, branch_length*0.8, branch_angle, color_map, lines, dots, color_idx+1)

def animate_neuron_tree():
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_facecolor('black')
    ax.axis('off')
    np.random.seed(42)
    # 生成所有分支和末端点
    lines, dots = [], []
    color_map = plt.get_cmap('hsv')
    n_roots = 4
    max_depth = 7
    for i in range(n_roots):
        angle = i * 2 * np.pi / n_roots + np.random.uniform(-0.2, 0.2)
        draw_branch(ax, 0, 0, angle, 0, max_depth, 1.0, np.pi/4, color_map, lines, dots, i*10)
    total = len(lines)
    def get_color(depth, max_depth, base_idx):
        # 越向外越浅，HSV色相+亮度渐变
        h = (base_idx % 100) / 100
        s = 0.7
        v = 0.3 + 0.7 * (depth / max_depth)
        return mcolors.hsv_to_rgb((h, s, v))
    def update(frame):
        ax.clear()
        ax.set_facecolor('black')
        ax.axis('off')
        n = int(total * frame / 100)
        # 记录已画过的末端点，避免重复
        drawn_dots = set()
        for (x1, y1), (cx, cy), (x2, y2), cidx, depth in lines[:n]:
            color = get_color(depth, max_depth, cidx)
            t = np.linspace(0, 1, 20)
            bx = (1-t)**2 * x1 + 2*(1-t)*t*cx + t**2 * x2
            by = (1-t)**2 * y1 + 2*(1-t)*t*cy + t**2 * y2
            ax.plot(bx, by, color=color, lw=0.8, alpha=0.85)
            # 每个分支的末端都画圆点
            if frame == 100 or n == total or (x2, y2) not in drawn_dots:
                ax.plot(x2, y2, 'o', color=color, markersize=3, alpha=0.95)
                drawn_dots.add((x2, y2))
        # 末端点（递归终止点）
        for x, y, cidx, depth in dots:
            if n > total * (depth/(max_depth+1)):
                color = get_color(depth, max_depth, cidx)
                ax.plot(x, y, 'o', color=color, markersize=3, alpha=0.95)
        ax.set_xlim(-3, 3)
        ax.set_ylim(-3, 3)
        return []
    ani = animation.FuncAnimation(fig, update, frames=101, interval=60, blit=False, repeat=False)
    plt.show()


# --- 主程序 ---
if __name__ == '__main__':
    print("请选择模式：1-分形神经元动画  2-Mandelbrot set 动画")
    mode = input("输入1或2：").strip()
    if mode == '2':
        mandelbrot_animation()
    else:
        animate_neuron_tree()