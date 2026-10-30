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
    if (ax - bx)**2 + (ay - by)**2 > 2.9:
        return False
    a_corners = get_corners(ax, ay, aang)
    b_corners = get_corners(bx, by, bang)
    axes = []
    for corners in (a_corners, b_corners):
        for i in range(4):
            x1, y1 = corners[i]
            x2, y2 = corners[(i + 1) % 4]
            axes.append((-(y2 - y1), x2 - x1))
    for nx, ny in axes:
        length = math.hypot(nx, ny)
        if length < 1e-12:
            continue
        nx /= length
        ny /= length
        projs_a = [px * nx + py * ny for px, py in a_corners]
        min_a, max_a = min(projs_a), max(projs_a)
        projs_b = [px * nx + py * ny for px, py in b_corners]
        min_b, max_b = min(projs_b), max(projs_b)
        if max_a < min_b - 1e-9 or max_b < min_a - 1e-9:
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
