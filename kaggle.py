# ============================================================
# COMPLETE PROJECT – single file for easy copy
# Save as main.py  OR  split into the named files if you prefer
# ============================================================

# === config.py ====
# settings you change most often

START_N = 1
END_N   = 50          # inclusive. Change for each batch (1-50, 51-100, ...)

TOTAL_STEPS = 80000   # lower = faster, higher = better (try 40000–150000)
DRAW_EVERY  = 0       # 0 = never draw (recommended on phone)

START_TEMP = 0.15
END_TEMP   = 0.0005
COOL_RATE  = 0.99997

BASE_MOVE_SIZE  = 0.05
BASE_ANGLE_SIZE = 0.04

BEST_FOLDER = "best_results"


# === geometry.py =====
import math

def get_corners(cx, cy, ang):
    c = math.cos(ang)
    s = math.sin(ang)
    half = 0.5
    local = [(-half, -half), (half, -half), (half, half), (-half, half)]
    corners = []
    for lx, ly in local:
        rx = lx * c - ly * s
        ry = lx * s + ly * c
        corners.append((cx + rx, cy + ry))
    return corners

def two_squares_overlap(ax, ay, aang, bx, by, bang):
    if (ax - bx)**2 + (ay - by)**2 > 2.9:
        return False

    a_corners = get_corners(ax, ay, aang)
    b_corners = get_corners(bx, by, bang)

    axes = []
    for corners in (a_corners, b_corners):
        for i in range(4):
            x1, y1 = corners[i]
            x2, y2 = corners[(i + 1) % 4]
            axes.append((-(y2 - y1), x2 - x1))

    for nx, ny in axes:
        length = math.hypot(nx, ny)
        if length < 1e-12:
            continue
        nx /= length
        ny /= length

        projs_a = [px * nx + py * ny for px, py in a_corners]
        min_a, max_a = min(projs_a), max(projs_a)

        projs_b = [px * nx + py * ny for px, py in b_corners]
        min_b, max_b = min(projs_b), max(projs_b)

        if max_a < min_b - 1e-9 or max_b < min_a - 1e-9:
            return False
    return True

def bounding_box(xs, ys, angs):
    min_x = min_y = float("inf")
    max_x = max_y = float("-inf")
    for i in range(len(xs)):
        for px, py in get_corners(xs[i], ys[i], angs[i]):
            if px < min_x: min_x = px
            if py < min_y: min_y = py
            if px > max_x: max_x = px
            if py > max_y: max_y = py
    return min_x, min_y, max_x, max_y

def current_box_size(xs, ys, angs):
    min_x, min_y, max_x, max_y = bounding_box(xs, ys, angs)
    return max(max_x - min_x, max_y - min_y)

def shift_to_origin(xs, ys, angs):
    min_x, min_y, _, _ = bounding_box(xs, ys, angs)
    for i in range(len(xs)):
        xs[i] -= min_x
        ys[i] -= min_y
    return xs, ys


# ==== anneal.py =====
import secrets

def make_random_start(how_many):
    rng = secrets.SystemRandom()
    side = math.ceil(math.sqrt(how_many)) + 0.8
    xs = [rng.uniform(0.5, side - 0.5) for _ in range(how_many)]
    ys = [rng.uniform(0.5, side - 0.5) for _ in range(how_many)]
    angs = [rng.uniform(-0.4, 0.4) for _ in range(how_many)]
    return xs, ys, angs

