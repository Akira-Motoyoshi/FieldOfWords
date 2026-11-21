"""Poison flower adults (2 frames each). Palette: POISON only.
rafflesia 48x48, blackhole 48x48, haetori / saboten / chili 32x32. Bottom-centre anchored."""
import math
from PIL import Image, ImageDraw
from palette import POISON, rgb
p = {k: rgb(v) for k, v in POISON.items()}

def canvas(w, h):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); return im, ImageDraw.Draw(im)

def rings(im):
    for col in (p["outline"], p["black"]):
        src = im.copy(); s = src.load(); d = im.load()
        for y in range(im.height):
            for x in range(im.width):
                if s[x, y][3]: continue
                if any(0 <= x+dx < im.width and 0 <= y+dy < im.height and s[x+dx, y+dy][3]
                       for dx, dy in ((1,0),(-1,0),(0,1),(0,-1))):
                    d[x, y] = (*col, 255)
    return im

SKULL = [".###.", "#.#.#", "#####", ".###.", ".#.#."]
def skull(im, x, y):
    for r, row in enumerate(SKULL):
        for c, ch in enumerate(row):
            if ch == "#": im.putpixel((x + c, y + r), (*p["bone"], 255))
    im.putpixel((x + 1, y + 1), (*p["black"], 255)); im.putpixel((x + 3, y + 1), (*p["black"], 255))

def px(im, x, y, col):
    if 0 <= x < im.width and 0 <= y < im.height: im.putpixel((int(x), int(y)), (*col, 255))

# ---------------------------------------------------------------- rafflesia
def rafflesia(f):
    im, d = canvas(48, 48); cx, cy = 24, 26
    d.polygon([(9, 45), (5, 38), (15, 41), (20, 45)], fill=p["ditch"])
    d.polygon([(39, 45), (43, 39), (33, 41), (28, 45)], fill=p["sick_dark"])
    petals = []
    for k in range(5):
        a = -math.pi/2 + k*2*math.pi/5 + 0.18
        x, y = cx + 11*math.cos(a), cy + 9*math.sin(a); petals.append((a, x, y))
        d.ellipse([x-9, y-8, x+9, y+8], fill=p["blood_dark"])
    for a, x, y in petals:
        d.ellipse([x-8, y-7, x+6, y+5], fill=p["blood"])
        tx, ty = cx + 20*math.cos(a), cy + 17*math.sin(a)           # jagged tip
        d.polygon([(x + 6*math.cos(a-.6), y + 6*math.sin(a-.6)), (tx, ty), (x + 6*math.cos(a+.6), y + 6*math.sin(a+.6))], fill=p["blood_dark"])
    d.ellipse([cx-8, cy-6, cx+8, cy+6], fill=p["bruise"]); d.ellipse([cx-5, cy-4, cx+5, cy+4], fill=p["black"])
    for k in range(7):                                               # fangs round the mouth
        a = k * 2*math.pi/7 + 0.4; x, y = cx + 6*math.cos(a), cy + 4.5*math.sin(a)
        d.polygon([(x-1.5, y-1.5), (x+1.5, y-1.5), (cx + 2*math.cos(a), cy + 1.5*math.sin(a))], fill=p["bone"])
    for a, x, y in petals:                                           # neon spots
        for off in (-3, 3):
            sx, sy = x + off*math.cos(a+1.4), y + off*math.sin(a+1.4)
            d.rectangle([sx-1, sy-1, sx, sy], fill=p["neon_lime"])
    im = rings(im)
    bob = 1 if f == 2 else 0
    skull(im, 22, 1 + bob)
    for i, x0 in enumerate((11, 17, 36)):                           # stench: 3 wavy lines
        for j in range(7):
            sway = 1 if ((j + (f == 2) + i) % 2) else 0
            px(im, x0 + sway, 12 - j*2 + (1 if f == 2 else 0), p["neon_lime"] if j < 4 else p["gas"])
    return im

