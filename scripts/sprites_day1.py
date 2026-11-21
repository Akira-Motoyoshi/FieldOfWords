"""Day 1 sprites: good sprout / good stem / poison sprout, 32x32, 2 frames each."""
from PIL import Image, ImageDraw
from palette import GOOD, POISON, rgb
g = {k: rgb(v) for k, v in GOOD.items()}; p = {k: rgb(v) for k, v in POISON.items()}

def outline(img, rings):
    for col in rings:
        src = img.copy(); s = src.load(); d = img.load()
        for y in range(img.height):
            for x in range(img.width):
                if s[x, y][3]: continue
                if any(0 <= x+dx < img.width and 0 <= y+dy < img.height and s[x+dx, y+dy][3]
                       for dx, dy in ((1,0),(-1,0),(0,1),(0,-1))):
                    d[x, y] = (*col, 255)
    return img

def new(): 
    im = Image.new("RGBA", (32, 32), (0,0,0,0)); return im, ImageDraw.Draw(im)

def good_sprout(f):
    im, d = new(); t = 1 if f == 2 else 0          # frame 2: leaves lift 1px
    d.rectangle([15, 22, 16, 30], fill=g["stem"]); d.line([(16, 22), (16, 30)], fill=g["stem_dark"])
    d.ellipse([7, 17 - t, 15, 23 - t], fill=g["stem"]); d.ellipse([17, 17 - t, 25, 23 - t], fill=g["stem"])
    d.line([(9, 20 - t), (14, 21 - t)], fill=g["leaf_light"]); d.line([(18, 21 - t), (23, 20 - t)], fill=g["leaf_light"])
    return outline(im, [g["outline"]])

def good_stem(f):
    im, d = new(); s = 1 if f == 2 else 0          # frame 2: tip sways right 1px
    d.rectangle([15, 9, 16, 30], fill=g["stem"]); d.line([(16, 9), (16, 30)], fill=g["stem_dark"])
    d.rectangle([15 + s, 6, 16 + s, 9], fill=g["stem"])                 # curled tip
    d.point((17 + s, 6), fill=g["stem"]); d.point((17 + s, 7), fill=g["leaf_light"])
    for (x0, y0, x1, y1) in ((6, 21, 15, 26), (17, 15, 26, 20)):        # big leaves
        d.ellipse([x0, y0 - s, x1, y1 - s], fill=g["stem"])
    d.line([(8, 23 - s), (14, 24 - s)], fill=g["leaf_light"]); d.line([(18, 18 - s), (24, 17 - s)], fill=g["leaf_light"])
    d.ellipse([9, 12, 15, 15], fill=g["stem"]); d.line([(10, 13), (14, 14)], fill=g["leaf_light"])   # small leaf
    return outline(im, [g["outline"]])

def poison_sprout(f):
    im, d = new()
    d.rectangle([15, 21, 16, 30], fill=p["purple"]); d.line([(16, 21), (16, 30)], fill=p["outline"])
    d.line([(15, 21), (13, 18), (13, 16)], fill=p["purple"], width=2)    # hooked, drooping head
    # jagged leaves (pointed, asymmetric)
    d.polygon([(15, 25), (7, 21), (5, 17), (9, 19), (8, 15), (12, 20)], fill=p["purple"])
    d.polygon([(17, 26), (24, 23), (27, 20), (23, 21), (25, 17), (19, 22)], fill=p["violet"])
    d.line([(8, 18), (13, 22)], fill=p["violet"]); d.line([(20, 23), (25, 19)], fill=p["purple"])
    # eye on the drooping head: open (f1) / closed (f2)
    d.rectangle([11, 13, 15, 16], fill=p["purple"])
    if f == 1:
        d.rectangle([12, 14, 13, 15], fill=p["neon_lime"]); d.point((13, 15), fill=p["black"])
    else:
        d.line([(12, 15), (14, 15)], fill=p["black"])
    d.point((8, 19), fill=p["neon_lime"]); d.point((24, 21), fill=p["neon_lime"])   # toxic spots
    im = outline(im, [p["outline"], p["black"]])
    d = ImageDraw.Draw(im)                         # gas drawn after outline: loose pixels
    if f == 2: d.point((9, 8), fill=p["gas"]); d.point((10, 6), fill=p["gas"])
    else: d.point((8, 9), fill=p["gas"])
    return im

SPRITES = {"flower_good_sprout": good_sprout, "flower_good_stem": good_stem, "flower_poison_sprout": poison_sprout}

if __name__ == "__main__":
    import sys, os
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    os.makedirs(out, exist_ok=True)
    for name, fn in SPRITES.items():
        for f in (1, 2): fn(f).save(f"{out}/{name}_f{f}.png")
