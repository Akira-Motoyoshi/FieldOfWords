"""Fixed palettes for ことばのかだん sprites. Good and poison sets never share a color."""
GOOD = {
  "outline":      "#94572a",  # warm brown outline (never black)
  "center":       "#80480e",  # sunflower centre / seeds
  "stem_dark":    "#2f8f3a",
  "stem":         "#55c24a",
  "leaf_light":   "#a8e86a",
  "yellow_deep":  "#f2b21c",
  "yellow":       "#ffe04a",
  "cream":        "#fff4c0",
  "white":        "#ffffff",
  "pink_deep":    "#ef6f9b",
  "pink":         "#ffb0cc",
  "red":          "#e8443a",
  "orange":       "#ff9a3a",
  "sky":          "#8fd4ff",
  "blue":         "#4c8ff0",
  "gold":         "#d49a1f",
}
POISON = {
  "black":        "#0e0a12",  # outer outline
  "outline":      "#3a1450",  # inner outline (deep purple)
  "purple":       "#682a8a",
  "violet":       "#8a44aa",
  "blood_dark":   "#4a0e16",
  "blood":        "#7a1c24",
  "bruise":       "#5a1e3e",
  "sick_dark":    "#2e3c1a",
  "ditch":        "#54682e",
  "grey_green":   "#76866a",
  "grey":         "#6c6874",
  "grey_dark":    "#3a3642",
  "gas":          "#9a6ab4",  # muted lavender for gas / highlights
  "bone":         "#b4ac9a",
  "neon_lime":    "#a8ff1e",  # neon 1 of 2
  "neon_pink":    "#ff2bd6",  # neon 2 of 2
}
NEON = {"neon_lime", "neon_pink"}

def rgb(h): h = h.lstrip("#"); return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def _lab(c):
    def lin(v):
        v /= 255
        return ((v + 0.055) / 1.055) ** 2.4 if v > 0.04045 else v / 12.92
    r, g, b = (lin(v) for v in c)
    x = (0.4124*r + 0.3576*g + 0.1805*b) / 0.95047
    y = (0.2126*r + 0.7152*g + 0.0722*b)
    z = (0.0193*r + 0.1192*g + 0.9505*b) / 1.08883
    f = lambda t: t ** (1/3) if t > 0.008856 else 7.787*t + 16/116
    fx, fy, fz = f(x), f(y), f(z)
    return 116*fy - 16, 500*(fx - fy), 200*(fy - fz)

def delta_e(c1, c2):
    a, b = _lab(c1), _lab(c2)
    return sum((p - q) ** 2 for p, q in zip(a, b)) ** 0.5

def quantize(img, which="good"):
    """Snap every opaque pixel of an RGBA image to the nearest colour of one palette."""
    pal = [rgb(v) for v in (GOOD if which == "good" else POISON).values()]
    img = img.convert("RGBA"); px = img.load()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = px[x, y]
            if a < 128: px[x, y] = (0, 0, 0, 0); continue
            px[x, y] = (*min(pal, key=lambda p: delta_e(p, (r, g, b))), 255)
    return img
