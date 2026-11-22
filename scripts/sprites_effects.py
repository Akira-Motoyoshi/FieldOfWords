"""Remaining assets: mold, milestone effects, normal effects, poison effects, gardener.
Palettes: poison family (mold, poison effects) -> POISON only | everything else -> GOOD only."""
import math, random
from PIL import Image, ImageDraw
from palette import GOOD, POISON, rgb
g = {k: rgb(v) for k, v in GOOD.items()}; p = {k: rgb(v) for k, v in POISON.items()}

def canvas(w, h):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); return im, ImageDraw.Draw(im)

def px(im, x, y, col):
    if 0 <= x < im.width and 0 <= y < im.height: im.putpixel((int(x), int(y)), (*col, 255))

def rings(im, cols):
    for col in cols:
        src = im.copy(); s = src.load(); d = im.load()
        for y in range(im.height):
            for x in range(im.width):
                if s[x, y][3]: continue
                if any(0 <= x+dx < im.width and 0 <= y+dy < im.height and s[x+dx, y+dy][3] for dx, dy in ((1,0),(-1,0),(0,1),(0,-1))):
                    d[x, y] = (*col, 255)
    return im

def flat_bottom(im, last_row):
    for y in range(last_row + 1, im.height):
        for x in range(im.width): im.putpixel((x, y), (0, 0, 0, 0))

