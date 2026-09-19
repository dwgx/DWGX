#!/usr/bin/env python3
"""Render dwgx.menu README + process-table.svg from profile.toml + GitHub."""
from __future__ import annotations

import base64
import io
import json
import math
import os
import re
import subprocess
import sys
import time
import tomllib
import unicodedata
import urllib.error
import urllib.request
import xml.sax.saxutils
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ami  # noqa: E402
import ami_book  # noqa: E402

JST = timezone(timedelta(hours=9))


def today_jst() -> date:
    return datetime.now(JST).date()


def now_jst() -> datetime:
    return datetime.now(JST)


def hhmm_jst(dt: datetime | None = None) -> str:
    return (dt or now_jst()).strftime("%H:%M")

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "profile.toml"
README = ROOT / "README.md"
SVG = ROOT / "assets" / "process-table.svg"
STATS_SVG = ROOT / "assets" / "stats.svg"
LANGS_SVG = ROOT / "assets" / "langs.svg"
DISCORD_SVG = ROOT / "assets" / "discord.svg"
PRESENCE_JSON = ROOT / "assets" / "discord-presence.json"
AVATAR_PNG = ROOT / "assets" / "discord-avatar.png"
MEDIA_SVG = ROOT / "assets" / "media.svg"
SETUP_SVG = ROOT / "assets" / "setup.svg"
STATUS_SVG = ROOT / "assets" / "status.svg"
DEVICES_SVG = ROOT / "assets" / "devices.svg"
EVENT_SVG = ROOT / "assets" / "eventlog.svg"
GUESTBOOK_SVG = ROOT / "assets" / "guestbook.svg"
ORIGIN_SVG = ROOT / "assets" / "origin-panel.svg"
BOOK_NAMES = ("post.svg", "dmi.svg")
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
PANEL_MARK = "live"
PANEL_MARK_COLOR = GREEN

# VGA 16-color AMIBIOS 3.31a
AMI_BLUE = "#0000AA"
AMI_NAVY = "#000055"
AMI_CYAN = "#55FFFF"
AMI_WHITE = "#FFFFFF"
AMI_YELLOW = "#FFFF55"
AMI_GRAY = "#AAAAAA"
AMI_W, AMI_H = 960, 500

# UI-04 palette (2026-09-18). New components use these; AMIBIOS assets migrate later.
UI_INK = "#0F131B"          # shell background
UI_PANEL = "#161C27"        # card / panel surface
UI_TEXT = "#EBE4D8"         # warm body text
UI_MUTED = "#A5AFBF"        # secondary text
UI_SAKURA = "#D6A0AC"       # signature / guestbook accent
UI_GOLD = "#CEB27C"         # ORIGIN accent
UI_BLUE = "#98B8DC"         # link / focus
UI_TERM = "#ACC4A5"         # terminal accent
UI_PAPER = "#E9DECA"        # ORIGIN plate paper
UI_PAPER_LINE = "#CEB27C"   # ORIGIN plate rule
UI_PAPER_TEXT = "#282A2F"   # ORIGIN plate body
UI_PAPER_INDEX = "#735A31"  # ORIGIN plate index


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


def plain_comment(body: str, limit: int = 72) -> str:
    text = (body or "").replace("\r", "\n")
    text = re.sub(r"```[\s\S]*?```", " ", text)
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"!\[.*?\]\(.*?\)", " ", text)
    text = re.sub(r"\[([^\]]*)]\([^)]*\)", r"\1", text)
    text = re.sub(r"[|*_`#<>{}\\]", " ", text)
    text = " ".join(text.split())
    if len(text) > limit:
        text = text[: limit - 1] + "..."
    return text or "(empty)"


def fetch_event_log_rows(login: str, issue: int, token: str, limit: int = 5) -> list[tuple[str, str, str]]:
    if issue <= 0:
        return []
    try:
        data = api_get(
            f"/repos/{login}/DWGX/issues/{issue}/comments",
            token,
            "per_page=100",
        )
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError):
        data = []
    if not isinstance(data, list):
        data = []
    rows: list[tuple[str, str, str]] = []
    for comment in data:
        user = str((comment.get("user") or {}).get("login") or "?")
        if user.endswith("[bot]"):
            continue
        body = plain_comment(str(comment.get("body") or ""), limit=48)
        when = jst_stamp(str(comment.get("created_at") or ""))
        rows.append((when, user, body))
    rows = rows[-limit:]
    rows.reverse()
    return rows


def guestbook_svg(rows: list[tuple[str, str, str]], issue: int) -> str:
    esc = xml.sax.saxutils.escape
    width = 900
    col_when, col_who = 160, 150
    head_h, row_h = 22, 24
    show = rows or [
        (
            "empty",
            "·",
            f"comment Event Log #{issue} · last 5 shown, newest first",
        )
    ]
    height = 4 + head_h + row_h * len(show)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" font-family="\'Lucida Console\',\'Courier New\',Consolas,monospace">',
        f'<rect width="{width}" height="{height}" fill="#000055" stroke="#55FFFF" stroke-width="2"/>',
        f'<rect x="0" y="0" width="{width}" height="{head_h}" fill="#AAAAAA"/>',
        '<text x="9" y="16" font-size="12" font-weight="700" fill="#000000">when (JST)</text>',
        f'<text x="{col_when + 9}" y="16" font-size="12" font-weight="700" fill="#000000">who</text>',
        f'<text x="{col_when + col_who + 9}" y="16" font-size="12" font-weight="700" fill="#000000">note</text>',
        f'<line x1="{col_when}" y1="0" x2="{col_when}" y2="{head_h}" stroke="#000055" stroke-width="2"/>',
        f'<line x1="{col_when + col_who}" y1="0" x2="{col_when + col_who}" y2="{head_h}" stroke="#000055" stroke-width="2"/>',
    ]
    y = head_h
    for when, who, note in show:
        who_fill = "#AAAAAA" if who in {".", "·", "--"} else "#FFFF55"
        note_fit = note if len(note) <= 54 else note[:53] + "..."
        parts.append(f'<text x="9" y="{y + 16}" font-size="12" fill="#FFFF55">{esc(when)}</text>')
        parts.append(
            f'<text x="{col_when + 9}" y="{y + 16}" font-size="12" fill="{who_fill}">{esc(who)}</text>'
        )
        parts.append(
            f'<text x="{col_when + col_who + 9}" y="{y + 16}" font-size="12" fill="#FFFF55">{esc(note_fit)}</text>'
        )
        y += row_h
    parts.append("</svg>")
    return "\n".join(parts)


