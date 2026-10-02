#!/usr/bin/env python3
"""POST and DMI, redrawn as INK LAB panels.

Two real defects get fixed by writing this module, both recorded in
ops/CONTRACT-data-panels-2026-10-02.md:

  * ``ami_book.dmi_svg(hw)`` accepted ``hw`` and then dropped it with
    ``_ = hw`` (ami_book.py:177). Its twenty SMBIOS rows were literals --
    hand-transcriptions of ``profile.toml [hardware]`` -- so the table was
    dead data and nothing edited there could ever reach the page. Nothing in
    this module is a literal: every value is read, and a group that is absent
    is not drawn rather than invented.
  * ``ami_book.post_svg()`` reprinted stats.panel's totals as a memory test.
    ``ext = max(1024, stars)`` printed the star count *as kilobytes*
    ("3336K OK Extended"), and the 1024 floor meant a real star count below
    that rendered as something else entirely. Those totals belong to
    stats.panel / status.panel; POST keeps only what POST alone owns -- which
    repository answers on which channel, its star count, and its latest
    release tag.

The rest is rule, not preference:

  * Type never goes below the measured floor: 26 units Latin, 38 CJK, the
    latter applied by ``M.type_line``. ``M.TYPE["micro"]`` is 20 units and is
    deliberately unused here.
  * Every horizontal measurement goes through ``M.mono_width``. ``ink.text_width``
    is a Georgia-class serif metric and comes out ~20% narrow on a mono run,
    which is how a rule once got drawn straight through its own label.
  * Stroke widths come from ``M.STROKE`` and never fall below 3.0 units.
  * A value that was not fetched renders as an em dash plus a "not fetched"
    marker naming what is missing. It never renders as 0.
"""
from __future__ import annotations

import pathlib
import re
import sys
import xml.etree.ElementTree as ElementTree

ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

import make_ink_decor as M  # noqa: E402  (path set above, on purpose)

ink = M.ink

W = 960
BODY = M.TYPE["label"]                     # 26 units: the measured Latin floor
RULE_W = M.STROKE["fine"]                  # 4.0 units; ink vanishes below 3.0
HAIR = M.STROKE["hair"]                    # 3.0 units: still the floor, not under it
TRACK = 1.0                                # per-glyph letter-spacing, in units
DASH = "—"
FOOT_GAP = 78                              # last content -> bottom edge


# ── measurement ──────────────────────────────────────────────────────────────

def _tw(body: str, size: float = BODY, tracking: float = TRACK) -> float:
    """Advance width of a run about to be drawn, with the CJK floor applied.

    ``mono_width`` counts ``n * (size * 0.6 + tracking)``; SVG adds the tracking
    between glyphs only, so this over-states by at most one tracking step. That
    errs toward "I need more room", which is the direction we want.
    """
    return M.mono_width(body, ink.type_for(body, size), tracking)


def _fit(body: str, limit: float, size: float = BODY, tracking: float = TRACK) -> str:
    """Truncate to a measured width. Returns the body unchanged when it fits."""
    text = str(body)
    if _tw(text, size, tracking) <= limit:
        return text
    while text and _tw(text + "…", size, tracking) > limit:
        text = text[:-1]
    return text + "…"


def _num(value) -> str:
    """Thousands-separated count, or an em dash when no number ever arrived.

    A genuine 0 stays 0. A missing key is None and stays a dash: those are
    different facts and the old panels drew them the same way.
    """
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return DASH
    return f"{int(value):,}"


# ── ink ──────────────────────────────────────────────────────────────────────

def _rule(x1: float, x2: float, y: float, colour: str, seed: int,
          width: float = RULE_W, opacity: float | None = None) -> str:
    return ink.brush_rule(x1, x2, y, width=width, seed=seed, colour=colour,
                          opacity=M.ALPHA["soft"] if opacity is None else opacity)


def _accent(x: float, y1: float, y2: float, colour: str, seed: int) -> str:
    """A short vertical mark living in the left margin, clear of the text column."""
    return ink.path(ink.hand_line(x, y1, x, y2, seed=seed, bend=0.04), colour,
                    RULE_W, M.ALPHA["soft"])