# ======================================================================= mold 48x48 (poison palette)
def mold(f):
    im, d = canvas(48, 48); rnd = random.Random(5)
    lumps = [(24, 36, 17, 11), (11, 40, 9, 7), (37, 38, 10, 8), (27, 25, 8, 7), (15, 30, 6, 5)]
    for cx, cy, rx, ry in lumps: d.ellipse([cx-rx, cy-ry, cx+rx, cy+ry], fill=p["purple"])
    for cx, cy, rx, ry in lumps: d.ellipse([cx-rx+2, cy-ry+1, cx+rx-1, cy+ry-3], fill=p["violet"])     # lit upper part
    for cx, cy, rx, ry in lumps[:3]: d.ellipse([cx-rx//2, cy-ry//3, cx+rx, cy+ry], fill=p["bruise"])     # shaded lower right
    for cx, cy, rx, ry in lumps: d.ellipse([cx-rx+3, cy-ry+2, cx-rx//4, cy-ry//4], fill=p["violet"])
    flat_bottom(im, 45)
    for _ in range(3):                                                                              # fuzzy, tufted edge (same both frames)
        add = []
        for y in range(10, 46):
            for x in range(1, 47):
                if im.getpixel((x, y))[3] == 0 and any(im.getpixel((x+dx, y+dy))[3] for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)) if 0 <= x+dx < 48 and 0 <= y+dy < 48):
                    if rnd.random() < (0.42 if y < 40 else 0.2): add.append((x, y, p["violet"] if rnd.random() < .55 else p["purple"]))
        for x, y, c in add: px(im, x, y, c)
    for y in range(10, 46):                                                                         # mottled colony texture
        for x in range(1, 47):
            c = im.getpixel((x, y))
            if c[3] and c[:3] in (p["violet"], p["purple"]) and rnd.random() < .16:
                px(im, x, y, p["bruise"] if c[:3] == p["violet"] else p["violet"])
    spots = [(8, 38), (14, 43), (19, 33), (30, 29), (24, 41), (36, 41), (40, 36), (31, 35), (22, 27), (13, 28), (28, 21), (43, 40)]
    for i, (x, y) in enumerate(spots):                                                              # lime spots pulse: 2x2 <-> 1x1
        big = (i + (f == 2)) % 2 == 0
        if im.getpixel((x, y))[3]:
            px(im, x, y, p["neon_lime"])
            if big: px(im, x+1, y, p["neon_lime"]); px(im, x, y+1, p["neon_lime"]); px(im, x+1, y+1, p["neon_lime"])
    for ex, ey in ((20, 35), (29, 35)):                                                             # eyes on the main lump
        d.ellipse([ex-2, ey-2, ex+2, ey+1], fill=p["bone"])
        if f == 1: px(im, ex, ey - 1, p["black"]); px(im, ex + 1, ey - 1, p["black"])
        else: d.line([(ex-2, ey), (ex+2, ey)], fill=p["black"])                                     # blink
    d.line([(21, 40), (28, 40)], fill=p["black"])                                                   # mouth + fangs
    for x in (22, 25, 27): px(im, x, 41, p["bone"]); px(im, x, 42, p["bone"])
    d.ellipse([9, 37, 12, 40], fill=p["bone"]); px(im, 10, 38 if f == 1 else 39, p["black"])         # side lump: one eye
    im = rings(im, [p["outline"], p["black"]])
    for i in range(6):                                                                              # spores drifting up
        x = 8 + i * 6 + (2 if f == 2 else 0) + (i % 2); y = 20 - i % 3 * 4 - (3 if f == 2 else 0)
        px(im, x, y, p["neon_lime"] if i % 2 == 0 else p["gas"])
    return im

# ======================================================================= milestone effects (good palette)
RAINBOW_COLORS = ["red", "orange", "yellow", "stem", "blue", "pink_deep", "pink"]   # outer -> inner (no "sky": same colour as the sky)
def rainbow(f):
    W, H, R = 72, 36, 34; im, d = canvas(W, H); cx, cy = W // 2, H
    for y in range(H):
        for x in range(W):
            r = math.hypot(x + .5 - cx, y + .5 - cy)
            if R - 21 <= r < R: im.putpixel((x, y), (*g[RAINBOW_COLORS[int((R - r) // 3)]], 255))
    for (x, y) in ([(2, 30), (68, 33), (35, 2)] if f == 1 else [(4, 33), (66, 30), (30, 4)]):
        px(im, x, y, g["white"])
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)): px(im, x + dx, y + dy, g["white"])
    return im

def art(half, cmap):
    """Build a 12x10 sprite from its left half (6 columns); the right half is the mirror image."""
    im, _ = canvas(12, 10)
    for y, row in enumerate(half):
        for x, ch in enumerate(row + row[::-1]):
            if ch in cmap: px(im, x, y, cmap[ch])
    return im

BF_OPEN = ["OO.A..", "OOOOA.", "OOOWOB", "OOOOOB", ".OOOOB", "..YYYB", ".YYYYB", ".YYWYB", "..YY.B", "......"]
BF_FOLD = ["...A..", "..OOA.", "..OOOB", ".OOWOB", ".OOOOB", "..OOYB", "..YYYB", "...YYB", "....YB", "......"]
def butterfly_a(f):     # warm: orange / yellow, brown body
    return art(BF_OPEN if f == 1 else BF_FOLD, {"O": g["orange"], "Y": g["yellow"], "W": g["white"], "B": g["center"], "A": g["outline"]})
def butterfly_b(f):     # cool: pink / sky, blue body
    return art(BF_OPEN if f == 1 else BF_FOLD, {"O": g["pink"], "Y": g["sky"], "W": g["white"], "B": g["blue"], "A": g["outline"]})

def build_milestone(): return {"fx_rainbow": rainbow, "fx_butterfly_a": butterfly_a, "fx_butterfly_b": butterfly_b}
def build_mold(): return {"flower_mold": mold}
# ======================================================================= normal effects 16x16 (good palette)
def fx_seed(f):
    im, d = canvas(16, 16); y = 0 if f == 1 else 2
    d.ellipse([6, 6 + y, 10, 12 + y], fill=g["center"]); px(im, 7, 7 + y, g["cream"]); px(im, 7, 8 + y, g["cream"])
    for (x, yy) in ((8, 5), (9, 4), (10, 4), (7, 4), (6, 3)): px(im, x, yy + y, g["stem"])
    px(im, 10, 3 + y, g["leaf_light"]); px(im, 6, 2 + y, g["leaf_light"])
    for k in range(2 if f == 1 else 3): px(im, 8, max(0, 1 - 1 + k * 0), g["white"]) if False else None
    for yy in range(0, 2 + (f - 1)): px(im, 12, 1 + yy * 2, g["white"])                       # trail
    return im if False else _ring_brown(im)

def _ring_brown(im): return rings(im, [g["outline"]])

def fx_sun(f):
    im, d = canvas(16, 16); c = 8
    d.ellipse([5, 5, 10, 10], fill=g["yellow"]); d.ellipse([6, 6, 9, 9], fill=g["cream"])
    rays = [(0, -1), (1, 0), (0, 1), (-1, 0), (1, -1), (1, 1), (-1, 1), (-1, -1)]
    for i, (dx, dy) in enumerate(rays):
        long = (i % 2 == 0) == (f == 1)
        for r in ((6, 7, 8) if long else (6, 7)): px(im, c - .5 + dx * r * (1 if i < 4 else .8) + (0 if dx >= 0 else -1) * 0, c - .5 + dy * r * (1 if i < 4 else .8), (g["yellow_deep"] if (i % 2 == 0) == (f == 1) else g["yellow"]))
    return _ring_brown(im)

def fx_drop(f):
    im, d = canvas(16, 16); y = 0 if f == 1 else 2
    drop = [".B.", ".B.", "BBB", "BWB", "BBB", ".B."]
    for (x0, y0) in ((1, 1), (9, 3), (5, 8)):
        for j, row in enumerate(drop):
            for i, ch in enumerate(row):
                if ch == "B": px(im, x0 + i, y0 + j + y, g["blue"])
                elif ch == "W": px(im, x0 + i, y0 + j + y, g["white"])
    return _ring_brown(im)

def fx_fertilizer(f):
    im, d = canvas(16, 16)
    d.rectangle([4, 5, 11, 13], fill=g["cream"]); d.polygon([(5, 5), (10, 5), (11, 3), (4, 3)], fill=g["yellow_deep"]); d.line([(4, 5), (11, 5)], fill=g["gold"])
    for (x, yy) in ((8, 10), (7, 9), (9, 9), (8, 8), (8, 11)): px(im, x, yy, g["stem"])
    px(im, 7, 8, g["leaf_light"]); px(im, 9, 8, g["leaf_light"])
    im = _ring_brown(im)
    sx, sy = (13, 2) if f == 1 else (2, 3)
    for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)): px(im, sx + dx, sy + dy, g["white"])
    return im

def fx_dew(f):
    im, d = canvas(16, 16)
    d.ellipse([1, 8, 14, 14], fill=g["stem"]); d.line([(3, 11), (12, 11)], fill=g["leaf_light"]); d.line([(2, 13), (13, 13)], fill=g["stem_dark"])
    im = _ring_brown(im)
    for (x, y) in ((4, 6), (9, 4), (12, 7)):
        px(im, x, y, g["sky"]); px(im, x, y + 1, g["sky"]); px(im, x + 1, y + 1, g["white"] if f == 1 else g["sky"])
    sx, sy = (7, 2) if f == 1 else (3, 3)
    for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)): px(im, sx + dx, sy + dy, g["white"])
    return im

def build_normal(): return {"fx_seed": fx_seed, "fx_sun": fx_sun, "fx_drop": fx_drop, "fx_fertilizer": fx_fertilizer, "fx_dew": fx_dew}

# ======================================================================= poison effects (poison palette)
FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
def dot_text(text, fill, f, size=12):
    from PIL import ImageFont
    font = ImageFont.truetype(FONT, size, index=0)
    w, h = len(text) * size + 6, size + 8
    mask = Image.new("L", (w, h), 0); md = ImageDraw.Draw(mask); md.fontmode = "1"
    dx, dy = (0, 0) if f == 1 else (1, -1)                          # f2: the text shakes
    md.text((3 + dx, 3 + dy), text, font=font, fill=255)
    im, _ = canvas(w, h)
    for y in range(h):
        for x in range(w):
            if mask.getpixel((x, y)) > 127: im.putpixel((x, y), (*fill, 255))
    return rings(im, [p["black"]])
def fx_text_piki(f): return dot_text("ピキッ", p["neon_pink"], f)
def fx_text_gogogo(f): return dot_text("ゴゴゴ", p["neon_lime"], f)

def art2(rows, cmap, w, h):
    im, _ = canvas(w, h)
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch in cmap: px(im, x, y, cmap[ch])
    return im

def fx_skull(f):
    rows = ["..bbbb..", ".bbbbbb.", ".bkbbkb.", ".bbbbbb.", "..bbbb..", "..bkbk.." if f == 1 else "..bbbb..", "........" if f == 1 else "..bkbk.."]
    return rings(art2(rows, {"b": p["bone"], "k": p["black"]}, 8, 8), [p["black"]])

def fx_poison_bubble(f):
    im, d = canvas(16, 16); u = 0 if f == 1 else -1
    d.ellipse([1, 4, 10, 13], fill=p["purple"]); d.ellipse([2, 5, 7, 9], fill=p["violet"]); px(im, 3, 6, p["bone"]); px(im, 4, 6, p["bone"])
    px(im, 8, 11, p["bruise"]); px(im, 9, 10, p["bruise"])
    d.ellipse([10, 1 + u, 14, 5 + u], fill=p["violet"]); px(im, 11, 2 + u, p["bone"])
    d.ellipse([11, 8 - u, 15, 12 - u], fill=p["purple"]); px(im, 12, 9 - u, p["gas"])
    px(im, 5, 11, p["neon_lime"]); px(im, 12 if f == 1 else 6, 3 if f == 1 else 12, p["neon_lime"])
    return rings(im, [p["black"]])

def fx_gas(f):                                          # soft cloud: no outline, dithered edge, so it reads as gas, not a rock
    im, d = canvas(16, 16); u = 0 if f == 1 else -2
    d.ellipse([1, 7 + u, 8, 13 + u], fill=p["gas"]); d.ellipse([6, 5 + u, 13, 12 + u], fill=p["gas"]); d.ellipse([4, 3 + u, 10, 8 + u], fill=p["gas"])
    d.ellipse([3, 8 + u, 6, 11 + u], fill=p["violet"]); d.ellipse([8, 8 + u, 11, 10 + u], fill=p["violet"])
    src = im.copy()
    for y in range(16):
        for x in range(16):
            if src.getpixel((x, y))[3] and (x + y) % 2 == 0 and any(0 <= x+dx < 16 and 0 <= y+dy < 16 and not src.getpixel((x+dx, y+dy))[3] or not (0 <= x+dx < 16 and 0 <= y+dy < 16) for dx, dy in ((1,0),(-1,0),(0,1),(0,-1))):
                im.putpixel((x, y), (0, 0, 0, 0))
    px(im, 6, 6 + u, p["neon_lime"]); px(im, 10, 9 + u, p["neon_lime"])
    return im

def build_poison_fx(): return {"fx_text_piki": fx_text_piki, "fx_text_gogogo": fx_text_gogogo, "fx_skull": fx_skull, "fx_poison_bubble": fx_poison_bubble, "fx_gas": fx_gas}

# ======================================================================= gardener (Muse) 24x32, good palette
def gardener(pose, f):
    im, d = canvas(24, 32); bob = 1 if (pose == "idle" and f == 2) else 0
    sh = lambda y: y + bob
    d.rectangle([8, sh(28), 10, 30], fill=g["center"]); d.rectangle([13, sh(28), 15, 30], fill=g["center"])             # boots
    d.rectangle([7, sh(20), 16, sh(28)], fill=g["blue"]); d.rectangle([7, sh(20), 9, sh(27)], fill=g["sky"])             # overalls
    d.rectangle([10, sh(20), 13, sh(22)], fill=g["white"])                                                              # shirt
    if pose == "idle":
        d.rectangle([4, sh(21), 6, sh(27)], fill=g["white"]); d.rectangle([17, sh(21), 19, sh(27)], fill=g["white"])
        d.rectangle([4, sh(27), 6, sh(28)], fill=g["cream"]); d.rectangle([17, sh(27), 19, sh(28)], fill=g["cream"])
    elif pose == "water":
        d.rectangle([4, sh(21), 6, sh(27)], fill=g["white"]); d.rectangle([4, sh(27), 6, sh(28)], fill=g["cream"])
        d.rectangle([17, 21, 19, 23], fill=g["white"]); d.rectangle([19, 22, 20, 23], fill=g["cream"])               # right arm forward
        t = 1 if f == 1 else 2                                                                                         # can tilts more in f2
        d.rectangle([19, 19, 23, 24], fill=g["blue"]); d.rectangle([19, 19, 23, 20], fill=g["sky"])
        d.line([(23, 24), (23, 25 + t)], fill=g["blue"])
    else:                                                                                                              # purify: both arms up
        d.rectangle([3, 12, 5, 21], fill=g["white"]); d.rectangle([18, 12, 20, 21], fill=g["white"])
        d.rectangle([3, 10, 5, 12], fill=g["cream"]); d.rectangle([18, 10, 20, 12], fill=g["cream"])
    d.ellipse([6, sh(9), 17, sh(20)], fill=g["cream"])                                                                  # face
    d.ellipse([3, sh(7), 20, sh(12)], fill=g["yellow"]); d.ellipse([7, sh(2), 16, sh(10)], fill=g["yellow"]); d.line([(7, sh(8)), (16, sh(8))], fill=g["red"])
    d.line([(4, sh(10)), (19, sh(10))], fill=g["yellow_deep"])
    blink = (f == 2 and pose != "water")
    for ex in (9, 14):
        if blink: d.line([(ex, sh(14)), (ex + 1, sh(14))], fill=g["outline"])
        else: px(im, ex, sh(13), g["outline"]); px(im, ex, sh(14), g["outline"])
    px(im, 7, sh(16), g["pink"]); px(im, 16, sh(16), g["pink"]); px(im, 11, sh(17), g["outline"]); px(im, 12, sh(17), g["outline"])
    im = rings(im, [g["outline"]])
    if pose == "water":
        for (x, y) in (((22, 28), (23, 30), (21, 31)) if f == 1 else ((23, 29), (22, 31), (21, 27))): px(im, x, y, g["white"]); px(im, x, y - 1, g["sky"])
    if pose == "purify":
        for (x, y) in (((1, 6), (22, 5), (2, 17), (21, 16)) if f == 1 else ((2, 3), (21, 8), (1, 14), (22, 19))):
            for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)): px(im, x + dx, y + dy, g["white"] if (x + y) % 2 else g["yellow"])
    return im

def build_gardener(): return {f"gardener_{pose}": (lambda f, pose=pose: gardener(pose, f)) for pose in ("idle", "water", "purify")}

def build_all():
    out = {}; out.update(build_mold()); out.update(build_milestone()); out.update(build_normal()); out.update(build_poison_fx()); out.update(build_gardener()); return out

if __name__ == "__main__":
    import sys, os
    out = sys.argv[1] if len(sys.argv) > 1 else "."; os.makedirs(out, exist_ok=True)
    for name, fn in build_all().items():
        for f in (1, 2): fn(f).save(f"{out}/{name}_f{f}.png")
