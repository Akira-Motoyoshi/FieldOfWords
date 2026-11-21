"""Good flowers: bud + bloom, 2 frames. Palette: GOOD only. Bottom-centre anchored, 1px brown outline.
himawari bloom 32x48 (others 32x32). tulip has 3 colours (red / yellow / blue)."""
import math
from PIL import Image, ImageDraw
from palette import GOOD, rgb
g = {k: rgb(v) for k, v in GOOD.items()}

def canvas(w, h):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); return im, ImageDraw.Draw(im)

def ring(im):
    src = im.copy(); s = src.load(); d = im.load()
    for y in range(im.height):
        for x in range(im.width):
            if s[x, y][3]: continue
            if any(0 <= x+dx < im.width and 0 <= y+dy < im.height and s[x+dx, y+dy][3]
                   for dx, dy in ((1,0),(-1,0),(0,1),(0,-1))):
                d[x, y] = (*g["outline"], 255)
    return im

def px(im, x, y, col):
    if 0 <= x < im.width and 0 <= y < im.height: im.putpixel((int(x), int(y)), (*col, 255))
def clear(im, x, y): im.putpixel((int(x), int(y)), (0, 0, 0, 0))

def leaf(d, pts, col=None, vein=None):
    d.polygon(pts, fill=col or g["stem"])

def sparkle(im, x, y, big=True):
    px(im, x, y, g["white"])
    if big:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)): px(im, x + dx, y + dy, g["white"])

# ------------------------------------------------------------------ himawari
def himawari_bloom(f):
    im, d = canvas(32, 48); sw = 1 if f == 2 else 0; hx, hy = 16 + sw, 13
    d.rectangle([15, 22, 16, 46], fill=g["stem"]); d.line([(16, 22), (16, 46)], fill=g["stem_dark"])
    lift = 1 if f == 2 else 0
    leaf(d, [(15, 36), (5, 30 - lift), (4, 35 - lift), (15, 40)]); leaf(d, [(17, 40), (27, 34 - lift), (28, 39 - lift), (17, 44)])
    d.line([(7, 32 - lift), (14, 37)], fill=g["leaf_light"]); d.line([(25, 36 - lift), (18, 41)], fill=g["leaf_light"])
    for k in range(12):
        a = k * math.pi / 6; x, y = hx + 9*math.cos(a), hy + 9*math.sin(a)
        d.ellipse([x-3, y-3, x+3, y+3], fill=g["yellow"] if k % 2 else g["yellow_deep"])
    d.ellipse([hx-6, hy-6, hx+6, hy+6], fill=g["center"])
    for sx, sy in ((-3, -2), (0, -4), (3, -1), (-1, 1), (2, 3), (-4, 2), (1, -1)): px(im, hx + sx, hy + sy, g["outline"])
    for sx, sy in ((-2, 3), (3, 2), (-3, -1), (2, -3)): px(im, hx + sx, hy + sy, g["yellow_deep"])
    im = ring(im)
    sparkle(im, 5 + sw*3, 4 + f, False); sparkle(im, 27 - sw*2, 8 - f, False)
    return im

