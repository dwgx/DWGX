"""Small paper components for the profile; data in, SVG out, no network access.

The relief uses the same GitHub calendar as the existing heatmap.  If that fetch
is unavailable, keep the already generated relief.  Its first fallback may read
the checked-in heatmap's actual cells; no missing day gets a fabricated count.
"""
from __future__ import annotations

from datetime import date
from html import escape
from pathlib import Path
import math
import re
import unicodedata
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
PAPER = "#F4EFE6"
INK = "#2A2320"
CLAY = "#A8452C"
MUTED = "#6B5647"
RULE = "#D6C8B6"
MONO = "ui-monospace,Consolas,'Liberation Mono',monospace"
SERIF = "Georgia,'Noto Serif CJK SC','Songti SC',serif"
LEVELS = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2,
          "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}
TOPS = ("#E4D9C8", "#D5AF8F", "#C48462", "#B16042", CLAY)
LEFTS = ("#CFC0AC", "#BC9276", "#A96647", "#914D34", "#853823")
RIGHTS = ("#D9CBB7", "#C69C7F", "#B37454", "#9E5438", "#943D26")


def _esc(value: object) -> str:
    return escape(str(value), quote=True)


def _fit(value: object, max_width: float, size: float) -> str:
    """Conservative monospace fit including full-width CJK characters."""
    value = str(value)
    used = 0.0
    result = []
    for char in value:
        step = size if unicodedata.east_asian_width(char) in {"F", "W"} else size * .61
        if used + step > max_width - size:
            return "".join(result).rstrip() + "…"
        result.append(char)
        used += step
    return value


def _number(value: object) -> str:
    if isinstance(value, (int, float)) and not isinstance(value, bool) and value >= 0:
        return f"{int(value):,}"
    return "—"


def _text(x: float, y: float, body: object, size: float = 14, colour: str = INK,
          anchor: str = "start", family: str = MONO, extra: str = "") -> str:
    return (f'<text x="{x:g}" y="{y:g}" fill="{colour}" font-size="{size:g}" '
            f'font-family="{family}" text-anchor="{anchor}"{extra}>{_esc(body)}</text>')


def _open(width: int, height: int, title: str, desc: str) -> list[str]:
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
            f'<title id="title">{_esc(title)}</title><desc id="desc">{_esc(desc)}</desc>',
            f'<rect width="{width}" height="{height}" fill="{PAPER}"/>',
            f'<path d="M0 .5H{width}M0 {height-.5:g}H{width}" fill="none" stroke="{RULE}"/>']


def overview_strip(profile: dict, ctx: dict) -> str:
    """A 960 × 128 overview from the renderer's existing, fetched context."""
    work = str(ctx.get("doing_line") or "")
    tags = ctx.get("tags") or {}
    releases = "  ·  ".join(f"{name} {tags[name]}" for name in ("WindsurfAPI", "KiroStudio")
                              if tags.get(name))
    if not releases:
        releases = str((profile.get("identity") or {}).get("note") or "")
    stamp = " ".join(str(ctx.get(k) or "") for k in ("today", "stamp")).strip()
    stamp = f"{stamp} JST" if stamp else ""
    description = " · ".join(x for x in [work, releases, stamp] if x)
    p = _open(960, 128, "dwgx · recent public work", description)
    p.append(f'<path d="M24 22v12" stroke="{CLAY}" stroke-width="3"/>')
    p.append(_text(36, 32, "RECENT PUBLIC WORK", 12, MUTED,
                   extra=' letter-spacing="1.6"'))
    if stamp:
        p.append(_text(936, 32, stamp, 12, MUTED, "end"))
    p.append(_text(24, 67, _fit(work, 570, 18) if work else "—", 18))
    p.append(f'<path d="M620 51v54" stroke="{RULE}"/>')
    for y, name in ((66, "WindsurfAPI"), (98, "KiroStudio")):
        p.append(_text(650, y, name, 13, MUTED))
        p.append(_text(936, y, _fit(tags.get(name) or "—", 155, 16), 16, INK, "end"))
    p.append("</svg>")
    return "".join(p)


