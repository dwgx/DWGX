#!/usr/bin/env python3
"""The four deep data panels, drawn in the INK LAB hand: stats, langs, media,
discord.

Same signatures and the same data shapes as the four functions they replace in
`render_profile.py` (`stats_svg`, `langs_svg`, `media_svg`, `discord_svg`), so
the caller only swaps the import:

    from ink_panels_deep import stats_panel, langs_panel, media_panel, discord_panel

What is different from the panels they replace, and why:

* **960-unit canvases.** The old ones were 280/400/495 units wide carrying
  11-13px type, which measures 3.5-4.2 CSS px on a 309px phone. Every run here
  goes out through `M.type_line`, so the Latin >= 26 / CJK >= 38 unit floor in
  `repo-kit/ink.py` cannot be bypassed by accident.
* **Every measurement is the mono metric.** `M.mono_width` is 0.6em per glyph
  and is what a monospaced run is actually set at; `ink.text_width` is a
  Georgia-class serif metric and comes out ~20% narrow on mono, which is how a
  rule once struck straight through its own caption. CJK glyphs are full width
  in both faces, so `run_width` counts them at 1.0em instead.
* **A value that never arrived is an em dash plus a note.** `fetch_extra_stats`
  used to hand back zeros after a GraphQL failure and `fetch_bili` used to hand
  back `{"follower": 0, "following": 0}`, so a dead API rendered as a real `0`.
  The fetch layer now passes `None` for a failure (see render_profile.py); a
  genuine `0` still prints as `0`.
* **Each panel ends in `_selfcheck`.** The panel's own SVG is parsed back, every
  filled mark and every text run is reduced to a box, and a mark that intersects
  a run raises. Ink over a label is the failure that shipped once already.

Nothing outside this file is touched, and nothing here reads the network.
"""
from __future__ import annotations

import pathlib
import re
import sys
import tomllib
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

import make_ink_decor as M  # noqa: E402  (sys.path set above, on purpose)

ink = M.ink
TYPE, STROKE, SPACE, ALPHA, RULES = M.TYPE, M.STROKE, M.SPACE, M.ALPHA, M.RULES
INK, GOLD, AURORA = M.INK, M.GOLD, M.AURORA
VIOLET, LAPIS, ROSE, MUTED = M.VIOLET, M.LAPIS, M.ROSE, M.MUTED

# One band width for all four. The type floors in repo-kit/ink.py are measured at
# 960 units (0.873x on desktop, 0.322x on a 309px phone), so a panel that is not
# 960 units wide is a panel whose type was measured against the wrong scale.
W = 960

EM_DASH = "—"      # the mark for "no value", never a zero
MISS = "not fetched"  # and the words that say why

LANG_FLOOR = 0.01   # below 1% a language is noise on a hand-drawn bar
LANG_MAX = 8        # bars drawn; everything past this is summed into "other"

__all__ = ["stats_panel", "langs_panel", "media_panel", "discord_panel",
           "run_width", "selfcheck"]


# ── measuring ────────────────────────────────────────────────────────────────
def _cjk(ch: str) -> bool:
    return ord(ch) > 0x2E7F


def run_width(body, size: float, family: str = ink.MONO,
              tracking: float = 0.0) -> float:
    """Advance width of a text run, in the metric of the face it is set in.

    Monospaced runs go through the 0.6em mono metric. Serif runs go through the
    Georgia-class serif metric. CJK is 1.0em in both, and the size is the one
    `type_line` will actually use, CJK floor included.
    """
    body = str(body)
    if not body:
        return 0.0
    size = ink.type_for(body, size)
    if family == ink.MONO:
        em = sum(1.0 if _cjk(c) else 0.6 for c in body)
        return em * size + len(body) * tracking
    return ink.text_width(body, size) + len(body) * tracking


