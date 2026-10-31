# ----------------------------------------------------------------
# FILE: anneal.py
# ----------------------------------------------------------------
import math
import secrets
from geometry import (two_squares_overlap, current_box_size,
                      shift_to_origin, is_valid_packing)
import config

def make_random_start(how_many):
    rng = secrets.SystemRandom()
    side = math.ceil(math.sqrt(how_many)) + 0.9
    xs = [rng.uniform(0.5, side-0.5) for _ in range(how_many)]
    ys = [rng.uniform(0.5, side-0.5) for _ in range(how_many)]
    angs = [rng.uniform(-0.5, 0.5) for _ in range(how_many)]
    return xs, ys, angs

def smart_start(how_many):
    """Grid + small random tilts + jitter"""
    k = math.ceil(math.sqrt(how_many))
    xs, ys, angs = [], [], []
    rng = secrets.SystemRandom()
    for i in range(how_many):
        xs.append((i % k) + 0.5 + rng.uniform(-0.08, 0.08))
        ys.append((i // k) + 0.5 + rng.uniform(-0.08, 0.08))
        angs.append(rng.uniform(-0.25, 0.25))
    return xs, ys, angs

def grid_packing(n):
    k = math.ceil(math.sqrt(n))
    xs = [(i % k) + 0.5 for i in range(n)]
    ys = [(i // k) + 0.5 for i in range(n)]
    angs = [0.0] * n
    return xs, ys, angs, float(k)

def run_one_search(how_many, total_steps, draw_every=0, draw_func=None):
    best_xs = best_ys = best_angs = None
    best_L = float("inf")

    for start_idx in range(config.NUM_STARTS):
        if start_idx == 0:
            xs, ys, angs = smart_start(how_many)
        else:
            xs, ys, angs = make_random_start(how_many)

        xs, ys = shift_to_origin(xs, ys, angs)
        box = current_box_size(xs, ys, angs)
        temp = config.START_TEMP
        rng = secrets.SystemRandom()

        print(f"  n={how_many} start#{start_idx+1}  L={box:.5f}")

        for step in range(total_steps):
            scale = max(0.12, temp / config.START_TEMP)
            move_sz  = config.BASE_MOVE_SIZE * scale
            angle_sz = config.BASE_ANGLE_SIZE * scale

            i = rng.randrange(how_many)
            old_x, old_y, old_a = xs[i], ys[i], angs[i]

            xs[i] += rng.gauss(0, move_sz)
            ys[i] += rng.gauss(0, move_sz)
            angs[i] += rng.gauss(0, angle_sz)

            if any(two_squares_overlap(xs[i], ys[i], angs[i], xs[j], ys[j], angs[j])
                   for j in range(how_many) if j != i):
                xs[i], ys[i], angs[i] = old_x, old_y, old_a
                continue

            new_box = current_box_size(xs, ys, angs)
            diff = new_box - box
            accept = diff < 0 or (temp > 1e-12 and rng.random() < math.exp(-diff / temp))

            if accept:
                box = new_box
                xs, ys = shift_to_origin(xs, ys, angs)
                box = current_box_size(xs, ys, angs)
            else:
                xs[i], ys[i], angs[i] = old_x, old_y, old_a

            temp = max(temp * config.COOL_RATE, config.END_TEMP)

            if draw_func and draw_every > 0 and step % draw_every == 0 and step > 0:
                score = box / math.sqrt(how_many) - 1.0
                print(f"    step {step}  L={box:.6f}  score={score:.6f}")
                draw_func(xs, ys, angs, box, step)

        # short local polish
        for _ in range(2500):
            i = rng.randrange(how_many)
            old = (xs[i], ys[i], angs[i])
            xs[i] += rng.gauss(0, 0.006)
            ys[i] += rng.gauss(0, 0.006)
            angs[i] += rng.gauss(0, 0.006)
            if any(two_squares_overlap(xs[i], ys[i], angs[i], xs[j], ys[j], angs[j])
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

        # final safety
        if is_valid_packing(xs, ys, angs, box) and box < best_L:
            best_L = box
            best_xs, best_ys, best_angs = xs[:], ys[:], angs[:]

    if best_xs is None:
        # fallback to grid
        return grid_packing(how_many)

    return best_xs, best_ys, best_angs, best_L