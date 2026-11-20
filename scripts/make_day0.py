#!/usr/bin/env python3
"""Garden images (8bit, 180x180 native -> 1080x1080) + slot layout for sprite compositing.

Usage: python3 make_day0.py <outdir>
Outputs: day0_x.png / day0_instagram.png / day0_threads.png / garden_layout_guide.png / garden_layout.json
Layout (5 cols x 3 rows = 15 slots) is shared with the daily compositor: sprites are placed
with their bottom-center at each slot's anchor.
"""
import json, random
from PIL import Image, ImageDraw

W = H = 180
SCALE = 6
COLS, ROWS = 5, 3
CELL_W, CELL_H = 32, 20            # one flower position (invisible grid inside the bed)
BED = (10, 70, 169, 141)           # single flower bed: x0, y0, x1, y1 (160 x 72)
ANCHOR_X0, PITCH_X = 26, 32
ANCHOR_Y = [90, 110, 130]          # sprite base line per row (row pitch 20)
HUD_Y = 148
INITIAL_ACTIVE = [7, 8, 9]
EXPANSION_ORDER = [6, 10, 13, 12, 14, 11, 15, 3, 2, 4, 1, 5]   # after the initial 3

def slot_anchor(i):
    r, c = divmod(i - 1, COLS)
    return ANCHOR_X0 + c * PITCH_X, ANCHOR_Y[r]

def slot_rect(i):
    ax, ay = slot_anchor(i)
    return ax - CELL_W // 2, ay - 10

GLYPHS = {
 "D":["110","101","101","101","110"], "A":["010","101","111","101","101"],
 "Y":["101","101","010","010","010"], "X":["101","101","010","101","101"],
 "G":["011","100","101","101","011"], "R":["110","101","110","101","101"],
 "E":["111","100","110","100","111"], "I":["111","010","010","010","111"],
 "S":["011","100","010","001","110"], "T":["111","010","010","010","010"],
 "H":["101","101","111","101","101"], "L":["100","100","100","100","111"],
 "O":["010","101","101","101","010"], "U":["101","101","101","101","111"],
 "N":["1001","1101","1011","1001","1001"], "M":["10001","11011","10101","10001","10001"],
 "0":["111","101","101","101","111"], "1":["010","110","010","010","111"],
 "2":["110","001","010","100","111"], "3":["110","001","010","001","110"],
 "4":["101","101","111","001","001"], "5":["111","100","110","001","110"],
 "6":["011","100","110","101","010"], "7":["111","001","010","010","010"],
 "8":["010","101","010","101","010"], "9":["010","101","011","001","110"],
 " ":["00","00","00","00","00"],
}
def text_w(s): return sum(len(GLYPHS[ch][0]) + 1 for ch in s) - 1
def draw_text(d, x, y, s, col):
    cx = x
    for ch in s:
        g = GLYPHS[ch]
        for r, row in enumerate(g):
            for c, v in enumerate(row):
                if v == "1": d.point((cx + c, y + r), fill=col)
        cx += len(g[0]) + 1
def banner(d, x, y, s):
    d.rectangle([x - 2, y - 2, x + text_w(s) + 1, y + 6], fill=(28, 30, 52))
    draw_text(d, x, y, s, (255, 255, 255))

def sprite(d, x, y, rows, cmap):
    for r, row in enumerate(rows):
        for c, ch in enumerate(row):
            if ch in cmap: d.point((x + c, y + r), fill=cmap[ch])
HEART = [".RR.RR.","RRRRRRR","RRRRRRR",".RRRRR.","..RRR..","...R..."]
DROP  = ["...B...","...B...","..BBB..",".BBBBB.","BBBBBBB","BBBBBBB",".BBBBB.","..BBB.."]
SPROUT= ["GG....GG","GGG..GGG",".GGGGGG.","...GG...","...GG...","...GG..."]
SUN   = ["Y..Y..Y.",".YYYYY..","..YYYY.Y","YYYYYYY.","..YYYY.Y",".YYYYY..","Y..Y..Y."]
CMAP = {"R":(235,70,90),"B":(70,150,235),"G":(80,200,90),"Y":(255,220,60)}

FENCE_Y0, FENCE_Y1, GROUND_Y0 = 44, 62, 62