def overview_strip_mobile(profile: dict, ctx: dict) -> str:
    """A 480 × 190 companion, intended for a native README picture source."""
    work = str(ctx.get("doing_line") or "")
    tags = ctx.get("tags") or {}
    stamp = " ".join(str(ctx.get(k) or "") for k in ("today", "stamp")).strip()
    stamp = f"{stamp} JST" if stamp else ""
    p = _open(480, 190, "dwgx · recent public work", " · ".join(x for x in (work, stamp) if x))
    p.append(f'<path d="M20 20v12" stroke="{CLAY}" stroke-width="3"/>')
    p.append(_text(32, 30, "RECENT PUBLIC WORK", 12, MUTED,
                   extra=' letter-spacing="1.3"'))
    first = _fit(work, 438, 18) if work else "—"
    if first.endswith("…"):
        # Preserve the continuation instead of dropping useful public activity.
        raw = first[:-1]
        split = raw.rfind(" · ")
        if split > 12:
            raw = raw[:split]
        first = raw
        rest = work[len(raw):].lstrip(" ·")
    else:
        rest = ""
    p.append(_text(20, 61, first, 18))
    if rest:
        p.append(_text(20, 84, _fit(rest, 438, 16), 16))
    p.append(f'<path d="M20 101H460" stroke="{RULE}"/>')
    for y, name in ((125, "WindsurfAPI"), (150, "KiroStudio")):
        p.append(_text(20, y, name, 13, MUTED))
        p.append(_text(460, y, _fit(tags.get(name) or "—", 250, 15), 15, INK, "end"))
    if stamp:
        p.append(_text(20, 178, stamp, 11, MUTED))
    p.append("</svg>")
    return "".join(p)


def _calendar_cells(calendar: dict | None) -> tuple[list[dict], int | None, str, str]:
    weeks = (calendar or {}).get("weeks") or []
    cells: list[dict] = []
    for col, week in enumerate(weeks[-53:]):
        for item in (week.get("contributionDays") or []):
            try:
                day = date.fromisoformat(str(item["date"]))
            except (KeyError, TypeError, ValueError):
                continue
            count = item.get("contributionCount")
            count = count if isinstance(count, int) and not isinstance(count, bool) and count >= 0 else None
            raw = item.get("contributionLevel")
            level = LEVELS.get(str(raw))
            if level is None:
                # An absent level is not a zero-contribution observation.
                if count is None:
                    continue
                level = 0 if count == 0 else 1
            cells.append({"col": col, "row": (day.weekday() + 1) % 7,
                          "level": level, "count": count, "date": day.isoformat()})
    if not cells:
        return [], None, "", ""
    total = (calendar or {}).get("totalContributions")
    if not isinstance(total, int) or isinstance(total, bool) or total < 0:
        total = sum(c["count"] for c in cells) if all(c["count"] is not None for c in cells) else None
    dates = [c["date"] for c in cells]
    return cells, total, min(dates), max(dates)


def _heatmap_cells() -> tuple[list[dict], int | None, str, str]:
    """Read the existing engine's fixed 34-unit heatmap cells and its legend.

    This fallback preserves only observed levels and the printed total; the
    original SVG does not contain per-day counts or exact dates.
    """
    try:
        root = ET.parse(ROOT / "assets" / "heatmap.svg").getroot()
    except (OSError, ET.ParseError):
        return [], None, "", ""
    shapes = []
    total = None
    for node in root.iter():
        if node.tag.endswith("text") and node.text:
            m = re.fullmatch(r"([\d,]+) TOTAL", node.text.strip())
            if m:
                total = int(m.group(1).replace(",", ""))
        if not node.tag.endswith("path") or node.get("fill") in {None, "none"}:
            continue
        data = node.get("d") or ""
        if re.search(r"[ACQSTVHZacqstvhz]", data.rstrip("Zz ")):
            continue
        points = [float(n) for n in re.findall(r"-?\d+(?:\.\d+)?", data)]
        if len(points) < 6 or len(points) % 2:
            continue
        xs, ys = points[::2], points[1::2]
        if not (17 < max(xs) - min(xs) < 30 and 17 < max(ys) - min(ys) < 30):
            continue
        shapes.append(((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, node.get("fill")))
    legend = sorted((x, colour) for x, y, colour in shapes if abs(y - 374) < 3 and 150 < x < 320)
    if len(legend) != 5:
        return [], None, "", ""
    levels = {colour: i for i, (_, colour) in enumerate(legend)}
    cells = []
    for x, y, colour in shapes:
        col, row = round((x - 105) / 34), round((y - 109) / 34)
        if (colour in levels and 0 <= col < 53 and 0 <= row < 7
                and abs(x - (105 + col * 34)) < 3 and abs(y - (109 + row * 34)) < 3):
            cells.append({"col": col, "row": row, "level": levels[colour],
                          "count": None, "date": ""})
    return cells, total, "", ""


def _points(points: list[tuple[float, float]]) -> str:
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in points)


