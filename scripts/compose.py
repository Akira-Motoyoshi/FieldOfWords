#!/usr/bin/env python3
"""Daily garden compositor.

  python3 compose.py --state garden/state.json --assets assets --out out [--gif]

Reads state.json (v2), draws background/fence/bed/HUD (make_day0.py), places the sprites
for each plot at its slot anchor (bottom-centre) and writes, per garden:
  <out>/<garden>.png        1080x1080, frame 1
  <out>/<garden>.gif        2 frames (only with --gif)
  <out>/<garden>.alt.txt    alt text draft (Japanese)
and <out>/report.json (drawn counts, missing sprites, sky stage). Missing sprites are
skipped and reported - the run never stops because of them.
"""
import argparse, json, os
from PIL import Image
import make_day0 as G

LABELS = {"x": ("x", "X GARDEN", "黒い鉄柵"),
          "instagram": ("instagram", "INSTAGRAM GARDEN", "夕焼け色の木柵"),
          "threads": ("threads", "THREADS GARDEN", "白い柵で、角が黒い")}
LARGE = {"rafflesia", "blackhole", "mold"}          # 48x48 sprites: draw last in their row
POISON_DRAW_CAP = 2
ADULT_AFTER_DAYS = 1                                # poison plot shows adult form from age_days >= 1
SKY_WORDS = ["水色", "薄紫がかっている", "紫色", "暗い紫で稲妻が走っている"]

def sky_stage(n_poison):
    return 0 if n_poison == 0 else 1 if n_poison <= 2 else 2 if n_poison <= 4 else 3

def sprite_name(plot):
    k = plot["kind"]
    if k == "good":
        st = plot.get("stage", "sprout")
        return f"flower_good_{st}" if st in ("sprout", "stem") else f"flower_good_{plot['species']}_{st}"
    if k == "poison":
        return "flower_poison_sprout" if plot.get("age_days", 0) < ADULT_AFTER_DAYS else f"flower_poison_{plot['species']}"
    if k == "purified":
        return f"flower_purified_{plot['species']}"
    if k == "mold":
        return "flower_mold"
    return None

def load(assets, name, frame, cache):
    for f in (frame, 1):
        path = f"{assets}/{name}_f{f}.png"
        if path in cache: return cache[path]
        if os.path.exists(path):
            cache[path] = Image.open(path).convert("RGBA"); return cache[path]
    return None

def plan_plots(garden):
    """Return [(slot_id, plot)] to draw, applying the poison cap (extras -> one mold)."""
    plots = [p for p in garden["plots"] if p.get("kind") not in (None, "empty")]
    poison = sorted([p for p in plots if p["kind"] == "poison"], key=lambda p: -p.get("age_days", 0))
    keep = {id(p) for p in poison[:POISON_DRAW_CAP]}
    extra = poison[POISON_DRAW_CAP:]
    out = [p for p in plots if p["kind"] != "poison" or id(p) in keep]
    if extra and not any(p["kind"] == "mold" for p in out):
        out.append({"id": extra[0]["id"], "kind": "mold", "count": len(extra)})
    return out, len(poison)

def alt_text(theme, garden, n_poison, n_good, n_bloom):
    fence = LABELS[theme][2]
    if not n_good and not n_poison:
        body = "花壇には土だけがあり、まだ何も育っていない"
    else:
        parts = []
        if n_good: parts.append(f"良い花が{n_good}輪" + (f"（うち開花{n_bloom}輪）" if n_bloom else ""))
        if n_poison: parts.append(f"毒の花が{n_poison}輪")
        body = "花壇には" + "、".join(parts) + "育っている"
    return f"ドット絵の庭。{body}。空は{SKY_WORDS[sky_stage(n_poison)]}。柵は{fence}。"

def hud_values(garden):
    h = {"sun": min(garden.get("sun_level", 0) / 5, 1.0),
         "health": max(0.0, min(garden.get("health", 50) / 100, 1.0))}
    h.update(garden.get("hud", {}))                 # optional override: {"water":0..1,"nutrition":0..1}
    return h

def render(theme, garden, assets, frame, cache, report):
    _, label, _ = LABELS[theme]
    drawn, n_poison = plan_plots(garden)
    st = sky_stage(n_poison)
    img = G.scene(theme, label, day=f"DAY {garden.get('day', 0)}", sky_stage=st,
                  hud_vals=hud_values(garden)).convert("RGBA")
    def key(p):
        r, _ = G.SLOTS[p["id"] - 1]; name = sprite_name(p) or ""
        return (r, any(t in name for t in LARGE), G.SLOTS[p["id"] - 1][1])
    for p in sorted(drawn, key=key):
        name = sprite_name(p); spr = load(assets, name, frame, cache)
        if spr is None:
            if frame == 1: report["missing"].append(name)
            continue
        ax, ay = G.slot_anchor(p["id"])
        img.alpha_composite(spr, (ax - spr.width // 2, ay - spr.height))
    return img.convert("RGB"), st, n_poison, drawn

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", required=True); ap.add_argument("--assets", default="assets")
    ap.add_argument("--out", default="out"); ap.add_argument("--gif", action="store_true")
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    state = json.load(open(a.state, encoding="utf-8")); cache = {}; reports = {}
    for name, garden in state["gardens"].items():
        theme = LABELS[name][0]; report = {"missing": []}
        frames = []
        for f in (1, 2):
            img, st, n_poison, drawn = render(theme, garden, a.assets, f, cache, report)
            frames.append(img)
        big = [im.resize((G.W * G.SCALE, G.H * G.SCALE), Image.NEAREST) for im in frames]
        big[0].save(f"{a.out}/{name}.png")
        if a.gif:
            big[0].save(f"{a.out}/{name}.gif", save_all=True, append_images=[big[1]], duration=700, loop=0)
        n_good = sum(1 for p in drawn if p["kind"] in ("good", "purified"))
        n_bloom = sum(1 for p in drawn if (p["kind"] == "good" and p.get("stage") == "bloom") or p["kind"] == "purified")
        open(f"{a.out}/{name}.alt.txt", "w", encoding="utf-8").write(alt_text(theme, garden, n_poison, n_good, n_bloom))
        report.update({"sky_stage": st, "poison_total": n_poison, "drawn": len(drawn),
                       "missing": sorted(set(report["missing"]))})
        reports[name] = report
    json.dump(reports, open(f"{a.out}/report.json", "w"), ensure_ascii=False, indent=2)
    print(json.dumps(reports, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