def _marker(x: float, y: float, items: list[str], seed: int) -> list[str]:
    """The "not fetched" mark. A word, so it can never be mistaken for a zero.

    Items are admitted while they measurably fit, and whatever was left over
    is counted rather than chopped: a diagnostic that silently ends in "…" has
    told the reader less than one that says how much it is not saying.
    """
    lead, track = "not fetched", 2.0
    lx = x + _tw(lead, BODY, track) + 20
    limit = W - 26 - lx
    shown = []
    for item in items:
        if _tw(" · ".join(shown + [item]), BODY) > limit:
            break
        shown.append(item)
    rest = len(items) - len(shown)
    label = " · ".join(shown) + (f" +{rest} more" if rest else "")
    return [
        _rule(x, x + 210, y - 26, M.ROSE, seed, HAIR, M.ALPHA["ghost"]),
        M.type_line(x, y, lead, BODY, M.ROSE, ink.MONO, tracking=track),
        M.type_line(x + _tw(lead, BODY, track) + 20, y, label, BODY, M.MUTED,
                    ink.MONO, tracking=TRACK),
    ]


def _footer(panel_body: list[str], h: int, left: str, right: str) -> None:
    """Baseline rule plus two corner runs. The left one is measured, not hoped
    for: two right-aligned runs on one line collided exactly the way the rails
    did, so the right run is dropped outright when it would eat the left."""
    panel_body.append(_rule(26, W - 26, h - 40, M.INK, 37, HAIR, M.ALPHA["faint"]))
    if right and _tw(right, BODY) + 24 + _tw("POST · channel map", BODY) > W - 52:
        right = ""
    panel_body.append(M.type_line(26, h - 12,
                                  _fit(left, W - 52 - _tw(right, BODY)) if right else left,
                                  BODY, M.MUTED, ink.MONO, tracking=TRACK))
    if right:
        panel_body.append(M.type_line(W - 26, h - 12, right, BODY, M.MUTED, ink.MONO,
                                      anchor="end", tracking=TRACK))


# ── interval self-check ──────────────────────────────────────────────────────

_NUM = re.compile(r"-?\d+(?:\.\d+)?")


def _box(el) -> tuple[float, float, float, float] | None:
    """Recover (x0, x1, y0, y1) from one element of our own output.

    Path data from ink.py is always a flat run of coordinate pairs -- ``M``/``L``
    for polylines, ``M``/``L`` for the brush outline it closes with ``Z`` -- so
    even-indexed numbers are x and odd-indexed are y. Taking min/max over the
    control points is conservative for a brush stroke, which is the safe
    direction for a collision test.
    """
    tag = el.tag.rsplit("}", 1)[-1]
    if tag == "path":
        nums = [float(v) for v in _NUM.findall(el.get("d") or "")]
        if len(nums) < 4:
            return None
        xs, ys = nums[0::2], nums[1::2]
        return min(xs), max(xs), min(ys), max(ys)
    if tag == "text":
        body = el.text or ""
        size = float(el.get("font-size") or BODY)
        tracking = float(el.get("letter-spacing") or 0)
        family = el.get("font-family") or ""
        width = (_tw(body, size, tracking) if "monospace" in family
                 else ink.text_width(body, size) + tracking * max(len(body) - 1, 0))
        x, y = float(el.get("x") or 0), float(el.get("y") or 0)
        anchor = el.get("text-anchor") or "start"
        x0 = {"start": x, "end": x - width}.get(anchor, x - width / 2)
        return x0, x0 + width, y - size * 0.80, y + size * 0.22
    return None


def _audit(body: str, panel: str, eps: float = 0.75) -> None:
    """Refuse to ship ink drawn through type.

    This parses back what the module just produced rather than a model of it,
    so anything that is wrong on screen is wrong here too. Two ink strokes are
    allowed to cross each other -- a rule may meet an accent on purpose -- but
    ink may never cross a glyph box, and no two type runs may overlap.
    """
    root = ElementTree.fromstring(f'<svg xmlns="http://www.w3.org/2000/svg">{body}</svg>')
    found = []
    for el in root:
        box = _box(el)
        if box is not None:
            found.append((el.tag.rsplit("}", 1)[-1], box))
    for i, (kind_a, a) in enumerate(found):
        for kind_b, b in found[i + 1:]:
            if kind_a == kind_b != "text":
                continue
            overlap_x = min(a[1], b[1]) - max(a[0], b[0])
            overlap_y = min(a[3], b[3]) - max(a[2], b[2])
            if overlap_x > eps and overlap_y > eps:
                raise AssertionError(
                    f"{panel}: {kind_a} and {kind_b} overlap "
                    f"{overlap_x:.1f}x{overlap_y:.1f} units at "
                    f"x={max(a[0], b[0]):.1f} y={max(a[2], b[2]):.1f}")


# ── POST ─────────────────────────────────────────────────────────────────────