def fit(body, size: float, max_w: float, family: str = ink.MONO,
        tracking: float = 0.0) -> str:
    """`body` truncated with an ellipsis until it fits `max_w`, or "" if hopeless.

    `ink.text` does not wrap and does not clip, so an over-long run is the other
    way a panel can collide with itself. Every caller measures first.
    """
    body = str(body)
    if run_width(body, size, family, tracking) <= max_w:
        return body
    keep = body
    while keep and run_width(keep + "…", size, family, tracking) > max_w:
        keep = keep[:-1]
    return keep + "…" if keep else ""


def _num(value) -> str | None:
    """Thousands-separated text, or None when the value never arrived.

    `0` is a real zero and stays a zero. Only None/absent/unparseable is a miss.
    """
    if value is None or isinstance(value, bool):
        return None
    try:
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return None


def _absent(x: float, y: float, size: float, colour: str,
            gap: float = 16.0) -> list[str]:
    """An em dash where the number would be, plus the words that explain it.

    A dash on its own is just a gap; the note is what makes "not fetched"
    legible instead of looking like a zero with no ink behind it.
    """
    out = [M.type_line(x, y, EM_DASH, size, colour, ink.SERIF)]
    out.append(M.type_line(x + run_width(EM_DASH, size, ink.SERIF) + gap, y, MISS,
                           TYPE["micro"], MUTED, ink.MONO, tracking="2"))
    return out


# ── the self-check ───────────────────────────────────────────────────────────
_COORD = re.compile(r"(-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)")
_SVG_NS = "}"


def _box_of_d(d: str):
    """Bounding box of a brush outline. `brush`/`brush_rule` emit only M and L,
    so the coordinate pairs in `d` are the whole truth -- and they already carry
    the stroke's width envelope, so this is the ink box, not a centre line."""
    pts = [(float(a), float(b)) for a, b in _COORD.findall(d)]
    if not pts:
        return None
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return (min(xs), min(ys), max(xs), max(ys))


def _hits(a, b, slack: float = 0.5) -> bool:
    """True when two boxes overlap by more than a rounding error."""
    return (a[0] < b[2] - slack and b[0] < a[2] - slack
            and a[1] < b[3] - slack and b[1] < a[3] - slack)


def selfcheck(svg: str, panel: str, w: int = W, h: int | None = None) -> int:
    """Parse this panel's own output and prove no ink crosses any type.

    Returns the number of boxes checked. Raises ValueError naming the fill colour
    and the run that collide. The panel frame is decoration and is excluded by
    its extent; every other filled mark and every text run is checked.
    """
    root = ET.fromstring(svg)
    h = int(float(root.get("height") or w)) if h is None else h

    ink_boxes: list[tuple] = []
    text_boxes: list[tuple] = []
    for el in root.iter():
        tag = el.tag.split(_SVG_NS)[-1]
        if tag == "path":
            fill = el.get("fill")
            if not fill or fill == "none" or el.get("stroke") not in (None, "none"):
                continue  # a stroked path is a line, not a mark with a body
            box = _box_of_d(el.get("d") or "")
            if box is None:
                continue
            if (box[2] - box[0]) >= w * 0.8 and (box[3] - box[1]) >= h * 0.8:
                continue  # the panel frame
            ink_boxes.append((box, fill))
        elif tag == "text":
            body = "".join(el.itertext())
            size = float(el.get("font-size") or TYPE["label"])
            family = el.get("font-family") or ink.SERIF
            adv = run_width(body, size, family, float(el.get("letter-spacing") or 0))
            x = float(el.get("x") or 0)
            if (el.get("text-anchor") or "start") == "end":
                x -= adv
            y = float(el.get("y") or 0)
            text_boxes.append(((x, y - size * 0.78, x + adv, y + size * 0.24), body))

    bad = [f"{fill} mark {tuple(round(v, 1) for v in box)} over {body!r}"
           for box, fill in ink_boxes for tbox, body in text_boxes
           if _hits(box, tbox)]
    if bad:
        raise ValueError(f"{panel}: ink crosses type -- " + "; ".join(bad))
    return len(ink_boxes) + len(text_boxes)


