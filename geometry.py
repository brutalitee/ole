# === geometry.py ===
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
    # early distance cull
    dx = bx - ax
    dy = by - ay
    if dx*dx + dy*dy > 2.9:
        return False

    # four axes only (two edge directions from each square)
    for axis_ang in (aang, aang + math.pi/2, bang, bang + math.pi/2):
        nx = math.cos(axis_ang)
        ny = math.sin(axis_ang)
        dist = abs(dx * nx + dy * ny)

        # half-width of a unit square projected onto this axis
        r1 = 0.5 * (abs(math.cos(axis_ang - aang)) + abs(math.sin(axis_ang - aang)))
        r2 = 0.5 * (abs(math.cos(axis_ang - bang)) + abs(math.sin(axis_ang - bang)))

        if dist > r1 + r2 + 1e-10:
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