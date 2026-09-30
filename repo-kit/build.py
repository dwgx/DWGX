#!/usr/bin/env python3
"""repo-kit · build a repository banner in its own style.

    python build.py <repo>                       # render into ./<repo>/assets
    python build.py <repo> --flat --inject       # render into ./assets and patch README.md
    python build.py <repo> --export DIR          # write a standalone repo-kit.toml
    python build.py x --all --preview --out DIR  # every repo plus a contact sheet

repos.toml is the only source of truth for the copy. Live GitHub numbers are
fetched when a token is available; without one the banner still renders with the
counters at zero. Stdlib only.
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
import styles_ink as INK  # noqa: E402

THEME = os.environ.get("REPO_KIT_THEME", "ink")
THEMES = {"ink": INK, "system": S}

BEGIN, END = "<!-- dwgx-banner:BEGIN -->", "<!-- dwgx-banner:END -->"


# --------------------------------------------------------------------- data


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
    """per_page=1 plus the Link header: rel="last" is the exact commit count."""
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
    return len(rows), str(rows[0].get("tag_name") or "")


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


# ------------------------------------------------------------------ context


def fmt(n: int) -> str:
    return f"{int(n):,}"


def build_ctx(spec: dict, meta: dict, history: list[int]) -> dict:
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
        "family": str(spec.get("family") or ""),
        "accent_role": str(spec.get("accent_role") or "gold"),
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
        max(1, min(9, round((stars if i == 0 else commits if i == 1 else releases + len(topics)) * 9 / total)))
        for i in range(len(stages))
    ]
    return ctx


# ------------------------------------------------------------------- output


def blob_bust(path: Path) -> str:
    """Git blob id of a file: a content hash we know before the commit exists.
    Used as the ?t= cache-buster so a refreshed banner is not served from camo."""
    import hashlib
    data = path.read_bytes()
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()[:12]


def readme_block(spec: dict, style: str, ctx: dict, bust: str = "") -> str:
    name = ctx["name"]
    meta_bits = " · ".join(b for b in (ctx["lang"], ctx["license"]) if b != "-")
    if ctx["stars"]:
        meta_bits += f" · ★{fmt(ctx['stars'])}"
    # plain links, not image syntax: ![docs](https://github.com/.../releases) renders
    # as a broken image because the target is a page, not a picture
    links = " · ".join(f"[{S.esc(l.get('label'))}]({S.esc(l.get('url'))})"
                       for l in ctx["links"])
    q = f"?t={bust}" if bust else ""
    if style in THEMES[THEME].DARK_ONLY:
        img = (f'<img src="docs/assets/banner.svg{q}" width="100%" '
               f'alt="{name} — {ctx["tagline"]}" />')
    else:
        img = (
            "<picture>\n"
            f'  <source media="(prefers-color-scheme: dark)" srcset="docs/assets/banner.svg{q}" />\n'
            f'  <source media="(prefers-color-scheme: light)" srcset="docs/assets/banner-light.svg{q}" />\n'
            f'  <img src="docs/assets/banner.svg{q}" width="100%" alt="{name} — {ctx["tagline"]}" />\n'
            "</picture>"
        )
    body = f"{meta_bits}\n\n{links}" if links else meta_bits
    return f"""{BEGIN}
<div align="center">

{img}

<br/>

{body}

