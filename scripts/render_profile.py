#!/usr/bin/env python3
"""Render dwgx.menu README + process-table.svg from profile.toml + GitHub."""
from __future__ import annotations

import io
import json
import math
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

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ami  # noqa: E402

JST = timezone(timedelta(hours=9))


def today_jst() -> date:
    return datetime.now(JST).date()

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "profile.toml"
README = ROOT / "README.md"
SVG = ROOT / "assets" / "process-table.svg"
STATS_SVG = ROOT / "assets" / "stats.svg"
LANGS_SVG = ROOT / "assets" / "langs.svg"
DISCORD_SVG = ROOT / "assets" / "discord.svg"
AVATAR_PNG = ROOT / "assets" / "discord-avatar.png"
MEDIA_SVG = ROOT / "assets" / "media.svg"
SETUP_SVG = ROOT / "assets" / "setup.svg"
STATUS_SVG = ROOT / "assets" / "status.svg"
DEVICES_SVG = ROOT / "assets" / "devices.svg"
EVENT_SVG = ROOT / "assets" / "eventlog.svg"
API = "https://api.github.com"
GQL = "https://api.github.com/graphql"

LANG_SKIP = {"HTML", "CSS", "SCSS", "Less", "Markdown", "Jinja"}
LANG_COLORS = {
    "JavaScript": "#f1e05a",
    "TypeScript": "#3178c6",
    "Python": "#3572A5",
    "Rust": "#dea584",
    "C++": "#f34b7d",
    "C#": "#178600",
    "C": "#555555",
    "Go": "#00ADD8",
    "Java": "#b07219",
    "Swift": "#F05138",
    "Shell": "#89e051",
    "PowerShell": "#012456",
    "Assembly": "#6E4C13",
    "Astro": "#ff5a03",
    "HTML": "#e34c26",
    "CSS": "#563d7c",
}

PINK = "#f2a6c4"
GOLD = "#c9a84c"
TEXT = "#e6edf3"
MUTED = "#8b949e"
BLUE = "#79c0ff"
GREEN = "#7ee787"

# VGA 16-color AMIBIOS 3.31a
AMI_BLUE = "#0000AA"
AMI_NAVY = "#000055"
AMI_CYAN = "#55FFFF"
AMI_WHITE = "#FFFFFF"
AMI_YELLOW = "#FFFF55"
AMI_GRAY = "#AAAAAA"
AMI_W, AMI_H = 960, 500


def load_profile() -> dict:
    with PROFILE.open("rb") as f:
        return tomllib.load(f)


def prompt_host(profile: dict) -> str:
    return str(profile.get("prompt") or "dwgx@main")


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


def api_graphql(query: str, variables: dict, token: str) -> dict:
    body = json.dumps({"query": query, "variables": variables}).encode("utf-8")
    req = urllib.request.Request(
        GQL,
        data=body,
        method="POST",
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "dwgx-profile-render",
            **({"Authorization": f"Bearer {token}"} if token else {}),
        },
    )
    with urllib.request.urlopen(req, timeout=45) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    if payload.get("errors"):
        raise RuntimeError(payload["errors"][0].get("message") or "graphql error")
    return payload.get("data") or {}


STATS_QUERY = """
query($login: String!, $from: DateTime) {
  user(login: $login) {
    followers { totalCount }
    issues { totalCount }
    pullRequests { totalCount }
    yearContrib: contributionsCollection {
      totalCommitContributions
    }
    todayContrib: contributionsCollection(from: $from) {
      totalCommitContributions
      totalPullRequestContributions
      totalIssueContributions
      commitContributionsByRepository(maxRepositories: 6) {
        contributions { totalCount }
        repository { name }
      }
    }
    repositories(first: 100, ownerAffiliations: OWNER, isFork: false, orderBy: {field: STARGAZERS, direction: DESC}) {
      nodes {
        languages(first: 8, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name color } }
        }
      }
    }
  }
}
"""


def fetch_extra_stats(login: str, token: str, repos: list[dict]) -> dict:
    extra = {
        "followers": 0,
        "issues": 0,
        "prs": 0,
        "commits_year": 0,
        "commits_today": 0,
        "prs_today": 0,
        "issues_today": 0,
        "today_repos": [],
        "langs": [],
    }
    start = datetime.now(JST).replace(hour=0, minute=0, second=0, microsecond=0)
    from_iso = start.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if token:
        try:
            data = api_graphql(STATS_QUERY, {"login": login, "from": from_iso}, token)
            user = (data.get("user") or {}) if isinstance(data, dict) else {}
            extra["followers"] = int(((user.get("followers") or {}).get("totalCount")) or 0)
            extra["issues"] = int(((user.get("issues") or {}).get("totalCount")) or 0)
            extra["prs"] = int(((user.get("pullRequests") or {}).get("totalCount")) or 0)
            extra["commits_year"] = int(
                ((user.get("yearContrib") or {}).get("totalCommitContributions")) or 0
            )
            today = user.get("todayContrib") or {}
            extra["commits_today"] = int(today.get("totalCommitContributions") or 0)
            extra["prs_today"] = int(today.get("totalPullRequestContributions") or 0)
            extra["issues_today"] = int(today.get("totalIssueContributions") or 0)
            extra["today_repos"] = [
                {
                    "name": ((row.get("repository") or {}).get("name") or ""),
                    "n": int(((row.get("contributions") or {}).get("totalCount")) or 0),
                }
                for row in (today.get("commitContributionsByRepository") or [])
                if (row.get("repository") or {}).get("name")
            ]
            sizes: dict[str, dict] = {}
            for node in ((user.get("repositories") or {}).get("nodes") or []):
                for edge in ((node.get("languages") or {}).get("edges") or []):
                    info = edge.get("node") or {}
                    name = info.get("name")
                    if not name or name in LANG_SKIP:
                        continue
                    rec = sizes.setdefault(name, {"size": 0, "color": info.get("color")})
                    rec["size"] += int(edge.get("size") or 0)
                    if info.get("color"):
                        rec["color"] = info.get("color")
            ranked = sorted(sizes.items(), key=lambda kv: -kv[1]["size"])
            extra["langs"] = [
                {
                    "name": name,
                    "size": rec["size"],
                    "color": rec.get("color") or LANG_COLORS.get(name) or GOLD,
                }
                for name, rec in ranked[:6]
            ]
            return extra
        except (urllib.error.URLError, urllib.error.HTTPError, RuntimeError, TimeoutError, json.JSONDecodeError):
            pass
    extra["langs"] = langs_from_repos(repos)
    return extra


