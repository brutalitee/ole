# ==== main.py =====
import config
from anneal import run_one_search
from visual import draw_picture
from best_manager import save_if_better, make_submission_csv
import time

def main():
    start_n = config.START_N
    end_n   = config.END_N
    print(f"=== Batch {start_n} → {end_n} ===")
    print(f"Steps per n: {config.TOTAL_STEPS}")

    for n in range(start_n, end_n + 1):
        t0 = time.time()
        print(f"\nWorking on n = {n} ...")

        xs, ys, angs, final_L = run_one_search(
            how_many=n,
            total_steps=config.TOTAL_STEPS,
            draw_every=config.DRAW_EVERY,
            draw_func=draw_picture if config.DRAW_EVERY > 0 else None,
        )

        save_if_better(n, xs, ys, angs, final_L)
        elapsed = time.time() - t0
        print(f"  finished n={n} in {elapsed/60:.1f} min   L={final_L:.6f}")

    # Always rebuild a full valid submission
    make_submission_csv("submission.csv")
    print("\nBatch done. submission.csv is ready (and safe to upload).")

if __name__ == "__main__":
    main()