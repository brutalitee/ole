import os
import json
import csv
import math
from anneal import grid_packing
import config
def ensure_folder():
    os.makedirs(config.BEST_FOLDER, exist_ok=True)
def best_file(n):
    return os.path.join(config.BEST_FOLDER, f"best_n{n}.json")
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
        data = {"n": n, "L": box, "score": box / math.sqrt(n) - 1.0, "xs": xs, "ys": ys, "angs": angs}
        with open(best_file(n), "w") as f:
            json.dump(data, f)
        print(f"  --> new best for n={n}  L={box:.6f}")
        return True
    else:
        print(f"  (not better than previous best L={old['L']:.6f})")
        return False
def make_submission_csv(filename="submission.csv"):
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
            rows.append([id_counter, n, i, f"{data['xs'][i]:.8f}", f"{data['ys'][i]:.8f}", f"{data['angs'][i]:.8f}"])
            id_counter += 1
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "n", "square_id", "x", "y", "angle"])
        writer.writerows(rows)
    print(f"wrote {filename} with {len(rows)} rows (complete 1-1000)")
