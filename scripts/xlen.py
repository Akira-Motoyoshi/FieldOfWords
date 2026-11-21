"""Approximate X (twitter-text v3) weighted length: CJK / fullwidth / emoji = 2, other = 1, URLs = 23."""
import re, unicodedata
URL = re.compile(r"https?://\S+")
def char_weight(ch):
    o = ord(ch)
    if (0x1100 <= o <= 0x11FF or 0x2E80 <= o <= 0xA4CF or 0xA960 <= o <= 0xA97F or 0xAC00 <= o <= 0xD7FF or
        0xF900 <= o <= 0xFAFF or 0xFE30 <= o <= 0xFE6F or 0xFF00 <= o <= 0xFF60 or 0xFFE0 <= o <= 0xFFE6 or
        0x20000 <= o <= 0x3FFFF): return 2
    if o >= 0x1F000 or 0x2600 <= o <= 0x27BF or o in (0xFE0F, 0x200D): return 2 if o not in (0xFE0F, 0x200D) else 0
    return 1
def xlen(text):
    n = 0; pos = 0
    for m in URL.finditer(text):
        n += sum(char_weight(c) for c in text[pos:m.start()]) + 23; pos = m.end()
    return n + sum(char_weight(c) for c in text[pos:])
if __name__ == "__main__":
    import sys
    t = open(sys.argv[1], encoding="utf-8").read().strip() if len(sys.argv) > 1 else sys.stdin.read().strip()
    print("chars:", len(t), "| X weighted:", xlen(t), "| limit 280")
