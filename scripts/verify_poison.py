import glob, sys, os
from PIL import Image, ImageOps
from palette import POISON, NEON, rgb, _lab
P = {rgb(v) for v in POISON.values()}; NE = {rgb(POISON[k]) for k in NEON}; BONE = rgb(POISON["bone"]); BLACK = rgb(POISON["black"])
SIZES = {"rafflesia": 48, "blackhole": 48, "haetori": 32, "saboten": 32, "chili": 32}
d = sys.argv[1]; ok = True; rows = []
for name, size in SIZES.items():
    frames = [Image.open(f"{d}/flower_poison_{name}_f{f}.png").convert("RGBA") for f in (1, 2)]
    for f, im in enumerate(frames, 1):
        px = list(im.getdata()); op = [q for q in px if q[3]]
        cols = {q[:3] for q in op}; fails = []
        if im.size != (size, size): fails.append("size")
        if cols - P: fails.append("off-palette")
        if any(0 < q[3] < 255 for q in px): fails.append("semi-alpha")
        if sum(1 for q in op if q[:3] in NE) < 3: fails.append("neon<3")
        if sum(1 for q in op if q[:3] == BONE) < 4: fails.append("no skull/eye/fang")
        if sum(1 for q in op if q[:3] == BLACK) < 10: fails.append("no black outline")
        bb = im.getbbox()
        if bb[3] != size: fails.append(f"bottom={bb[3]}")
        if abs((bb[0] + bb[2]) / 2 - size / 2) > 3: fails.append("off-centre")
        flip = ImageOps.mirror(im); a, b = im.load(), flip.load()
        diff = sum(1 for y in range(size) for x in range(size) if a[x, y] != b[x, y] and (a[x, y][3] or b[x, y][3]))
        asym = diff / max(1, len(op))
        if asym < 0.10: fails.append(f"too symmetric {asym:.2f}")
        dark = [_lab(q[:3])[0] for q in op if q[:3] not in NE]
        if sum(dark) / len(dark) > 50: fails.append("too bright")
        rows.append((name, f, round(asym, 2), round(sum(dark)/len(dark), 1), len(cols), fails or "ok")); ok &= not fails
    a, b = frames; n = sum(1 for y in range(a.height) for x in range(a.width) if a.getpixel((x, y)) != b.getpixel((x, y)))
    if n < 6: rows.append((name, "frames", "identical", n, "", "FAIL")); ok = False
for r in rows: print(r)
print("ALL OK" if ok else "FAIL")