def fetch_event_log(login: str, issue: int, token: str, limit: int = 5) -> str:
    header = "| when (JST) | who | note |\n|---|---|---|"
    rows = fetch_event_log_rows(login, issue, token, limit=limit)
    if issue <= 0:
        return header + "\n| ---- -- -- --:-- | -- | guestbook issue not wired |"
    if not rows:
        issue_url = f"https://github.com/{login}/DWGX/issues/{issue}"
        return header + f"\n| empty | · | comment [Event Log #{issue}]({issue_url}) · last 5 shown |"
    lines = [header]
    for when, user, body in rows:
        lines.append(f"| {when} | [{user}](https://github.com/{user}) | {body} |")
    return "\n".join(lines)


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
    """Legacy ASCII card. Reads pin["legacy"] — a labeled design snapshot, not live data."""
    name = str(pin["name"])
    legacy = pin.get("legacy") or {}
    stars = int((repos.get(name) or {}).get("stargazers_count") or 0)
    blurb = str(legacy.get("blurb") or "")
    lang = str(pin.get("lang") or "")
    stage = str(legacy.get("stage") or "")
    if legacy.get("star_in_stage"):
        stage = f"{stage} ★{stars}"
    diff = str(legacy.get("diff") or "")
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


def facet_html(form: str, items: list) -> str:
    """One distinguishing structure per card: index / route / protocol / loop / link / layers / settings."""
    vals = [esc(str(x)) for x in items]
    if not vals:
        return ""
    if form == "route":
        return "<samp>" + " → ".join(vals) + "</samp>"
    if form == "loop":
        return "<samp>$ " + " → ".join(vals) + "</samp>"
    if form == "link":
        return " ⇄ ".join(f"<code>{v}</code>" for v in vals)
    if form == "layers":
        return "<br />".join(f"<code>{v}</code>" for v in vals)
    if form == "settings":
        return "<samp>" + " / ".join(vals) + "</samp>"
    if form == "index":
        return " ".join(f"<code>{v}</code>" for v in vals)
    return " · ".join(f"<code>{v}</code>" for v in vals)


def project_card(pin: dict, repos: dict[str, dict], tags: dict[str, str]) -> str:
    name = str(pin.get("name") or "")
    url = f"https://github.com/dwgx/{name}"
    stars = int((repos.get(name) or {}).get("stargazers_count") or 0)
    tag = str(tags.get(name) or "")
    meta = [str(pin.get("tech") or ""), str(pin.get("lang") or "")]
    line = " · ".join(m for m in meta if m)
    if stars:
        line += f" · ★{fmt_num(stars)}"
    if tag:
        line += f" · {esc(tag)}"
    return (
        '<td width="50%" valign="top" align="left">\n'
        f'<p><samp>{esc(str(pin.get("tag") or ""))}</samp></p>\n'
        f'<h4><a href="{url}">{esc(name)}</a></h4>\n'
        f'<p>{esc(str(pin.get("role") or ""))}</p>\n'
        f'<p>{facet_html(str(pin.get("form") or ""), list(pin.get("items") or []))}'
        f"<br /><sub>{line}</sub></p>\n"
        f'<p><a href="{url}">打开项目 →</a></p>\n'
        "</td>"
    )


def render_project_cards(
    profile: dict, repos: dict[str, dict], tags: dict[str, str], public_count: int, stars: int
) -> str:
    pins = list(profile.get("pin") or [])[:6]
    cells = [project_card(p, repos, tags) for p in pins]
    rows: list[str] = []
    for i in range(0, len(cells), 2):
        rows.append("<tr>\n" + "\n".join(cells[i : i + 2]) + "\n</tr>")
    foot = (
        f"\n\n[{public_count} public repos · {fmt_num(stars)} stars · browse all →]"
        "(https://github.com/dwgx?tab=repositories)"
    )
    return "<table>\n" + "\n".join(rows) + "\n</table>" + foot


