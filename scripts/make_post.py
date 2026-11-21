#!/usr/bin/env python3
"""Daily post text builder (Day 1+).

  python3 make_post.py --state garden/state.json --out posts_out

Per garden it writes <garden>.txt. X gets the compact version (<= 278 X-weighted chars, CJK = 2; margin of 2 under X's 280);
Instagram / Threads get the full version (<= 300 chars). Lines carry a priority; when the text is too
long the lowest-priority lines are dropped first. Never quotes a comment; only counts and kind names.
"""
import argparse, json, os
from xlen import xlen

MILESTONES = {"rainbow": 10, "butterfly": 20}      # TODO(undecided): lower values for Day 0-2?
CLOSING = "おはなでいっぱいにしてね!"
HASHTAG = "#ことばのかだん"                          # appended to every post (user instruction, reported by Muse 2026-11-21)
ORDER = ["x", "instagram", "threads"]              # fixed display order for ties
# X: Buffer measured Day 0 + hashtag at 297 where xlen.py says 296 -> keep a margin of 2 (278)
LIMITS = {"x": ("xw", 278), "instagram": ("chars", 300), "threads": ("chars", 300)}
NAMES = {"x": "X", "instagram": "Instagram", "threads": "Threads"}
POISON_NAME = {"rafflesia": "ラフレシア", "haetori": "ハエトリソウ", "saboten": "サボテン", "chili": "チリペッパー花", "blackhole": "ブラックホール花"}
POISON_KIND = {"rafflesia": "悪口", "haetori": "嫌味", "saboten": "批判", "chili": "煽り", "blackhole": "強いチクチク"}
PURIFIED_NAME = {"rafflesia": "金の薔薇", "haetori": "ひまわり", "saboten": "ピンクのサボテン", "chili": "ガーベラ", "blackhole": "星の花"}
GOOD_NAME = {"himawari": "ひまわり", "sakuraso": "さくら草", "tulip": "チューリップ", "kinbara": "金の薔薇", "nohana": "野の花"}
STAGE_RANK = {"sprout": 1, "stem": 2, "bud": 3, "bloom": 4}
POISON_CAP = 2

def stage_of(g):
    best = 0
    for p in g["plots"]:
        if p["kind"] == "good": best = max(best, STAGE_RANK.get(p.get("stage", "sprout"), 1))
        elif p["kind"] == "purified": best = max(best, 4)
    return best

def blooms_of(g):
    return sum(1 for p in g["plots"] if (p["kind"] == "good" and p.get("stage") == "bloom") or p["kind"] == "purified")

def ranking(gardens):
    """stage -> health -> blooms. Returns [(rank, [names])] with ties grouped (dense by group, number = position)."""
    keyed = sorted(gardens, key=lambda n: (-stage_of(gardens[n]), -gardens[n].get("health", 50), -blooms_of(gardens[n]), ORDER.index(n) if n in ORDER else 9))
    sig = lambda n: (stage_of(gardens[n]), gardens[n].get("health", 50), blooms_of(gardens[n]))
    groups, pos = [], 1
    for n in keyed:
        if groups and sig(groups[-1][1][0]) == sig(n): groups[-1][1].append(n)
        else: groups.append((pos, [n]))
        pos += 1
    return groups

def rank_line(gardens, compact):
    parts = [f"{r}位 " + "・".join(NAMES[n] for n in ns) for r, ns in ranking(gardens)]
    return "順位：" + (" / ".join(parts) if not compact else " ".join(parts))