def sky(d, theme):
    for y in range(0, GROUND_Y0 + 1):
        t = min(y / 44, 1)
        d.line([(0, y), (W, y)], fill=(int(120 + 60 * t), int(195 + 30 * t), 250))
    if theme == "instagram":
        for y in range(28, 46):
            d.line([(0, y), (W, y)], fill=(255, 190 - int((y - 28) * 1.2), 120))
        for y in range(46, GROUND_Y0 + 1):
            d.line([(0, y), (W, y)], fill=(255, 140, 150))
    sprite(d, 150, 6, SUN, CMAP)
    for cx, cy in [(24, 20), (90, 26), (126, 16)]:
        for dx, dy, w in [(2, 0, 6), (0, 2, 10), (1, 4, 8)]:
            d.line([(cx + dx, cy + dy), (cx + dx + w, cy + dy)], fill=(255, 255, 255))
    rnd = random.Random(7)
    for _ in range(14):
        d.point((rnd.randrange(W), rnd.randrange(14, 40)), fill=(255, 255, 255))

def ground(d, theme):
    rnd = random.Random(3)
    if theme == "x":
        for gy in range(GROUND_Y0, HUD_Y, 12):
            for gx in range(0, W, 12):
                d.rectangle([gx, gy, gx + 11, gy + 11], fill=rnd.choice([(150,150,155),(135,135,140),(165,165,170)]))
                d.line([(gx, gy), (gx + 11, gy)], fill=(100,100,106))
                d.line([(gx, gy), (gx, gy + 11)], fill=(100,100,106))
    elif theme == "instagram":
        d.rectangle([0, GROUND_Y0, W, HUD_Y], fill=(236,196,146))
        for _ in range(70):
            d.point((rnd.randrange(W), rnd.randrange(GROUND_Y0, HUD_Y)), fill=(214,170,120))
    else:
        d.rectangle([0, GROUND_Y0, W, HUD_Y], fill=(112,200,92))
        for _ in range(80):
            d.point((rnd.randrange(W), rnd.randrange(GROUND_Y0, HUD_Y)), fill=(88,172,72))
        for _ in range(36):
            x, y = rnd.randrange(W - 1), rnd.randrange(GROUND_Y0 + 2, HUD_Y)
            d.point((x, y), fill=(245,245,245)); d.point((x + 1, y), fill=(220,220,220))

def fence(d, theme):
    y0, y1 = FENCE_Y0, FENCE_Y1
    if theme == "x":   pick, edge, rail = (22,22,28), (0,0,0), (60,60,70)
    elif theme == "instagram": pick, edge, rail = (214,128,66), (120,64,30), (170,96,48)
    else:              pick, edge, rail = (246,246,246), (170,170,176), (225,225,230)
    d.rectangle([0, y0 + 6, W, y0 + 9], fill=rail)
    d.rectangle([0, y1 - 6, W, y1 - 3], fill=rail)
    for x in range(2, W, 7):
        d.rectangle([x, y0 + 2, x + 3, y1], fill=pick)
        d.line([(x, y0 + 2), (x, y1)], fill=edge); d.line([(x + 3, y0 + 2), (x + 3, y1)], fill=edge)
        d.point((x + 1, y0 + 1), fill=pick); d.point((x + 2, y0 + 1), fill=pick)
        if theme == "x": d.point((x + 1, y0), fill=edge)
    if theme == "threads":
        for x in (0, W - 6):
            d.rectangle([x, y0 - 6, x + 5, y1 + 2], fill=(20,20,24))
            d.rectangle([x + 1, y0 - 5, x + 2, y1 + 1], fill=(60,60,66))

