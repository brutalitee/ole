import time
import config
from anneal import run_one_search
from best_manager import save_if_better, make_submission_csv
from visual import draw_picture
def main():
    print(f"=== Batch {config.START_N} -> {config.END_N} ===")
    print(f"Steps per n: {config.TOTAL_STEPS}")
    print("Lightweight pure-Python PNG pictures enabled\n")
    for n in range(config.START_N, config.END_N + 1):
        t0 = time.time()
        print(f"Working on n = {n} ...")
        xs, ys, angs, final_L = run_one_search(how_many=n, total_steps=config.TOTAL_STEPS, draw_every=config.DRAW_EVERY, draw_func=draw_picture)
        draw_picture(xs, ys, angs, final_L, config.TOTAL_STEPS)
        save_if_better(n, xs, ys, angs, final_L)
        elapsed = time.time() - t0
        print(f"  finished n={n} in {elapsed/60:.1f} min   L={final_L:.6f}\n")
    make_submission_csv("submission.csv")
    print("Batch done. submission.csv + PNG pictures are ready.")
if __name__ == "__main__":
    main()
