# ==== best_manager.py =====
import os
import json
import csv
import math
import time
import hashlib
from anneal import grid_packing
import config

HISTORY_FILE = "history.csv"

# Public best-known upper bounds / proven optima (snapshot of stable published values)
# Used only for comparison and integrity checks. Not claimed as your results.
PUBLIC_BEST = {
    1: 1.0,
    2: 2.0,
    3: 2.0,
    4: 2.0,
    5: 2.7071067811865475,   # 2 + 1/sqrt(2)  proven
    6: 3.0,
    7: 3.0,
    8: 3.0,
    9: 3.0,
    10: 3.7071067811865475,  # 3 + 1/sqrt(2)  proven
    11: 3.87708359002281,    # Trump, widely accepted optimal
    12: 4.0,
    13: 4.0,
    14: 4.0,
    15: 4.0,
    16: 4.0,
    17: 4.67553009360455,
    18: 4.822875655532295,   # 7/2 + sqrt(7)/2
    19: 4.885618083164126,   # 3 + 4/3 * sqrt(2)
    20: 5.0,
    21: 5.0,
    22: 5.0,
    23: 5.0,
    24: 5.0,
    25: 5.0,
    26: 5.621320343559643,
    27: 5.707106781186548,   # 5 + 1/sqrt(2)
    28: 5.82842712474619,    # approx 3+2*sqrt(2) family
    29: 5.9338,
    30: 6.0,
    31: 6.0,
    32: 6.0,
    33: 6.0,
    34: 6.0,
    35: 6.0,
    36: 6.0,
    37: 6.5986,
    38: 6.707106781186548,
    39: 6.8229,
    40: 6.8284,
}

def ensure_folder():
    os.makedirs(config.BEST_FOLDER, exist_ok=True)

def get_code_hash():
    try:
        with open("main.py", "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()[:8]
    except Exception:
        return "nohash"

def log_history(n, step, L, note=""):
    exists = os.path.exists(HISTORY_FILE)
    with open(HISTORY_FILE, "a", newline="") as f:
        w = csv.writer(f)
        if not exists:
            w.writerow(["timestamp", "n", "step", "L", "score", "code_hash", "branch", "note"])
        score = L / math.sqrt(n) - 1.0 if n > 0 else 0.0
        w.writerow([
            time.strftime("%Y-%m-%d %H:%M:%S"),
            n, step, f"{L:.6f}", f"{score:.6f}",
            get_code_hash(), config.BRANCH_NAME, note
        ])

def best_file(n):
    return os.path.join(config.BEST_FOLDER, f"best_n{n}.json")

def load_best(n):
    path = best_file(n)
    if not os.path.exists(path):
        return None
    with open(path, "r") as f:
        return json.load(f)

def save_if_better(n, xs, ys, angs, box, step=None):
    ensure_folder()
    old = load_best(n)
    if old is None or box < old["L"] - 1e-9:
        data = {
            "n": n,
            "L": float(box),
            "score": box / math.sqrt(n) - 1.0,
            "xs": xs,
            "ys": ys,
            "angs": angs,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "branch": config.BRANCH_NAME,
            "code_hash": get_code_hash(),
        }
        with open(best_file(n), "w") as f:
            json.dump(data, f, indent=2)
        print(f"  --> new best for n={n}  L={box:.6f}")
        log_history(n, step or config.TOTAL_STEPS, box, note="new best")
        return True
    else:
        print(f"  (not better than previous best L={old['L']:.6f})")
        log_history(n, step or config.TOTAL_STEPS, box, note="no improvement")
        return False

def compare_to_public(n, box):
    if n not in PUBLIC_BEST:
        print(f"  (no public reference stored for n={n})")
        return
    pub = PUBLIC_BEST[n]
    gap = box - pub
    print(f"  public best-known ≈ {pub:.6f}   your L = {box:.6f}   gap = {gap:+.6f}")
    if box < pub - 1e-6:
        print("  WARNING: your L is better than stored public value – check overlap/L calculation")
    grid_L = math.ceil(math.sqrt(n))
    if box > grid_L + 0.01:
        print("  WARNING: worse than trivial grid – something is wrong")

def make_submission_csv(filename="submission.csv"):
    ensure_folder()
    rows = []
    id_counter = 0

    for n in range(1, 1001):
        data = load_best(n)
        if data is None:
            xs, ys, angs, L = grid_packing(n)
            save_if_better(n, xs, ys, angs, L, step=0)
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

    total_score = 0.0
    count = 0
    for n in range(1, 1001):
        d = load_best(n)
        if d:
            total_score += d["L"] / math.sqrt(n) - 1.0
            count += 1
    print(f"wrote {filename} with {len(rows)} rows | total_score≈{total_score:.5f} ({count} n)")