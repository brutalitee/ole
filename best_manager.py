# ----------------------------------------------------------------
# FILE: best_manager.py
# ----------------------------------------------------------------
import os
import json
import csv
import math
import time
import hashlib
import glob
from anneal import grid_packing
from geometry import is_valid_packing
import config

HISTORY_FILE = "history.csv"

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

    # hard reject invalid packings
    if not is_valid_packing(xs, ys, angs, box):
        print(f"  !!! INVALID packing for n={n} (L={box:.6f}) – rejected")
        log_history(n, step or 0, box, note="INVALID rejected")
        return False

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

def should_skip(n):
    """Resume helper – skip if we already have a decent result"""
    data = load_best(n)
    if data is None:
        return False
    # skip if score is already quite good (you can tighten later)
    return data["score"] < 0.15

def make_submission_csv(filename="submission.csv"):
    ensure_folder()
    rows = []
    id_counter = 0
    total_score = 0.0
    count = 0

    for n in range(1, 1001):
        data = load_best(n)
        if data is None or not is_valid_packing(data["xs"], data["ys"], data["angs"], data["L"]):
            xs, ys, angs, L = grid_packing(n)
            save_if_better(n, xs, ys, angs, L, step=0)
            data = load_best(n)

        for i in range(n):
            rows.append([
                id_counter, n, i,
                f"{data['xs'][i]:.8f}",
                f"{data['ys'][i]:.8f}",
                f"{data['angs'][i]:.8f}",
            ])
            id_counter += 1

        total_score += data["L"] / math.sqrt(n) - 1.0
        count += 1

    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "n", "square_id", "x", "y", "angle"])
        writer.writerows(rows)

    print(f"wrote {filename} with {len(rows)} rows | total_score≈{total_score:.5f} ({count} n)")