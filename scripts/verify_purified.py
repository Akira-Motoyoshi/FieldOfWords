import sys
from PIL import Image
from palette import GOOD, POISON, rgb, _lab
G = {k: rgb(v) for k, v in GOOD.items()}; GS = set(G.values()); BROWN = {G["outline"]}
SIZES = {"rafflesia": 48, "blackhole": 48, "haetori": 32, "saboten": 32, "chili": 32}
SIG = {"rafflesia": [("gold", 10), ("yellow_deep", 20), ("white", 3)], "haetori": [("yellow", 12), ("yellow_deep", 8), ("cream", 6)],
       "saboten": [("pink", 12), ("stem", 30), ("cream", 4)], "chili": [("orange", 25), ("yellow", 8)], "blackhole": [("blue", 40), ("sky", 15), ("white", 6)]}
d = sys.argv[1]; poison_dir = sys.argv[2] if len(sys.argv) > 2 else d; ok = True; rows = []
def mean_l(im, skip):
    L = [_lab(q[:3])[0] for q in im.getdata() if q[3] and q[:3] not in skip]; return sum(L) / len(L)
for name, size in SIZES.items():
    frames = [Image.open(f"{d}/flower_purified_{name}_f{f}.png").convert("RGBA") for f in (1, 2)]
    for f, im in enumerate(frames, 1):
        px = list(im.getdata()); op = [q for q in px if q[3]]; cols = {q[:3] for q in op}; fails = []
        if im.size != (size, size): fails.append("size")
        if cols - GS: fails.append("off-GOOD-palette")
        if any(0 < q[3] < 255 for q in px): fails.append("semi-alpha")
        bb = im.getbbox()
        if bb[3] != size: fails.append(f"bottom={bb[3]}")
        if abs((bb[0] + bb[2]) / 2 - size / 2) > 4: fails.append("off-centre")
        lm = mean_l(im, BROWN)
        if lm < 60: fails.append("too dark")
        for c, n in SIG[name]:
            k = sum(1 for q in op if q[:3] == G[c])
            if k < n: fails.append(f"{c}={k}<{n}")
        po = Image.open(f"{poison_dir}/flower_poison_{name}_f{f}.png").convert("RGBA")
        gap = lm - mean_l(po, {rgb(POISON['neon_lime']), rgb(POISON['neon_pink'])})
        if gap < 25: fails.append(f"flip too weak {gap:.0f}")
        rows.append((name, f, round(lm, 1), f"flip +{gap:.0f}L", fails or "ok")); ok &= not fails
    a, b = frames; n = sum(1 for y in range(a.height) for x in range(a.width) if a.getpixel((x, y)) != b.getpixel((x, y)))
    if n < 6: rows.append((name, "frames identical", n, "", "FAIL")); ok = False
for r in rows: print(r)
print("ALL OK" if ok else "FAIL")
