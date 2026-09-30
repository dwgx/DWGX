#!/usr/bin/env python3
"""repo-kit · push a staging directory into a repository as one commit.

    python push_repo.py <repo> <staging-dir> [--dry-run]

Uses the Git Data API, not git transport: it reads the branch head, writes one
tree that replaces the staged paths, creates one commit and moves the ref. Six
HTTP calls per repository and nothing to clone.
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent))
from build import gh_token  # noqa: E402

API = "https://api.github.com"
PATHS = ("README.md", "repo-kit.toml", "docs/assets/banner.svg",
         "docs/assets/banner-light.svg", ".github/workflows/banner.yml")


def call(method: str, path: str, token: str, body: dict | None = None) -> object:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        f"{API}{path}",
        data=data,
        method=method,
        headers={
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
            "User-Agent": "dwgx-repo-kit",
            "Authorization": f"Bearer {token}",
        },
    )
    with urllib.request.urlopen(req, timeout=45) as resp:
        raw = resp.read().decode()
    return json.loads(raw) if raw else {}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("repo")
    ap.add_argument("staging")
    ap.add_argument("--owner", default="dwgx")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    token = gh_token()
    if not token:
        print("no token", file=sys.stderr)
        return 2
    stage = Path(args.staging)
    files = [p for p in PATHS if (stage / p).exists()]
    if not files:
        print(f"{args.repo}: nothing staged in {stage}", file=sys.stderr)
        return 2

    info = call("GET", f"/repos/{args.owner}/{args.repo}", token)
    branch = info.get("default_branch") or "main"
    ref = call("GET", f"/repos/{args.owner}/{args.repo}/git/ref/heads/{branch}", token)
    head = ((ref or {}).get("object") or {}).get("sha")
    if not head:
        print(f"{args.repo}: no branch {branch}", file=sys.stderr)
        return 2

    entries = [
        {
            "path": p,
            "mode": "100644",
            "type": "blob",
            "content": (stage / p).read_text(encoding="utf-8"),
        }
        for p in files
    ]
    sizes = {p: len(e["content"].encode()) for p, e in zip(files, entries)}
    print(f"{args.repo}: {len(files)} files -> {branch} " +
          ", ".join(f"{p.split('/')[-1]} {s:,}B" for p, s in sizes.items()))
    if args.dry_run:
        return 0

    tree = call("POST", f"/repos/{args.owner}/{args.repo}/git/trees",
                token, {"base_tree": head, "tree": entries})
    commit = call("POST", f"/repos/{args.owner}/{args.repo}/git/commits", token, {
        "message": "feat: repo-kit banner + regeneration workflow",
        "tree": tree.get("sha"),
        "parents": [head],
    })
    call("PATCH", f"/repos/{args.owner}/{args.repo}/git/refs/heads/{branch}", token,
         {"sha": commit.get("sha"), "force": False})
    print(f"{args.repo}: committed {commit.get('sha', '')[:8]} on {branch}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

