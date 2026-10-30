import math
import secrets
from geometry import two_squares_overlap, current_box_size, shift_to_origin
import config
def make_random_start(how_many):
    rng = secrets.SystemRandom()
    side = math.ceil(math.sqrt(how_many)) + 0.8
    xs = [rng.uniform(0.5, side - 0.5) for _ in range(how_many)]
    ys = [rng.uniform(0.5, side - 0.5) for _ in range(how_many)]
    angs = [rng.uniform(-0.4, 0.4) for _ in range(how_many)]
    return xs, ys, angs
def grid_packing(n):
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
    temp = config.START_TEMP
    rng = secrets.SystemRandom()
    print(f"  n={how_many}  starting L={box:.5f}")
    for step in range(total_steps):
        scale = max(0.15, temp / config.START_TEMP)
        move_sz  = config.BASE_MOVE_SIZE  * scale
        angle_sz = config.BASE_ANGLE_SIZE * scale
        i = rng.randrange(how_many)
        old_x, old_y, old_a = xs[i], ys[i], angs[i]
        xs[i] += rng.gauss(0, move_sz)
        ys[i] += rng.gauss(0, move_sz)
        angs[i] += rng.gauss(0, angle_sz)
        hit = False
        for j in range(how_many):
            if j == i:
                continue
            if two_squares_overlap(xs[i], ys[i], angs[i], xs[j], ys[j], angs[j]):
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
        temp *= config.COOL_RATE
        if temp < config.END_TEMP:
            temp = config.END_TEMP
        if draw_func and draw_every > 0 and step % draw_every == 0 and step > 0:
            score = box / math.sqrt(how_many) - 1.0
            print(f"    step {step}  L={box:.6f}  score={score:.6f}")
            draw_func(xs, ys, angs, box, step)
    for _ in range(2500):
        i = rng.randrange(how_many)
        old = (xs[i], ys[i], angs[i])
        xs[i] += rng.gauss(0, 0.008)
        ys[i] += rng.gauss(0, 0.008)
        angs[i] += rng.gauss(0, 0.008)
        if any(two_squares_overlap(xs[i], ys[i], angs[i], xs[j], ys[j], angs[j]) for j in range(how_many) if j != i):
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