def contribution_relief(calendar: dict | None) -> str:
    """A 960 × 400 isometric calendar, using counts when supplied, else levels.

    An unavailable calendar keeps the previous SVG byte-for-byte.  On first
    construction only, a checked-in heatmap may supply the observed levels.
    Return an empty string if neither actual source exists; callers should then
    leave an existing file untouched and omit a new image reference.
    """
    cells, total, start, end = _calendar_cells(calendar)
    source = "GitHub contribution calendar"
    if not cells:
        existing = ROOT / "assets" / "contribution-relief.svg"
        if existing.exists():
            return existing.read_text(encoding="utf-8")
        cells, total, start, end = _heatmap_cells()
        source = "assets/heatmap.svg · existing calendar snapshot"
    if not cells:
        return ""
    cols = max(c["col"] for c in cells) + 1
    measured = all(c["count"] is not None for c in cells)
    max_count = max((c["count"] or 0) for c in cells)
    mode = "height = √ daily contributions" if measured else "height = GitHub contribution level"
    description = (f"{source}. {cols} weeks. {mode}. "
                   + (f"{total:,} contributions. " if total is not None else "")
                   + (f"{start} to {end}." if start else ""))
    p = _open(960, 400, "dwgx · contribution relief", description)
    p.append(_text(30, 36, "CONTRIBUTION RELIEF", 12, MUTED,
                   extra=' letter-spacing="2"'))
    p.append(_text(30, 75, "日々の記録", 28, INK, family=SERIF))
    if total is not None:
        p.append(_text(930, 55, f"{total:,}", 32, INK, "end", SERIF))
        p.append(_text(930, 76, "contributions", 12, MUTED, "end"))
    p.append(f'<path d="M30 95H930" stroke="{RULE}" fill="none"/>')

    # A shallow oblique projection leaves every week visible at profile width.
    # There are no filters or animation timers: all geometry is useful ink.
    vx, vy, ux, uy = 14.1, 2.45, -9.0, 7.4
    ox = (960 - ((cols - 1) * vx + 14.1 + 7 * 9.0)) / 2 + 7 * 9.0
    oy = 164.0
    for cell in sorted(cells, key=lambda c: (c["col"] * vy + c["row"] * uy, c["col"])):
        level = cell["level"]
        count = cell["count"]
        if measured and max_count:
            height = 2 if not count else 5 + 60 * math.sqrt(count / max_count)
        else:
            height = (2, 11, 25, 43, 66)[level]
        x, y = ox + cell["col"] * vx + cell["row"] * ux, oy + cell["col"] * vy + cell["row"] * uy
        # Slight gutters distinguish the 371 daily tiles without heavy outlines.
        a, b = (x, y - height), (x + vx * .88, y + vy * .88 - height)
        c, d = (b[0] + ux * .88, b[1] + uy * .88), (x + ux * .88, y + uy * .88 - height)
        tip = cell["date"] or f"week {cell['col'] + 1}, weekday {cell['row'] + 1}"
        tip += f": {count} contributions" if count is not None else f": level {level}/4"
        p.append(f'<g><title>{_esc(tip)}</title>')
        p.append(f'<polygon points="{_points([d, c, (c[0],c[1]+height), (d[0],d[1]+height)])}" fill="{LEFTS[level]}"/>')
        p.append(f'<polygon points="{_points([b, c, (c[0],c[1]+height), (b[0],b[1]+height)])}" fill="{RIGHTS[level]}"/>')
        p.append(f'<polygon points="{_points([a,b,c,d])}" fill="{TOPS[level]}"/></g>')
    p.append(f'<path d="M30 352H930" stroke="{RULE}" fill="none"/>')
    footer = f"{start} — {end}" if start else f"{cols} weeks · calendar snapshot"
    p.append(_text(30, 380, footer, 12, MUTED))
    p.append(_text(703, 380, "LESS", 10, MUTED, "end"))
    for i, colour in enumerate(TOPS):
        x = 718 + i * 29
        p.append(f'<path d="M{x} 369l12 3-7 6-12-3Z" fill="{colour}"/>')
    p.append(_text(875, 380, "MORE", 10, MUTED))
    p.append("</svg>")
    return "".join(p)