def grid_packing(n):
    """Safe trivial packing – always valid."""
    k = math.ceil(math.sqrt(n))
    xs, ys, angs = [], [], []
    for i in range(n):
        xs.append((i % k) + 0.5)
        ys.append((i // k) + 0.5)
        angs.append(0.0)
    return xs, ys, angs, float(k)

def run_one_search(how_many, total_steps, draw_every=0, draw_func=None):
    xs, ys, angs = make_random_start(how_many)
    xs, ys = shift_to_origin(xs, ys, angs)
    box = current_box_size(xs, ys, angs)
    temp = START_TEMP
    rng = secrets.SystemRandom()

    print(f"  n={how_many}  starting L={box:.5f}")

    for step in range(total_steps):
        scale = max(0.15, temp / START_TEMP)
        move_sz  = BASE_MOVE_SIZE  * scale
        angle_sz = BASE_ANGLE_SIZE * scale

        i = rng.randrange(how_many)
        old_x, old_y, old_a = xs[i], ys[i], angs[i]

        xs[i] += rng.gauss(0, move_sz)
        ys[i] += rng.gauss(0, move_sz)
        angs[i] += rng.gauss(0, angle_sz)

        hit = False
        for j in range(how_many):
            if j == i:
                continue
            if two_squares_overlap(xs[i], ys[i], angs[i],
                                   xs[j], ys[j], angs[j]):
                hit = True
                break

        if hit:
            xs[i], ys[i], angs[i] = old_x, old_y, old_a
            continue

        new_box = current_box_size(xs, ys, angs)
        diff = new_box - box

        accept = False
        if diff < 0:
            accept = True
        elif temp > 1e-12 and rng.random() < math.exp(-diff / temp):
            accept = True

        if accept:
            box = new_box
            xs, ys = shift_to_origin(xs, ys, angs)
            box = current_box_size(xs, ys, angs)
        else:
            xs[i], ys[i], angs[i] = old_x, old_y, old_a

        temp *= COOL_RATE
        if temp < END_TEMP:
            temp = END_TEMP

        if draw_func and draw_every > 0 and step % draw_every == 0 and step > 0:
            score = box / math.sqrt(how_many) - 1.0
            print(f"    step {step}  L={box:.6f}  score={score:.6f}")
            draw_func(xs, ys, angs, box, step)

    # cheap local polish
    for _ in range(3000):
        i = rng.randrange(how_many)
        old = (xs[i], ys[i], angs[i])
        xs[i] += rng.gauss(0, 0.008)
        ys[i] += rng.gauss(0, 0.008)
        angs[i] += rng.gauss(0, 0.008)
        if any(two_squares_overlap(xs[i], ys[i], angs[i],
                                   xs[j], ys[j], angs[j])
               for j in range(how_many) if j != i):
            xs[i], ys[i], angs[i] = old
            continue
        new_box = current_box_size(xs, ys, angs)
        if new_box < box - 1e-12:
            box = new_box
            xs, ys = shift_to_origin(xs, ys, angs)
            box = current_box_size(xs, ys, angs)
        else:
            xs[i], ys[i], angs[i] = old

    return xs, ys, angs, box


# ==== visual.py =====
# Optional – only used when DRAW_EVERY > 0
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon

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
except ImportError:
    def draw_picture(*args, **kwargs):
        pass


# ==== best_manager.py =====
import os
import json
import csv

def ensure_folder():
    os.makedirs(BEST_FOLDER, exist_ok=True)

def best_file(n):
    return os.path.join(BEST_FOLDER, f"best_n{n}.json")

def load_best(n):
    path = best_file(n)
    if not os.path.exists(path):
        return None
    with open(path, "r") as f:
        return json.load(f)

def save_if_better(n, xs, ys, angs, box):
    ensure_folder()
    old = load_best(n)
    if old is None or box < old["L"] - 1e-9:
        data = {
            "n": n,
            "L": box,
            "score": box / math.sqrt(n) - 1.0,
            "xs": xs,
            "ys": ys,
            "angs": angs,
        }
        with open(best_file(n), "w") as f:
            json.dump(data, f)
        print(f"  --> new best for n={n}  L={box:.6f}")
        return True
    else:
        print(f"  (not better than previous best L={old['L']:.6f})")
        return False

def make_submission_csv(filename="submission.csv"):
    """Build a complete submission for n=1..1000.
    Uses saved best results; falls back to grid packing for missing n.
    """
    ensure_folder()
    rows = []
    id_counter = 0

    for n in range(1, 1001):
        data = load_best(n)
        if data is None:
            xs, ys, angs, L = grid_packing(n)
            save_if_better(n, xs, ys, angs, L)
            data = load_best(n)

        for i in range(n):
            rows.append([
                id_counter,
                n,
                i,
                f"{data['xs'][i]:.8f}",
                f"{data['ys'][i]:.8f}",
                f"{data['angs'][i]:.8f}",
            ])
            id_counter += 1

    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "n", "square_id", "x", "y", "angle"])
        writer.writerows(rows)
    print(f"wrote {filename} with {len(rows)} rows (complete 1–1000)")


# ==== main.py =====
import time

def main():
    print(f"=== Batch {START_N} → {END_N} ===")
    print(f"Steps per n: {TOTAL_STEPS}")

    for n in range(START_N, END_N + 1):
        t0 = time.time()
        print(f"\nWorking on n = {n} ...")

        xs, ys, angs, final_L = run_one_search(
            how_many=n,
            total_steps=TOTAL_STEPS,
            draw_every=DRAW_EVERY,
            draw_func=draw_picture if DRAW_EVERY > 0 else None,
        )

        save_if_better(n, xs, ys, angs, final_L)
        elapsed = time.time() - t0
        print(f"  finished n={n} in {elapsed/60:.1f} min   L={final_L:.6f}")

    make_submission_csv("submission.csv")
    print("\nBatch done. submission.csv is ready (and safe to upload).")

if __name__ == "__main__":
    main()
