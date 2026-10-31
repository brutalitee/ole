# ----------------------------------------------------------------
# FILE: main.py
# ----------------------------------------------------------------
import time
import config
from anneal import run_one_search
from best_manager import save_if_better, make_submission_csv, should_skip
from visual import draw_picture

def main():
    print(f"=== {config.BRANCH_NAME} | Batch {config.START_N} → {config.END_N} ===")
    print(f"Steps per start: {config.TOTAL_STEPS} | Starts: {config.NUM_STARTS}")
    print("Robust geometry + multi-start + resume + pure PNG\n")

    for n in range(config.START_N, config.END_N + 1):
        if should_skip(n):
            print(f"Skipping n={n} (already has good result)")
            continue

        t0 = time.time()
        print(f"Working on n = {n} ...")

        xs, ys, angs, final_L = run_one_search(
            how_many=n,
            total_steps=config.TOTAL_STEPS,
            draw_every=config.DRAW_EVERY,
            draw_func=draw_picture,
        )

        draw_picture(xs, ys, angs, final_L, config.TOTAL_STEPS)
        save_if_better(n, xs, ys, angs, final_L, step=config.TOTAL_STEPS)

        elapsed = time.time() - t0
        print(f"  finished n={n} in {elapsed/60:.1f} min   L={final_L:.6f}\n")

    make_submission_csv("submission.csv")
    print("Batch done. submission.csv + PNGs + history.csv ready.")

if __name__ == "__main__":
    main()