# ==== visual.py =====
import struct
import zlib
from geometry import get_corners
import config

def _png_chunk(chunk_type, data):
    chunk = chunk_type + data
    return (struct.pack(">I", len(data)) +
            chunk +
            struct.pack(">I", zlib.crc32(chunk) & 0xffffffff))

def save_png(filename, width, height, rgba_pixels):
    raw = b""
    for y in range(height):
        raw += b"\x00"
        for x in range(width):
            r, g, b, a = rgba_pixels[y * width + x]
            raw += bytes((r, g, b, a))
    compressed = zlib.compress(raw, level=6)
    png = b"\x89PNG\r\n\x1a\n"
    png += _png_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
    png += _png_chunk(b"IDAT", compressed)
    png += _png_chunk(b"IEND", b"")
    with open(filename, "wb") as f:
        f.write(png)

def draw_picture(xs, ys, angs, box, step):
    size = config.PIC_SIZE
    margin = 0.08 * box
    scale = (size - 2) / (box + 2 * margin)

    pixels = [(255, 255, 255, 255)] * (size * size)

    def set_pixel(px, py, color=(0, 0, 0, 255)):
        if 0 <= px < size and 0 <= py < size:
            pixels[py * size + px] = color

    def draw_line(x0, y0, x1, y1):
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            set_pixel(x0, y0)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    for i in range(len(xs)):
        corners = get_corners(xs[i], ys[i], angs[i])
        pts = []
        for px, py in corners:
            screen_x = int((px + margin) * scale)
            screen_y = int((box - py + margin) * scale)
            pts.append((screen_x, screen_y))
        for j in range(4):
            draw_line(pts[j][0], pts[j][1], pts[(j+1)%4][0], pts[(j+1)%4][1])

    # outer box
    b0 = int(margin * scale)
    b1 = int((box + margin) * scale)
    draw_line(b0, b0, b1, b0)
    draw_line(b1, b0, b1, b1)
    draw_line(b1, b1, b0, b1)
    draw_line(b0, b1, b0, b0)

    filename = f"pack_n{len(xs)}_step{step}.png"
    save_png(filename, size, size, pixels)
    print(f"  saved picture {filename}")