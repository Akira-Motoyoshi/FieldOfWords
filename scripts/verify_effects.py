#!/usr/bin/env python3
"""Checks the remaining assets: mold, milestone effects, normal effects, poison effects, gardener.
  python3 verify_effects.py <assets dir>
Family rule: good family -> GOOD palette only | poison family -> POISON palette only (neon allowed only there)."""
import sys
from PIL import Image, ImageOps
from palette import GOOD, POISON, NEON, rgb, _lab
GS = {rgb(v) for v in GOOD.values()}; PS = {rgb(v) for v in POISON.values()}; NE = {rgb(POISON[k]) for k in NEON}
BONE, BLACK = rgb(POISON["bone"]), rgb(POISON["black"])
SPEC = {  # name: (w, h, family, min differing pixels between f1/f2)
 "flower_mold": (48, 48, "poison", 6), "fx_rainbow": (72, 36, "good", 6), "fx_butterfly_a": (12, 10, "good", 6), "fx_butterfly_b": (12, 10, "good", 6),
 "fx_seed": (16, 16, "good", 6), "fx_sun": (16, 16, "good", 6), "fx_drop": (16, 16, "good", 6), "fx_fertilizer": (16, 16, "good", 6), "fx_dew": (16, 16, "good", 6),
 "fx_skull": (8, 8, "poison", 3), "fx_poison_bubble": (16, 16, "poison", 6), "fx_gas": (16, 16, "poison", 6),
 "fx_text_piki": (42, 20, "poison", 6), "fx_text_gogogo": (42, 20, "poison", 6),
 "gardener_idle": (24, 32, "good", 6), "gardener_water": (24, 32, "good", 6), "gardener_purify": (24, 32, "good", 6)}
d = sys.argv[1]; ok = True
for name, (w, h, fam, mindiff) in SPEC.items():
    frames = [Image.open(f"{d}/{name}_f{f}.png").convert("RGBA") for f in (1, 2)]; notes = []
    for f, im in enumerate(frames, 1):
        px = list(im.getdata()); op = [q for q in px if q[3]]; cols = {q[:3] for q in op}; fails = []
        if im.size != (w, h): fails.append(f"size{im.size}")
        if not op: fails.append("empty")
        elif cols - (GS if fam == "good" else PS): fails.append("off-palette")
        if any(0 < q[3] < 255 for q in px): fails.append("semi-alpha")
        if name == "flower_mold" and op:                       # same strict rules as the poison flowers
            if sum(1 for q in op if q[:3] in NE) < 3: fails.append("neon<3")
            if sum(1 for q in op if q[:3] == BONE) < 4: fails.append("no eye/fang")
            if sum(1 for q in op if q[:3] == BLACK) < 10: fails.append("no black outline")
            bb = im.getbbox(); m = ImageOps.mirror(im); a, b = im.load(), m.load()
            if bb[3] != h: fails.append(f"bottom={bb[3]}")
            if abs((bb[0] + bb[2]) / 2 - w / 2) > 3: fails.append("off-centre")
            if sum(1 for y in range(h) for x in range(w) if a[x, y] != b[x, y] and (a[x, y][3] or b[x, y][3])) / len(op) < .10: fails.append("too symmetric")
            if sum(_lab(q[:3])[0] for q in op if q[:3] not in NE) / len([q for q in op if q[:3] not in NE]) > 50: fails.append("too bright")
        if name.startswith("gardener") and op:
            bb = im.getbbox()
            if bb[3] != h: fails.append(f"bottom={bb[3]}")
            if abs((bb[0] + bb[2]) / 2 - w / 2) > 5: fails.append("off-centre")
        if name in ("fx_text_piki", "fx_text_gogogo") and op and sum(1 for q in op if q[:3] in NE) < 20: fails.append("text too faint")
        if fails: notes.append((f"f{f}", fails)); ok = False
    n = sum(1 for y in range(h) for x in range(w) if frames[0].getpixel((x, y)) != frames[1].getpixel((x, y)))
    if n < mindiff: notes.append(("frames", f"only {n} px differ")); ok = False
    print(f"{name:20s} {w}x{h} {fam:6s} diff {n:4d}px", "ok" if not notes else notes)
print("ALL OK" if ok else "FAIL")
