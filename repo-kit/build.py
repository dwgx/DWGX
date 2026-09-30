#!/usr/bin/env python3
"""repo-kit · build a repository banner in its own style.

    python build.py <repo> [--out <dir>] [--preview] [--no-write]

repos.toml is the only source of truth for the copy. Live GitHub numbers are
fetched when a token is available; without one the banner still renders, just
with the counters at zero. Output: assets/banner.svg, plus assets/banner-light.svg
for the styles that ship a light variant, plus the README block to paste.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tomllib
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import styles as S  # noqa: E402


def gh_token() -> str:
    for name in ("GITHUB_TOKEN", "GH_TOKEN"):
        value = os.environ.get(name)
        if value:
            return value
    try:
        return subprocess.check_output(["gh", "auth", "token"], timeout=15).decode().strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def api_get(path: str, token: str, accept: str = "application/vnd.github+json") -> object:
    req = urllib.request.Request(
        f"https://api.github.com{path}",
        headers={
            "Accept": accept,
            "User-Agent": "dwgx-repo-kit",
            **({"Authorization": f"Bearer {token}"} if token else {}),
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def count_commits(owner: str, repo: str, token: str) -> int:
    req = urllib.request.Request(
        f"https://api.github.com/repos/{owner}/{repo}/commits?per_page=1",
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "dwgx-repo-kit",
            **({"Authorization": f"Bearer {token}"} if token else {}),
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        link = resp.headers.get("Link") or ""
    found = re.search(r'page=(\d+)>;\s*rel="last"', link)
    return int(found.group(1)) if found else 0


def latest_release(owner: str, repo: str, token: str) -> tuple[int, str]:
    try:
        rows = api_get(f"/repos/{owner}/{repo}/releases?per_page=100", token)
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError):
        return 0, ""
    if not isinstance(rows, list) or not rows:
        return 0, ""
    head = rows[0]
    return len(rows), str(head.get("tag_name") or "")


def star_history(owner: str, repo: str, token: str) -> list[int]:
    stamps: list[str] = []
    page = 1
    while page <= 200:
        batch = api_get(
            f"/repos/{owner}/{repo}/stargazers?per_page=100&page={page}",
            token,
            accept="application/vnd.github.star+json",
        )
        if not isinstance(batch, list) or not batch:
            break
        for row in batch:
            at = (row or {}).get("starred_at")
            if at:
                stamps.append(at)
        if len(batch) < 100:
            break
        page += 1
    if not stamps:
        return []
    stamps.sort()
    points = list(range(1, len(stamps) + 1))
    step = max(1, len(points) // 24)
    return points[::step][:24]


def fmt(n: int) -> str:
    return f"{int(n):,}"


def build_ctx(spec: dict, meta: dict, history: list[int]) -> dict:
    """Generic repo fields plus whatever the chosen style needs to plot."""
    topics = [str(t) for t in (spec.get("topics") or [])]
    lang = str(spec.get("lang") or "-")
    license_ = str(spec.get("license") or "-")
    stars = int(meta.get("stars") or 0)
    commits = int(meta.get("commits") or 0)
    releases = int(meta.get("releases") or 0)
    ctx = {
        "name": str(spec.get("name") or ""),
        "tagline": str(spec.get("tagline") or ""),
        "install": str(spec.get("install") or ""),
        "lang": lang,
        "license": license_,
        "topics": topics,
        "links": [dict(l) for l in (spec.get("links") or [])],
        "stars": stars,
        "commits": commits,
        "releases": releases,
        "stamp": str(meta.get("tag") or ""),
        "pushed": str(meta.get("pushed") or "1970-01-01T00:00:00Z"),
    }

    ctx["post_rows"] = spec.get("post_rows") or [
        [lang, "OK", True],
        [license_, "OK", True],
        *[[t, "OK", True] for t in topics[:4]],
        ["STARS", fmt(stars) if stars else "NP", bool(stars)],
        ["COMMITS", fmt(commits) if commits else "NP", bool(commits)],
    ]
    ctx["memory"] = max(1024, min(32768, commits * 64 or 4096))
    ctx["term_lines"] = [
        ["$ " + S.clip(ctx["install"] or "./run", 74), "#79C0FF", "700"],
        [f"# {S.clip(ctx['tagline'], 74)}", "#A5AFBF", "400"],
        [f"stars {fmt(stars)}   commits {fmt(commits)}   releases {releases}", "#CEB27C", "400"],
        [" ".join("#" + t for t in topics[:6]), "#A5AFBF", "400"],
        [f"{lang} · {license_} · last push {ctx['pushed'][:10]}", "#A5AFBF", "400"],
        ["ready.", "#D6A0AC", "400"],
    ]
    ctx["role"] = str(spec.get("role") or "SERVER")
    ctx["messages"] = spec.get("messages") or [
        [t, "request" if i % 2 == 0 else "reply"] for i, t in enumerate(topics[:5])
    ] or [[ctx["tagline"], "request"], ["response", "reply"]]
    ctx["children"] = topics[:6] or [lang, license_, "src", "docs", "tests", "build"]
    ctx["stats"] = [
        ["stars", fmt(stars) or "0"],
        ["commits", fmt(commits) or "0"],
        ["releases", str(releases)],
        ["lang", lang],
    ]
    hero_h = min(140, 40 + commits // 9) if commits else 32
    side_h = min(120, 24 + int(stars * 0.8)) if stars else 32
    ctx["blocks"] = [
        (660, hero_h, True), (740, side_h, False), (820, hero_h, False),
        (900, side_h, False), (980, hero_h, False), (1060, side_h, False),
        (1140, hero_h, False),
    ]
    ctx["trace"] = history
    stages = spec.get("stages") or topics[:5] or ["ingest", "route", "adapt", "serve", "log"]
    ctx["stages"] = stages
    total = max(1, stars + commits + releases)
    ctx["stage_progress"] = [
        max(1, min(9, round((stars if i == 0 else commits if i == 1 else releases + topics.__len__()) * 9 / total)))
        for i in range(len(stages))
    ]
    return ctx


def render(style: str, ctx: dict, light: bool) -> str:
    return S.STYLES[style](ctx, light)


def readme_block(spec: dict, style: str, ctx: dict) -> str:
    name = ctx["name"]
    meta_bits = " · ".join(b for b in (ctx["lang"], ctx["license"]) if b != "-")
    if ctx["stars"]:
        meta_bits += f" · ★{fmt(ctx['stars'])}"
    badges = " ".join(
        f"[![{S.esc(l.get('label'))}]({S.esc(l.get('url'))})]({S.esc(l.get('url'))})"
        for l in ctx["links"]
    )
    if style in S.DARK_ONLY:
        img = f'<img src="docs/assets/banner.svg" width="100%" alt="{name} — {ctx["tagline"]}" />'
    else:
        img = (
            "<picture>\n"
            '  <source media="(prefers-color-scheme: dark)" srcset="docs/assets/banner.svg" />\n'
            '  <source media="(prefers-color-scheme: light)" srcset="docs/assets/banner-light.svg" />\n'
            f'  <img src="docs/assets/banner.svg" width="100%" alt="{name} — {ctx["tagline"]}" />\n'
            "</picture>"
        )
    body = f"{meta_bits}\n\n{badges}" if badges else meta_bits
    return f"""<!-- dwgx-banner:BEGIN -->