def disk_svg(pin: dict, stars: int, tag: str, index: int) -> str:
    """Floppy-disk card for one project (Expansion-02 look, 288x270). Data-driven: name/tech/stars/tag."""
    name = str(pin.get("name") or "")
    tech = str(pin.get("tech") or "")
    accent = str(pin.get("accent") or UI_SAKURA)
    size = 21
    while size > 12 and len(name) * 0.62 * size > 207:
        size -= 1
    stat = f"★{fmt_num(stars)}" if stars else "no stars"
    if tag:
        stat += f"  ·  {tag}"
    writing = "".join(f'<path d="M92 {220 + i * 4} H196" fill="none" stroke="#322846" stroke-width="1"/>' for i in range(6))
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="288" height="270" viewBox="0 0 288 270" '
        'role="img" aria-label="' + esc(f"{name} release archive") + '" '
        "font-family=\"'Lucida Console',Consolas,'Courier New',monospace\">"
        '<rect x="9" y="8" width="270" height="252" fill="#21162F" stroke="#322846" stroke-width="2"/>'
        '<path d="M10 260 V9 H249 L278 38 V260" fill="none" stroke="#796080" stroke-width="1"/>'
        '<rect x="64" y="9" width="139" height="61" fill="#534658" stroke="#B4A5C8" stroke-width="1"/>'
        '<rect x="81" y="9" width="40" height="46" fill="#06020F"/>'
        '<rect x="134" y="17" width="55" height="40" fill="#837987" stroke="#322846" stroke-width="1"/>'
        '<rect x="26" y="89" width="233" height="115" fill="#EEE6D5" stroke="#241C2E" stroke-width="1"/>'
        f'<rect x="26" y="89" width="233" height="25" fill="{accent}"/>'
        f'<text x="37" y="106" font-size="9" fill="#241C2E">{esc(f"DISK {index:02d}  /  RELEASE ARCHIVE")}</text>'
        f'<text x="39" y="140" font-size="{size}" font-weight="700" fill="#241C2E">{esc(name)}</text>'
        f'<text x="39" y="164" font-size="12" fill="#51465B">{esc(tech[:30])}</text>'
        '<path d="M39 177 H245" fill="none" stroke="#9A8D83" stroke-width="1"/>'
        f'<text x="39" y="194" font-size="10" fill="#665567">{esc(stat)}</text>'
        f"{writing}"
        '<rect x="25" y="231" width="15" height="15" fill="#06020F" stroke="#322846" stroke-width="1"/>'
        '<rect x="248" y="231" width="15" height="15" fill="#06020F" stroke="#322846" stroke-width="1"/>'
        '<path d="M20.5 20.5 l3 3" fill="none" stroke="#B4A5C8" stroke-width="1"/>'
        '<path d="M261.5 245.5 l3 3" fill="none" stroke="#B4A5C8" stroke-width="1"/>'
        f'<text x="144" y="258" font-size="12" fill="{accent}" text-anchor="middle">[ OPEN REPO ]</text>'
        "</svg>"
    )


def disk_slug(name: str) -> str:
    return "disk-" + name.lower() + ".svg"


def render_project_disks(profile: dict, repos: dict[str, dict], tags: dict[str, str]) -> str:
    pins = list(profile.get("pin") or [])[:6]
    cells: list[str] = []
    for i, pin in enumerate(pins, 1):
        name = str(pin.get("name") or "")
        stars = int((repos.get(name) or {}).get("stargazers_count") or 0)
        tag = str(tags.get(name) or "")
        img = f"https://raw.githubusercontent.com/dwgx/DWGX/main/assets/{disk_slug(name)}"
        cells.append(
            '<td width="33%" valign="top" align="center">\n'
            f'<a href="https://github.com/dwgx/{name}">'
            f'<img src="{img}" width="100%" alt="{esc(name)} release archive" /></a>\n'
            "</td>"
        )
    rows: list[str] = []
    for i in range(0, len(cells), 3):
        rows.append("<tr>\n" + "\n".join(cells[i : i + 3]) + "\n</tr>")
    return "<table>\n" + "\n".join(rows) + "\n</table>"


def render_legacy_pins(profile: dict, repos: dict[str, dict]) -> str:
    pins = list(profile.get("pin") or [])[:6]
    cells = [f'<td width="33%" valign="top">\n\n{pin_box(p, repos)}\n\n</td>' for p in pins]
    rows: list[str] = []
    for i in range(0, len(cells), 3):
        rows.append("<tr>\n" + "\n".join(cells[i : i + 3]) + "\n</tr>")
    table = "<table>\n" + "\n".join(rows) + "\n</table>"
    return (
        "<details>\n"
        "<summary>原版 ASCII 卡片 / 设计快照（数字与阶段不是实时数据）</summary>\n\n"
        f"{table}\n\n"
        "</details>"
    )


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
        f'<text x="{width - 16}" y="18.0" text-anchor="end" font-size="13" font-weight="400" fill="{PANEL_MARK_COLOR}">{esc(PANEL_MARK)}</text>',
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


def http_json(url: str, timeout: int = 20, attempts: int = 3) -> dict | None:
    for i in range(attempts):
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 dwgx-profile-render"},
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
            return payload if isinstance(payload, dict) else None
        except (
            urllib.error.URLError,
            urllib.error.HTTPError,
            TimeoutError,
            json.JSONDecodeError,
            OSError,
        ):
            time.sleep(1.2 * (i + 1))
    return None


