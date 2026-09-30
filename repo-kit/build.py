#!/usr/bin/env python3
"""repo-kit · build one repository's hero banner + README header block.

    python build.py <repo> [--out <dir>] [--no-write]

repos.toml is the only source of truth. Fetches live GitHub numbers when a token
is available, writes <out>/assets/banner.svg, and prints the README block that
belongs between the dwgx-banner markers. Stdlib only.
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

INK = "#0F131B"
PANEL = "#161C27"
LINE = "#2A3240"
TEXT = "#EBE4D8"
MUTED = "#A5AFBF"
SAKURA = "#D6A0AC"
GOLD = "#CEB27C"
CYAN = "#79C0FF"
GREEN = "#7EE787"
ACCENTS = {"sakura": SAKURA, "gold": GOLD, "cyan": CYAN, "green": GREEN}

W, H = 1200, 320
FONT = "ui-monospace,'Cascadia Mono',Consolas,'SF Mono',monospace"


def esc(value: object) -> str:
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


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


def star_history(owner: str, repo: str, token: str) -> list[int]:
    """Star counts sampled to at most 24 points, oldest first."""
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


def sparkline(points: list[int], x: float, y: float, w: float, h: float, color: str) -> str:
    if len(points) < 2:
        return (
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="3" '
            f'fill="none" stroke="{LINE}"/>'
        )
    lo, hi = min(points), max(points)
    span = max(1, hi - lo)
    step = w / (len(points) - 1)
    coords = " ".join(
        f"{x + i * step:.1f},{y + h - (v - lo) / span * h:.1f}" for i, v in enumerate(points)
    )
    return (
        f'<polygon points="{x:.1f},{y + h:.1f} {coords} {x + w:.1f},{y + h:.1f}" '
        f'fill="{color}" fill-opacity="0.12"/>'
        f'<polyline points="{coords}" fill="none" stroke="{color}" stroke-width="2"/>'
    )


def banner(spec: dict, owner: str, meta: dict, history: list[int]) -> str:
    accent = ACCENTS.get(str(spec.get("accent") or "sakura"), SAKURA)
    name = str(spec.get("name") or "")
    tagline = str(spec.get("tagline") or "")
    install = str(spec.get("install") or "")
    stars = int(meta.get("stars") or 0)
    commits = int(meta.get("commits") or 0)
    pushed = str(meta.get("pushed") or "")

    parts: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" role="img" aria-label="{esc(name)} — {esc(tagline)}" '
        f'font-family="{FONT}">',
        f'<rect width="{W}" height="{H}" fill="{INK}"/>',
        f'<rect x="8" y="8" width="{W-16}" height="{H-16}" fill="none" stroke="{LINE}"/>',
        f'<rect x="12" y="12" width="{W-24}" height="{H-24}" fill="none" stroke="{PANEL}"/>',
        f'<text x="34" y="50" font-size="15" fill="{MUTED}">{esc(owner)}//{esc(name)}</text>',
        f'<line x1="34" y1="62" x2="{W-34}" y2="62" stroke="{LINE}"/>',
        f'<text x="34" y="118" font-size="46" font-weight="700" fill="{accent}">{esc(name)}</text>',
        f'<text x="34" y="152" font-size="17" fill="{TEXT}">{esc(tagline)}</text>',
    ]

    if install:
        box_w = min(780, 48 + len(install) * 9.0)
        parts += [
            f'<rect x="34" y="176" width="{box_w:.0f}" height="38" rx="4" '
            f'fill="{PANEL}" stroke="{LINE}"/>',
            f'<text x="50" y="201" font-size="14" fill="{accent}">$</text>',
            f'<text x="72" y="201" font-size="14" fill="{TEXT}">{esc(install)}</text>',
        ]

    topics = [str(t) for t in (spec.get("topics") or [])][:8]
    if topics:
        parts.append(
            f'<text x="34" y="244" font-size="13" fill="{MUTED}">'
            f'{"  ".join("#" + esc(t) for t in topics)}</text>'
        )

    bits = [
        str(spec.get("lang") or "-"),
        str(spec.get("license") or "-"),
        f"★{stars:,}" if stars else "",
        f"{commits:,} commits" if commits else "",
        pushed[:10] if pushed else "",
    ]
    parts += [
        f'<text x="{W-34}" y="50" text-anchor="end" font-size="13" fill="{MUTED}">'
        f'{"  ·  ".join(b for b in bits if b)}</text>',
        sparkline(history, W - 434, 96, 400, 92, accent),
        f'<text x="{W-34}" y="206" text-anchor="end" font-size="12" fill="{MUTED}">'
        f"star history</text>",
    ]

    x = 34.0
    for link in list(spec.get("links") or [])[:4]:
        label = str(link.get("label") or "")
        pill_w = 18 + len(label) * 9.6
        parts += [
            f'<rect x="{x:.0f}" y="{H-48}" width="{pill_w:.0f}" height="26" rx="13" '
            f'fill="{PANEL}" stroke="{LINE}"/>',
            f'<text x="{x + pill_w / 2:.0f}" y="{H-31}" text-anchor="middle" font-size="12" '
            f'fill="{TEXT}">{esc(label)}</text>',
        ]
        x += pill_w + 10

    parts.append("</svg>")
    return "".join(parts)


def readme_block(spec: dict, meta: dict) -> str:
    name = str(spec.get("name") or "")
    tagline = str(spec.get("tagline") or "")
    stars = int(meta.get("stars") or 0)
    meta_bits = " · ".join(
        b for b in (str(spec.get("lang") or "-"), str(spec.get("license") or "-")) if b != "-"
    )
    if stars:
        meta_bits += f" · ★{stars:,}"
    topics = " ".join(f"`{t}`" for t in (spec.get("topics") or [])[:6])
    badges = " ".join(
        f"[![{esc(l.get('label'))}]({esc(l.get('url'))})]({esc(l.get('url'))})"
        for l in (spec.get("links") or [])
    )
    return f"""<!-- dwgx-banner:BEGIN -->
<div align="center">

<img src="docs/assets/banner.svg" width="100%" alt="{name} — {tagline}" />

<br/>

{meta_bits} · {topics}

{badges}

</div>
<!-- dwgx-banner:END -->"""


def main() -> int:
    ap = argparse.ArgumentParser(description="build one repo banner")
    ap.add_argument("repo")
    ap.add_argument("--toml", default=str(Path(__file__).with_name("repos.toml")))
    ap.add_argument("--out", default=".")
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args()

    with open(args.toml, "rb") as fh:
        conf = tomllib.load(fh)
    owner = str(conf.get("owner") or "dwgx")
    spec = next((r for r in conf.get("repo") or [] if str(r.get("name")) == args.repo), None)
    if spec is None:
        print(f"no such repo in {args.toml}: {args.repo}", file=sys.stderr)
        return 2

    token = gh_token()
    meta: dict = {}
    history: list[int] = []
    if token:
        try:
            info = api_get(f"/repos/{owner}/{args.repo}", token)
            meta = {"stars": info.get("stargazers_count"), "pushed": info.get("pushed_at")}
            meta["commits"] = count_commits(owner, args.repo, token)
            history = star_history(owner, args.repo, token)
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError) as exc:
            print(f"live data unavailable ({exc}); drawing without it", file=sys.stderr)

    svg = banner(spec, owner, meta, history)
    if not args.no_write:
        target = Path(args.out) / "assets" / "banner.svg"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(svg, encoding="utf-8")
        print(f"wrote {target} ({len(svg.encode())} bytes)")
    print(readme_block(spec, meta))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())