</div>
{END}"""


def inject_readme(path: Path, block: str) -> bool:
    """Replace the block between the markers, else insert it under the H1."""
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8")
    if BEGIN in text and END in text:
        head, rest = text.split(BEGIN, 1)
        _, tail = rest.split(END, 1)
        new = f"{head}{block}{tail}"
    else:
        lines = text.split("\n")
        at = next((i + 1 for i, line in enumerate(lines[:6]) if line.startswith("# ")), 1)
        new = "\n".join(lines[:at] + ["", block, ""] + lines[at:])
    if new == text:
        return False
    path.write_text(new, encoding="utf-8")
    return True


def q(value: object) -> str:
    return '"' + str(value).replace('"', "'") + '"'


def export_spec(spec: dict, owner: str) -> str:
    """A single-repo repo-kit.toml so each repo can regenerate its own banner."""
    lines = [
        "# repo-kit · 本仓库的 banner 规格",
        "# 改这个文件，workflow 会重新渲染 docs/assets/banner*.svg 与 README 区块",
        "# 生成器：https://github.com/dwgx/DWGX/tree/main/repo-kit",
        f"owner = {q(owner)}",
        "",
        "[[repo]]",
        f"name = {q(spec['name'])}",
        f"style = {q(spec.get('style', 'pipe'))}",
        f"tagline = {q(spec.get('tagline', ''))}",
        f"install = {q(spec.get('install', ''))}",
        f"lang = {q(spec.get('lang', ''))}",
        f"license = {q(spec.get('license', 'none'))}",
    ]
    if spec.get("role"):
        lines.append(f"role = {q(spec['role'])}")
    for key in ("stages", "topics"):
        values = [str(v) for v in (spec.get(key) or [])]
        if values:
            lines.append(f"{key} = [{', '.join(q(v) for v in values)}]")
    for key in ("messages", "post_rows"):
        rows = spec.get(key) or []
        if rows:
            lines.append(f"{key} = ["
                         + ", ".join("[" + ", ".join(q(c) for c in row) + "]" for row in rows)
                         + "]")
    links = spec.get("links") or []
    if links:
        lines.append("links = ["
                     + ", ".join("{ label = %s, url = %s }" % (q(l.get("label", "")), q(l.get("url", "")))
                                 for l in links)
                     + "]")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description="build a repo banner in its own style")
    ap.add_argument("repo")
    ap.add_argument("--toml", default=str(Path(__file__).with_name("repos.toml")))
    ap.add_argument("--out", default=".")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--preview", action="store_true")
    ap.add_argument("--inject", action="store_true")
    ap.add_argument("--flat", action="store_true")
    ap.add_argument("--export")
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
        if style not in THEMES[THEME].STYLES:
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
        target = Path(args.out) if args.flat else Path(args.out) / str(spec["name"])
        if not args.no_write:
            assets = target / "docs" / "assets"
            assets.mkdir(parents=True, exist_ok=True)
            dark = THEMES[THEME].STYLES[style](ctx, False)
            (assets / "banner.svg").write_text(dark, encoding="utf-8")
            size = len(dark.encode())
            if style not in THEMES[THEME].DARK_ONLY:
                light = THEMES[THEME].STYLES[style](ctx, True)
                (assets / "banner-light.svg").write_text(light, encoding="utf-8")
                size += len(light.encode())
            print(f"{str(spec['name']):<24} {style:<7} {size:>7,} B")
        if args.inject and not args.no_write:
            changed = inject_readme(target / "README.md",
                                    readme_block(spec, style, ctx,
                                                 blob_bust(assets / "banner.svg")))
            print(f"{str(spec['name']):<24} README {'patched' if changed else 'already current'}")
        if args.export and not args.all:
            out = Path(args.export)
            out.mkdir(parents=True, exist_ok=True)
            (out / "repo-kit.toml").write_text(export_spec(spec, owner), encoding="utf-8")
            print(f"{str(spec['name']):<24} spec -> {out / 'repo-kit.toml'}")
        cards.append(
            f'<figure><figcaption>{S.esc(spec["name"])} · {style}</figcaption>'
            f'<img src="{S.esc(str(spec["name"]))}/docs/assets/banner.svg" width="100%"></figure>'
        )

    if args.preview and not args.no_write:
        page = (
            "<!doctype html><meta charset=utf-8><title>repo-kit preview</title>"
            "<style>body{background:#010409;color:#8b949e;font:13px ui-monospace,monospace;"
            "margin:0;padding:24px}figure{margin:0 0 28px}figcaption{padding:6px 0}</style>"
            + "".join(cards)
        )
        Path(args.out, "preview.html").write_text(page, encoding="utf-8")
        print(f"preview -> {Path(args.out, 'preview.html')}")

    if not args.all and not args.inject and not args.export:
        print(readme_block(specs[0], str(specs[0].get("style") or "pipe"),
                           build_ctx(specs[0], {}, [])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())