# The channel map is POST's own: which repository answers where. Set once,
# drawn every time; unlike the numbers beside it, it does not change per run.
# The third field says whether the device is backed by the repository API at
# all. genesis.wiki is the root device and is not a repository, so reporting
# its missing star count and tag as "not fetched" would be a lie in the other
# direction -- nothing was fetched because nothing was ever expected.
CHANNELS = (
    ("IDE 0 Master", "genesis.wiki", False),
    ("IDE 0 Slave", "WindsurfAPI", True),
    ("IDE 1 Master", "KiroStudio", True),
    ("IDE 1 Slave", "vrchat-il2cpp-re", True),
)

NA, ROOT_DEV = "n/a", "root"

X_CHAN, X_DEV, X_STARS, X_REL = 52, 270, 636, 664
P_ROW_H = 46
ROW_Y0 = 160
CAP_Y = 96


def post_panel(repos: dict, extra: dict, public: int, stars: int, tags: dict) -> str:
    """The self-test screen: which device answers, with what version.

    ``public``, ``stars`` and ``extra`` are deliberately *not* printed as
    values -- total stars, repo count, commits today and commits this year are
    stats.panel's and status.panel's numbers, and reprinting them here (as the
    old panel did, wearing a memory-test costume) is how one page ends up
    quoting four different truths. They are read for one purpose only: to say
    out loud that a count came back empty. A total of 0 because GitHub was
    unreachable must not be able to read as a real zero anywhere.
    """
    repos, extra, tags = repos or {}, extra or {}, tags or {}
    rows, missing = [], []
    for channel, name, api_backed in CHANNELS:
        if not api_backed:
            rows.append((channel, name, NA, ROOT_DEV))
            continue
        raw = (repos.get(name) or {}).get("stargazers_count")
        rows.append((channel, name, _num(raw), tags.get(name) or None))
        if not isinstance(raw, (int, float)):
            missing.append(f"stars · {name}")
        if not tags.get(name):
            missing.append(f"release · {name}")
    if not public:
        missing.append("public repo count")
    if not stars:
        missing.append("star total")
    if extra.get("commits_today") is None:
        missing.append("commits today")

    h = int(ROW_Y0 + len(rows) * P_ROW_H + (56 if missing else 24) + FOOT_GAP)
    body: list[str] = []
    for x, cap, anchor in ((X_CHAN, "CHANNEL", "start"), (X_DEV, "DEVICE", "start"),
                           (X_STARS, "STARS", "end"), (X_REL, "RELEASE", "start")):
        body.append(M.type_line(x, CAP_Y, cap, BODY, M.MUTED, ink.MONO,
                                anchor=anchor, tracking="4"))
    body.append(_rule(26, W - 26, CAP_Y + 16, M.INK, 23, HAIR, M.ALPHA["faint"]))

    for i, (channel, name, stars_text, tag) in enumerate(rows):
        y = ROW_Y0 + i * P_ROW_H
        body.append(ink.path(
            ink.hand_line(26, y - 8, 34, y - 5, seed=ink.seed_of(name), bend=0.1),
            M.GOLD, RULE_W, M.ALPHA["soft"]))
        body.append(M.type_line(X_CHAN, y, channel, BODY, M.INK, ink.MONO, tracking=TRACK))
        body.append(M.type_line(X_DEV, y, name, BODY, M.AURORA, ink.MONO, tracking=TRACK))
        body.append(M.type_line(X_STARS, y, stars_text, BODY,
                                M.MUTED if stars_text in (DASH, NA) else M.GOLD,
                                ink.MONO, anchor="end", tracking=TRACK))
        release = _fit(tag, W - 26 - X_REL) if tag else DASH
        body.append(M.type_line(X_REL, y, release, BODY,
                                M.LAPIS if tag else M.MUTED, ink.MONO, tracking=TRACK))
        if i:
            body.append(_rule(26, W - 26, y - 28, M.INK, 100 + i * 5, HAIR,
                              M.ALPHA["ghost"]))

    if missing:
        body += _marker(26, ROW_Y0 + len(rows) * P_ROW_H, missing, 59)
    _footer(body, h, "POST · channel map · profile.toml + GitHub",
            f"[{len(rows)} channels]")
    _audit("".join(body), "post.panel")
    return M.doc(W, h, "POST · boot channel map",
                 M.panel_doc(W, h, "POST · boot channel map", "") + "".join(body))


# ── DMI ──────────────────────────────────────────────────────────────────────

# profile.toml [hardware], in the order a machine is actually built up.
HW_TABLE = "profile.toml [hardware]"
GROUPS = (
    ("rog", "ROG STRIX", M.GOLD),
    ("homecloud", "HOMECLOUD", M.LAPIS),
    ("macbook", "MACBOOK", M.AURORA),
    ("mobile", "MOBILE", M.ROSE),
)

