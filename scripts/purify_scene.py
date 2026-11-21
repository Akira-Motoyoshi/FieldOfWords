#!/usr/bin/env python3
"""Purification scenes: before / after images and a transition GIF.

  python3 purify_scene.py --assets assets --out purify_out --garden threads --species rafflesia [--slot 3] [--day 3]

Outputs: <species>_before.png, <species>_after.png, <species>_before_after.png (2 panels side by side,
2160x1080), <species>.gif (before -> sparkles -> dither mix -> after). The transition is built from the
two sprites only (no new art), so it never fails when the assets exist.
"""
import argparse, os, random
from PIL import Image
import compose as C
import make_day0 as G

LABEL = C.LABELS
ASSETS = "assets"

def sprite_img(assets, name, frame=1):
    return C.load(assets, name, frame, {})

def build_scene(theme, day, plots, target, sky_st, health, hud_extra=None):
    """Draw background + context plots; the target sprite is pasted separately."""
    garden = {"day": day, "sun_level": 3, "health": health, "hud": {"water": 0.6, "nutrition": 0.5}, "plots": plots}
    drawn, _ = C.plan_plots(garden)
    img = G.scene(theme, LABEL[theme][1], day=f"DAY {day}", sky_stage=sky_st, hud_vals=C.hud_values(garden)).convert("RGBA")
    cache = {}
    for p in sorted(drawn, key=lambda p: (G.SLOTS[p["id"] - 1][0], G.SLOTS[p["id"] - 1][1])):   # context plants
        spr = C.load(ASSETS, C.sprite_name(p, theme), 1, cache)
        if spr is not None: paste_sprite(img, spr, p["id"])
    return img, drawn

def paste_sprite(img, spr, slot):
    ax, ay = G.slot_anchor(slot); img.alpha_composite(spr, (ax - spr.width // 2, ay - spr.height))

def mix(poison, purified, phase):
    size = (max(poison.width, purified.width), max(poison.height, purified.height))
    def put(sp):
        c = Image.new("RGBA", size, (0, 0, 0, 0)); c.alpha_composite(sp, ((size[0] - sp.width) // 2, size[1] - sp.height)); return c
    a, b = put(poison), put(purified); out = Image.new("RGBA", size, (0, 0, 0, 0))
    for y in range(size[1]):
        for x in range(size[0]):
            first, second = (b, a) if (x + y) % 2 == phase else (a, b)
            q = first.getpixel((x, y)); out.putpixel((x, y), q if q[3] else second.getpixel((x, y)))
    return out

def sparkles(img, slot, spr_w, spr_h, n=9, seed=1, big=True):
    ax, ay = G.slot_anchor(slot); rnd = random.Random(seed); W = (255, 255, 255, 255)
    for i in range(n):
        x = ax + rnd.randint(-spr_w // 2 - 3, spr_w // 2 + 3); y = ay - rnd.randint(2, spr_h)
        img.putpixel((x, y), W)
        if big and i % 2 == 0:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                if 0 <= x + dx < G.W and 0 <= y + dy < G.H: img.putpixel((x + dx, y + dy), W)

def up(im): return im.convert("RGB").resize((G.W * G.SCALE, G.H * G.SCALE), Image.NEAREST)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--assets", default="assets"); ap.add_argument("--out", default="purify_out")
    ap.add_argument("--garden", default="threads"); ap.add_argument("--species", required=True)
    ap.add_argument("--slot", type=int, default=0); ap.add_argument("--day", type=int, default=3)
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    global ASSETS; ASSETS = a.assets
    sp = a.species; slot = a.slot or C.choose_slot(sp, {11, 7})
    poison_s, good_s = sprite_img(a.assets, f"flower_poison_{sp}"), sprite_img(a.assets, f"flower_purified_{sp}")
    if poison_s is None or good_s is None: raise SystemExit(f"missing sprite for {sp}")
    context = [{"id": 11, "kind": "good", "stage": "bloom", "species": "himawari"} if False else {"id": 11, "kind": "good", "stage": "bloom", "species": "sakuraso"},
               {"id": 7, "kind": "good", "stage": "bud", "species": "tulip", "color": "yellow"}]
    # frames: (poison|mix|good, sky stage, health, sparkle count)
    def frame(kind, sky_st, health, spark=0, phase=0):
        img, _ = build_scene(a.garden, a.day, context, sp, sky_st, health)
        spr = {"poison": poison_s, "good": good_s}.get(kind) or mix(poison_s, good_s, phase)
        paste_sprite(img, spr, slot)
        if spark: sparkles(img, slot, spr.width, spr.height, n=spark, seed=spark)
        return img
    before, after = frame("poison", 1, 40), frame("good", 0, 50, spark=7, phase=0)
    seq = [(frame("poison", 1, 40), 700), (frame("poison", 1, 40, spark=8), 350), (frame("mix", 1, 42, spark=10, phase=0), 280),
           (frame("mix", 1, 46, spark=12, phase=1), 280), (frame("good", 0, 50, spark=9), 350), (frame("good", 0, 50), 1400)]
    up(before).save(f"{a.out}/{sp}_before.png"); up(after).save(f"{a.out}/{sp}_after.png")
    pair = Image.new("RGB", (G.W * G.SCALE * 2, G.H * G.SCALE)); pair.paste(up(before), (0, 0)); pair.paste(up(after), (G.W * G.SCALE, 0))
    pair.save(f"{a.out}/{sp}_before_after.png")
    frames = [up(im) for im, _ in seq]
    frames[0].save(f"{a.out}/{sp}.gif", save_all=True, append_images=frames[1:], duration=[d for _, d in seq], loop=0)
    print(f"{sp}: slot {slot}, {len(frames)} frames, {os.path.getsize(f'{a.out}/{sp}.gif')//1024} KB")

if __name__ == "__main__":
    main()