def langs_from_repos(repos: list[dict]) -> list[dict]:
    counts: dict[str, int] = {}
    for r in repos:
        if r.get("fork"):
            continue
        name = r.get("language")
        pl = r.get("primaryLanguage")
        if isinstance(pl, dict):
            name = pl.get("name") or name
        if not name or name in LANG_SKIP:
            continue
        counts[name] = counts.get(name, 0) + 1
    ranked = sorted(counts.items(), key=lambda kv: -kv[1])
    return [
        {"name": n, "size": c, "color": LANG_COLORS.get(n) or GOLD}
        for n, c in ranked[:6]
    ]


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


def jst_stamp(iso: str) -> str:
    raw = (iso or "").strip()
    if not raw:
        return "---- -- -- --:--"
    try:
        if raw.endswith("Z"):
            raw = raw[:-1] + "+00:00"
        dt = datetime.fromisoformat(raw.replace(" ", "T", 1))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        local = dt.astimezone(JST)
        return local.strftime("%Y-%m-%d %H:%M")
    except ValueError:
        return (iso or "")[:16]


def parse_dt(iso: str) -> datetime | None:
    raw = (iso or "").strip()
    if not raw:
        return None
    try:
        if raw.endswith("Z"):
            raw = raw[:-1] + "+00:00"
        dt = datetime.fromisoformat(raw.replace(" ", "T", 1))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        return None


def ago_label(iso: str) -> str:
    dt = parse_dt(iso)
    if not dt:
        return "?"
    sec = int((datetime.now(timezone.utc) - dt.astimezone(timezone.utc)).total_seconds())
    if sec < 0:
        sec = 0
    if sec < 90:
        return f"{sec}s"
    if sec < 3600:
        return f"{sec // 60}m"
    if sec < 86400:
        return f"{sec // 3600}h"
    return f"{sec // 86400}d"


def latest_work(events: list[dict]) -> dict:
    for ev in events:
        kind = ev.get("type") or ""
        name = ((ev.get("repo") or {}).get("name") or "").split("/")[-1]
        if not name or name.lower() == "dwgx":
            continue
        payload = ev.get("payload") or {}
        created = str(ev.get("created_at") or "")
        msg = ""
        sha = ""
        verb = kind.replace("Event", "").lower()
        if kind == "PushEvent":
            verb = "push"
            commits = payload.get("commits") or []
            if not commits:
                continue
            last = commits[-1]
            msg = (last.get("message") or "").split("\n")[0]
            sha = (last.get("sha") or "")[:7]
        elif kind == "ReleaseEvent":
            verb = "release"
            rel = payload.get("release") or {}
            msg = str(rel.get("tag_name") or rel.get("name") or "")
        elif kind == "IssuesEvent":
            action = str(payload.get("action") or "")
            if action not in {"opened", "closed", "reopened"}:
                continue
            verb = {"opened": "open", "closed": "close", "reopened": "reopen"}[action]
            msg = ((payload.get("issue") or {}).get("title") or "")
        elif kind == "PullRequestEvent":
            verb = "pr"
            msg = ((payload.get("pull_request") or {}).get("title") or "")
        elif kind == "CreateEvent":
            if payload.get("ref_type") != "tag":
                continue
            verb = "tag"
            msg = str(payload.get("ref") or "")
        elif kind == "IssueCommentEvent":
            continue
        else:
            continue
        return {
            "repo": name,
            "verb": verb,
            "created": created,
            "msg": msg[:72],
            "sha": sha,
            "ago": ago_label(created),
        }
    return {}


def dmesg_events(events: list[dict], limit: int = 8) -> list[dict]:
    out: list[dict] = []
    for ev in events:
        kind = ev.get("type")
        name = ((ev.get("repo") or {}).get("name") or "").split("/")[-1]
        if not name or name.lower() == "dwgx":
            continue
        payload = ev.get("payload") or {}
        created = str(ev.get("created_at") or "")
        line = ""
        if kind == "PushEvent":
            commits = payload.get("commits") or []
            if not commits:
                continue
            last = commits[-1]
            line = (last.get("message") or "").split("\n")[0]
            verb = "push"
        elif kind == "ReleaseEvent":
            line = ((payload.get("release") or {}).get("tag_name") or "release")
            verb = "rel"
        elif kind == "IssuesEvent":
            action = str(payload.get("action") or "issue")
            if action in {"labeled", "unlabeled", "assigned", "unassigned", "milestoned"}:
                continue
            line = ((payload.get("issue") or {}).get("title") or "")
            verb = {"opened": "open", "closed": "close", "reopened": "reopen"}.get(action, action[:6])
        elif kind == "PullRequestEvent":
            line = ((payload.get("pull_request") or {}).get("title") or "")
            verb = "pr"
        else:
            continue
        out.append(
            {
                "repo": name,
                "verb": verb,
                "msg": line[:58],
                "stamp": jst_stamp(created)[11:],
                "ago": ago_label(created),
            }
        )
        if len(out) >= limit:
            break
    return out