# ---------------------------------------------------------------- haetori
def haetori(f):
    im, d = canvas(32, 32)
    d.rectangle([15, 23, 16, 29], fill=p["ditch"])
    d.polygon([(15, 28), (7, 25), (5, 29), (14, 30)], fill=p["sick_dark"]); d.polygon([(17, 27), (26, 24), (28, 28), (18, 30)], fill=p["ditch"])
    d.ellipse([4, 6, 28, 24], fill=p["ditch"])                       # head
    d.ellipse([5, 12, 28, 24], fill=p["sick_dark"]); d.ellipse([4, 6, 27, 21], fill=p["ditch"])   # shaded lower-right
    for i, x in enumerate((6, 10, 14, 18, 22)):                      # jagged crest (uneven)
        d.polygon([(x, 8), (x + 3, 8), (x + 1, 4 - (i % 2))], fill=p["sick_dark"] if i % 2 else p["ditch"])
    d.polygon([(3, 14), (0, 10), (5, 10)], fill=p["sick_dark"]); d.polygon([(29, 16), (31, 11), (26, 11)], fill=p["sick_dark"])
    def fang(cx, y, h, down):
        widths = [3, 2, 2, 1][:h]
        for i, w in enumerate(widths):
            yy = y + i if down else y - i
            for xx in range(cx - w // 2, cx - w // 2 + w): px(im, xx, yy, p["bone"])
    if f == 1:   # jaws open: big pink mouth, long thin fangs
        d.ellipse([7, 11, 25, 21], fill=p["neon_pink"])
        for x in (10, 14, 18, 22): fang(x, 11, 4, True)
        for x in (12, 16, 20): fang(x, 21, 4, False)
    else:        # snapped shut: thin pink line, fangs interleaved
        d.ellipse([7, 15, 25, 18], fill=p["neon_pink"])
        for x in (10, 14, 18, 22): fang(x, 15, 3, True)
        for x in (12, 16, 20): fang(x, 18, 3, False)
    return rings(im)

# ---------------------------------------------------------------- saboten
def saboten(f):
    im, d = canvas(32, 32)
    d.rounded_rectangle([9, 9, 23, 29], 4, fill=p["grey_green"])
    d.rectangle([19, 11, 23, 28], fill=p["grey"])                    # shaded side
    d.line([(13, 10), (13, 28)], fill=p["grey"]); d.line([(17, 10), (17, 28)], fill=p["grey_dark"])
    d.rounded_rectangle([4, 15, 11, 19], 2, fill=p["grey_green"]); d.rounded_rectangle([3, 8, 7, 18], 2, fill=p["grey_green"])  # left arm only
    d.rectangle([22, 20, 26, 22], fill=p["grey"])                    # short right stub
    for (x, y) in ((9, 11), (23, 13), (9, 22), (23, 24), (5, 8), (3, 14), (26, 20), (15, 9), (11, 27)):
        px(im, x, y, p["grey_dark"]); px(im, x + (1 if x > 16 else -1), y - 1, p["neon_pink"])   # spikes with neon tips
    if f == 1:   # eyes open, frown
        for ex in (12, 18):
            d.rectangle([ex, 15, ex + 2, 17], fill=p["bone"]); px(im, ex + 1, 16, p["black"])
    else:        # blink
        for ex in (12, 18): d.line([(ex, 16), (ex + 2, 16)], fill=p["black"])
    d.line([(11, 13), (14, 14)], fill=p["black"]); d.line([(21, 12), (18, 14)], fill=p["black"])   # angry brows (asymmetric)
    d.line([(13, 21), (17, 20)], fill=p["black"]); px(im, 18, 21, p["black"])
    px(im, 14, 22, p["bone"]); px(im, 16, 22, p["bone"]); px(im, 14, 23, p["bone"])   # fangs
    fx = 16 + (1 if f == 2 else 0)                                   # the one bright thing: a tiny flower, swaying
    for dx, dy in ((0, -2), (-2, 0), (2, 0), (0, 2), (-1, -1), (1, -1)):
        px(im, fx + dx, 5 + dy, p["neon_pink"])
    px(im, fx, 5, p["bone"]); px(im, 15, 8, p["ditch"]); px(im, 16, 8, p["ditch"])
    return rings(im)

# ---------------------------------------------------------------- chili
def chili(f):
    im, d = canvas(32, 32)
    d.rectangle([15, 26, 16, 29], fill=p["sick_dark"])
    d.polygon([(15, 28), (9, 26), (8, 29), (14, 30)], fill=p["ditch"]); d.polygon([(17, 28), (23, 26), (24, 29), (18, 30)], fill=p["sick_dark"])
    d.ellipse([7, 8, 25, 26], fill=p["blood_dark"]); d.ellipse([7, 8, 22, 23], fill=p["blood"])
    d.polygon([(25, 20), (29, 16), (26, 24)], fill=p["blood_dark"])  # curved chili tip -> asymmetric
    for ex, ey, sl in ((9, 14, 1), (18, 15, 0)):                     # slanted angry eyes (right one lower)
        d.rectangle([ex, ey, ex + 4, ey + 2], fill=p["bone"]); px(im, ex + 2, ey + 1, p["black"]); px(im, ex + 3, ey + 1, p["black"])
    d.line([(8, 11), (14, 13)], fill=p["black"]); d.line([(25, 12), (18, 14)], fill=p["black"])
    d.line([(10, 21), (22, 21)], fill=p["black"])                    # snarl with teeth
    for x in range(11, 22, 2): d.polygon([(x, 21), (x + 1, 21), (x, 24)], fill=p["bone"])
    lean = 1 if f == 2 else 0
    for x0, h in ((11, 6 + lean), (16, 9 - lean), (21, 5 + lean)):   # flames on top
        d.polygon([(x0 - 3 + lean, 8), (x0 + lean * 2, 8 - h), (x0 + 3 + lean, 8)], fill=p["neon_lime"])
    d.polygon([(14, 8), (16 + lean, 3), (18, 8)], fill=p["neon_lime"])
    im = rings(im)
    px(im, 6 + lean, 4, p["gas"]); px(im, 25 - lean, 2, p["gas"])
    return im

# ---------------------------------------------------------------- blackhole
def blackhole(f):
    im, d = canvas(48, 48); cx, cy = 24, 24
    d.polygon([(23, 43), (14, 41), (10, 45), (22, 45)], fill=p["ditch"]); d.polygon([(25, 43), (34, 40), (38, 45), (26, 45)], fill=p["sick_dark"])
    d.rectangle([23, 38, 24, 44], fill=p["sick_dark"])
    d.ellipse([cx-14, cy-14, cx+14, cy+14], fill=p["black"])
    phase = 0.0 if f == 1 else 0.72
    for arm in range(3):
        col = (p["purple"], p["violet"], p["purple"])[arm]
        for t in range(0, 70):
            th = arm*2*math.pi/3 + phase + t*0.115
            r = 19 - 13*(t/69)
            x, y = cx + r*math.cos(th), cy + r*math.sin(th)
            w = 0.7 if r > 15 else (1.3 if r > 9 else 1.0)
            d.ellipse([x-w, y-w, x+w, y+w], fill=col)
    d.ellipse([cx-6, cy-6, cx+6, cy+6], fill=p["outline"]); d.ellipse([cx-4, cy-4, cx+4, cy+4], fill=p["black"])
    for k in range(14):                                              # neon rim of the vortex
        a = k*2*math.pi/14 + phase*2
        if k % 3 != 2: px(im, cx + 7.2*math.cos(a), cy + 7.2*math.sin(a), p["neon_pink"])
    im = rings(im)
    skull(im, 22, 1)
    for i in range(7):                                               # dust pulled toward the centre
        a = i*2*math.pi/7 + 0.5; r = 21 - (3 if f == 2 else 0) - (i % 3)
        x, y = cx + r*math.cos(a), cy + r*0.95*math.sin(a)
        if 4 < y < 42: px(im, x, y, p["bone"] if i % 2 else p["gas"])
    return im

SPRITES = {"rafflesia": rafflesia, "haetori": haetori, "saboten": saboten, "chili": chili, "blackhole": blackhole}

if __name__ == "__main__":
    import sys, os
    out = sys.argv[1] if len(sys.argv) > 1 else "."; os.makedirs(out, exist_ok=True)
    for name, fn in SPRITES.items():
        for f in (1, 2): fn(f).save(f"{out}/flower_poison_{name}_f{f}.png")