def bed(d, theme):
    x0, y0, x1, y1 = BED
    edge = {"x": ((60,60,68), (110,110,120)),
            "instagram": ((255,140,180), (255,185,210)),
            "threads": ((236,236,240), (255,255,255))}[theme]
    d.rectangle([x0 - 3, y0 - 3, x1 + 3, y1 + 3], fill=(40,28,20))   # outline
    d.rectangle([x0 - 2, y0 - 2, x1 + 2, y1 + 2], fill=edge[0])        # frame
    d.line([(x0 - 2, y0 - 2), (x1 + 2, y0 - 2)], fill=edge[1])
    d.line([(x0 - 2, y0 - 2), (x0 - 2, y1 + 2)], fill=edge[1])
    d.rectangle([x0, y0, x1, y1], fill=(124,82,46))                    # soil
    rnd = random.Random(5)
    for _ in range(420):
        d.point((rnd.randrange(x0 + 1, x1), rnd.randrange(y0 + 1, y1)),
                fill=rnd.choice([(104,66,36), (140,96,56)]))
    for _ in range(9):
        cx, cy = rnd.randrange(x0 + 4, x1 - 8), rnd.randrange(y0 + 4, y1 - 5)
        d.line([(cx, cy), (cx + 3, cy + 1), (cx + 5, cy + 3)], fill=(88,54,28))

def hud(d):
    d.rectangle([0, HUD_Y, W, H], fill=(28,30,52))
    d.line([(0, HUD_Y), (W, HUD_Y)], fill=(90,100,160))
    def bar(x, y, frac, col):
        d.rectangle([x, y, x + 51, y + 6], fill=(18,18,32), outline=(100,100,130))
        n = int(50 * frac)
        if n: d.rectangle([x + 1, y + 1, x + n, y + 5], fill=col)
    sprite(d, 8, 152, SUN, CMAP);     bar(22, 153, 0.0, (255,220,60))
    sprite(d, 96, 152, DROP, CMAP);   bar(110, 153, 0.0, (70,150,235))
    sprite(d, 8, 165, SPROUT, CMAP);  bar(22, 165, 0.0, (80,200,90))
    sprite(d, 96, 165, HEART, CMAP);  bar(110, 165, 0.5, (235,70,90))

def scene(theme, label, day="DAY 0", with_hud=True):
    img = Image.new("RGB", (W, H)); d = ImageDraw.Draw(img)
    sky(d, theme); ground(d, theme); fence(d, theme); bed(d, theme)
    banner(d, 5, 5, day)
    banner(d, (W - text_w(label)) // 2, 5, label)
    if with_hud: hud(d)
    return img

def save(img, path):
    img.resize((W * SCALE, H * SCALE), Image.NEAREST).save(path)

def guide(path):
    img = scene("x", "SLOT GUIDE"); d = ImageDraw.Draw(img)
    for i in range(1, COLS * ROWS + 1):
        x, y = slot_rect(i); ax, ay = slot_anchor(i)
        d.rectangle([x, y, x + CELL_W - 1, y + CELL_H - 1], outline=(255,0,200))
        draw_text(d, x + 2, y + 2, str(i), (255,255,255))
        d.line([(ax - 2, ay), (ax + 2, ay)], fill=(255,255,0)); d.line([(ax, ay - 2), (ax, ay + 2)], fill=(255,255,0))
        if i in INITIAL_ACTIVE:
            d.rectangle([ax - 16, ay - 32, ax + 15, ay - 1], outline=(0,255,255))   # 32x32 sprite box
    save(img, path)

if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    save(scene("x", "X GARDEN"), f"{out}/day0_x.png")
    save(scene("instagram", "INSTAGRAM GARDEN"), f"{out}/day0_instagram.png")
    save(scene("threads", "THREADS GARDEN"), f"{out}/day0_threads.png")
    guide(f"{out}/garden_layout_guide.png")
    layout = {
        "native_size": W, "scale": SCALE, "grid": {"cols": COLS, "rows": ROWS},
        "bed_rect": list(BED), "cell_size": [CELL_W, CELL_H],
        "slots": [{"id": i, "row": (i - 1) // COLS, "col": (i - 1) % COLS,
                   "cell_xy": list(slot_rect(i)), "anchor": list(slot_anchor(i))}
                  for i in range(1, COLS * ROWS + 1)],
        "initial_active": INITIAL_ACTIVE,
        "expansion_order": EXPANSION_ORDER,
        "draw_order": "row 0 -> row 2, left -> right (back to front). Large sprites last within their row",
        "sprite_rule": "sprite bottom-center = slot anchor. Normal 32x32, tall 32x48 (sunflower), large 48x48 (rafflesia, black-hole flower, mold) may overlap neighbours by up to 8px",
        "hud_y": HUD_Y,
    }
    json.dump(layout, open(f"{out}/garden_layout.json", "w"), ensure_ascii=False, indent=2)