def himawari_bud(f):
    im, d = canvas(32, 32); sw = 1 if f == 2 else 0
    d.rectangle([15, 16, 16, 30], fill=g["stem"]); d.line([(16, 16), (16, 30)], fill=g["stem_dark"])
    leaf(d, [(15, 26), (6, 20), (5, 25), (14, 29)]); leaf(d, [(17, 24), (26, 18), (27, 23), (18, 27)])
    d.line([(8, 22), (14, 26)], fill=g["leaf_light"]); d.line([(24, 20), (18, 24)], fill=g["leaf_light"])
    d.ellipse([11 + sw, 3, 21 + sw, 11], fill=g["yellow"]); d.line([(13 + sw, 5), (19 + sw, 5)], fill=g["yellow_deep"])
    d.ellipse([10, 7, 22, 19], fill=g["stem"]); d.arc([10, 7, 22, 19], 200, 340, fill=g["leaf_light"])
    for x0, x1 in ((10, 13), (14, 17), (19, 22)): d.polygon([(x0, 15), (x1, 15), ((x0 + x1) // 2, 21)], fill=g["stem_dark"])
    return ring(im)

# ------------------------------------------------------------------ sakuraso
def rosette(d, base=29):
    leaf(d, [(15, base), (5, base - 6), (4, base - 1), (14, base + 1)], g["stem_dark"])
    leaf(d, [(17, base), (27, base - 6), (28, base - 1), (18, base + 1)], g["stem_dark"])
    leaf(d, [(13, base + 1), (8, base - 2), (7, base + 1)], g["stem"]); leaf(d, [(19, base + 1), (24, base - 2), (25, base + 1)], g["stem"])
    d.line([(7, base - 4), (13, base - 1)], fill=g["stem"]); d.line([(25, base - 4), (19, base - 1)], fill=g["stem"])

def sakuraso_bloom(f):
    im, d = canvas(32, 32); cx, cy = 16 + (1 if f == 2 else 0), 12
    d.rectangle([15, 17, 16, 28], fill=g["stem"]); rosette(d, 29)
    for k in range(5):
        a = -math.pi/2 + k * 2*math.pi/5; x, y = cx + 6*math.cos(a), cy + 6*math.sin(a)
        d.ellipse([x-4.5, y-4.5, x+4.5, y+4.5], fill=g["pink_deep"])
    for k in range(5):
        a = -math.pi/2 + k * 2*math.pi/5; x, y = cx + 6*math.cos(a), cy + 6*math.sin(a)
        d.ellipse([x-4, y-4, x+3, y+3], fill=g["pink"])
    d.ellipse([cx-3, cy-3, cx+3, cy+3], fill=g["cream"]); d.point((cx, cy), fill=g["yellow"]); d.point((cx - 1, cy - 1), fill=g["yellow_deep"])
    for k in range(5):                                   # heart-notch at each petal tip
        a = -math.pi/2 + k * 2*math.pi/5; clear(im, cx + 10.5*math.cos(a), cy + 10.5*math.sin(a))
    im = ring(im)
    sparkle(im, 4 + 2*(f == 2), 4, False); sparkle(im, 28 - 2*(f == 2), 14 + f, False)
    return im

def sakuraso_bud(f):
    im, d = canvas(32, 32); t = 1 if f == 2 else 0
    d.rectangle([15, 17, 16, 28], fill=g["stem"]); rosette(d, 29)
    d.ellipse([11 + t, 6, 21 + t, 18], fill=g["pink"]); d.line([(16 + t, 7), (16 + t, 16)], fill=g["pink_deep"])
    d.line([(13 + t, 8), (13 + t, 15)], fill=g["pink_deep"]); d.ellipse([12 + t, 7, 15 + t, 10], fill=g["white"])
    d.polygon([(11 + t, 15), (21 + t, 15), (16 + t, 21)], fill=g["stem_dark"]); d.polygon([(13 + t, 15), (19 + t, 15), (16 + t, 19)], fill=g["stem"])
    return ring(im)

# ------------------------------------------------------------------ tulip (red / yellow / blue)
TULIP = {"red": ("red", "pink_deep", "pink"), "yellow": ("yellow", "yellow_deep", "cream"), "blue": ("blue", "sky", "white")}
def tulip_leaves(d, lift=0):
    d.rectangle([15, 22, 16, 30], fill=g["stem"]); d.line([(16, 22), (16, 30)], fill=g["stem_dark"])
    d.polygon([(15, 30), (4, 19 - lift), (6, 15 - lift), (14, 25)], fill=g["stem"]); d.line([(6, 18 - lift), (14, 27)], fill=g["leaf_light"])
    d.polygon([(17, 30), (27, 22 - lift), (26, 18 - lift), (18, 26)], fill=g["stem"]); d.line([(25, 21 - lift), (18, 28)], fill=g["leaf_light"])

def tulip_bloom(color, f):
    main, shade, hi = (g[k] for k in TULIP[color]); im, d = canvas(32, 32); sw = 1 if f == 2 else 0
    tulip_leaves(d, sw)
    d.ellipse([8 + sw, 10, 24 + sw, 26], fill=main)
    d.polygon([(8 + sw, 16), (8 + sw, 4), (13 + sw, 11)], fill=main); d.polygon([(24 + sw, 16), (24 + sw, 4), (19 + sw, 11)], fill=main)
    d.polygon([(12 + sw, 11), (16 + sw, 2), (20 + sw, 11)], fill=main)
    d.polygon([(13 + sw, 11), (16 + sw, 4), (19 + sw, 11), (18 + sw, 20), (14 + sw, 20)], fill=hi)
    d.line([(21 + sw, 12), (23 + sw, 22)], fill=shade); d.line([(22 + sw, 13), (22 + sw, 20)], fill=shade)
    d.line([(9 + sw, 14), (10 + sw, 22)], fill=shade)
    d.rectangle([15, 25, 16, 27], fill=g["stem_dark"])
    return ring(im)

def tulip_bud(color, f):
    main, shade, hi = (g[k] for k in TULIP[color]); im, d = canvas(32, 32); sw = 1 if f == 2 else 0
    tulip_leaves(d, sw)
    d.ellipse([11 + sw, 8, 21 + sw, 25], fill=main); d.polygon([(13 + sw, 11), (16 + sw, 3), (19 + sw, 11)], fill=main)
    d.line([(13 + sw, 12), (13 + sw, 20)], fill=hi); d.line([(19 + sw, 12), (19 + sw, 21)], fill=shade)
    d.rectangle([15, 24, 16, 26], fill=g["stem_dark"])
    return ring(im)

# ------------------------------------------------------------------ kinbara (gold rose)
def rose_stem(d):
    d.rectangle([15, 21, 16, 30], fill=g["stem"]); d.line([(16, 21), (16, 30)], fill=g["stem_dark"])
    leaf(d, [(15, 28), (6, 22), (5, 27), (14, 30)]); leaf(d, [(17, 27), (26, 21), (27, 26), (18, 29)])
    d.line([(8, 24), (14, 28)], fill=g["leaf_light"]); d.line([(24, 23), (18, 27)], fill=g["leaf_light"])
    for y in (23, 26): d.polygon([(14, y), (12, y - 2), (14, y - 2)], fill=g["stem_dark"]); d.polygon([(17, y + 1), (19, y - 1), (17, y - 1)], fill=g["stem_dark"])

def kinbara_bloom(f):
    im, d = canvas(32, 32); cx, cy = 16, 12
    rose_stem(d)
    d.polygon([(cx-4, cy+7), (cx+4, cy+7), (cx, cy+13)], fill=g["stem_dark"])
    for k in range(6):                                           # outer petals, each outlined in gold
        a = k * math.pi/3 + 0.3; x, y = cx + 6.5*math.cos(a), cy + 5.5*math.sin(a)
        d.ellipse([x-4.5, y-4, x+4.5, y+4], fill=g["yellow_deep"], outline=g["gold"])
    for k in range(4):                                           # inner petals
        a = k * math.pi/2 + 0.8; x, y = cx + 3*math.cos(a), cy + 2.5*math.sin(a)
        d.ellipse([x-3.5, y-3, x+3.5, y+3], fill=g["yellow"], outline=g["gold"])
    d.ellipse([cx-2, cy-2, cx+2, cy+2], fill=g["cream"], outline=g["gold"])
    d.arc([cx-3, cy-3, cx+3, cy+3], 200, 500, fill=g["yellow_deep"])
    for dx, dy in ((-7, -4), (6, -5), (-5, 4)): px(im, cx + dx, cy + dy, g["cream"])
    im = ring(im)
    pts = [((4, 4), (27, 6), (25, 21)), ((27, 3), (4, 10), (7, 22))][f - 1]
    for i, (x, y) in enumerate(pts): sparkle(im, x, y, big=(i != 2))
    return im

def kinbara_bud(f):
    im, d = canvas(32, 32); cx = 16 + (1 if f == 2 else 0)
    rose_stem(d)
    d.ellipse([cx-5, 6, cx+5, 20], fill=g["yellow_deep"]); d.polygon([(cx-4, 9), (cx, 2), (cx+4, 9)], fill=g["yellow_deep"])
    d.line([(cx-3, 8), (cx-3, 17)], fill=g["yellow"]); d.line([(cx+3, 9), (cx+3, 18)], fill=g["gold"])
    d.polygon([(cx-6, 15), (cx-2, 15), (cx-5, 22)], fill=g["stem_dark"]); d.polygon([(cx+6, 15), (cx+2, 15), (cx+5, 22)], fill=g["stem_dark"])
    d.polygon([(cx-2, 17), (cx+2, 17), (cx, 23)], fill=g["stem"])
    im = ring(im)
    sparkle(im, (25, 6)[f - 1], (6, 11)[f - 1], True); sparkle(im, (6, 26)[f - 1], (12, 4)[f - 1], f == 1)
    return im

# ------------------------------------------------------------------ nohana (three tiny wild flowers)
def small_flower(d, cx, cy, petal):
    for k in range(5):
        a = -math.pi/2 + k * 2*math.pi/5; x, y = cx + 3*math.cos(a), cy + 3*math.sin(a)
        d.ellipse([x-2, y-2, x+2, y+2], fill=petal)
    d.ellipse([cx-1, cy-1, cx+1, cy+1], fill=g["yellow"])

def nohana_bloom(f):
    im, d = canvas(32, 32); s = 1 if f == 2 else 0
    spots = [(9 + s, 14, g["white"], 9), (22 - s, 9, g["sky"], 22), (15 + s, 21, g["white"], 15)]
    for x, y, col, bx in spots:
        d.line([(x, y + 3), (bx, 30)], fill=g["stem_dark"]); d.line([(x + 1, y + 3), (bx + 1, 30)], fill=g["stem"])
    leaf(d, [(10, 30), (5, 25), (4, 29), (9, 30)]); leaf(d, [(21, 30), (27, 25), (28, 29), (22, 30)]); leaf(d, [(15, 30), (14, 26), (17, 30)], g["leaf_light"])
    for x, y, col, bx in spots: small_flower(d, x, y, col)
    return ring(im)

def nohana_bud(f):
    im, d = canvas(32, 32); s = 1 if f == 2 else 0
    for x, y, col in ((9, 18, g["white"]), (22, 14, g["white"]), (15 + s, 23, g["sky"])):
        d.line([(x, y + 2), (x, 30)], fill=g["stem_dark"]); d.line([(x + 1, y + 2), (x + 1, 30)], fill=g["stem"])
        d.ellipse([x - 1 + (s if x == 22 else 0), y - 1, x + 3 + (s if x == 22 else 0), y + 3], fill=col)
    leaf(d, [(10, 30), (6, 26), (5, 30), (9, 30)]); leaf(d, [(21, 30), (26, 26), (27, 30), (22, 30)])
    return ring(im)

def build():
    out = {}
    out["himawari"] = (himawari_bud, himawari_bloom); out["sakuraso"] = (sakuraso_bud, sakuraso_bloom)
    out["kinbara"] = (kinbara_bud, kinbara_bloom); out["nohana"] = (nohana_bud, nohana_bloom)
    files = {}
    for sp, (b, bl) in out.items():
        files[f"flower_good_{sp}_bud"] = b; files[f"flower_good_{sp}_bloom"] = bl
    for c in TULIP:
        files[f"flower_good_tulip_{c}_bud"] = (lambda f, c=c: tulip_bud(c, f))
        files[f"flower_good_tulip_{c}_bloom"] = (lambda f, c=c: tulip_bloom(c, f))
    return files

if __name__ == "__main__":
    import sys, os
    out = sys.argv[1] if len(sys.argv) > 1 else "."; os.makedirs(out, exist_ok=True)
    for name, fn in build().items():
        for f in (1, 2): fn(f).save(f"{out}/{name}_f{f}.png")