def fetch_heads(login: str, names: list[str], token: str) -> list[dict]:
    rows: list[dict] = []
    for name in names:
        try:
            data = api_get(f"/repos/{login}/{name}/commits", token, "per_page=1")
            if not isinstance(data, list) or not data:
                continue
            c = data[0]
            commit = c.get("commit") or {}
            date = ((commit.get("committer") or {}).get("date")) or (
                (commit.get("author") or {}).get("date") or ""
            )
            rows.append(
                {
                    "name": name,
                    "sha": str(c.get("sha") or "")[:7],
                    "msg": (commit.get("message") or "").split("\n")[0][:42],
                    "ago": ago_label(date),
                }
            )
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError):
            continue
    return rows


def fmt_recent_line(iso: str, verb: str, name: str, repo: dict, overrides: dict[str, str]) -> str:
    stars = int(repo.get("stargazers_count") or 0)
    lang = lang_short(repo.get("language"))
    desc = overrides.get(name) or (repo.get("description") or "").replace("\n", " ").strip()
    if len(desc) > 42:
        desc = desc[:41] + "…"
    stamp = jst_stamp(iso)
    return f" {stamp}  {verb}  {name:<22} {f'★{stars}':<6} {lang:<6} {desc}"


def recent_log(
    events: list[dict],
    repos: dict[str, dict],
    overrides: dict[str, str],
    limit: int = 10,
) -> str:
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
        verb = "push"
        if kind == "ReleaseEvent":
            verb = "rel "
        elif kind == "CreateEvent":
            verb = "tag "
        lines.append(fmt_recent_line(str(ev.get("created_at") or ""), verb, name, r, overrides))
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
            lines.append(fmt_recent_line(str(r.get("pushed_at") or ""), "push", name, r, overrides))
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
        f'<text x="16.0" y="18.0" font-size="13" font-weight="700" fill="{PINK}">{esc(prompt_host(profile))}</text>',
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
    header = str(hw.get("header") or "dwgx@main")
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
    for pin in pins[:6]:
        name = pin["name"]
        box = pin_box(pin, repos)
        cells.append(
            f'<td width="33%" valign="top">\n\n{box}\n\n'
            f'[open module →](https://github.com/dwgx/{name})\n\n</td>'
        )
    rows: list[str] = []
    for i in range(0, len(cells), 3):
        rows.append("<tr>\n" + "\n".join(cells[i : i + 3]) + "\n</tr>")
    foot = (
        f"\n\n[{public_count} public repos · {stars} stars · browse all →]"
        "(https://github.com/dwgx?tab=repositories)"
    )
    return "<table>\n" + "\n".join(rows) + "\n</table>" + foot


def fmt_num(n: int) -> str:
    return f"{int(n):,}"


def panel_frame(width: int, height: int, host: str, title: str, body: list[str]) -> str:
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" '
        f"font-family=\"ui-monospace,'Cascadia Mono',Consolas,'SF Mono',monospace\">",
        f'<rect width="{width}" height="{height}" rx="4" fill="#0d1117" stroke="#30363d" stroke-width="1"/>',
        f'<rect x="1" y="1" width="{width-2}" height="26" rx="3" fill="#161b22"/>',
        f'<line x1="0" y1="26" x2="{width}" y2="26" stroke="#30363d" stroke-width="1"/>',
        f'<text x="16.0" y="18.0" font-size="13" font-weight="700" fill="{PINK}">{esc(host)}</text>',
        f'<text x="{16 + text_w(host, True) + 12:.1f}" y="18.0" font-size="13" font-weight="700" fill="{TEXT}">{esc(title)}</text>',
        f'<text x="{width - 72}" y="18.0" font-size="13" font-weight="400" fill="{GREEN}">live</text>',
    ]
    parts.extend(body)
    parts.append("</svg>")
    return "".join(parts)


def stats_svg(host: str, user: dict, stars: int, extra: dict) -> str:
    rows = [
        ("Total Stars", fmt_num(stars), GOLD),
        ("Public Repos", fmt_num(int(user.get("public_repos") or 0)), PINK),
        ("Followers", fmt_num(int(extra.get("followers") or user.get("followers") or 0)), TEXT),
        ("Pull Requests", fmt_num(int(extra.get("prs") or 0)), BLUE),
        ("Commits (year)", fmt_num(int(extra.get("commits_year") or 0)), GREEN),
        ("Issues", fmt_num(int(extra.get("issues") or 0)), MUTED),
    ]
    width, height = 495, 170
    body: list[str] = []
    col_w = 230
    for i, (label, value, color) in enumerate(rows):
        col = i % 2
        row = i // 2
        x = 20 + col * col_w
        y = 58 + row * 34
        body.append(
            f'<text x="{x}" y="{y}" font-size="12" font-weight="400" fill="{MUTED}">{esc(label)}</text>'
        )
        body.append(
            f'<text x="{x}" y="{y + 16}" font-size="16" font-weight="700" fill="{color}">{esc(value)}</text>'
        )
    return panel_frame(width, height, host, "stats.panel", body)


