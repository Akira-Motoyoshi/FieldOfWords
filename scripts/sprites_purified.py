"""Purified flowers (poison -> good). Palette: GOOD only. Same canvas size as the poison source.
rafflesia -> giant crowned gold rose 48x48 | haetori -> smiling sunflower 32x32
saboten -> pink-blooming cactus 32x32 | chili -> sun gerbera 32x32 | blackhole -> star flower 48x48"""
import math
from PIL import Image, ImageDraw
from sprites_good import g, canvas, ring, px, clear, leaf, sparkle

# ------------------------------------------------------------------ rafflesia -> giant gold rose with crown
def p_rafflesia(f):
    im, d = canvas(48, 48); cx, cy = 24, 27
    d.polygon([(9, 46), (5, 39), (15, 42), (20, 46)], fill=g["stem"]); d.polygon([(39, 46), (43, 40), (33, 42), (28, 46)], fill=g["stem_dark"])
    d.rectangle([22, 40, 25, 46], fill=g["stem"]); d.line([(25, 40), (25, 46)], fill=g["stem_dark"])
    d.polygon([(19, 41), (14, 38), (18, 44)], fill=g["stem_dark"]); d.polygon([(29, 41), (34, 37), (30, 44)], fill=g["stem_dark"])
    for k in range(8):                                                   # outer petals
        a = k * math.pi/4 + 0.2; x, y = cx + 11*math.cos(a), cy + 9.5*math.sin(a)
        d.ellipse([x-7, y-6, x+7, y+6], fill=g["yellow_deep"], outline=g["gold"])
    for k in range(6):                                                   # middle petals
        a = k * math.pi/3 + 0.7; x, y = cx + 6.5*math.cos(a), cy + 5.5*math.sin(a)
        d.ellipse([x-5, y-4, x+5, y+4], fill=g["yellow"], outline=g["gold"])
    for k in range(4):                                                   # inner petals
        a = k * math.pi/2 + 0.3; x, y = cx + 3*math.cos(a), cy + 2.5*math.sin(a)
        d.ellipse([x-3.5, y-3, x+3.5, y+3], fill=g["cream"], outline=g["gold"])
    d.arc([cx-3, cy-3, cx+3, cy+3], 200, 500, fill=g["yellow_deep"])
    d.polygon([(17, 10), (17, 3), (21, 7), (24, 1), (27, 7), (31, 3), (31, 10)], fill=g["gold"])   # crown
    d.rectangle([17, 9, 31, 11], fill=g["yellow"]); d.line([(17, 11), (31, 11)], fill=g["gold"])
    px(im, 24, 5, g["red"] if f == 1 else g["pink_deep"]); px(im, 19, 9, g["sky"]); px(im, 29, 9, g["pink"])
    im = ring(im)
    pts = [((4, 6), (43, 9), (41, 33), (6, 31)), ((43, 4), (4, 14), (7, 36), (42, 28))][f - 1]
    for i, (x, y) in enumerate(pts): sparkle(im, x, y, big=(i % 2 == 0))
    return im

# ------------------------------------------------------------------ haetori -> smiling sunflower
def p_haetori(f):
    im, d = canvas(32, 32); sw = 1 if f == 2 else 0; hx, hy = 16 + sw, 11
    d.rectangle([15, 18, 16, 30], fill=g["stem"]); d.line([(16, 18), (16, 30)], fill=g["stem_dark"])
    leaf(d, [(15, 27), (6, 22 - sw), (5, 26 - sw), (14, 30)]); leaf(d, [(17, 25), (26, 20 - sw), (27, 24 - sw), (18, 28)])
    d.line([(8, 24 - sw), (14, 28)], fill=g["leaf_light"]); d.line([(24, 22 - sw), (18, 26)], fill=g["leaf_light"])
    for k in range(10):
        a = k * math.pi/5; x, y = hx + 7.5*math.cos(a), hy + 7.5*math.sin(a)
        d.ellipse([x-2.8, y-2.8, x+2.8, y+2.8], fill=g["yellow"] if k % 2 else g["yellow_deep"])
    d.ellipse([hx-5.5, hy-5.5, hx+5.5, hy+5.5], fill=g["center"])
    px(im, hx - 2, hy - 2, g["cream"]); px(im, hx - 2, hy - 1, g["cream"])
    if f == 1: px(im, hx + 2, hy - 2, g["cream"]); px(im, hx + 2, hy - 1, g["cream"])
    else:      d.line([(hx + 1, hy - 2), (hx + 3, hy - 2)], fill=g["cream"])             # wink
    for (dx, dy) in ((-3, 1), (-2, 2), (-1, 3), (0, 3), (1, 3), (2, 2), (3, 1)): px(im, hx + dx, hy + dy, g["cream"])   # big smile
    return ring(im)

# ------------------------------------------------------------------ saboten -> pink-blooming cactus
def pink_flower(d, cx, cy, r=3):
    for k in range(5):
        a = -math.pi/2 + k * 2*math.pi/5; x, y = cx + r*math.cos(a), cy + r*math.sin(a)
        d.ellipse([x-2, y-2, x+2, y+2], fill=g["pink"])
    d.ellipse([cx-1, cy-1, cx+1, cy+1], fill=g["cream"])