# ── 1. stats ─────────────────────────────────────────────────────────────────
def stats_panel(host: str, user: dict, stars, extra: dict) -> str:
    """The account totals this page owns, set at display size.

    `user` is GET /users/dwgx, `stars` the summed star count, `extra` the
    GraphQL block. These six numbers live here and nowhere else -- POST, the
    boot order and the process board all used to reprint them.
    """
    user = user or {}
    extra = extra or {}
    follow = extra.get("followers")
    if follow is None:  # GraphQL has no answer -> REST did
        follow = user.get("followers")
    rows = [
        ("Total Stars", _num(stars), GOLD),
        ("Public Repos", _num(user.get("public_repos")), AURORA),
        ("Followers", _num(follow), INK),
        ("Pull Requests", _num(extra.get("prs")), LAPIS),
        ("Commits (year)", _num(extra.get("commits_year")), ROSE),
        ("Issues", _num(extra.get("issues")), VIOLET),
    ]

    h = 392
    body: list[str] = []
    for i, (name, value, colour) in enumerate(rows):
        x = (26, 348, 670)[i % 3]
        y = 124 + (i // 3) * 128
        body.append(M.type_line(x, y, name, TYPE["micro"], MUTED, ink.MONO,
                                tracking="2"))
        if value is None:
            body += _absent(x, y + 54, TYPE["display"], colour)
        else:
            body.append(M.type_line(x, y + 54, value, TYPE["display"], colour,
                                    ink.SERIF))
    body.append(M.type_line(W - 26, 46, "github.com/dwgx", TYPE["micro"], MUTED,
                            ink.MONO, anchor="end", tracking="2"))
    body.append(ink.brush_rule(26, W - 26, 214, width=STROKE["hair"], seed=13,
                             colour=INK, opacity=ALPHA["ghost"]))
    body.append(ink.brush_rule(26, W - 26, 344, width=STROKE["hair"], seed=17,
                             colour=INK, opacity=ALPHA["faint"]))
    body.append(M.type_line(26, 370, host, TYPE["micro"], MUTED, ink.MONO,
                            tracking="2"))

    svg = M.doc(W, h, "stats.panel",
                M.panel_doc(W, h, "stats.panel", "") + "".join(body))
    selfcheck(svg, "stats.panel", W, h)
    return svg


# ── 2. langs ─────────────────────────────────────────────────────────────────
def _size(lang: dict) -> int:
    try:
        return int(lang.get("size") or 0)
    except (TypeError, ValueError):
        return 0


def langs_panel(host: str, langs, metric: str = "bytes") -> str:
    """Byte share per language as hand-drawn bars, longest share first.

    Bars are brush strokes, not rects: a rect reads as a table cell and this is
    a sketch. Anything under 1% and anything past the eighth bar is summed into
    one `other` row, so the bars always add up to the number printed above them.

    `metric` names the denominator being drawn. It is a parameter because the two
    are indistinguishable in the artwork: the fetch layer falls back to counting
    *repositories* when it has no token, the chart looks exactly the same, and
    the percentages then mean something else entirely. Pass "repos" for that
    case and the panel says so.
    """
    rows_src = [l for l in (langs or []) if _size(l) > 0]
    total = sum(_size(l) for l in rows_src)
    unit = "BYTES" if metric == "bytes" else "REPOS"

    if not rows_src or total <= 0:
        h = 300
        body = _absent(26, 150, TYPE["display"], MUTED)
        body.append(M.type_line(W - 26, 46, "no language data", TYPE["micro"],
                                MUTED, ink.MONO, anchor="end", tracking="2"))
        body.append(ink.brush_rule(26, W - 26, 214, width=STROKE["hair"], seed=13,
                                 colour=INK, opacity=ALPHA["ghost"]))
        body.append(M.type_line(26, 250, host, TYPE["micro"], MUTED, ink.MONO,
                                tracking="2"))
        svg = M.doc(W, h, "langs.panel",
                    M.panel_doc(W, h, "langs.panel", "") + "".join(body))
        selfcheck(svg, "langs.panel", W, h)
        return svg

    ranked = sorted(rows_src, key=_size, reverse=True)
    keep: list[dict] = []
    rest = 0
    for lang in ranked:
        if len(keep) < LANG_MAX and _size(lang) / total >= LANG_FLOOR:
            keep.append(lang)
        else:
            rest += _size(lang)

    # first pass: what the names will actually be, so the bar column can be
    # measured off the longest one instead of a guess
    char = TYPE["micro"] * 0.6 + 2
    names = [fit(str(l.get("name") or "?"), TYPE["micro"], 15 * char, ink.MONO, 2)
             for l in keep]
    if rest:
        names.append("other")
    rows_n = len(names)

    top, row_h = 132, 40
    h = top + rows_n * row_h + 66
    bar_x = 26 + max(run_width(n, TYPE["micro"], ink.MONO, 2) for n in names) + 28
    pct_w = run_width("100%", TYPE["micro"], ink.MONO, 2)
    bar_w = (W - 26 - pct_w - 28) - bar_x

    body = [M.type_line(W - 26, 46, f"{total:,} {unit.lower()}", TYPE["micro"],
                        GOLD, ink.MONO, anchor="end", tracking="2"),
            M.type_line(26, 104, "LANGUAGE", TYPE["micro"], MUTED, ink.MONO,
                        tracking="4"),
            M.type_line(W - 26, 104, f"SHARE OF {unit}", TYPE["micro"], MUTED,
                        ink.MONO, anchor="end", tracking="4")]

    shares = [_size(l) / total for l in keep] + ([rest / total] if rest else [])
    colours = [str(l.get("color") or GOLD) for l in keep] + [MUTED]
    for i, (name, share, colour) in enumerate(zip(names, shares, colours)):
        y = top + i * row_h
        bar_y = y - 8
        body.append(M.type_line(26, y, name, TYPE["micro"], INK, ink.MONO,
                                tracking="2"))
        body.append(ink.brush_rule(bar_x, bar_x + bar_w, bar_y, width=STROKE["fine"],
                                 seed=37 + i, colour=MUTED,
                                 opacity=ALPHA["faint"], enter=0.02, exit_=0.02))
        body.append(ink.brush_rule(bar_x, bar_x + max(bar_w * share, 16.0), bar_y,
                                 width=STROKE["body"], seed=101 + i, colour=colour,
                                 enter=0.02, exit_=0.04))
        body.append(M.type_line(W - 26, y, f"{share * 100:.0f}%", TYPE["micro"],
                                GOLD, ink.MONO, anchor="end", tracking="1"))

    body.append(ink.brush_rule(26, W - 26, h - 48, width=STROKE["hair"], seed=17,
                             colour=INK, opacity=ALPHA["faint"]))
    body.append(M.type_line(26, h - 20, host, TYPE["micro"], MUTED, ink.MONO,
                            tracking="2"))
    body.append(M.type_line(W - 26, h - 20, f"denominator: {metric}", TYPE["micro"],
                            MUTED, ink.MONO, anchor="end", tracking="2"))

    svg = M.doc(W, h, "langs.panel",
                M.panel_doc(W, h, "langs.panel", "") + "".join(body))
    selfcheck(svg, "langs.panel", W, h)
    return svg


# ── 3. media ─────────────────────────────────────────────────────────────────
_LINKS: dict | None = None


def _links() -> dict:
    """profile.toml's [links], read once.

    The old media panel hardcoded `space.bilibili.com/1452905012`, so editing
    `links.bilibili` in profile.toml never moved it. Reading the file is honest,
    and failing to read it drops the line rather than printing a stale address.
    """
    global _LINKS
    if _LINKS is None:
        try:
            with open(ROOT / "profile.toml", "rb") as fh:
                _LINKS = tomllib.load(fh).get("links") or {}
        except (OSError, ValueError):
            _LINKS = {}
    return _LINKS


def media_panel(host: str, data, url: str = "") -> str:
    """Bilibili followers and following, and whether the API answered at all.

    `data` is the fetch block: a real zero is a zero, a failed fetch is None (or
    carries an "error") and prints an em dash with the reason beside it. The old
    panel turned a network failure into "0 fans", which no reader could tell
    from an account nobody follows.
    """
    data = data or {}
    failed = bool(data.get("error")) or data.get("ok") is False

    def pick(key):
        return None if failed else data.get(key)

    space = fit((url or str(_links().get("bilibili") or "")).replace("https://", "")
                or "", TYPE["micro"], (W - 26 - 200) * 1.0, ink.MONO, 2)
    live = not failed and pick("follower") is not None and pick("following") is not None

    h = 330
    body: list[str] = []
    for i, (name, key, colour) in enumerate(
            (("Followers", "follower", ROSE), ("Following", "following", GOLD))):
        x = 26 + i * 322
        value = _num(pick(key))
        body.append(M.type_line(x, 128, name, TYPE["micro"], MUTED, ink.MONO,
                                tracking="2"))
        if value is None:
            body += _absent(x, 182, TYPE["display"], colour)
        else:
            body.append(M.type_line(x, 182, value, TYPE["display"], colour,
                                    ink.SERIF))

    # the presence signal: a hand-drawn ring, solid when the API answered and
    # broken when it did not. This panel is two numbers and a sign of life.
    body += _signal(760, 150, 46, live, seed=53)
    body.append(M.type_line(760, 232, "reachable" if live else MISS, TYPE["micro"],
                            AURORA if live else MUTED, ink.MONO, anchor="middle",
                            tracking="2"))

    body.append(M.type_line(W - 26, 46, f"bili_mid {_links().get('bili_mid', '')}".strip(),
                            TYPE["micro"], MUTED, ink.MONO, anchor="end",
                            tracking="2"))
    body.append(ink.brush_rule(26, W - 26, 246, width=STROKE["hair"], seed=13,
                               colour=INK, opacity=ALPHA["ghost"]))
    if space:
        body.append(M.type_line(26, 278, space, TYPE["micro"], INK, ink.MONO,
                                tracking="2"))
    body.append(M.type_line(26, 306, host, TYPE["micro"], MUTED, ink.MONO,
                            tracking="2"))

    svg = M.doc(W, h, "bili.stat", M.panel_doc(W, h, "bili.stat", "") + "".join(body))
    selfcheck(svg, "bili.stat", W, h)
    return svg


def _signal(cx: float, cy: float, r: float, on: bool, seed: int) -> list[str]:
    """A ring that answers the only question this panel really asks: is the
    account there? Solid when yes, dashed when no -- shape, not just colour."""
    if on:
        return [ink.path(ink.circle(cx, cy, r, seed=seed, w=0.035), GOLD,
                         STROKE["fine"], ALPHA["full"]),
                ink.path(ink.circle(cx, cy, r * 0.34, seed=seed + 3, w=0.05),
                         GOLD, STROKE["fine"], ALPHA["soft"])]
    return [ink.path(d, MUTED, STROKE["fine"], ALPHA["soft"])
            for d in ink.dashed_ellipse(cx, cy, r, r, dash_count=14, seed=seed,
                                        w=0.05)]


# ── 4. discord ───────────────────────────────────────────────────────────────
_STATUS_INK = {"online": INK, "idle": GOLD, "dnd": ROSE}
_STATUS_RING = {"online": "solid", "idle": "dashed", "dnd": "solid",
                "offline": "dashed"}


def _activity_line(presence: dict) -> str:
    """The activity, or "" when Lanyard only echoed the status back.

    The old panel printed the same word twice -- `offline` in the identity line
    and `offline` again as the activity line. An activity earns its own line
    only when it says something the status does not.
    """
    status = str(presence.get("status") or "").strip()
    activity = str(presence.get("activity") or "").strip()
    if activity.lower() in {"", status.lower(), "offline", "idle"}:
        return ""
    return activity


def discord_panel(host: str, presence: dict) -> str:
    """Who this is, and whether they are at the keyboard right now.

    The old panel inlined a base64 PNG avatar -- the bulk of the file -- for a
    56px square. The status is the part that matters, so it is drawn: a solid
    ring when the account is live, a broken one when it is away or the answer
    came off the on-disk cache, and the signal survives with no image bytes.
    """
    presence = presence or {}
    status = str(presence.get("status") or "").strip()
    username = str(presence.get("username") or "").strip()
    display = str(presence.get("display") or username).strip()
    platform = str(presence.get("platform") or "").strip()
    stale = bool(presence.get("stale"))
    activity = _activity_line(presence) if status else ""

    live = status == "online" and not stale
    ring = "solid" if (_STATUS_RING.get(status, "dashed") == "solid" and not stale) \
        else "dashed"
    colour = _STATUS_INK.get(status, MUTED)

    right_x = 214
    max_w = W - 26 - right_x
    h = 318
    body: list[str] = []

    if ring == "solid":
        body.append(ink.path(ink.circle(104, 170, 56, seed=59, w=0.03),
                             colour, STROKE["fine"], ALPHA["full"]))
    else:
        body += [ink.path(d, colour, STROKE["fine"], ALPHA["soft"])
                 for d in ink.dashed_ellipse(104, 170, 56, 56, dash_count=16,
                                             seed=59, w=0.04)]
    if live:  # the aerosol only appears when somebody is actually there
        body += ink.spray(104, 170, 46, n=14, seed=61, colour=colour, density=0.5)
    if display:
        body.append(M.type_line(104, 182, display[0], TYPE["title"], colour,
                                ink.SERIF, anchor="middle"))
    else:
        body.append(M.type_line(104, 182, EM_DASH, TYPE["title"], colour,
                                ink.SERIF, anchor="middle"))

    body.append(M.type_line(104, 252, fit(status or EM_DASH, TYPE["micro"], 168,
                                          ink.MONO, 1), TYPE["micro"], colour,
                            ink.MONO, anchor="middle", tracking="1"))

    if display:
        body.append(M.type_line(right_x, 148, fit(display, TYPE["title"], max_w,
                                                  ink.SERIF), TYPE["title"], INK,
                                ink.SERIF))
    else:
        body += _absent(right_x, 148, TYPE["title"], MUTED)

    where = f"@{username}" if username else ""
    if status:
        where += f" · {status}"
    if platform:
        where += f" · {platform}"
    if where:
        body.append(M.type_line(right_x, 182, fit(where, TYPE["micro"], max_w,
                                                  ink.MONO, 2), TYPE["micro"],
                                MUTED, ink.MONO, tracking="2"))
    if activity:
        body.append(M.type_line(right_x, 220, fit(activity, TYPE["label"], max_w,
                                                  ink.SERIF), TYPE["label"], GOLD,
                                ink.SERIF))

    # provenance, not status: a stale answer is called out in the header, where
    # the ring caption still has room to say what the status actually is
    body.append(M.type_line(W - 26, 46, "lanyard · cached" if stale else "lanyard",
                            TYPE["micro"], ROSE if stale else MUTED, ink.MONO,
                            anchor="end", tracking="2"))
    body.append(ink.brush_rule(26, W - 26, 274, width=STROKE["hair"], seed=13,
                               colour=INK, opacity=ALPHA["ghost"]))
    body.append(M.type_line(26, 298, host, TYPE["micro"], MUTED, ink.MONO,
                            tracking="2"))

    svg = M.doc(W, h, "discord.presence",
                M.panel_doc(W, h, "discord.presence", "") + "".join(body))
    selfcheck(svg, "discord.presence", W, h)
    return svg