def fetch_presence(discord_id: str) -> dict:
    empty = {
        "status": "offline",
        "username": "dwgx",
        "display": "dwgx",
        "activity": "offline",
        "platform": "",
        "avatar": None,
        "stale": True,
    }
    if not discord_id:
        return empty
    for url in (
        f"https://api.lanyard.rest/v1/users/{discord_id}",
        f"https://lanyard.rest/v1/users/{discord_id}",
    ):
        payload = http_json(url)
        if not payload or payload.get("success") is False:
            continue
        data = payload.get("data") or {}
        if not (data.get("discord_user") or data.get("discord_status")):
            continue
        parsed = presence_from_lanyard(discord_id, data)
        parsed["stale"] = False
        PRESENCE_JSON.write_text(
            json.dumps(parsed, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return parsed
    cached = read_cached_presence()
    return cached or empty


def presence_from_lanyard(discord_id: str, data: dict) -> dict:
    user = data.get("discord_user") or {}
    status = str(data.get("discord_status") or "offline")
    acts = data.get("activities") or []
    activity = "idle" if status != "offline" else "offline"
    spotify = data.get("spotify") or {}
    if data.get("listening_to_spotify") and isinstance(spotify, dict):
        song = str(spotify.get("song") or "").strip()
        artist = str(spotify.get("artist") or "").strip()
        bits = [x for x in (song, artist) if x]
        activity = "Spotify · " + " — ".join(bits) if bits else "Spotify"
    else:
        for act in acts:
            name = (act.get("name") or "").strip()
            details = (act.get("details") or "").strip()
            state = (act.get("state") or "").strip()
            if name and name.lower() != "custom status":
                extra = details or state
                activity = f"{name} · {extra}" if extra else name
                break
            if state:
                activity = state
    platforms = []
    if data.get("active_on_discord_desktop"):
        platforms.append("desktop")
    if data.get("active_on_discord_mobile"):
        platforms.append("mobile")
    if data.get("active_on_discord_web"):
        platforms.append("web")
    avatar_hash = user.get("avatar")
    avatar_url = None
    if avatar_hash:
        avatar_url = (
            f"https://cdn.discordapp.com/avatars/{discord_id}/{avatar_hash}.png?size=128"
        )
    return {
        "status": status,
        "username": str(user.get("username") or "dwgx"),
        "display": str(user.get("global_name") or user.get("username") or "dwgx"),
        "activity": activity[:64],
        "platform": "+".join(platforms),
        "avatar": avatar_url,
    }


def read_cached_presence() -> dict | None:
    if not PRESENCE_JSON.exists():
        return None
    try:
        blob = json.loads(PRESENCE_JSON.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(blob, dict):
        return None
    blob["stale"] = True
    return blob


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


def discord_activity_line(presence: dict) -> str:
    status = str(presence.get("status") or "offline")
    activity = str(presence.get("activity") or "").strip()
    platform = str(presence.get("platform") or "").strip()
    if activity.lower() in {"", status, "offline", "idle"}:
        line = status
        if platform and status != "offline":
            line = f"{status} · {platform}"
        return line
    return activity


def discord_svg(host: str, presence: dict) -> str:
    width, height = 400, 110
    status = str(presence.get("status") or "offline")
    color = STATUS_COLOR.get(status, MUTED)
    display = str(presence.get("display") or "dwgx")
    username = str(presence.get("username") or "dwgx")
    platform = str(presence.get("platform") or "")
    where = f"@{username} · {status}"
    if platform:
        where = f"{where} · {platform}"
    line = discord_activity_line(presence)
    body: list[str] = []
    if AVATAR_PNG.exists():
        b64 = base64.b64encode(AVATAR_PNG.read_bytes()).decode("ascii")
        href = f"data:image/png;base64,{b64}"
        body.append(
            f'<image href="{href}" x="12" y="38" width="56" height="56"/>'
        )
        tx = 80
    else:
        body.append(f'<circle cx="24" cy="68" r="7" fill="{color}"/>')
        tx = 42
    body.extend(
        [
            f'<text x="{tx}" y="58" font-size="15" font-weight="700" fill="{TEXT}">{esc(display)}</text>',
            f'<text x="{tx}" y="76" font-size="12" fill="{MUTED}">{esc(where)}</text>',
            f'<text x="{tx}" y="94" font-size="12" fill="{PINK}">{esc(line)}</text>',
        ]
    )
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


def render_profile_nav() -> str:
    items = [
        ("#dwgxcfg", "配置"),
        ("#origingenesis", "ORIGIN"),
        ("#pinned", "项目"),
        ("#featured", "幻想万華鏡"),
        ("#eventlog", "留言"),
    ]
    links = " / ".join(f'<a href="{href}">{label}</a>' for href, label in items)
    return f'<p align="center"><samp>〔 {links} 〕</samp></p>'


# UI-04 网页里的装饰资产（Owner 2026-09-19：全部纳入）。这些是设计原件，静态 SVG。
ORNAMENTS = {
    "faceplate": "decor-faceplate.svg",
    "key-01": "decor-key-01.svg",
    "key-02": "decor-key-02.svg",
    "key-03": "decor-key-03.svg",
    "key-04": "decor-key-04.svg",
    "key-05": "decor-key-05.svg",
    "key-06": "decor-key-06.svg",
    "rail-01": "decor-rail-01.svg",
    "rail-02": "decor-rail-02.svg",
    "rail-03": "decor-rail-03.svg",
    "rail-04": "decor-rail-04.svg",
    "rail-05": "decor-rail-05.svg",
    "rail-06": "decor-rail-06.svg",
    "rail-07": "decor-rail-07.svg",
    "rail-08": "decor-rail-08.svg",
    "io-panel": "decor-io.svg",
    "phantasm": "decor-phantasm.svg",
    "eof": "decor-eof.svg",
    "stamp-bios": "decor-stamp-bios.svg",
    "stamp-ascii": "decor-stamp-ascii.svg",
    "stamp-touhou": "decor-stamp-touhou.svg",
    "stamp-dwgx": "decor-stamp-dwgx.svg",
    "media-aux": "exp-media-aux.svg",
}


def ornament(key: str, alt: str, width: str = "100%", href: str = "", outer: bool = True) -> str:
    """One static design asset, wrapped in machine-readable DWGX-ORNAMENT markers."""
    src = f"https://raw.githubusercontent.com/dwgx/DWGX/main/assets/{ORNAMENTS[key]}"
    img = f'<img src="{src}" width="{width}" alt="{esc(alt)}" />'
    if href:
        img = f'<a href="{href}">{img}</a>'
    block = f"<!-- DWGX-ORNAMENT:{key}:BEGIN -->\n<p align=\"center\">\n{img}\n</p>\n<!-- DWGX-ORNAMENT:{key}:END -->"
    return block if outer else img


def origin_panel_svg(profile: dict) -> str:
    """ORIGIN protocol plate — warm paper, gold rules. Deterministic: profile.toml only."""
    flag = profile.get("flagship") or {}
    concepts = list(profile.get("origin_concept") or [])[:4]
    name = str(flag.get("name") or "ORIGIN")
    kicker = str(flag.get("kicker") or "The Root Source")
    tagline = str(flag.get("zh_tagline") or "")
    host = str(flag.get("url") or "https://genesis.wiki").replace("https://", "")
    width, height = 920, 300
    serif = "'Noto Serif SC','Source Han Serif SC','Songti SC','SimSun',serif"
    mono = "ui-monospace,'Cascadia Mono',Consolas,'SF Mono',monospace"
    parts: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">',
        f'<rect width="{width}" height="{height}" rx="2" fill="{UI_PAPER}" '
        f'stroke="{UI_PAPER_LINE}" stroke-width="1"/>',
        f'<text x="44" y="52" font-family="{mono}" font-size="14" font-weight="700" '
        f'fill="{UI_PAPER_INDEX}" letter-spacing="2">{esc(name)} · {esc(kicker)}</text>',
        f'<text x="{width - 44}" y="52" font-family="{mono}" font-size="11" '
        f'fill="{UI_PAPER_INDEX}" text-anchor="end" letter-spacing="1">WORK IN PROGRESS</text>',
        f'<line x1="44" y1="72" x2="{width - 44}" y2="72" stroke="{UI_PAPER_LINE}" stroke-width="1"/>',
        f'<text x="44" y="132" font-family="{serif}" font-size="34" fill="{UI_PAPER_TEXT}">'
        f"{esc(tagline)}</text>",
        f'<line x1="44" y1="164" x2="{width - 44}" y2="164" stroke="{UI_PAPER_LINE}" stroke-width="1"/>',
    ]
    for i, concept in enumerate(concepts):
        x = 44 + i * 210
        parts.append(
            f'<text x="{x}" y="200" font-family="{mono}" font-size="12" '
            f'fill="{UI_PAPER_INDEX}">{i + 1:02d}</text>'
        )
        parts.append(
            f'<text x="{x + 30}" y="200" font-family="{mono}" font-size="15" font-weight="700" '
            f'fill="{UI_PAPER_TEXT}" letter-spacing="2">{esc(str(concept.get("key") or ""))}</text>'
        )
        parts.append(
            f'<text x="{x}" y="228" font-family="{serif}" font-size="13" fill="{UI_PAPER_TEXT}">'
            f'{esc(str(concept.get("desc") or ""))}</text>'
        )
    parts.append(
        f'<line x1="44" y1="252" x2="{width - 44}" y2="252" stroke="{UI_PAPER_LINE}" stroke-width="1"/>'
    )
    parts.append(
        f'<text x="44" y="276" font-family="{serif}" font-size="12" fill="{UI_PAPER_INDEX}">'
        "概念索引，不是四个同名 API。</text>"
    )
    parts.append(
        f'<text x="{width - 44}" y="276" font-family="{mono}" font-size="12" '
        f'fill="{UI_PAPER_INDEX}" text-anchor="end">{esc(host)}</text>'
    )
    parts.append("</svg>")
    return "".join(parts)


def boot_menu_keys() -> str:
    keys = [
        ("key-01", "#dwgxcfg", "MAIN — jump to section"),
        ("key-02", "#processtable", "PROCESS — jump to section"),
        ("key-03", "#origingenesis", "ORIGIN — jump to section"),
        ("key-04", "#pinned", "MODULES — jump to section"),
        ("key-05", "#featured", "PHANTASM — jump to section"),
        ("key-06", "#eventlog", "GUESTBOOK — jump to section"),
    ]
    imgs = "\n".join(
        f'<a href="{href}">{ornament(key, alt, "124", outer=False)}</a>' for key, href, alt in keys
    )
    return (
        '<a name="dwgx-boot-menu"></a>\n'
        "<!-- DWGX-ORNAMENT:boot-menu:BEGIN -->\n"
        f'<p align="center">\n{imgs}\n</p>\n'
        "<!-- DWGX-ORNAMENT:boot-menu:END -->"
    )


def render_origin_section(profile: dict) -> str:
    flag = profile.get("flagship") or {}
    concepts = list(profile.get("origin_concept") or [])
    name = str(flag.get("name") or "ORIGIN")
    title = str(flag.get("title") or "")
    blurb = str(flag.get("blurb") or "")
    url = str(flag.get("url") or "https://genesis.wiki")
    tagline = str(flag.get("zh_tagline") or "")
    intro = "\n\n".join(str(p) for p in (flag.get("zh_intro") or []))
    now = str(flag.get("zh_now") or "")
    far = str(flag.get("zh_far") or "")
    rows = "\n".join(
        f"| `{esc(str(c.get('key') or ''))}` | {esc(str(c.get('desc') or ''))} |" for c in concepts
    )
    img = "https://raw.githubusercontent.com/dwgx/DWGX/main/assets/origin-panel.svg"
    alt = f"{name} — {title}: {blurb}"
    return f"""### `origin.genesis`

<div align="center">

<img src="{img}" width="92%" alt="{esc(alt)}" />

<sub>{esc(title)}</sub>

*{esc(tagline)}*

</div>

{intro}

| 概念索引 | 含义 |
| :-- | :-- |
{rows}

这四项是介绍用的概念索引，不是四个同名 API，也不是固定调用顺序。

<details>
<summary>当前在推进什么 / 更远的方向</summary>

{now}

{far}

</details>

[打开 genesis.wiki →]({url})"""


def render_bbs_entry(gb: int, sign_href: str) -> str:
    """BBS entry block, placed inside the existing `event.log` section."""
    reply = sign_href if gb else "https://github.com/dwgx/DWGX/issues"
    thread = f"https://github.com/dwgx/DWGX/issues/{gb}" if gb else reply
    guest_label = f"回复 #{gb}" if gb else "打开 Issues"
    tail = f"[打开 Event Log #{gb}]({thread})" if gb else "[打开 Issues]({})".format(thread)
    return f"""留言，讨论，还有边做边写的记录。

| 频道 | 放什么 | 入口 |
| :-- | :-- | :-- |
| `GUESTBOOK` | 留一句话 | [{guest_label}]({reply}) |
| `TALK` | 聊问题、交换想法 | [打开 Issues](https://github.com/dwgx/DWGX/issues) |
| `DEVLOG` | 记录一次有意义的推进 | 列表未接入 · 先发在 Issues 里 |
| `PATCHES` | 真实的文件变更与审阅 | [主页仓库的 PR](https://github.com/dwgx/DWGX/pulls) |

<details>
<summary>写 DEVLOG / 使用约定</summary>

一个问题或一个阶段开一篇：写清这次想解决什么、改了什么、看到了什么结果、还不确定什么。代码改动留在所属项目仓库，这里链接原 PR 或做复盘。

留言正文在 GitHub 原帖阅读，首页不自动搬运每一条。所有内容公开，请不要贴密钥与私人资料。

</details>

没有接入的频道会直接写未接入，不用“0 条”代替未知。→ {tail}"""


def shield_stars(n: int) -> str:
    if n >= 1000:
        return f"{n/1000:.1f}k".replace(".0k", "k")
    return str(n)


def render_readme(profile: dict, ctx: dict) -> str:
    ident = profile["identity"]
    ship = profile.get("ship") or {}
    links = profile["links"]
    today = ctx["today"]
    stamp = ctx.get("stamp") or "00:00"
    bust = str(ctx.get("bust") or "0")
    n = ctx["process_count"]
    more = max(0, ctx["public_repos"] - 5)
    windsurf_stars = ctx["stars_map"].get("WindsurfAPI", 0)
    wtag = ctx["tags"].get("WindsurfAPI") or "v?"
    ktag = ctx["tags"].get("KiroStudio") or "v?"
    now = f"ORIGIN · WindsurfAPI {wtag} · KiroStudio {ktag}"
    gb = int((profile.get("guestbook") or {}).get("issue") or 0)
    genesis = links.get("genesis") or "https://genesis.wiki"
    sign_href = (
        f"https://github.com/dwgx/DWGX/issues/{gb}#issuecomment-new"
        if gb
        else "https://github.com/dwgx/DWGX/issues"
    )
    text = f"""<!-- ════════════════════════════════════════════════════════════════ -->
<!--  dwgx.menu  v{profile.get('version','2.2')}  ·  generated {today} {stamp} JST          -->
<!--  source: profile.toml  ·  renderer: scripts/render_profile.py     -->
<!-- ════════════════════════════════════════════════════════════════ -->

<img src="https://raw.githubusercontent.com/dwgx/DWGX/main/assets/bios-header.svg" width="100%" alt="dwgx.menu · AMIBIOS POST" />

{ornament('faceplate', 'dwgx.menu / personal-machine faceplate')}

<div align="center">

<img src="{links['qq_avatar']}" width="128" style="border-radius:50%;" />

<br/>

[![Typing SVG](https://readme-typing-svg.demolab.com?font=Noto+Serif+JP&weight=600&size=22&pause=1200&color={UI_SAKURA.lstrip('#')}&center=true&vCenter=true&random=false&width=620&lines=%E4%B9%9F%E8%AE%B8%E6%88%91%E5%B0%B1%E6%98%AFdwgx;WindsurfAPI+%C2%B7+KiroStudio+%C2%B7+ORIGIN;injected+into+process)](https://dwgx.github.io)

<p>
  <img src="https://komarev.com/ghpvc/?username=dwgx&style=flat-square&color={UI_SAKURA.lstrip('#')}&label=visits" />
  &nbsp;
  <img src="https://img.shields.io/github/followers/dwgx?style=flat-square&color={UI_SAKURA.lstrip('#')}&label=follow" />
  &nbsp;
  <img src="https://img.shields.io/github/stars/dwgx?style=flat-square&color={UI_GOLD.lstrip('#')}&label=stars" />
</p>

<p>
  <img src="https://img.shields.io/badge/total_stars-{ctx['total_stars']}-{UI_GOLD.lstrip('#')}?style=flat-square&labelColor={UI_INK.lstrip('#')}" />
  &nbsp;
  <img src="https://img.shields.io/badge/public_repos-{ctx['public_repos']}-{UI_SAKURA.lstrip('#')}?style=flat-square&labelColor={UI_INK.lstrip('#')}" />
  &nbsp;
  <img src="https://img.shields.io/github/stars/dwgx/WindsurfAPI?style=flat-square&color={UI_INK.lstrip('#')}&label=flagship%20WindsurfAPI" />
</p>

</div>

{boot_menu_keys()}

{render_profile_nav()}

---

{ornament('rail-01', 'SYSTEM CONFIGURATION')}

### `dwgx.cfg`

```ini
; {today} {stamp} JST

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

{ornament('rail-02', 'PROCESS MEMORY')}

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

### `cmos.book`

<details>
<summary>POST — CPU cache · memory test · IDE auto-detect</summary>
<p align="center"><img src="https://raw.githubusercontent.com/dwgx/DWGX/main/assets/post.svg" width="100%" alt="POST" /></p>
</details>

<details>
<summary>DMI — SMBIOS Type 0 BIOS · Type 1 system · Type 2 ROG · Type 3 Homecloud</summary>
<p align="center"><img src="https://raw.githubusercontent.com/dwgx/DWGX/main/assets/dmi.svg" width="100%" alt="DMI" /></p>
</details>

---

{ornament('rail-03', 'GENESIS CHAMBER')}

{render_origin_section(profile)}

---

{ornament('rail-04', 'EXPANSION SLOTS')}

<div align="center">

### `pinned`

{ctx['project_disks']}

{ctx['project_cards']}

<sub>六个项目，保留原名单与原顺序；磁盘卡是入口，文字卡给细节。</sub>

</div>

{ctx['legacy_pins']}

---

### `release.disks`

<p align="center">
<a href="https://github.com/dwgx/WindsurfAPI/releases"><img src="https://raw.githubusercontent.com/dwgx/DWGX/main/assets/exp-disk-windsurf.svg" width="260" alt="WindsurfAPI — release archive" /></a>
<a href="https://github.com/dwgx/KiroStudio/releases"><img src="https://raw.githubusercontent.com/dwgx/DWGX/main/assets/exp-disk-kiro.svg" width="260" alt="KiroStudio — release archive" /></a>
<a href="https://github.com/dwgx/SmartCLI/releases"><img src="https://raw.githubusercontent.com/dwgx/DWGX/main/assets/exp-disk-smartcli.svg" width="260" alt="SmartCLI — release archive" /></a>
</p>
<p align="center"><sub>发布档案入口 · 点开查看版本与说明</sub></p>

### `demo.deck`

<p align="center"><a href="https://github.com/dwgx/SmartCLI#driving-a-real-tui"><img src="https://raw.githubusercontent.com/dwgx/DWGX/main/assets/exp-demo-deck.svg" width="100%" alt="SmartCLI — open the existing project demonstration" /></a></p>

<details>
<summary>PLAY 01 · 看 SmartCLI 已有的 lazygit 演示</summary>

<p align="center"><a href="https://github.com/dwgx/SmartCLI#driving-a-real-tui"><img src="https://raw.githubusercontent.com/dwgx/SmartCLI/main/showcase/drive-lazygit.gif" width="700" alt="SmartCLI 项目已有的 lazygit TUI 演示；这是录制画面，不是实时终端" /></a></p>

演示来自 SmartCLI 仓库；这里没有新执行一次测试，也不把装饰图当成运行证据。

</details>

---

### `recent.log`

```
{ctx['recent']}
```

---

{ornament('rail-05', 'MACHINE INVENTORY')}

{ornament('io-panel', 'Decorative rear I/O panel')}

### `hardware.dmp`

```
{ctx['hardware']}
```

---

<div align="center">

### `discord.presence`

<a href="{links['discord']}">
<img src="https://raw.githubusercontent.com/dwgx/DWGX/main/assets/discord.svg" alt="discord presence" />
</a>

<br/>

<img src="https://raw.githubusercontent.com/dwgx/DWGX/main/assets/media.svg" alt="bili.stat" />

</div>

---

<div align="center">

{ornament('media-aux', 'NewAppleMusicPlayer — project link, decorative equalizer', '640', 'https://github.com/dwgx/NewAppleMusicPlayer')}

</div>

---

{ornament('rail-06', 'PHANTASM ARCHIVE')}

{ornament('phantasm', 'Touhou / The Memories of Phantasm danmaku ornament')}

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

<br/><br/>

[影像 / 作品 →]({links['bilibili']}) · [演示 / 留档 →]({links['youtube']})

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

{ornament('rail-07', 'ACTIVITY MEMORY')}

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

<p align="center">
<a href="{links['site']}"><img src="https://raw.githubusercontent.com/dwgx/DWGX/main/assets/key-del.svg" height="48" alt="DEL Setup" /></a>
<a href="{genesis}"><img src="https://raw.githubusercontent.com/dwgx/DWGX/main/assets/key-f2.svg" height="48" alt="F2 HDD-0 ORIGIN" /></a>
<a href="{links['youtube']}"><img src="https://raw.githubusercontent.com/dwgx/DWGX/main/assets/key-f8.svg" height="48" alt="F8 BBS YouTube" /></a>
<a href="{links['bilibili']}"><img src="https://raw.githubusercontent.com/dwgx/DWGX/main/assets/key-f9.svg" height="48" alt="F9 BBS Bilibili" /></a>
<img src="https://raw.githubusercontent.com/dwgx/DWGX/main/assets/key-f10.svg" height="48" alt="F10 maybe I'm dwgx" />
</p>

### `field.notes`

<p align="center">
<a href="{links['blog']}"><img src="https://raw.githubusercontent.com/dwgx/DWGX/main/assets/exp-ticket-blog.svg" width="260" alt="工程笔记 — public reading destination" /></a>
<a href="https://dwgx.github.io/WindsurfAPI/HISTORY-LEDGER-VIZ.html"><img src="https://raw.githubusercontent.com/dwgx/DWGX/main/assets/exp-ticket-ledger.svg" width="260" alt="WindsurfAPI 开发账本 — public reading destination" /></a>
<a href="{genesis}"><img src="https://raw.githubusercontent.com/dwgx/DWGX/main/assets/exp-ticket-genesis.svg" width="260" alt="ORIGIN 文档 — public reading destination" /></a>
</p>
<p align="center"><sub>笔记 · 开发记录 · 世界文档</sub></p>

{ornament('rail-08', 'BBS GUESTBOOK')}

### `event.log`

<p align="center">
<img src="https://raw.githubusercontent.com/dwgx/DWGX/main/assets/bbs-header.svg" width="100%" alt="DWGX BBS · 留言／讨论／DEVLOG／PR" />
</p>

<p align="center">
<a href="{sign_href}"><img src="https://raw.githubusercontent.com/dwgx/DWGX/main/assets/bbs-port-guest.svg" width="210" alt="留言大厅" /></a>
<a href="https://github.com/dwgx/DWGX/issues"><img src="https://raw.githubusercontent.com/dwgx/DWGX/main/assets/bbs-port-talk.svg" width="210" alt="讨论话题" /></a>
<a href="https://github.com/dwgx/DWGX/issues"><img src="https://raw.githubusercontent.com/dwgx/DWGX/main/assets/bbs-port-devlog.svg" width="210" alt="我的 DEVLOG" /></a>
<a href="https://github.com/dwgx/DWGX/pulls"><img src="https://raw.githubusercontent.com/dwgx/DWGX/main/assets/bbs-port-patch.svg" width="210" alt="改动与 PR" /></a>
</p>

{render_bbs_entry(gb, sign_href)}

<p align="center">
<a href="{sign_href}"><img src="https://raw.githubusercontent.com/dwgx/DWGX/main/assets/sign-log.svg" height="30" alt="F1 Sign Event Log" /></a>
</p>

<p align="center">
<img src="https://raw.githubusercontent.com/dwgx/DWGX/main/assets/guestbook.svg" width="100%" alt="event.log" />
</p>

<p align="center">
<img src="https://raw.githubusercontent.com/dwgx/DWGX/main/assets/marquee.svg" height="30" width="62%" alt="VGA marquee" />
<img src="https://raw.githubusercontent.com/dwgx/DWGX/main/assets/viewed.svg" height="30" alt="Best viewed with AMIBIOS" />
<img src="https://raw.githubusercontent.com/dwgx/DWGX/main/assets/vga.svg" height="30" alt="80x25 VGA" />
</p>

<p align="center">
<img src="https://raw.githubusercontent.com/dwgx/DWGX/main/assets/decor-stamp-bios.svg" width="88" alt="BIOS decorative web button" />
<img src="https://raw.githubusercontent.com/dwgx/DWGX/main/assets/decor-stamp-ascii.svg" width="88" alt="ASCII decorative web button" />
<img src="https://raw.githubusercontent.com/dwgx/DWGX/main/assets/decor-stamp-touhou.svg" width="88" alt="TOUHOU decorative web button" />
<img src="https://raw.githubusercontent.com/dwgx/DWGX/main/assets/decor-stamp-dwgx.svg" width="88" alt="DWGX decorative web button" />
</p>
<p align="center">
<a href="#dwgx-boot-menu"><img src="https://raw.githubusercontent.com/dwgx/DWGX/main/assets/decor-eof.svg" width="100%" alt="End of file — return to boot.menu" /></a>
</p>
"""
    out: list[str] = []
    needle = "https://raw.githubusercontent.com/dwgx/DWGX/"
    i = 0
    while True:
        j = text.find(needle, i)
        if j < 0:
            out.append(text[i:])
            break
        out.append(text[i:j])
        k = j
        while k < len(text) and text[k] not in '" >':
            k += 1
        url = text[j:k]
        if "?t=" not in url:
            url += f"?t={bust}"
        out.append(url)
        i = k
    return "".join(out)


def main() -> int:
    global PANEL_MARK, PANEL_MARK_COLOR
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
    stamp = hhmm_jst()
    bust = str(int(now_jst().timestamp()))
    host = prompt_host(profile)
    presence = fetch_presence(str((profile.get("links") or {}).get("discord_id") or ""))
    if presence.get("stale"):
        PANEL_MARK = "cached"
        PANEL_MARK_COLOR = MUTED
    else:
        PANEL_MARK = stamp
        PANEL_MARK_COLOR = GREEN
    SVG.parent.mkdir(parents=True, exist_ok=True)
    SVG.write_text(process_svg(profile, by_name, tags), encoding="utf-8")
    ORIGIN_SVG.write_text(origin_panel_svg(profile), encoding="utf-8")
    disk_files: list[str] = []
    for i, pin in enumerate((profile.get("pin") or [])[:6], 1):
        name = str(pin.get("name") or "")
        pin_stars = int((by_name.get(name) or {}).get("stargazers_count") or 0)
        tag = str(tags.get(name) or "")
        disk = ROOT / "assets" / disk_slug(name)
        disk.write_text(disk_svg(pin, pin_stars, tag, i), encoding="utf-8")
        disk_files.append(disk.name)
    STATS_SVG.write_text(stats_svg(host, user, stars, extra), encoding="utf-8")
    LANGS_SVG.write_text(langs_svg(host, extra.get("langs") or []), encoding="utf-8")
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
    book = ami_book.render_book(
        {
            "repos": by_name,
            "extra": extra,
            "tags": tags,
            "hardware": profile.get("hardware") or {},
            "langs": extra.get("langs") or [],
            "public": public,
            "stars": stars,
        }
    )
    for name, svg in book.items():
        (ROOT / "assets" / name).write_text(svg, encoding="utf-8")
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
    gb_issue = int((profile.get("guestbook") or {}).get("issue") or 0)
    gb_rows = fetch_event_log_rows(login, gb_issue, token)
    GUESTBOOK_SVG.write_text(guestbook_svg(gb_rows, gb_issue or 5), encoding="utf-8")
    ctx = {
        "today": today,
        "stamp": stamp,
        "bust": bust,
        "uptime": days,
        "public_repos": public,
        "total_stars": stars,
        "process_count": len(profile.get("process") or []),
        "recent": recent_log(events, by_name, overrides),
        "hardware": hardware_dump(profile, days),
        "project_cards": render_project_cards(profile, by_name, tags, public, stars),
        "project_disks": render_project_disks(profile, by_name, tags),
        "legacy_pins": render_legacy_pins(profile, by_name),
        "stars_map": {k: int(v.get("stargazers_count") or 0) for k, v in by_name.items()},
        "tags": tags,
        "hexdump": hex_dump_block(),
        "doing_line": doing_line[:110],
        "event_log": fetch_event_log(login, gb_issue, token),
    }
    README.write_text(render_readme(profile, ctx).rstrip() + "\n", encoding="utf-8")
    print(f"wrote {README.relative_to(ROOT)}")
    print(f"wrote {SVG.relative_to(ROOT)}")
    print(f"wrote {ORIGIN_SVG.relative_to(ROOT)}")
    print("wrote disks", ", ".join(disk_files))
    print(f"wrote {STATS_SVG.relative_to(ROOT)}")
    print(f"wrote {LANGS_SVG.relative_to(ROOT)}")
    print(f"wrote {DISCORD_SVG.relative_to(ROOT)}")
    print(f"wrote {MEDIA_SVG.relative_to(ROOT)}")
    print(f"wrote {SETUP_SVG.relative_to(ROOT)}")
    print(f"wrote {STATUS_SVG.relative_to(ROOT)}")
    print(f"wrote {DEVICES_SVG.relative_to(ROOT)}")
    print(f"wrote {EVENT_SVG.relative_to(ROOT)}")
    print(f"wrote {GUESTBOOK_SVG.relative_to(ROOT)}")
    print("wrote book", ", ".join(BOOK_NAMES))
    print(
        f"public_repos={public} stars={stars} uptime={days} "
        f"windsurf={tags['WindsurfAPI']} kiro={tags['KiroStudio']} "
        f"discord={presence.get('status')} stale={presence.get('stale')} "
        f"activity={presence.get('activity')}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
