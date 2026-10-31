# ==== anneal.py =====
import math
import secrets
from geometry import two_squares_overlap, current_box_size, shift_to_origin
import config

def grid_packing(n):
    k = math.ceil(math.sqrt(n))
    xs, ys, angs = [], [], []
    for i in range(n):
        xs.append((i % k) + 0.5)
        ys.append((i // k) + 0.5)
        angs.append(0.0)
    return xs, ys, angs, float(k)

def simple_45_start(n):
    # basic constructive start for a few classic cases
    # returns xs, ys, angs, rough_L or None if not applicable
    if n == 5:
        # classic 2 + 1/sqrt(2) style layout (approximate positions)
        s = 2 + 1/math.sqrt(2)
        xs = [0.5, 1.5, 0.5, 1.5, 1.0]
        ys = [0.5, 0.5, 1.5, 1.5, 1.0]
        angs = [0.0, 0.0, 0.0, 0.0, math.pi/4]
        return xs, ys, angs, s
    if n == 10:
        s = 3 + 1/math.sqrt(2)
        xs, ys, angs = [], [], []
        # three rows of three + one tilted
        for i in range(9):
            xs.append((i % 3) + 0.5)
            ys.append((i // 3) + 0.5)
            angs.append(0.0)
        xs.append(1.5)
        ys.append(1.5)
        angs.append(math.pi/4)
        return xs, ys, angs, s
    return None

def run_one_search(how_many, total_steps, draw_every=0, draw_func=None):
    from best_manager import load_best

    # prefer previous best, then simple construction, then grid
    old = load_best(how_many)
    if old is not None:
        xs = list(old["xs"])
        ys = list(old["ys"])
        angs = list(old["angs"])
        box = old["L"]
        print(f"  n={how_many}  starting from previous best L={box:.5f}")
    else:
        constr = simple_45_start(how_many)
        if constr is not None:
            xs, ys, angs, box = constr
            print(f"  n={how_many}  starting from simple 45-deg construction L={box:.5f}")
        else:
            xs, ys, angs, box = grid_packing(how_many)
            print(f"  n={how_many}  starting from grid L={box:.5f}")

    xs, ys = shift_to_origin(xs, ys, angs)
    box = current_box_size(xs, ys, angs)
    temp = config.START_TEMP
    rng = secrets.SystemRandom()

    for step in range(total_steps):
        scale = max(0.15, temp / config.START_TEMP)
        move_sz  = config.BASE_MOVE_SIZE  * scale
        angle_sz = config.BASE_ANGLE_SIZE * scale

        i = rng.randrange(how_many)
        old_x, old_y, old_a = xs[i], ys[i], angs[i]

        xs[i] += rng.gauss(0, move_sz)
        ys[i] += rng.gauss(0, move_sz)
        angs[i] += rng.gauss(0, angle_sz)

        hit = any(two_squares_overlap(xs[i], ys[i], angs[i], xs[j], ys[j], angs[j])
                  for j in range(how_many) if j != i)

        if hit:
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

    # local polish
    for _ in range(3000):
        i = rng.randrange(how_many)
        old = (xs[i], ys[i], angs[i])
        xs[i] += rng.gauss(0, 0.007)
        ys[i] += rng.gauss(0, 0.007)
        angs[i] += rng.gauss(0, 0.007)

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

    return xs, ys, angs, box