import glob, sys
from PIL import Image
from palette import GOOD, POISON, rgb
G = {rgb(v) for v in GOOD.values()}; P = {rgb(v) for v in POISON.values()}
ok = True
for f in sorted(glob.glob(sys.argv[1] + "/*.png")):
    im = Image.open(f).convert("RGBA"); pal = P if "poison" in f else G
    cols = {px[:3] for px in im.getdata() if px[3]}
    bad = cols - pal; semi = {px[3] for px in im.getdata() if 0 < px[3] < 255}
    bbox = im.getbbox(); bottom = bbox[3] if bbox else None
    print(f.split("/")[-1], im.size, "colors", len(cols), "OFF-PALETTE" if bad else "ok",
          "semi-alpha!" if semi else "", "bottom", bottom)
    ok &= not bad and not semi
print("ALL OK" if ok else "FAIL")