def _pt(cx: float, cy: float, r: float, deg: float) -> tuple[float, float]:
    rad = math.radians(deg - 90)
    return cx + r * math.cos(rad), cy + r * math.sin(rad)


def donut_slice(cx: float, cy: float, r_out: float, r_in: float, a0: float, a1: float) -> str:
    if a1 - a0 <= 0.01:
        return ""
    a1 = min(a1, a0 + 359.9)
    large = 1 if (a1 - a0) > 180 else 0
    x0, y0 = _pt(cx, cy, r_out, a0)
    x1, y1 = _pt(cx, cy, r_out, a1)
    x2, y2 = _pt(cx, cy, r_in, a1)
    x3, y3 = _pt(cx, cy, r_in, a0)
    return (
        f"M {x0:.2f} {y0:.2f} "
        f"A {r_out:.2f} {r_out:.2f} 0 {large} 1 {x1:.2f} {y1:.2f} "
        f"L {x2:.2f} {y2:.2f} "
        f"A {r_in:.2f} {r_in:.2f} 0 {large} 0 {x3:.2f} {y3:.2f} Z"
    )


def langs_svg(host: str, langs: list[dict]) -> str:
    width, height = 495, 170
    body: list[str] = []
    total = sum(int(x.get("size") or 0) for x in langs) or 1
    if not langs:
        body.append(
            f'<text x="20" y="80" font-size="13" fill="{MUTED}">no language data</text>'
        )
        return panel_frame(width, height, host, "langs.panel", body)
    cx, cy, r_out, r_in = 92.0, 100.0, 58.0, 32.0
    angle = 0.0
    for lang in langs[:6]:
        pct = int(lang["size"]) / total
        sweep = max(1.2, pct * 360.0)
        color = str(lang.get("color") or GOLD)
        path = donut_slice(cx, cy, r_out, r_in, angle, angle + sweep)
        if path:
            body.append(f'<path d="{path}" fill="{esc(color)}" />')
        angle += sweep
    body.append(f'<circle cx="{cx}" cy="{cy}" r="{r_in - 1}" fill="#0d1117"/>')
    body.append(
        f'<text x="{cx}" y="{cy + 4}" text-anchor="middle" font-size="11" font-weight="700" fill="{PINK}">langs</text>'
    )
    for i, lang in enumerate(langs[:6]):
        y = 52 + i * 18
        pct = int(lang["size"]) / total * 100
        color = str(lang.get("color") or GOLD)
        name = str(lang["name"])
        body.append(f'<rect x="170" y="{y - 8}" width="10" height="10" rx="2" fill="{esc(color)}"/>')
        body.append(
            f'<text x="186" y="{y + 1}" font-size="12" fill="{TEXT}">{esc(name)}</text>'
        )
        body.append(
            f'<text x="455" y="{y + 1}" text-anchor="end" font-size="12" fill="{MUTED}">{pct:.0f}%</text>'
        )
    return panel_frame(width, height, host, "langs.panel", body)


STATUS_COLOR = {
    "online": GREEN,
    "idle": GOLD,
    "dnd": "#f85149",
    "offline": MUTED,
}


def fetch_presence(discord_id: str) -> dict:
    empty = {
        "status": "offline",
        "username": "dwgx",
        "display": "dwgx",
        "activity": "AFK · probably coding",
        "avatar": None,
    }
    if not discord_id:
        return empty
    try:
        req = urllib.request.Request(
            f"https://api.lanyard.rest/v1/users/{discord_id}",
            headers={"User-Agent": "dwgx-profile-render"},
        )
        with urllib.request.urlopen(req, timeout=12) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        data = payload.get("data") or {}
        user = data.get("discord_user") or {}
        acts = data.get("activities") or []
        activity = "AFK · probably coding"
        for act in acts:
            name = (act.get("name") or "").strip()
            details = (act.get("details") or "").strip()
            state = (act.get("state") or "").strip()
            if name and name.lower() != "custom status":
                bits = [name]
                if details:
                    bits.append(details)
                elif state:
                    bits.append(state)
                activity = " · ".join(bits)
                break
            if state:
                activity = state
        avatar_hash = user.get("avatar")
        avatar_url = None
        if avatar_hash:
            avatar_url = (
                f"https://cdn.discordapp.com/avatars/{discord_id}/{avatar_hash}.png?size=128"
            )
        return {
            "status": str(data.get("discord_status") or "offline"),
            "username": str(user.get("username") or "dwgx"),
            "display": str(user.get("global_name") or user.get("username") or "dwgx"),
            "activity": activity[:64],
            "avatar": avatar_url,
        }
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError):
        return empty


def _hex_rgb(color: str) -> tuple[int, int, int]:
    h = color.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def circle_avatar(blob: bytes, status_color: str) -> bytes:
    from PIL import Image, ImageDraw

    im = Image.open(io.BytesIO(blob)).convert("RGBA").resize((128, 128), Image.Resampling.LANCZOS)
    mask = Image.new("L", (128, 128), 0)
    ImageDraw.Draw(mask).ellipse((1, 1, 126, 126), fill=255)
    out = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    out.paste(im, (0, 0), mask)
    draw = ImageDraw.Draw(out)
    draw.ellipse((90, 90, 126, 126), fill=(13, 17, 23, 255))
    draw.ellipse((96, 96, 120, 120), fill=_hex_rgb(status_color) + (255,))
    buf = io.BytesIO()
    out.save(buf, format="PNG")
    return buf.getvalue()


