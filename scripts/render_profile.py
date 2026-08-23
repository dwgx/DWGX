#!/usr/bin/env python3
"""Render dwgx.menu README + process-table.svg from profile.toml + GitHub."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tomllib
import unicodedata
import urllib.error
import urllib.request
import xml.sax.saxutils
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

JST = timezone(timedelta(hours=9))


def today_jst() -> date:
    return datetime.now(JST).date()

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "profile.toml"
README = ROOT / "README.md"
SVG = ROOT / "assets" / "process-table.svg"
API = "https://api.github.com"

PINK = "#f2a6c4"
GOLD = "#c9a84c"
TEXT = "#e6edf3"
MUTED = "#8b949e"
BLUE = "#79c0ff"
GREEN = "#7ee787"


def load_profile() -> dict:
    with PROFILE.open("rb") as f:
        return tomllib.load(f)


def gh_token() -> str:
    env = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or ""
    if env:
        return env
    try:
        out = subprocess.check_output(
            ["gh", "auth", "token"],
            text=True,
            stderr=subprocess.DEVNULL,
            timeout=15,
        )
        return out.strip()
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return ""


def api_get(path: str, token: str, params: str = "") -> object:
    url = f"{API}{path}"
    if params:
        url = f"{url}?{params}"
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "dwgx-profile-render",
            **({"Authorization": f"Bearer {token}"} if token else {}),
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_user(login: str, token: str) -> dict:
    return api_get(f"/users/{login}", token)  # type: ignore[return-value]


def fetch_repos(login: str, token: str) -> list[dict]:
    repos: list[dict] = []
    for page in range(1, 6):
        batch = api_get(
            f"/users/{login}/repos",
            token,
            f"per_page=100&page={page}&sort=updated",
        )
        if not isinstance(batch, list) or not batch:
            break
        repos.extend(batch)
        if len(batch) < 100:
            break
    return repos


def fetch_events(login: str, token: str) -> list[dict]:
    try:
        data = api_get(f"/users/{login}/events/public", token, "per_page=100")
        return data if isinstance(data, list) else []
    except urllib.error.URLError:
        return []


def fetch_latest_tag(full_name: str, token: str) -> str:
    try:
        data = api_get(f"/repos/{full_name}/releases/latest", token)
        if isinstance(data, dict):
            return str(data.get("tag_name") or "")
    except urllib.error.HTTPError:
        return ""
    return ""


def uptime_days(born: str, today: date | None = None) -> int:
    y, m, d = (int(x) for x in born.split("-"))
    return ((today or today_jst()) - date(y, m, d)).days


def repo_index(repos: list[dict]) -> dict[str, dict]:
    return {r["name"]: r for r in repos}


def total_stars(repos: list[dict]) -> int:
    return sum(int(r.get("stargazers_count") or 0) for r in repos)


def lang_short(name: str | None) -> str:
    if not name:
        return "-"
    table = {
        "JavaScript": "js",
        "TypeScript": "ts",
        "Python": "py",
        "Rust": "rust",
        "C++": "cpp",
        "C#": "c#",
        "C": "c",
        "Go": "go",
        "Java": "java",
        "Swift": "swift",
        "Shell": "sh",
        "HTML": "html",
        "Assembly": "asm",
        "PowerShell": "ps",
        "Astro": "astro",
    }
    return table.get(name, name.lower()[:6])


def fmt_recent_line(day: str, verb: str, name: str, repo: dict) -> str:
    stars = int(repo.get("stargazers_count") or 0)
    lang = lang_short(repo.get("language"))
    desc = (repo.get("description") or "").replace("\n", " ").strip()
    if len(desc) > 42:
        desc = desc[:41] + "…"
    return f" {day} --:--   {verb}  {name:<22} {f'★{stars}':<6} {lang:<6} {desc}"


def recent_log(events: list[dict], repos: dict[str, dict], limit: int = 10) -> str:
    seen: set[str] = set()
    lines: list[str] = []
    for ev in events:
        kind = ev.get("type")
        repo_full = (ev.get("repo") or {}).get("name") or ""
        name = repo_full.split("/", 1)[-1]
        if not name or name in seen or name.lower() in {"dwgx"}:
            continue
        if kind not in {"PushEvent", "ReleaseEvent", "CreateEvent"}:
            continue
        if kind == "CreateEvent" and (ev.get("payload") or {}).get("ref_type") not in {
            "tag",
            "repository",
        }:
            continue
        r = repos.get(name)
        if not r:
            continue
        seen.add(name)
        created = str(ev.get("created_at") or "")[:10] or "----------"
        verb = "push"
        if kind == "ReleaseEvent":
            verb = "rel "
        elif kind == "CreateEvent":
            verb = "tag "
        lines.append(fmt_recent_line(created, verb, name, r))
        if len(lines) >= limit:
            break
    if len(lines) < limit:
        extra = sorted(
            repos.values(),
            key=lambda r: str(r.get("pushed_at") or ""),
            reverse=True,
        )
        for r in extra:
            name = r.get("name") or ""
            if not name or name in seen or r.get("fork") or name.lower() in {"dwgx"}:
                continue
            seen.add(name)
            day = str(r.get("pushed_at") or "")[:10] or "----------"
            lines.append(fmt_recent_line(day, "push", name, r))
            if len(lines) >= limit:
                break
    return "\n".join(lines) if lines else " (no public events)"


def esc(s: str) -> str:
    return xml.sax.saxutils.escape(s)


def text_w(s: str, bold: bool = False) -> float:
    return round(len(s) * (8.7 if bold else 7.8), 1)


def process_svg(profile: dict, repos: dict[str, dict], tags: dict[str, str]) -> str:
    rows = profile.get("process") or []
    n = len(rows)
    row_h = 22
    header_h = 26
    col_y = 48
    first_y = 72
    height = first_y + (n - 1) * row_h + 34
    width = 617
    parts: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" '
        f"font-family=\"ui-monospace,'Cascadia Mono',Consolas,'SF Mono',monospace\">",
        f'<rect width="{width}" height="{height}" rx="4" fill="#0d1117" stroke="#30363d" stroke-width="1"/>',
        f'<rect x="1" y="1" width="{width-2}" height="{header_h}" rx="3" fill="#161b22"/>',
        '<line x1="0" y1="26" x2="617" y2="26" stroke="#30363d" stroke-width="1"/>',
        f'<text x="16.0" y="18.0" font-size="13" font-weight="700" fill="{PINK}">dwgx@kobe</text>',
        f'<text x="109.6" y="18.0" font-size="13" font-weight="700" fill="{TEXT}">process.table</text>',
        f'<text x="234.4" y="18.0" font-size="13" font-weight="400" fill="{MUTED}">[{n} tasks]</text>',
        f'<text x="476.2" y="18.0" font-size="13" font-weight="400" fill="{GREEN}">active · JST+9</text>',
        f'<text x="16.0" y="{col_y}.0" font-size="13" font-weight="700" fill="{MUTED}">PID</text>',
        f'<text x="62.8" y="{col_y}.0" font-size="13" font-weight="700" fill="{MUTED}">MODULE</text>',
        f'<text x="250.0" y="{col_y}.0" font-size="13" font-weight="700" fill="{MUTED}">LANG</text>',
        f'<text x="296.8" y="{col_y}.0" font-size="13" font-weight="700" fill="{MUTED}">STATUS</text>',
        '<line x1="16" y1="54" x2="601" y2="54" stroke="#30363d" stroke-width="1"/>',
    ]
    for i, row in enumerate(rows):
        y = first_y + i * row_h
        if i % 2 == 1:
            parts.append(
                f'<rect x="1" y="{y-15}" width="{width-2}" height="{row_h}" fill="#161b22" fill-opacity="0.5"/>'
            )
        pid = f"{i+1:04d}"
        name = str(row.get("name") or "")
        lang = str(row.get("lang") or "-")
        status = str(row.get("status") or "")
        status_color = str(row.get("status_color") or GOLD)
        r = repos.get(name, {})
        note = str(row.get("note") or row.get("fallback_note") or "")
        kind = row.get("note_kind") or row.get("kind")
        if kind == "stars":
            stars = int(r.get("stargazers_count") or 0)
            note = f"★{stars}"
        elif kind == "release":
            tag = tags.get(name) or ""
            note = tag if tag else str(row.get("fallback_note") or "")
        parts.append(
            f'<text x="16.0" y="{y}.0" font-size="13" font-weight="700" fill="{GOLD}">{esc(pid)}</text>'
        )
        parts.append(
            f'<text x="62.8" y="{y}.0" font-size="13" font-weight="400" fill="{TEXT}">{esc(name)}</text>'
        )
        parts.append(
            f'<text x="250.0" y="{y}.0" font-size="13" font-weight="400" fill="{BLUE}">{esc(lang)}</text>'
        )
        if kind == "bar":
            bar = float(row.get("bar") or 0)
            bw = 100.0
            fw = round(bw * max(0.0, min(1.0, bar)), 1)
            pct = f"{int(round(bar * 100))}%"
            parts.append(
                f'<rect x="296.8" y="{y-8}.0" width="{bw}" height="10" rx="3" fill="#30363d"/>'
            )
            parts.append(
                f'<rect x="296.8" y="{y-8}.0" width="{fw}" height="10" rx="3" fill="{PINK}"/>'
            )
            parts.append(
                f'<text x="404.8" y="{y}.0" font-size="13" font-weight="700" fill="{GOLD}">{esc(pct)}</text>'
            )
            parts.append(
                f'<text x="432.2" y="{y}.0" font-size="13" font-weight="400" fill="{MUTED}">{esc(note)}</text>'
            )
        else:
            parts.append(
                f'<text x="296.8" y="{y}.0" font-size="13" font-weight="700" fill="{status_color}">{esc(status)}</text>'
            )
            nx = round(296.8 + text_w(status, bold=True) + 8.0, 1)
            if note:
                parts.append(
                    f'<text x="{nx}" y="{y}.0" font-size="13" font-weight="400" fill="{MUTED}">{esc(note)}</text>'
                )
    parts.append("</svg>")
    return "".join(parts)


def disp_len(text: str) -> int:
    n = 0
    for ch in text:
        n += 2 if unicodedata.east_asian_width(ch) in {"F", "W"} else 1
    return n


def pad_body(text: str, width: int = 46) -> str:
    out = []
    w = 0
    for ch in text:
        cw = 2 if unicodedata.east_asian_width(ch) in {"F", "W"} else 1
        if w + cw > width:
            break
        out.append(ch)
        w += cw
    return "".join(out) + (" " * (width - w))


def label_prefix(name: str) -> str:
    # 16 visible chars ending with ╡ then two spaces in the caller.
    room = 14  # " NAME " + bars, then ╡
    core = f" {name} "
    bars = "═" * max(1, room - len(core))
    s = core + bars + "╡"
    if len(s) < 16:
        s = core + ("═" * (15 - len(core))) + "╡"
    return s[:16]


def hardware_dump(profile: dict, days: int) -> str:
    hw = profile["hardware"]
    lines: list[str] = []
    header = str(hw.get("header") or "dwgx@kobe")
    core = f"─── {header} "
    top = "╭" + core + ("─" * max(1, 48 - len(core))) + "╮"
    empty = "│  " + pad_body("") + "│"
    lines.append("               " + top)
    lines.append("               " + empty)

    def emit(label: str | None, body_lines: list[str]) -> None:
        for i, body in enumerate(body_lines):
            if i == 0 and label:
                prefix = label_prefix(label)
                lines.append(f"{prefix}  {pad_body(body)}│")
            else:
                lines.append("               │  " + pad_body(body) + "│")
        lines.append("               " + empty)

    emit("ROG Strix", list(hw["rog"]))
    emit("Homecloud", list(hw["homecloud"]))
    emit("MacBook", list(hw["macbook"]))
    emit("Mobile", list(hw["mobile"]))
    comment = hw.get("mobile_comment")
    if comment:
        lines.insert(-1, "               │  " + pad_body("; " + comment) + "│")
    emit("Peripheral", list(hw["peripheral"]))
    lines.append("               │  " + pad_body(f"uptime     {days} days") + "│")
    lines.append("               │  " + pad_body("status     online · JST+9") + "│")
    bot = "╰" + ("─" * (disp_len(top) - 2)) + "╯"
    lines.append("               " + bot)
    return "\n".join(lines)


def pin_box(pin: dict, repos: dict[str, dict]) -> str:
    name = str(pin["name"])
    r = repos.get(name, {})
    stars = int(r.get("stargazers_count") or 0)
    blurb = str(pin.get("blurb") or "")
    lang = str(pin.get("lang") or "")
    stage = str(pin.get("stage") or "")
    if pin.get("star_in_stage"):
        stage = f"{stage} ★{stars}"
    diff = str(pin.get("diff") or "")
    inner_w = 24
    def box_line(s: str) -> str:
        s = s[:inner_w]
        return "║  " + s.ljust(inner_w) + "║"
    body = [
        "╔" + "═" * (inner_w + 2) + "╗",
        "║ " + name.ljust(inner_w + 1) + "║",
        "╠" + "═" * (inner_w + 2) + "╣",
        box_line(""),
    ]
    for raw in blurb.split("\n"):
        body.append(box_line(raw))
    body.append(box_line(""))
    body.append(box_line(f"lang  · {lang}"))
    body.append(box_line(f"stage · {stage}"))
    body.append(box_line(f"diff  · {diff}"))
    body.append("╚" + "═" * (inner_w + 2) + "╝")
    return "```\n" + "\n".join(body) + "\n```"


def pinned_table(profile: dict, repos: dict[str, dict], public_count: int, stars: int) -> str:
    pins = list(profile.get("pin") or [])
    cells: list[str] = []
    for pin in pins[:5]:
        name = pin["name"]
        box = pin_box(pin, repos)
        cells.append(
            f'<td width="33%" valign="top">\n\n{box}\n\n'
            f'[open module →](https://github.com/dwgx/{name})\n\n</td>'
        )
    more = max(0, public_count - 5)
    more_box = pin_box(
        {
            "name": f"+ {more} more modules",
            "blurb": f"{public_count} public repos\n{stars} total stars\nsolo crew · kobe",
            "lang": "polyglot",
            "stage": "shipping",
            "diff": "★★★★★",
        },
        {},
    )
    cells.append(
        f'<td width="33%" valign="top">\n\n{more_box}\n\n'
        f"[browse all →](https://github.com/dwgx?tab=repositories)\n\n</td>"
    )
    # 2 rows of 3
    row1 = "<tr>\n" + "\n".join(cells[:3]) + "\n</tr>"
    row2 = "<tr>\n" + "\n".join(cells[3:6]) + "\n</tr>"
    return "<table>\n" + row1 + "\n" + row2 + "\n</table>"


def shield_stars(n: int) -> str:
    if n >= 1000:
        return f"{n/1000:.1f}k".replace(".0k", "k")
    return str(n)


def render_readme(profile: dict, ctx: dict) -> str:
    ident = profile["identity"]
    links = profile["links"]
    today = ctx["today"]
    n = ctx["process_count"]
    more = max(0, ctx["public_repos"] - 5)
    windsurf_stars = ctx["stars_map"].get("WindsurfAPI", 0)
    now = (profile.get("now") or {}).get("line") or ""
    now = now.format(
        windsurf_tag=ctx["tags"].get("WindsurfAPI") or "v?",
        kiro_tag=ctx["tags"].get("KiroStudio") or "v?",
        vrcsm_tag=ctx["tags"].get("VRCSM") or "v?",
    )
    return f"""<!-- ════════════════════════════════════════════════════════════════ -->
