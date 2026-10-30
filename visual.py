# ==== visual.py =====
import matplotlib
matplotlib.use("Agg")          # important for Termux / headless
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from geometry import get_corners

def draw_picture(xs, ys, angs, box, step):
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.set_xlim(-0.1, box + 0.1)
    ax.set_ylim(-0.1, box + 0.1)
    ax.set_aspect("equal")
    for i in range(len(xs)):
        corners = get_corners(xs[i], ys[i], angs[i])
        poly = Polygon(corners, closed=True, fill=False,
                       edgecolor="black", linewidth=0.8)
        ax.add_patch(poly)
    ax.set_title(f"n={len(xs)}  L={box:.5f}  step={step}")
    plt.savefig(f"pack_n{len(xs)}_step{step}.png", dpi=100, bbox_inches="tight")
    plt.close()