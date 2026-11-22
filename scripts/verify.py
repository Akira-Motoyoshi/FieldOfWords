import glob, sys
from PIL import Image
from palette import GOOD, POISON, rgb
G = {rgb(v) for v in GOOD.values()}; P = {rgb(v) for v in POISON.values()}
ok = True
# Scope: the Day 1 sprites only. The palette is chosen from the file name, so poison-family files without
# "poison" in the name (mold, fx_gas, fx_skull, fx_text_*) would be checked against the wrong palette.
# Everything else is covered by verify_poison / verify_good / verify_purified / verify_effects.
DAY1 = ("flower_good_sprout_", "flower_good_stem_", "flower_poison_sprout_")
for f in sorted(x for x in glob.glob(sys.argv[1] + "/*.png") if x.rsplit("/", 1)[-1].startswith(DAY1)):
    im = Image.open(f).convert("RGBA"); pal = P if "poison" in f else G
    cols = {px[:3] for px in im.getdata() if px[3]}
    bad = cols - pal; semi = {px[3] for px in im.getdata() if 0 < px[3] < 255}
    bbox = im.getbbox(); bottom = bbox[3] if bbox else None
    print(f.split("/")[-1], im.size, "colors", len(cols), "OFF-PALETTE" if bad else "ok",
          "semi-alpha!" if semi else "", "bottom", bottom)
    ok &= not bad and not semi
print("ALL OK" if ok else "FAIL")
