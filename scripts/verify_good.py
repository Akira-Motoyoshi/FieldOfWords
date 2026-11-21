import sys
from PIL import Image
from palette import GOOD, rgb, _lab
G = {k: rgb(v) for k, v in GOOD.items()}; GS = set(G.values())
GREEN = {G["stem"], G["stem_dark"], G["leaf_light"]}; BROWN = {G["outline"]}
SIG = {  # signature colours that must appear (>= n pixels) in the bloom
 "himawari": [("yellow", 15), ("yellow_deep", 10)], "sakuraso": [("pink", 15), ("pink_deep", 5)],
 "kinbara": [("gold", 8), ("yellow_deep", 10), ("white", 3)], "nohana": [("white", 10), ("sky", 5)],
 "tulip_red": [("red", 25)], "tulip_yellow": [("yellow", 25)], "tulip_blue": [("blue", 25)]}
d = sys.argv[1]; ok = True; rows = []
for key, sig in SIG.items():
    sp = key
    size = (32, 48) if key == "himawari" else (32, 32)
    counts = {}
    for stage in ("bud", "bloom"):
        frames = [Image.open(f"{d}/flower_good_{sp}_{stage}_f{f}.png").convert("RGBA") for f in (1, 2)]
        for f, im in enumerate(frames, 1):
            px = list(im.getdata()); op = [q for q in px if q[3]]; cols = {q[:3] for q in op}; fails = []
            exp = size if stage == "bloom" else (32, 32)
            if im.size != exp: fails.append(f"size{im.size}")
            if cols - GS: fails.append("off-palette")
            if any(0 < q[3] < 255 for q in px): fails.append("semi-alpha")
            bb = im.getbbox()
            if bb[3] != im.height: fails.append(f"bottom={bb[3]}")
            if abs((bb[0] + bb[2]) / 2 - im.width / 2) > 4: fails.append("off-centre")
            lum = [_lab(q[:3])[0] for q in op if q[:3] not in BROWN]
            if sum(lum) / len(lum) < 60: fails.append("too dark")
            if stage == "bloom":
                for name, n in sig:
                    c = sum(1 for q in op if q[:3] == G[name])
                    if c < n: fails.append(f"{name}={c}<{n}")
            counts[(stage, f)] = sum(1 for q in op if q[:3] not in GREEN | BROWN)
            rows.append((sp, stage, f, round(sum(lum)/len(lum), 1), len(cols), fails or "ok")); ok &= not fails
        a, b = frames; n = sum(1 for y in range(a.height) for x in range(a.width) if a.getpixel((x, y)) != b.getpixel((x, y)))
        if n < 6: rows.append((sp, stage, "frames identical", n, "", "FAIL")); ok = False
    if counts[("bloom", 1)] <= counts[("bud", 1)] * 1.3:
        rows.append((sp, "bloom not bigger than bud", counts[("bloom", 1)], counts[("bud", 1)], "", "FAIL")); ok = False
for r in rows: print(r)
print("ALL OK" if ok else "FAIL")