<!--  dwgx.menu  v{profile.get('version','2.2')}  ·  generated {today} JST          -->
<!--  source: profile.toml  ·  renderer: scripts/render_profile.py     -->
<!-- ════════════════════════════════════════════════════════════════ -->

<img src="https://raw.githubusercontent.com/dwgx/DWGX/main/assets/bios-header.svg" width="100%" alt="dwgx.menu · AMIBIOS POST" />

<div align="center">

<img src="{links['qq_avatar']}" width="128" style="border-radius:50%;" />

<br/>

[![Typing SVG](https://readme-typing-svg.demolab.com?font=Noto+Serif+JP&weight=600&size=22&pause=1200&color=F2A6C4&center=true&vCenter=true&random=false&width=620&lines=injected+into+process+%C2%B7+host%3Dkobe;JavaScript+%C2%B7+Rust+%C2%B7+C%2B%2B+%C2%B7+C%23+%C2%B7+Swift+%C2%B7+TypeScript;Reverse+Engineering+%C2%B7+Game+Hacking+%C2%B7+Systems)](https://dwgx.github.io)

<p>
  <img src="https://komarev.com/ghpvc/?username=dwgx&style=flat-square&color=f2a6c4&label=visits" />
  &nbsp;
  <img src="https://img.shields.io/github/followers/dwgx?style=flat-square&color=f2a6c4&label=follow" />
  &nbsp;
  <img src="https://img.shields.io/github/stars/dwgx?style=flat-square&color=c9a84c&label=stars" />
</p>

<p>
  <img src="https://img.shields.io/badge/total_stars-{ctx['total_stars']}-c9a84c?style=flat-square&labelColor=06020f" />
  &nbsp;
  <img src="https://img.shields.io/badge/public_repos-{ctx['public_repos']}-f2a6c4?style=flat-square&labelColor=06020f" />
  &nbsp;
  <img src="https://img.shields.io/github/stars/dwgx/WindsurfAPI?style=flat-square&color=2d1b69&label=flagship%20WindsurfAPI" />
</p>

<p><code>now</code> · {now}</p>

</div>

---

### `main.cfg`

```ini
; dwgx.cfg  —  last modified {today} JST
; injection status: active  ·  process.count: {n}

[identity]
alias      = {ident['alias']}
location   = {ident['location']}
motto      = {ident['motto']}
bio        = {ident['bio']}

[role]
primary    = {ident['role']}
origin     = {ident['origin']}
focus      = {ident['focus']}
anti-focus = {ident['anti_focus']}

[languages]
flagship   = {ident['languages_flagship']}
active     = {ident['languages_active']}
previous   = {ident['languages_previous']}
```

---

### `process.table`

<div align="center">

<img src="https://raw.githubusercontent.com/dwgx/DWGX/main/assets/process-table.svg" width="88%" alt="process.table" />

</div>

---

<div align="center">

### `pinned`

{ctx['pinned_table']}

</div>

---

### `recent.log`

```
{ctx['recent']}
```

---

### `hardware.dmp`

```
{ctx['hardware']}
```

---

<div align="center">

### `discord.presence`

<a href="{links['discord']}">
  <img src="{links['lanyard']}" alt="discord presence" />
</a>

---

### `featured`

## 幻想万華鏡 ~ The Memories of Phantasm

<img src="assets/gensou.gif" width="640" />

<br/>

<sub>滿福神社製作  ·  全18話  ·  BDRip  ·  東方Project 二次創作</sub>

<br/><br/>

<img src="https://img.shields.io/badge/東方Project-二次創作-f2a6c4?style=flat-square&labelColor=06020f" />
<img src="https://img.shields.io/badge/滿福神社-Studio-c9a84c?style=flat-square&labelColor=06020f" />
<img src="https://img.shields.io/badge/Episodes-18-d4c8ef?style=flat-square&labelColor=06020f" />
<img src="https://img.shields.io/badge/Format-BDRip-2d1b69?style=flat-square&labelColor=06020f" />

</div>

---

<!-- ════════════════════════════════════════════════════════════════ -->
<!--  style switch: scene-nfo release note                            -->
<!-- ════════════════════════════════════════════════════════════════ -->

. d w g x . p r e s e n t s .

dwgx.menu · v{profile.get('version','2.2')} · 2026  
scene release // kobe, jp // solo crew

**group** — dwgx  
**location** — kobe · jp · jst+9  
**release** — personal-profile.v{profile.get('version','2.2')}  
**files** — profile.toml + renderer + bios assets  
**target** — github.com/dwgx  
**born** — 20100705  
**date** — {today.replace('-', '.')}  
**now** — {now}

<div align="center">

### `━─·  [ stack.manifest ]  ·─━`

<img src="https://raw.githubusercontent.com/dwgx/DWGX/main/assets/stack.svg" width="92%" alt="stack.manifest" />

</div>

. s h o u t o u t s .

to every anon who kept pushing commits with zero stars and zero watchers  
to every kid who built something just to see if it could be done

— dwgx, kobe

---

### `achievements`

<div align="center">

<img src="https://img.shields.io/badge/★-Solo_Crew-f2a6c4?style=for-the-badge&labelColor=06020f" />
<img src="https://img.shields.io/badge/★-IL2CPP_Diver-c9a84c?style=for-the-badge&labelColor=06020f" />
<img src="https://img.shields.io/badge/★-Starstruck_x3-ed8b00?style=for-the-badge&labelColor=06020f" />
<img src="https://img.shields.io/badge/★-Pull_Shark_x3-3178c6?style=for-the-badge&labelColor=06020f" />
<img src="https://img.shields.io/badge/★-Pair_Extraordinaire_x4-f778ba?style=for-the-badge&labelColor=06020f" />

<br/>

<img src="https://img.shields.io/badge/★-Galaxy_Brain-6f42c1?style=for-the-badge&labelColor=06020f" />
<img src="https://img.shields.io/badge/★-Public_Sponsor-ea4aaa?style=for-the-badge&labelColor=06020f" />
<img src="https://img.shields.io/badge/★-Quickdraw-d01c1f?style=for-the-badge&labelColor=06020f" />
<img src="https://img.shields.io/badge/★-YOLO-ededed?style=for-the-badge&labelColor=06020f" />
<img src="https://img.shields.io/badge/★-{ctx['uptime']}_Days_Uptime-8a7aaa?style=for-the-badge&labelColor=06020f" />

<br/>

<img src="https://img.shields.io/badge/★-Cheat_Scene_Alumnus-2d1b69?style=for-the-badge&labelColor=06020f" />
<img src="https://img.shields.io/badge/★-Flipper_Hacker-ff8300?style=for-the-badge&labelColor=06020f" />
<img src="https://img.shields.io/badge/★-Paper_Plugin_Dev-6db33f?style=for-the-badge&labelColor=06020f" />
<img src="https://img.shields.io/badge/★-Live2D_Pet_Maker-ff66aa?style=for-the-badge&labelColor=06020f" />
<img src="https://img.shields.io/badge/★-Flagship_{shield_stars(windsurf_stars)}-2d1b69?style=for-the-badge&labelColor=06020f" />

</div>

---

### `3d.contrib`

<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/dwgx/DWGX/main/profile-3d-contrib/profile-night-rainbow.svg" />
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/dwgx/DWGX/main/profile-3d-contrib/profile-season.svg" />
  <img src="https://raw.githubusercontent.com/dwgx/DWGX/main/profile-3d-contrib/profile-season.svg" width="100%" alt="3d contribution" />
</picture>

</div>

---

### `stats`

<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://github-readme-stats-sigma-five.vercel.app/api?username=dwgx&show_icons=true&hide_border=true&bg_color=06020f&title_color=f2a6c4&icon_color=c9a84c&text_color=d4c8ef&ring_color=f2a6c4" />
  <img height="170" src="https://github-readme-stats-sigma-five.vercel.app/api?username=dwgx&show_icons=true&hide_border=true&bg_color=06020f&title_color=f2a6c4&icon_color=c9a84c&text_color=d4c8ef&ring_color=f2a6c4" />
</picture>
&nbsp;&nbsp;
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://github-readme-stats-sigma-five.vercel.app/api/top-langs/?username=dwgx&layout=compact&hide_border=true&bg_color=06020f&title_color=f2a6c4&text_color=d4c8ef" />
  <img height="170" src="https://github-readme-stats-sigma-five.vercel.app/api/top-langs/?username=dwgx&layout=compact&hide_border=true&bg_color=06020f&title_color=f2a6c4&text_color=d4c8ef" />
</picture>

</div>

---

### `contribution.snake`

<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/dwgx/DWGX/output/github-contribution-grid-snake-dark.svg" />
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/dwgx/DWGX/output/github-contribution-grid-snake.svg" />
  <img alt="dwgx contribution snake" src="https://raw.githubusercontent.com/dwgx/DWGX/output/github-contribution-grid-snake.svg" width="100%" />
</picture>

</div>

---

<div align="center">

```
    ╭───────────────────────────────────────────────────────────╮
    │                                                           │
    │                   be   water   my   friend.               │
    │                                                           │
    ╰───────────────────────────────────────────────────────────╯
```

</div>

---

### `hex.dump`

```
 00401000  e5 b8 9d e7 8e 8b e5 b0   ac e7 ac 91 00 00 00 00   帝王尬笑....
 00401010  64 77 67 78 40 6b 6f 62   65 3a 7e 2f 64 65 76 24   dwgx@kobe:~/dev$
 00401020  72 65 76 65 72 73 65 2e   65 6e 67 69 6e 65 65 72   reverse.engineer
 00401030  67 61 6d 65 20 68 61 63   6b 69 6e 67 20 73 79 73   game hacking sys
 00401040  62 65 20 77 61 74 65 72   20 6d 79 20 66 72 69 65   be water my frie
 00401050  6e 64 20 2f 2f 20 73 6f   6c 6f 20 20 63 72 65 77   nd // solo  crew
 00401060  69 6e 64 65 70 20 73 69   6e 63 65 20 32 30 31 30   indep since 2010
```

---

### `hotkeys`

<div align="center">

<kbd>F1</kbd> [dwgx.github.io]({links['site']})
&nbsp;&nbsp;·&nbsp;&nbsp;
<kbd>F2</kbd> [blog.dwgx.top]({links['blog']})
&nbsp;&nbsp;·&nbsp;&nbsp;
<kbd>F3</kbd> [YouTube]({links['youtube']})
&nbsp;&nbsp;·&nbsp;&nbsp;
<kbd>F4</kbd> [Bilibili]({links['bilibili']})
&nbsp;&nbsp;·&nbsp;&nbsp;
<kbd>F5</kbd> [QQ]({links['qq']})

</div>

```
 ─── dwgx@kobe ── JST+9 ── mode: shipping ── uptime {ctx['uptime']}d ── be water ───
```
"""


def main() -> int:
    profile = load_profile()
    login = str(profile.get("login") or "dwgx")
    token = gh_token()
    user = fetch_user(login, token)
    repos = fetch_repos(login, token)
    events = fetch_events(login, token)
    by_name = repo_index(repos)
    tags = {
        "WindsurfAPI": fetch_latest_tag(f"{login}/WindsurfAPI", token),
        "KiroStudio": fetch_latest_tag(f"{login}/KiroStudio", token),
        "VRCSM": fetch_latest_tag(f"{login}/VRCSM", token),
    }
    public = int(user.get("public_repos") or len(repos))
    stars = total_stars(repos)
    days = uptime_days(str(profile.get("born") or "2010-07-05"))
    today = today_jst().isoformat()
    svg = process_svg(profile, by_name, tags)
    SVG.parent.mkdir(parents=True, exist_ok=True)
    SVG.write_text(svg, encoding="utf-8")
    ctx = {
        "today": today,
        "uptime": days,
        "public_repos": public,
        "total_stars": stars,
        "process_count": len(profile.get("process") or []),
        "recent": recent_log(events, by_name),
        "hardware": hardware_dump(profile, days),
        "pinned_table": pinned_table(profile, by_name, public, stars),
        "stars_map": {k: int(v.get("stargazers_count") or 0) for k, v in by_name.items()},
        "tags": tags,
    }
    README.write_text(render_readme(profile, ctx).rstrip() + "\n", encoding="utf-8")
    print(f"wrote {README.relative_to(ROOT)}")
    print(f"wrote {SVG.relative_to(ROOT)}")
    print(
        f"public_repos={public} stars={stars} uptime={days} "
        f"windsurf={tags['WindsurfAPI']} kiro={tags['KiroStudio']}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