<div align="center">

{img}

<br/>

{body}

</div>
<!-- dwgx-banner:END -->"""


def main() -> int:
    ap = argparse.ArgumentParser(description="build one repo banner in its own style")
    ap.add_argument("repo")
    ap.add_argument("--toml", default=str(Path(__file__).with_name("repos.toml")))
    ap.add_argument("--out", default=".")
    ap.add_argument("--all", action="store_true", help="build every repo in the toml")
    ap.add_argument("--preview", action="store_true", help="also write preview.html")
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args()

    with open(args.toml, "rb") as fh:
        conf = tomllib.load(fh)
    owner = str(conf.get("owner") or "dwgx")
    all_specs = [r for r in (conf.get("repo") or [])]
    specs = all_specs if args.all else [r for r in all_specs if str(r.get("name")) == args.repo]
    if not specs:
        print(f"no such repo in {args.toml}: {args.repo}", file=sys.stderr)
        return 2

    token = gh_token()
    cards: list[str] = []
    for spec in specs:
        style = str(spec.get("style") or "pipe")
        if style not in S.STYLES:
            print(f"{spec.get('name')}: unknown style {style!r}", file=sys.stderr)
            return 2
        meta: dict = {}
        history: list[int] = []
        if token:
            try:
                info = api_get(f"/repos/{owner}/{spec['name']}", token)
                meta = {"stars": info.get("stargazers_count"), "pushed": info.get("pushed_at")}
                meta["commits"] = count_commits(owner, str(spec["name"]), token)
                meta["releases"], meta["tag"] = latest_release(owner, str(spec["name"]), token)
                history = star_history(owner, str(spec["name"]), token)
            except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError) as exc:
                print(f"{spec['name']}: live data unavailable ({exc})", file=sys.stderr)
        ctx = build_ctx(spec, meta, history)
        dark = render(style, ctx, False)
        target_dir = Path(args.out) / str(spec["name"])
        if not args.no_write:
            (target_dir / "assets").mkdir(parents=True, exist_ok=True)
            (target_dir / "assets" / "banner.svg").write_text(dark, encoding="utf-8")
            size = len(dark.encode())
            if style not in S.DARK_ONLY:
                light_svg = render(style, ctx, True)
                (target_dir / "assets" / "banner-light.svg").write_text(light_svg, encoding="utf-8")
                size += len(light_svg.encode())
            print(f"{spec['name']:<24} {style:<7} {size:>7,} B  -> {target_dir}")
        cards.append(
            f'<figure><figcaption>{S.esc(spec["name"])} · {style}</figcaption>'
            f'<img src="{S.esc(str(spec["name"]))}/assets/banner.svg" width="100%"></figure>'
        )

    if args.preview and not args.no_write:
        page = (
            "<!doctype html><meta charset=utf-8><title>repo-kit preview</title>"
            "<style>body{background:#010409;color:#8b949e;font:13px ui-monospace,monospace;"
            "margin:0;padding:24px}figure{margin:0 0 28px}figcaption{padding:6px 0}</style>"
            + "".join(cards)
        )
        Path(args.out, "preview.html").write_text(page, encoding="utf-8")
        print(f"preview: {Path(args.out, 'preview.html')}")

    if not args.all:
        print(readme_block(specs[0], str(specs[0].get("style") or "pipe"),
                           build_ctx(specs[0], {}, [])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())