def save_avatar(url: str | None, status: str = "offline") -> bool:
    color = STATUS_COLOR.get(status, MUTED)
    blob = b""
    if url:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "dwgx-profile-render"})
            with urllib.request.urlopen(req, timeout=12) as resp:
                blob = resp.read()
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError):
            blob = b""
    if not blob and AVATAR_PNG.exists():
        blob = AVATAR_PNG.read_bytes()
    if not blob:
        return False
    try:
        AVATAR_PNG.write_bytes(circle_avatar(blob, color))
        return True
    except Exception:
        if blob[:8] == b"\x89PNG\r\n\x1a\n":
            AVATAR_PNG.write_bytes(blob)
            return True
        return AVATAR_PNG.exists()


def discord_svg(host: str, presence: dict) -> str:
    width, height = 400, 110
    status = str(presence.get("status") or "offline")
    color = STATUS_COLOR.get(status, MUTED)
    display = str(presence.get("display") or "dwgx")
    username = str(presence.get("username") or "dwgx")
    activity = str(presence.get("activity") or "")
    body = [
        f'<circle cx="24" cy="68" r="7" fill="{color}"/>',
        f'<text x="42" y="58" font-size="15" font-weight="700" fill="{TEXT}">{esc(display)}</text>',
        f'<text x="42" y="76" font-size="12" fill="{MUTED}">@{esc(username)} · {esc(status)}</text>',
        f'<text x="42" y="94" font-size="12" fill="{PINK}">{esc(activity)}</text>',
    ]
    return panel_frame(width, height, host, "discord.presence", body)


def _removed_setup_svg(repos: dict[str, dict], tags: dict[str, str]) -> str:
    """Classic AMIBIOS CMOS Setup — blue VGA. Not a clock."""
    w, h = 920, 430
    blue, cyan, white, yellow, gray, navy = (
        "#0000aa",
        "#55ffff",
        "#ffffff",
        "#ffff55",
        "#aaaaaa",
        "#000055",
    )
    wapi = repos.get("WindsurfAPI") or {}
    wstars = int(wapi.get("stargazers_count") or wapi.get("stargazerCount") or 0)
    rows = [
        ("#1", "ORIGIN", "genesis.wiki  world protocol", True),
        ("#2", "WindsurfAPI", f"{tags.get('WindsurfAPI') or 'live'}  ★{wstars}", False),
        ("#3", "KiroStudio", f"{tags.get('KiroStudio') or 'live'}  Anthropic gateway", False),
        ("#4", "vrchat-il2cpp-re", "Unity 6  64K classes", False),
        ("#5", "SmartCLI", "PTY + pyte  agent TUI", False),
        ("#6", "YuKiKo / VRCSM", "QQ bot  VRChat cache", False),
    ]
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        "font-family=\"'Lucida Console',Consolas,'Courier New',monospace\">",
        f'<rect width="{w}" height="{h}" fill="{blue}"/>',
        f'<rect x="8" y="8" width="{w-16}" height="32" fill="{navy}"/>',
        f'<text x="460" y="30" text-anchor="middle" font-size="16" font-weight="700" fill="{white}">AMIBIOS SETUP UTILITY - COPYRIGHT (C) 2026 dwgx</text>',
        f'<text x="24" y="62" font-size="14" fill="{yellow}">Main</text>',
        f'<text x="88" y="62" font-size="14" fill="{cyan}">Advanced</text>',
        f'<text x="188" y="62" font-size="14" fill="{white}">Boot</text>',
        f'<text x="252" y="62" font-size="14" fill="{cyan}">Security</text>',
        f'<text x="348" y="62" font-size="14" fill="{cyan}">Exit</text>',
        f'<rect x="12" y="72" width="896" height="318" fill="{navy}" stroke="{cyan}" stroke-width="2"/>',
        f'<text x="28" y="96" font-size="13" fill="{yellow}">Boot Settings</text>',
        f'<text x="28" y="118" font-size="13" fill="{gray}">Quiet Boot                                 [Disabled]</text>',
        f'<text x="28" y="138" font-size="13" fill="{gray}">Bootup Num-Lock                            [On]</text>',
        f'<text x="28" y="168" font-size="13" fill="{yellow}">Boot Device Priority</text>',
    ]
    y = 194
    for slot, name, note, selected in rows:
        if selected:
            parts.append(f'<rect x="22" y="{y-15}" width="876" height="20" fill="{gray}"/>')
            fill = navy
        else:
            fill = white
        label = f"{slot}  {name:<18} {note}"
        parts.append(
            f'<text x="32" y="{y}" font-size="13" fill="{fill}">{esc(label)}</text>'
        )
        y += 24
    parts.extend(
        [
            f'<rect x="8" y="{h-36}" width="{w-16}" height="28" fill="{navy}"/>',
            f'<text x="24" y="{h-16}" font-size="12" fill="{yellow}">↑↓ Select   Enter: Boot   F9: Setup Defaults   F10: Save &amp; Exit   ESC: Exit</text>',
            "</svg>",
        ]
    )
    return "".join(parts)


def hex_dump_block() -> str:
    payloads = [
        "帝王尬笑",
        "maybe I'm dwgx",
        "genesis.wiki",
        "幻想万華鏡",
        "WindsurfAPI",
        "indep.2010",
    ]
    lines = []
    addr = 0x401000
    for s in payloads:
        raw = s.encode("utf-8")
        padded = (raw + b"\x00" * 16)[:16]
        left = " ".join(f"{b:02x}" for b in padded[:8])
        right = " ".join(f"{b:02x}" for b in padded[8:])
        vis = s if len(s) <= 16 else s[:16]
        lines.append(f" {addr:08X}  {left}   {right}   {vis}")
        addr += 16
    return "\n".join(lines)


