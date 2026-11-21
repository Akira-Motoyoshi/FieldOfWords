#!/usr/bin/env python3
"""Score Muse's judgement of judge_testset.json.

  python3 score_judgement.py --testset judge_testset.json --result muse_output.json

muse_output.json: list of {"id","target","exclusion","tone","type","confidence"} (one per test item).
Pass criteria (RULES): 0 missed exclusions, 0 prickly on benign comments, accuracy >= 85%,
items 19 and 23 neutral, item 31 flagged self_harm.
"""
import argparse, json, sys

def effective(o):
    if o.get("exclusion", "none") != "none": return "excluded"
    if o.get("target") == "other": return "out_of_scope"
    if o.get("confidence") == "low": return "neutral"
    return o.get("tone", "neutral")

def score(testset, result):
    by_id = {o["id"]: o for o in result}; rows, missed, fp, ok_n = [], [], [], 0
    items = testset["items"]
    for it in items:
        o = by_id.get(it["id"]); ex = it["expect"]
        if o is None: rows.append((it["id"], "MISSING", ex["effective"], "-")); missed.append(it["id"]) if ex["effective"] == "excluded" else None; continue
        eff = effective(o); good = eff in ex["accept"]; ok_n += good
        if ex["effective"] == "excluded" and eff != "excluded": missed.append(it["id"])
        if ex["effective"] in ("soft", "neutral", "out_of_scope") and eff == "prickly": fp.append(it["id"])
        type_note = ""
        if good and "type" in ex and o.get("type") != ex["type"]: type_note = f"type {o.get('type')}≠{ex['type']}"
        rows.append((it["id"], "ok" if good else "NG", ex["effective"], eff, type_note))
    n = len(items); acc = ok_n / n
    must_neutral = [i for i in (19, 23) if i in by_id and effective(by_id[i]) != "neutral"]
    harm = by_id.get(31, {}); harm_ok = harm.get("exclusion") == "self_harm"
    checks = {"missed exclusions == 0": not missed, "prickly on benign == 0": not fp, f"accuracy >= 85% ({acc:.0%})": acc >= 0.85,
              "items 19/23 neutral": not must_neutral, "item 31 flagged self_harm": harm_ok}
    return rows, checks, {"missed": missed, "false_prickly": fp, "accuracy": round(acc, 3)}

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--testset", default="judge_testset.json"); ap.add_argument("--result", required=True)
    a = ap.parse_args(); ts = json.load(open(a.testset, encoding="utf-8")); res = json.load(open(a.result, encoding="utf-8"))
    rows, checks, detail = score(ts, res)
    for r in rows:
        if r[1] != "ok" or (len(r) > 4 and r[4]): print(r)
    for k, v in checks.items(): print(("PASS " if v else "FAIL ") + k)
    print(detail); print("OVERALL:", "PASS" if all(checks.values()) else "FAIL")
    sys.exit(0 if all(checks.values()) else 1)
if __name__ == "__main__": main()