def lines_for(name, g, gardens, day, compact):
    L = []   # (priority, text) ; lower number = more important
    plots = g["plots"]; ev = g.get("events_today", {})
    n_good = sum(1 for p in plots if p["kind"] in ("good", "purified")); n_bloom = blooms_of(g)
    poison = sorted([p for p in plots if p["kind"] == "poison"], key=lambda p: -p.get("age_days", 0))
    title = f"【ことばのかだん Day {day}】"
    L.append((0, title))
    own = f"{NAMES[name]}の庭：" + (f"花{n_good}輪" + (f"（開花{n_bloom}）" if n_bloom else "") if n_good else "まだ土だけ")
    if poison: own += ("／" if compact else "、") + f"毒花{len(poison)}輪"
    L.append((0, own))
    unavailable = g.get("unavailable_metrics", [])
    t = g.get("yesterday_tally", {})
    if "comment_text" in unavailable:
        L.append((2, "コメントの判定：この媒体では取得できません"))
    else:
        L.append((1, ("ふわふわ{soft}・チクチク{prickly}・中立{neutral}・集計外{excluded}" if not compact else "ふわふわ{soft}／チクチク{prickly}／中立{neutral}").format(
            soft=t.get("soft", 0), prickly=t.get("prickly", 0), neutral=t.get("neutral", 0), excluded=t.get("excluded", 0))))
    purified = ev.get("purified", [])
    new_poison = ev.get("new_poison") or [p["species"] for p in poison if p.get("age_days", 0) == 0]
    shown = poison[:POISON_CAP]
    if purified:
        L.append((1, "・".join(f"{POISON_NAME[s]}が{PURIFIED_NAME[s]}に変わりました" for s in purified[:2])))
    if new_poison:
        names = "・".join(f"{POISON_NAME[s]}（{POISON_KIND[s]}）" for s in new_poison[:POISON_CAP])
        L.append((1, f"{names}が咲きました" if compact else f"{names}が咲きました。"))
        if len(poison) > POISON_CAP: L.append((3, f"ほか{len(poison) - POISON_CAP}輪はナゾのカビ園に"))
    if poison and "comment_text" not in unavailable:     # no comment text -> kind words cannot be counted -> no promise
        k = max(1, 3 - g.get("purify_pool", 0) % 3)
        oldest = shown[0]["species"]
        L.append((2, f"あと{k}件のふわふわで{POISON_NAME[oldest]}が{PURIFIED_NAME[oldest]}に変わります"))
    if ev.get("bloomed"):
        L.append((3, "・".join(GOOD_NAME[s] for s in ev["bloomed"][:2]) + "が開花しました"))
    if "reposts" not in unavailable and g.get("totals", {}).get("reposts") is not None and not g.get("milestones", {}).get("rainbow"):
        left = MILESTONES["rainbow"] - g["totals"]["reposts"]
        if left > 0: L.append((4, f"リポスト{g['totals']['reposts']}件、虹まであと{left}件"))
    L.append((0, rank_line(gardens, compact)))
    L.append((1, CLOSING))
    L.append((0, HASHTAG))
    return L

def build(name, g, gardens, day):
    compact = name == "x"; unit, limit = LIMITS[name]
    measure = (lambda s: xlen(s)) if unit == "xw" else len
    L = lines_for(name, g, gardens, day, compact)
    while measure("\n".join(t for _, t in L)) > limit:
        cand = [i for i, (p, _) in enumerate(L) if p > 0]
        if not cand: break
        L.pop(max(cand, key=lambda i: (L[i][0], -i)))
    text = "\n".join(t for _, t in L)
    return text, measure(text), limit

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--state", required=True); ap.add_argument("--out", default="posts_out")
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    st = json.load(open(a.state, encoding="utf-8")); gardens = st["gardens"]; report = {}
    for name, g in gardens.items():
        text, n, limit = build(name, g, gardens, g.get("day", 0))
        open(f"{a.out}/{name}.txt", "w", encoding="utf-8").write(text + "\n")
        report[name] = {"length": n, "limit": limit, "ok": n <= limit}
        print(f"--- {name} ({n}/{limit}{'' if n <= limit else ' OVER'})\n{text}\n")
    json.dump(report, open(f"{a.out}/post_report.json", "w"), ensure_ascii=False, indent=2)
if __name__ == "__main__": main()