def fetch_bili(mid: str) -> dict:
    out = {"follower": 0, "following": 0}
    if not mid:
        return out
    try:
        req = urllib.request.Request(
            f"https://api.bilibili.com/x/relation/stat?vmid={mid}",
            headers={"User-Agent": "Mozilla/5.0 dwgx-profile-render"},
        )
        with urllib.request.urlopen(req, timeout=12) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        data = payload.get("data") or {}
        out["follower"] = int(data.get("follower") or 0)
        out["following"] = int(data.get("following") or 0)
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError, OSError):
        pass
    return out


def media_svg(host: str, bili: dict) -> str:
    fans = fmt_num(int(bili.get("follower") or 0))
    following = fmt_num(int(bili.get("following") or 0))
    body = [
        f'<text x="20" y="62" font-size="12" fill="{MUTED}">Bilibili</text>',
        f'<text x="20" y="84" font-size="22" font-weight="700" fill="{PINK}">{esc(fans)}</text>',
        f'<text x="20" y="104" font-size="12" fill="{TEXT}">fans</text>',
        f'<text x="150" y="62" font-size="12" fill="{MUTED}">following</text>',
        f'<text x="150" y="84" font-size="22" font-weight="700" fill="{GOLD}">{esc(following)}</text>',
        f'<text x="20" y="124" font-size="12" fill="{MUTED}">space.bilibili.com/1452905012</text>',
    ]
    return panel_frame(280, 140, host, "bili.stat", body)


def _dead_kv_svg(host: str, title: str, rows: list[tuple[str, str, str]], width: int = 495, height: int = 170) -> str:
    body: list[str] = []
    y = 52
    for label, value, color in rows[:6]:
        body.append(
            f'<text x="18" y="{y}" font-size="12" fill="{MUTED}">{esc(label)}</text>'
        )
        body.append(
            f'<text x="130" y="{y}" font-size="13" font-weight="700" fill="{color}">{esc(value)}</text>'
        )
        y += 20
    return panel_frame(width, height, host, title, body)


def doing_svg(host: str, work: dict, extra: dict) -> str:
    if not work:
        rows = [("task", "idle", MUTED), ("hint", "no public events", MUTED)]
    else:
        rows = [
            ("task", f"{work.get('verb')}  {work.get('repo')}", GREEN),
            ("when", f"{work.get('ago')} ago  {jst_stamp(str(work.get('created') or ''))}", GOLD),
            ("head", work.get("sha") or "-", BLUE),
            ("msg", (work.get("msg") or "-")[:46], TEXT),
            ("today", f"{extra.get('commits_today') or 0} commits  {extra.get('prs_today') or 0} prs", PINK),
        ]
    return kv_svg(host, "now.work", rows)


def git_svg(host: str, heads: list[dict]) -> str:
    body: list[str] = []
    y = 50
    if not heads:
        body.append(f'<text x="18" y="80" font-size="13" fill="{MUTED}">no heads</text>')
    for row in heads[:6]:
        body.append(
            f'<text x="18" y="{y}" font-size="12" font-weight="700" fill="{TEXT}">{esc(str(row["name"]))}</text>'
        )
        body.append(
            f'<text x="168" y="{y}" font-size="12" fill="{GOLD}">{esc(str(row["sha"]))}</text>'
        )
        body.append(
            f'<text x="228" y="{y}" font-size="12" fill="{MUTED}">{esc(str(row["ago"]))}</text>'
        )
        body.append(
            f'<text x="270" y="{y}" font-size="12" fill="{PINK}">{esc(str(row["msg"]))}</text>'
        )
        y += 20
    return panel_frame(495, 170, host, "git.head", body)


def dmesg_svg(host: str, lines: list[dict]) -> str:
    body: list[str] = []
    y = 48
    if not lines:
        body.append(f'<text x="18" y="80" font-size="13" fill="{MUTED}">quiet</text>')
    for row in lines[:8]:
        body.append(
            f'<text x="16" y="{y}" font-size="12" fill="{MUTED}">[{esc(str(row["stamp"]))} {esc(str(row["ago"]))}]</text>'
        )
        body.append(
            f'<text x="130" y="{y}" font-size="12" fill="{GOLD}">{esc(str(row["verb"]))}</text>'
        )
        body.append(
            f'<text x="175" y="{y}" font-size="12" fill="{TEXT}">{esc(str(row["repo"]))}</text>'
        )
        body.append(
            f'<text x="330" y="{y}" font-size="12" fill="{PINK}">{esc(str(row["msg"]))}</text>'
        )
        y += 18
    return panel_frame(920, 200, host, "dmesg", body)


def inbox_svg(host: str, repos: dict[str, dict]) -> str:
    names = ["WindsurfAPI", "KiroStudio", "VRCSM", "SmartCLI", "YuKiKo", "cursorapi"]
    rows: list[tuple[str, str, str]] = []
    for name in names:
        r = repos.get(name) or {}
        n = int(r.get("open_issues_count") or 0)
        color = PINK if n else GREEN
        rows.append((name, f"{n} open", color))
    return kv_svg(host, "inbox.issues", rows)


