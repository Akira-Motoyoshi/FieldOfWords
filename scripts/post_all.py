#!/usr/bin/env python3
"""Multi-SNS poster: Bluesky (full auto) + Misskey (full auto).

Threads is posted separately through the official Muse connector
(approval card per post), so it is not handled here.

Credentials are read from environment variables only. Never hard-code
or commit them. Values are supplied at runtime from Muse's Secure Vault
connector layer / process environment.

  Bluesky : BSKY_HANDLE, BSKY_APP_PASSWORD   (app password, not the login password)
  Misskey : MISSKEY_TOKEN  (API access token for misskey.io, notes:create scope)

Usage:
  python3 post_all.py --file post.txt [--dry-run]
  python3 post_all.py --text "hello" [--only bluesky|misskey] [--dry-run]

Output: one JSON line per platform with status and the post URL (permalink).
Character limits are enforced per platform before posting:
  Bluesky 300 graphemes, Misskey 3000 chars (we cap at 500 to match Threads).
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone

import requests

CAP = 500  # keep every platform's copy identical and Threads-compatible


def truncate(text: str, limit: int) -> str:
    return text if len(text) <= limit else text[: limit - 1] + "…"


def post_bluesky(text: str, dry: bool) -> dict:
    handle = os.environ.get("BSKY_HANDLE", "")
    password = os.environ.get("BSKY_APP_PASSWORD", "")
    if dry:
        return {"platform": "bluesky", "status": "dry-run", "chars": len(text)}
    if not handle or not password:
        return {"platform": "bluesky", "status": "skipped", "reason": "BSKY_HANDLE/BSKY_APP_PASSWORD not set"}
    base = "https://bsky.social/xrpc"
    s = requests.Session()
    r = s.post(f"{base}/com.atproto.server.createSession",
               json={"identifier": handle, "password": password}, timeout=30)
    r.raise_for_status()
    sess = r.json()
    did, token = sess["did"], sess["accessJwt"]
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    record = {"$type": "app.bsky.feed.post", "text": truncate(text, 300),
              "createdAt": now, "langs": ["ja"]}
    r = s.post(f"{base}/com.atproto.repo.createRecord",
               headers={"Authorization": f"Bearer {token}"},
               json={"repo": did, "collection": "app.bsky.feed.post", "record": record},
               timeout=30)
    r.raise_for_status()
    uri = r.json()["uri"]  # at://did/app.bsky.feed.post/<rkey>
    rkey = uri.rsplit("/", 1)[-1]
    url = f"https://bsky.app/profile/{handle}/post/{rkey}"
    return {"platform": "bluesky", "status": "posted", "url": url}


def post_misskey(text: str, dry: bool) -> dict:
    token = os.environ.get("MISSKEY_TOKEN", "")
    if dry:
        return {"platform": "misskey", "status": "dry-run", "chars": len(text)}
    if not token:
        return {"platform": "misskey", "status": "skipped", "reason": "MISSKEY_TOKEN not set"}
    host = os.environ.get("MISSKEY_HOST", "sushi.ski")
    r = requests.post(f"https://{host}/api/notes/create",
                      json={"i": token, "text": truncate(text, CAP), "visibility": "public"},
                      timeout=30)
    r.raise_for_status()
    note = r.json()["createdNote"]
    url = f"https://{host}/notes/{note['id']}"
    return {"platform": "misskey", "status": "posted", "url": url}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--text", default="")
    ap.add_argument("--file", default="")
    ap.add_argument("--only", choices=["bluesky", "misskey"], default="")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    text = args.text
    if args.file:
        with open(args.file, encoding="utf-8") as f:
            text = f.read().strip()
    if not text:
        print(json.dumps({"error": "empty text"}))
        return 1
    text = truncate(text, CAP)

    results = []
    if args.only in ("", "bluesky"):
        try:
            results.append(post_bluesky(text, args.dry_run))
        except Exception as e:  # keep going: the other platform may still succeed
            results.append({"platform": "bluesky", "status": "error", "reason": str(e)[:200]})
    if args.only in ("", "misskey"):
        try:
            results.append(post_misskey(text, args.dry_run))
        except Exception as e:
            results.append({"platform": "misskey", "status": "error", "reason": str(e)[:200]})
    for res in results:
        print(json.dumps(res, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
