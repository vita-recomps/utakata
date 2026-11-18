"""Draws utakata's icon, shinobido2.ico: a throwing star on a dark rounded square, in the style of
ss-delta's (a plain shape, no game artwork; the game window shows the game's own icon at run time).
The fork keeps the result in vita3k/games/shinobido2/; the Linux and macOS setups take their PNG and
.icns from it. Needs Pillow.

  python -I tools/make-icon.py <out.ico> [<preview.png>]
"""
import math
import sys

from PIL import Image, ImageDraw

S = 1024  # drawn at this size, then scaled down for each of the icon's sizes
BACKGROUND = (20, 16, 18, 255)
STAR = (178, 28, 36, 255)
SIZES = (16, 24, 32, 48, 64, 128, 256)


def blade_points(cx, cy, angle, tip, waist, waist_angle, steps=24):
    """One blade, tip outward at angle: its two edges curve in (a concave kite)."""
    pts = []
    for side in (-1, 1):
        a0 = angle + side * waist_angle
        start = (cx + waist * math.cos(a0), cy + waist * math.sin(a0))
        end = (cx + tip * math.cos(angle), cy + tip * math.sin(angle))
        # control point pulled toward the blade's axis, so each edge curves inward
        ctrl_r = (waist + tip) * 0.42
        ctrl = (cx + ctrl_r * math.cos(angle + side * waist_angle * 0.18),
                cy + ctrl_r * math.sin(angle + side * waist_angle * 0.18))
        edge = []
        for i in range(steps + 1):
            t = i / steps
            x = (1 - t) ** 2 * start[0] + 2 * (1 - t) * t * ctrl[0] + t * t * end[0]
            y = (1 - t) ** 2 * start[1] + 2 * (1 - t) * t * ctrl[1] + t * t * end[1]
            edge.append((x, y))
        pts.append(edge)
    # first edge from its waist to the tip, the second back from the tip to its waist
    return pts[0] + pts[1][::-1][1:]


def draw():
    img = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    margin = S * 0.03
    d.rounded_rectangle((margin, margin, S - margin, S - margin), radius=S * 0.18, fill=BACKGROUND)
    cx = cy = S / 2
    tip, waist = S * 0.40, S * 0.16
    for k in range(4):
        angle = math.radians(-90 + 45 + 90 * k)  # an X, so it reads as a star at 16 pixels
        d.polygon(blade_points(cx, cy, angle, tip, waist, math.radians(46)), fill=STAR)
    d.ellipse((cx - waist, cy - waist, cx + waist, cy + waist), fill=STAR)
    d.ellipse((cx - S * 0.05, cy - S * 0.05, cx + S * 0.05, cy + S * 0.05), fill=BACKGROUND)
    return img


def main():
    if len(sys.argv) not in (2, 3):
        sys.exit(__doc__)
    big = draw()
    images = [big.resize((n, n), Image.LANCZOS) for n in SIZES]
    # Pillow writes every size as a PNG inside the .ico, which the kit's ico_to_png reads
    images[-1].save(sys.argv[1], format='ICO', sizes=[(n, n) for n in SIZES], append_images=images[:-1])
    if len(sys.argv) == 3:
        images[-1].save(sys.argv[2])


if __name__ == '__main__':
    main()