def today_svg(host: str, extra: dict) -> str:
    rows = [
        ("commits", str(extra.get("commits_today") or 0), GOLD),
        ("pull reqs", str(extra.get("prs_today") or 0), BLUE),
        ("issues", str(extra.get("issues_today") or 0), PINK),
        ("year cmt", str(extra.get("commits_year") or 0), TEXT),
    ]
    y_repos = extra.get("today_repos") or []
    if y_repos:
        top = y_repos[0]
        rows.append(("hot repo", f"{top.get('name')} ×{top.get('n')}", GREEN))
    return kv_svg(host, "today.work", rows)


def flagship_block(profile: dict) -> str:
    flag = profile.get("flagship") or {}
    name = str(flag.get("name") or "ORIGIN")
    kicker = str(flag.get("kicker") or "Genesis Protocol")
    title = str(flag.get("title") or "")
    blurb = str(flag.get("blurb") or "")
    url = str(flag.get("url") or "https://genesis.wiki")
    facts = str(flag.get("facts") or "")
    inner = 64
    def line(s: str) -> str:
        s = s[:inner]
        return "║  " + s.ljust(inner) + "║"

    def wrap(s: str) -> list[str]:
        words = s.split()
        out: list[str] = []
        cur = ""
        for w in words:
            trial = (cur + " " + w).strip()
            if len(trial) <= inner:
                cur = trial
            else:
                if cur:
                    out.append(cur)
                cur = w
        if cur:
            out.append(cur)
        return out or [""]

    body_lines = [line(f"{name}  ·  {kicker}"), "╠" + "═" * (inner + 2) + "╣", line("")]
    for chunk in wrap(title) + wrap(blurb):
        body_lines.append(line(chunk))
    body_lines.extend([line(""), line(facts), line(f"open →  {url}")])
    box = "\n".join(
        ["╔" + "═" * (inner + 2) + "╗", *body_lines, "╚" + "═" * (inner + 2) + "╝"]
    )
    return f"""### `origin.genesis`

<div align="center">

```
{box}
```

[{url.replace('https://', '')} →]({url})

</div>"""


def shield_stars(n: int) -> str:
    if n >= 1000:
        return f"{n/1000:.1f}k".replace(".0k", "k")
    return str(n)