X0, X_ACCENT = 40, 22
X_RIGHT = W - 26
TOP = 92
HEAD_DY, RULE_DY, ROW_DY, B_ROW, BLOCK_GAP = 30, 44, 36, 36, 26


def _kv(line) -> tuple[str, str]:
    """`host       ASUS ROG Strix G18  (primary)` -> ("host", "ASUS ROG ...").

    The table's own two-space column is the contract, so the split happens on
    the *first* run of two or more spaces and everything after it survives --
    including the internal double space in `18"  2.5K`.
    """
    parts = re.split(r"\s{2,}", str(line).strip(), maxsplit=1)
    if len(parts) == 2:
        return parts[0].strip(), parts[1].strip()
    return "", str(line).strip()


def _block(x: int, y: int, idx: int, note: str, name: str, colour: str,
           pairs: list[tuple[str, str]], seed: int) -> tuple[list[str], float]:
    out = [_accent(X_ACCENT, y + 8, y + RULE_DY + len(pairs) * B_ROW, colour, seed)]
    tag = f"{idx:02d}"
    out.append(M.type_line(x, y + HEAD_DY, tag, BODY, colour, ink.MONO, tracking="2"))
    nx = x + _tw(tag, BODY, 2.0) + 18
    out.append(M.type_line(nx, y + HEAD_DY, name, BODY, M.INK, ink.MONO, tracking="4"))

    # Where the rows came from, right-aligned and dropped rather than overlapped.
    if X_RIGHT - _tw(note, BODY) > nx + _tw(name, BODY, 4.0) + 24:
        out.append(M.type_line(X_RIGHT, y + HEAD_DY, note, BODY, M.MUTED, ink.MONO,
                               anchor="end", tracking=TRACK))
    out.append(_rule(x, X_RIGHT, y + RULE_DY, colour, seed + 3, RULE_W, M.ALPHA["ghost"]))

    # Key column measured from the widest key in *this* block, so a long key
    # such as `phone-2` cannot push the values out of the panel.
    vx = x + max(_tw(k, BODY) for k, _ in pairs) + 22
    for i, (k, v) in enumerate(pairs):
        ry = y + RULE_DY + ROW_DY + i * B_ROW
        out.append(M.type_line(x, ry, k, BODY, M.MUTED, ink.MONO, tracking=TRACK))
        out.append(M.type_line(vx, ry, _fit(v, X_RIGHT - vx), BODY, M.INK, ink.MONO,
                               tracking=TRACK))
    return out, RULE_DY + ROW_DY + len(pairs) * B_ROW + 20


def dmi_panel(hw: dict) -> str:
    """The hardware inventory, read straight out of ``profile.toml [hardware]``.

    Four groups -- rog, homecloud, macbook, mobile -- one block each, keys and
    values in two measured columns. ``peripheral`` is deliberately absent: it
    belongs to a USB panel that was never wired up, and smuggling it in here
    would put it on the page without anyone deciding to. An empty table draws
    a single "not fetched" mark; it does not draw a plausible computer.
    """
    hw = hw or {}
    blocks = []
    for key, name, colour in GROUPS:
        lines = list(hw.get(key) or [])
        if key == "mobile" and hw.get("mobile_comment"):
            lines.append(str(hw["mobile_comment"]))
        pairs = [pair for pair in (_kv(line) for line in lines) if pair[0] or pair[1]]
        if pairs:
            blocks.append((f"{HW_TABLE}.{key}", name, colour, pairs))

    found = len(blocks)
    missing = []
    if not blocks:
        blocks = [(HW_TABLE, "NO INVENTORY", M.ROSE, [("hw", DASH)])]
        missing.append(f"{HW_TABLE}: no rows")

    body: list[str] = []
    y = TOP
    for i, (note, name, colour, pairs) in enumerate(blocks):
        y += BLOCK_GAP if i else 0
        chunk, height = _block(X0, y, i + 1, note, name, colour, pairs,
                               ink.seed_of(note))
        body += chunk
        y += height
    if missing:
        body += _marker(X0, y + 30, missing, 71)
        y += 56
    h = int(y + FOOT_GAP)
    _footer(body, h, "DMI · hardware inventory from profile.toml",
            f"[{found} group{'s' if found != 1 else ''}]")
    _audit("".join(body), "dmi.panel")
    return M.doc(W, h, "DMI · hardware inventory",
                 M.panel_doc(W, h, "DMI · hardware inventory", "") + "".join(body))