def p_saboten(f):
    im, d = canvas(32, 32); sw = 1 if f == 2 else 0
    d.rounded_rectangle([9, 11, 23, 30], 4, fill=g["stem"]); d.rectangle([19, 13, 23, 29], fill=g["stem_dark"])
    d.line([(13, 12), (13, 29)], fill=g["leaf_light"]); d.line([(17, 12), (17, 29)], fill=g["stem_dark"])
    d.rounded_rectangle([4, 16, 11, 20], 2, fill=g["stem"]); d.rounded_rectangle([3, 11, 7, 19], 2, fill=g["stem"])
    d.rectangle([22, 21, 26, 23], fill=g["stem_dark"])
    for (x, y) in ((9, 14), (23, 16), (9, 24), (23, 26), (15, 12), (11, 27)): px(im, x, y, g["cream"])     # soft white spines
    for ex in (12, 18):
        d.rectangle([ex, 17, ex + 2, 19], fill=g["white"]); px(im, ex + 1, 18, g["outline"])
    if f == 2:
        for ex in (12, 18): d.line([(ex, 18), (ex + 2, 18)], fill=g["outline"])
    d.line([(13, 22), (14, 23)], fill=g["outline"]); d.line([(14, 23), (17, 23)], fill=g["outline"]); d.line([(17, 23), (18, 22)], fill=g["outline"])
    pink_flower(d, 16 + sw, 8, 3); pink_flower(d, 5, 9, 2); pink_flower(d, 23, 14, 2)
    d.rectangle([15, 10, 16, 11], fill=g["stem"])
    return ring(im)

# ------------------------------------------------------------------ chili -> sun gerbera
def p_chili(f):
    im, d = canvas(32, 32); hx, hy = 16, 12; ph = 0.22 if f == 2 else 0.0
    d.rectangle([15, 20, 16, 30], fill=g["stem"]); d.line([(16, 20), (16, 30)], fill=g["stem_dark"])
    leaf(d, [(15, 29), (7, 23), (6, 27), (14, 30)]); leaf(d, [(17, 28), (25, 22), (26, 26), (18, 29)])
    d.line([(8, 25), (14, 29)], fill=g["leaf_light"]); d.line([(24, 24), (18, 28)], fill=g["leaf_light"])
    for k in range(14):
        a = k * 2*math.pi/14 + ph; x, y = hx + 8*math.cos(a), hy + 8*math.sin(a)
        d.ellipse([x-2.2, y-2.2, x+2.2, y+2.2], fill=g["orange"] if k % 2 else g["yellow_deep"])
    for k in range(14):
        a = k * 2*math.pi/14 + ph; x, y = hx + 5*math.cos(a), hy + 5*math.sin(a)
        d.ellipse([x-1.6, y-1.6, x+1.6, y+1.6], fill=g["orange"])
    d.ellipse([hx-4, hy-4, hx+4, hy+4], fill=g["yellow"]); d.ellipse([hx-2, hy-2, hx+2, hy+2], fill=g["yellow_deep"])
    px(im, hx - 3, hy - 2, g["cream"]); px(im, hx - 2, hy - 3, g["white"])
    return ring(im)

# ------------------------------------------------------------------ blackhole -> star flower
def star(cx, cy, R, r, rot):
    pts = []
    for i in range(10):
        a = -math.pi/2 + rot + i * math.pi/5; rad = R if i % 2 == 0 else r
        pts.append((cx + rad*math.cos(a), cy + rad*math.sin(a)))
    return pts

def p_blackhole(f):
    im, d = canvas(48, 48); cx, cy = 24, 23; rot = 0.14 if f == 2 else 0.0
    d.polygon([(23, 44), (13, 42), (9, 46), (22, 46)], fill=g["stem"]); d.polygon([(25, 44), (35, 41), (39, 46), (26, 46)], fill=g["stem_dark"])
    d.rectangle([23, 36, 24, 46], fill=g["stem"]); d.line([(24, 36), (24, 46)], fill=g["stem_dark"])
    d.polygon(star(cx, cy, 20, 9, rot), fill=g["blue"])
    d.polygon(star(cx - 1, cy - 1, 15, 6, rot), fill=g["sky"])
    d.polygon(star(cx, cy, 10, 5, rot + 0.3), fill=g["blue"])
    d.ellipse([cx-4, cy-4, cx+4, cy+4], fill=g["yellow"]); d.ellipse([cx-2, cy-2, cx+2, cy+2], fill=g["yellow_deep"])
    px(im, cx - 3, cy - 2, g["cream"])
    dots = [(14, 17), (33, 18), (24, 9), (18, 31), (31, 30), (24, 35)] if f == 1 else [(15, 19), (32, 16), (24, 11), (17, 30), (32, 32), (24, 33)]
    for (x, y) in dots: px(im, x, y, g["white"])                       # little stars inside the petals
    im = ring(im)
    pts = [((4, 6), (43, 8), (42, 34), (6, 30)), ((44, 5), (5, 12), (8, 36), (41, 28))][f - 1]
    for i, (x, y) in enumerate(pts): sparkle(im, x, y, big=(i % 2 == 0))
    return im

SPRITES = {"rafflesia": p_rafflesia, "haetori": p_haetori, "saboten": p_saboten, "chili": p_chili, "blackhole": p_blackhole}

if __name__ == "__main__":
    import sys, os
    out = sys.argv[1] if len(sys.argv) > 1 else "."; os.makedirs(out, exist_ok=True)
    for name, fn in SPRITES.items():
        for f in (1, 2): fn(f).save(f"{out}/flower_purified_{name}_f{f}.png")