def render_readme(profile: dict, ctx: dict) -> str:
    ident = profile["identity"]
    ship = profile.get("ship") or {}
    links = profile["links"]
    today = ctx["today"]
    n = ctx["process_count"]
    more = max(0, ctx["public_repos"] - 5)
    windsurf_stars = ctx["stars_map"].get("WindsurfAPI", 0)
    wtag = ctx["tags"].get("WindsurfAPI") or "v?"
    ktag = ctx["tags"].get("KiroStudio") or "v?"
    now = f"ORIGIN · WindsurfAPI {wtag} · KiroStudio {ktag}"
    return f"""<!-- ════════════════════════════════════════════════════════════════ -->
<!--  dwgx.menu  v{profile.get('version','2.2')}  ·  generated {today} JST          -->
<!--  source: profile.toml  ·  renderer: scripts/render_profile.py     -->
<!-- ════════════════════════════════════════════════════════════════ -->

<img src="https://raw.githubusercontent.com/dwgx/DWGX/main/assets/bios-header.svg" width="100%" alt="dwgx.menu · AMIBIOS POST" />

<div align="center">

<img src="{links['qq_avatar']}" width="128" style="border-radius:50%;" />

<br/>

[![Typing SVG](https://readme-typing-svg.demolab.com?font=Noto+Serif+JP&weight=600&size=22&pause=1200&color=F2A6C4&center=true&vCenter=true&random=false&width=620&lines=%E4%B9%9F%E8%AE%B8%E6%88%91%E5%B0%B1%E6%98%AFdwgx;WindsurfAPI+%C2%B7+KiroStudio+%C2%B7+ORIGIN;injected+into+process)](https://dwgx.github.io)

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

</div>

---

### `dwgx.cfg`

```ini
; {today}

[who]
name = dwgx
aka  = 帝王尬笑
from = {ident.get('from', 'Kobe')}
note = {ident.get('note', '也许我就是dwgx')}

[ship]
ORIGIN      = {ship.get('origin', 'genesis.wiki')}
WindsurfAPI = {ship.get('windsurf', 'js gateway')} · {wtag}
KiroStudio  = {ship.get('kiro', 'rust gateway')} · {ktag}

[also]
other = {ship.get('also', 'VRChat RE · SmartCLI')}
from  = {ship.get('came', 'MC clients')}
```

---

### `process.table`

<div align="center">

<img src="https://raw.githubusercontent.com/dwgx/DWGX/main/assets/process-table.svg" width="88%" alt="process.table" />

</div>

---

### `setup.utility`

<details>
<summary>Boot — 1st ORIGIN · 2nd WindsurfAPI · 3rd KiroStudio</summary>

<p align="center">
<img src="https://raw.githubusercontent.com/dwgx/DWGX/main/assets/setup.svg" width="100%" alt="AMIBIOS Boot" />
</p>

</details>

---

### `status.pages`

<details>
<summary>Main — last public work · {ctx.get('doing_line') or now}</summary>

<p align="center">
<img src="https://raw.githubusercontent.com/dwgx/DWGX/main/assets/status.svg" width="100%" alt="AMIBIOS Main" />
</p>

</details>

<details>
<summary>Advanced — git HEADs as IDE devices</summary>

<p align="center">
<img src="https://raw.githubusercontent.com/dwgx/DWGX/main/assets/devices.svg" width="100%" alt="AMIBIOS Advanced" />
</p>

</details>

<details>
<summary>Log — public events</summary>

<p align="center">
<img src="https://raw.githubusercontent.com/dwgx/DWGX/main/assets/eventlog.svg" width="100%" alt="AMIBIOS Log" />
</p>

</details>

---

{flagship_block(profile)}

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
<img src="https://raw.githubusercontent.com/dwgx/DWGX/main/assets/discord-avatar.png" width="80" height="80" alt="discord avatar" />
</a>

<img src="https://raw.githubusercontent.com/dwgx/DWGX/main/assets/discord.svg" alt="discord presence" />

<br/>

<img src="https://raw.githubusercontent.com/dwgx/DWGX/main/assets/media.svg" alt="bili.stat" />

</div>

---

<div align="center">

### `featured`

## 幻想万華鏡 ~ The Memories of Phantasm

<img src="https://raw.githubusercontent.com/dwgx/DWGX/main/assets/gensou.gif" width="640" alt="幻想万華鏡" />

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

<div align="center">

### `stack`

<img src="https://raw.githubusercontent.com/dwgx/DWGX/main/assets/stack.svg" width="92%" alt="stack" />

</div>

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

<img height="170" src="https://raw.githubusercontent.com/dwgx/DWGX/main/assets/stats.svg" alt="stats.panel" />
&nbsp;&nbsp;
<img height="170" src="https://raw.githubusercontent.com/dwgx/DWGX/main/assets/langs.svg" alt="langs.panel" />

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

### `hex.dump`

```
{ctx['hexdump']}
```

---

### `hotkeys`

```
 DEL   Setup            {links['site']}
 F2    HDD-0 ORIGIN     {links.get('genesis') or 'https://genesis.wiki'}
 F8    BBS Popup        {links['youtube']}
 F9    BBS Popup        {links['bilibili']}
 F10   Save & Exit      maybe I'm dwgx
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
    extra = fetch_extra_stats(login, token, repos)
    if not extra.get("followers"):
        extra["followers"] = int(user.get("followers") or 0)
    days = uptime_days(str(profile.get("born") or "2010-07-05"))
    today = today_jst().isoformat()
    host = prompt_host(profile)
    SVG.parent.mkdir(parents=True, exist_ok=True)
    SVG.write_text(process_svg(profile, by_name, tags), encoding="utf-8")
    STATS_SVG.write_text(stats_svg(host, user, stars, extra), encoding="utf-8")
    LANGS_SVG.write_text(langs_svg(host, extra.get("langs") or []), encoding="utf-8")
    presence = fetch_presence(str((profile.get("links") or {}).get("discord_id") or ""))
    save_avatar(presence.get("avatar"), str(presence.get("status") or "offline"))
    DISCORD_SVG.write_text(discord_svg(host, presence), encoding="utf-8")
    bili = fetch_bili(str((profile.get("links") or {}).get("bili_mid") or ""))
    MEDIA_SVG.write_text(media_svg(host, bili), encoding="utf-8")
    work = latest_work(events)
    heads = fetch_heads(
        login,
        ["WindsurfAPI", "KiroStudio", "VRCSM", "SmartCLI", "YuKiKo", "cursorapi"],
        token,
    )
    if work and not work.get("sha"):
        for h in heads:
            if h["name"] == work.get("repo"):
                work["msg"] = work.get("msg") or h["msg"]
                work["sha"] = h["sha"]
                break
    dmesg = dmesg_events(events)
    SETUP_SVG.write_text(ami.setup_svg(by_name, tags), encoding="utf-8")
    STATUS_SVG.write_text(ami.status_svg(work, extra, by_name, today), encoding="utf-8")
    DEVICES_SVG.write_text(ami.devices_svg(heads), encoding="utf-8")
    EVENT_SVG.write_text(ami.eventlog_svg(dmesg), encoding="utf-8")
    doing_line = ""
    if work:
        doing_line = (
            f"{work.get('verb')} {work.get('repo')} · {work.get('ago')} ago"
            + (f" · {work.get('msg')}" if work.get("msg") else "")
        )
    overrides = {
        str(k): str(v)
        for k, v in (profile.get("log_desc") or {}).items()
    }
    ctx = {
        "today": today,
        "uptime": days,
        "public_repos": public,
        "total_stars": stars,
        "process_count": len(profile.get("process") or []),
        "recent": recent_log(events, by_name, overrides),
        "hardware": hardware_dump(profile, days),
        "pinned_table": pinned_table(profile, by_name, public, stars),
        "stars_map": {k: int(v.get("stargazers_count") or 0) for k, v in by_name.items()},
        "tags": tags,
        "hexdump": hex_dump_block(),
        "doing_line": doing_line[:110],
    }
    README.write_text(render_readme(profile, ctx).rstrip() + "\n", encoding="utf-8")
    print(f"wrote {README.relative_to(ROOT)}")
    print(f"wrote {SVG.relative_to(ROOT)}")
    print(f"wrote {STATS_SVG.relative_to(ROOT)}")
    print(f"wrote {LANGS_SVG.relative_to(ROOT)}")
    print(f"wrote {DISCORD_SVG.relative_to(ROOT)}")
    print(f"wrote {MEDIA_SVG.relative_to(ROOT)}")
    print(f"wrote {SETUP_SVG.relative_to(ROOT)}")
    print(f"wrote {STATUS_SVG.relative_to(ROOT)}")
    print(f"wrote {DEVICES_SVG.relative_to(ROOT)}")
    print(f"wrote {EVENT_SVG.relative_to(ROOT)}")
    print(
        f"public_repos={public} stars={stars} uptime={days} "
        f"windsurf={tags['WindsurfAPI']} kiro={tags['KiroStudio']}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
