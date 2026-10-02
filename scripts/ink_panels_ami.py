#!/usr/bin/env python3
"""INK LAB redraws of the four AMIBIOS CMOS screens: boot / main / devices / log.

Same four functions and the same data shapes as scripts/ami.py —

    setup_panel(repos, tags)              status_panel(work, extra, repos, today)
    devices_panel(heads)                  eventlog_panel(lines)

— so the renderer swaps one import and nothing else. What changed is the drawing:
hand-inked rules and marks on the crayon ground, one type scale, and nothing set
below the measured floor.

Three rules this file keeps, all of them learned from a bug that shipped once:

  * every layout number comes from M.mono_width. ink.text_width is a Georgia-class
    serif table and comes back ~20% narrow on a monospaced run, which is how a
    rule ended up drawn straight through its own label;
  * a value that was never fetched is an em dash and a struck circle, never a 0
    that reads like a measurement. fetch_extra_stats seeds every field with 0 and
    hands those seeds back untouched when GraphQL fails, and tags come back as ""
    from a caught exception, so both look exactly like real data if you print them;
  * every panel ends with assert_clear(), which re-parses the markup this module
    just emitted — filled paths, stroked paths, dots and type — and fails if any
    ink box touches any text box.

status_panel deliberately carries only what no other panel prints. Total stars,
public repos, the year count, the WindsurfAPI star count and the WindsurfAPI issue
count all live on stats, langs and post already; repeating them here was the reason
the page showed the same five numbers four times. Today's commit count stays,
because this is the one screen that says "today".
"""
from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

import make_ink_decor as M  # noqa: E402  (path set above, on purpose)

ink = M.ink

# tokens, re-exported so no colour, stroke or size is spelled as a literal here
INK, GOLD, AURORA = M.INK, M.GOLD, M.AURORA
VIOLET, LAPIS, ROSE, MUTED = M.VIOLET, M.LAPIS, M.ROSE, M.MUTED
TYPE, STROKE, ALPHA = M.TYPE, M.STROKE, M.ALPHA

W = 960
PAD = 44
RIGHT = W - PAD                       # last x a run may reach, 916
VALUE_X = 520                         # the settings gutter, measured not guessed
HEAD = TYPE["label"]                  # 26 — the measured Latin floor, used everywhere
BIG = TYPE["title"]                   # 38 — hero values, and the CJK floor
HEAD_TRACK = 6.0
RUN_TRACK = 2.0
GUTTER = 26.0                         # minimum air between one run and the next
CHROME = 72.0                         # make_ink_decor.panel_doc owns everything above
SLACK = 3.0                           # hand jitter, carried as extra box on every stroke
DASH = "—"                            # a value that was never fetched
ROWS = 8                              # dmesg_events caps the feed here; [:11] was fiction

_FILL_PATH = re.compile(r'<path d="([^"]+)" fill="(?!none")')
_STROKE_PATH = re.compile(
    r'<path d="([^"]+)" fill="none" stroke="[^"]+" stroke-width="([\d.]+)"')
_DOT = re.compile(r'<circle cx="(-?[\d.]+)" cy="(-?[\d.]+)" r="([\d.]+)" fill="(?!none")')
_TEXT = re.compile(
    r'<text x="(-?[\d.]+)" y="(-?[\d.]+)" font-size="([\d.]+)"[^>]*?'
    r'text-anchor="(\w+)"[^>]*?>')
_TOKENS = re.compile(r"[MmLlHhVvAaCcSsQqTtZz]|-?\d*\.?\d+")
_WORDS = re.compile(r"[\u2e80-\u9fff\uff00-\uffef]|[^\s\u2e80-\u9fff\uff00-\uffef]+|\s+")
_ARITY = {"M": 2, "L": 2, "H": 1, "V": 1, "A": 7, "C": 6, "S": 4, "Q": 4, "T": 2, "Z": 0}


# ── metrics ───────────────────────────────────────────────────────────────────
def _cjk(ch: str) -> bool:
    return ord(ch) > 0x2E7F


def run_width(body, size: float = HEAD, tracking: float = 0.0) -> float:
    """Advance of a monospaced run, in viewBox units.

    M.mono_width is the metric for every Latin run here. CJK glyphs are full-width
    in the same mono face, so each one adds the 0.4em that a flat 0.6em per glyph
    misses — measuring against the wrong number is how text ends up under a rule
    that was placed for it.
    """
    s = str(body)
    return M.mono_width(s, size, tracking) + sum(size * 0.4 for ch in s if _cjk(ch))


def serif_width(body, size: float = HEAD, tracking: float = 0.0) -> float:
    """Advance of a serif run, which is the one ink.text_width actually models."""
    s = str(body)
    return ink.text_width(s, size) + tracking * max(len(s), 1)


def _width_of(family: str):
    return run_width if family == ink.MONO else serif_width


def fit(body, room: float, size: float = HEAD, tracking: float = 0.0,
        family: str = ink.MONO) -> str:
    """Trim a run to the room it was given. The ellipsis is measured, not free."""
    s = str(body)
    measure = _width_of(family)
    if measure(s, size, tracking) <= room:
        return s
    while s and measure(s + "…", size, tracking) > room:
        s = s[:-1]
    return s + "…"


def wrap(body, room: float, size: float = HEAD, tracking: float = 0.0, limit: int = 2,
         family: str = ink.MONO) -> list[str]:
    """Greedy wrap. Latin breaks on a space, CJK breaks between glyphs."""
    measure = _width_of(family)
    lines: list[str] = []
    cur = ""
    for tok in _WORDS.findall(str(body)):
        if tok.isspace():
            if cur and not cur.endswith(" "):
                cur += " "
            continue
        if cur and measure(cur + tok, size, tracking) > room:
            lines.append(cur.rstrip())
            if len(lines) >= limit:
                return lines
            cur = tok
        else:
            cur += tok
    if cur.strip():
        lines.append(cur.rstrip())
    return lines[:limit]


def prose_size(body, size: float = HEAD) -> float:
    """A paragraph that mixes scripts is set at one size, the taller of the two.

    ink.type_for raises a run to 38 the moment it sees a CJK glyph, which is right
    for a single run and wrong for a wrapped paragraph: line one at 38 and line
    two at 26 reads as a mistake. The block takes the floor once, for every line.
    """
    return ink.type_for(body, size)


# ── the value ledger ──────────────────────────────────────────────────────────
def as_count(value) -> int | None:
    """An integer we can honestly print, or None when the fetch never landed.

    fetch_extra_stats initialises every field to 0 and returns those seeds
    unchanged when GraphQL throws, so a 0 here means "not fetched" far more often
    than it means "none". Printing it would invent a measurement.
    """
    if value is None or isinstance(value, bool):
        return None
    try:
        n = int(value)
    except (TypeError, ValueError):
        return None
    return n or None


def as_repo_count(repos: dict, name: str, field: str) -> int | None:
    """A REST repository field, where 0 is a real answer and absent is not.

    The GraphQL counters and the repository counters fail differently: one hands
    back a seeded zero, the other simply omits the repository. Same em dash, two
    different reasons, and only one of them is ever a measurement.
    """
    row = (repos or {}).get(name)
    if not isinstance(row, dict) or field not in row:
        return None
    try:
        return int(row[field])
    except (TypeError, ValueError):
        return None


def _path_points(d: str) -> list[tuple[float, float]]:
    """Absolute endpoints of a path, for the overlap ledger.

    The ink engine only emits M/L for filled shapes, but brush() falls back to
    relative arcs for a degenerate one-point stroke, so those are resolved here
    rather than skipped and left unchecked.
    """
    toks = _TOKENS.findall(d)
    pts: list[tuple[float, float]] = []
    cur = (0.0, 0.0)
    i, cmd = 0, "M"
    while i < len(toks):
        if toks[i].isalpha():
            cmd = toks[i]
            i += 1
            if cmd in "Zz":
                continue
        need = _ARITY.get(cmd.upper(), 2)
        try:
            vals = [float(v) for v in toks[i:i + need]]
        except ValueError:
            break
        if len(vals) < need:
            break
        i += need
        rel = cmd.islower()
        if cmd in "MmLl":
            cur = (cur[0] + vals[0], cur[1] + vals[1]) if rel else (vals[0], vals[1])
        elif cmd in "Hh":
            cur = (cur[0] + vals[0], cur[1]) if rel else (vals[0], cur[1])
        elif cmd in "Vv":
            cur = (cur[0], cur[1] + vals[0]) if rel else (cur[0], vals[0])
        else:                                     # every curve ends on its last pair
            cur = (cur[0] + vals[-2], cur[1] + vals[-1]) if rel else (vals[-2], vals[-1])
        pts.append(cur)
    return pts


def _bounds(pts: list[tuple[float, float]], grow: float) -> tuple[float, float, float, float]:
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return (min(xs) - grow, min(ys) - grow, max(xs) + grow, max(ys) + grow)


def _ink_boxes(body: str) -> list[tuple[float, float, float, float]]:
    """Every drop of ink in one panel as a box: fills, strokes and dots alike.

    Strokes are grown by half their width plus SLACK, because a hand-drawn line
    wanders off its own centreline. Leaving stroked marks out of this set is what
    lets a divider creep into a label one late edit at a time.
    """
    boxes: list[tuple[float, float, float, float]] = []
    for d in _FILL_PATH.findall(body):
        pts = _path_points(d)
        if pts:
            boxes.append(_bounds(pts, 1.0))
    for d, width in _STROKE_PATH.findall(body):
        pts = _path_points(d)
        if pts:
            boxes.append(_bounds(pts, float(width) / 2 + SLACK))
    for cx, cy, r in _DOT.findall(body):
        boxes.append((float(cx) - float(r) - SLACK, float(cy) - float(r) - SLACK,
                      float(cx) + float(r) + SLACK, float(cy) + float(r) + SLACK))
    return boxes


def _hits(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> bool:
    return (min(a[2], b[2]) - max(a[0], b[0])) > 0 and (min(a[3], b[3]) - max(a[1], b[1])) > 0


def _assert_clear(body: str, runs: list[tuple], title: str, w: int, h: int) -> None:
    """Re-read the panel this module just drew and fail on any ink/type contact."""
    parsed = _TEXT.findall(body)
    if len(parsed) != len(runs):
        raise AssertionError(f"{title}: ledger recorded {len(runs)} runs, "
                             f"markup carries {len(parsed)}")
    for (px, py, _size, _anchor), run in zip(parsed, runs):
        if abs(float(px) - round(run[6])) > 0.51 or abs(float(py) - round(run[7])) > 0.51:
            raise AssertionError(f"{title}: ledger drift on {run[5]!r}")

    for x0, y0, x1, y1, size, s, _rx, _ry in runs:
        if size < HEAD - 0.01:
            raise AssertionError(f"{title}: {s!r} set at {size}, floor is {HEAD}")
        if x0 < PAD - 0.01 or x1 > w - 30:
            raise AssertionError(f"{title}: {s!r} runs off the plate at {x0:.0f}..{x1:.0f}")
        if y0 < CHROME - 0.01 or y1 > h - 6:
            raise AssertionError(f"{title}: {s!r} sits at y {y0:.0f}..{y1:.0f}")
    for box in _ink_boxes(body):
        if box[1] < CHROME - 0.01 or box[3] > h - 6:
            raise AssertionError(f"{title}: ink at y {box[1]:.0f}..{box[3]:.0f} leaves "
                                 f"the plate")
        if box[0] < 18 or box[2] > w - 22:
            raise AssertionError(f"{title}: ink at x {box[0]:.0f}..{box[2]:.0f} leaves "
                                 f"the plate")
        for x0, y0, x1, y1, _size, s, _rx, _ry in runs:
            if _hits(box, (x0, y0, x1, y1)):
                raise AssertionError(
                    f"{title}: ink [{box[0]:.0f},{box[1]:.0f},{box[2]:.0f},{box[3]:.0f}] "
                    f"overlaps {s!r} [{x0:.0f},{y0:.0f},{x1:.0f},{y1:.0f}]")


def missing_mark(b: "Board", cx: float, cy: float, colour: str = ROSE) -> None:
    """The struck circle. The only glyph on these four screens that means 'no'."""
    seed = ink.seed_of(f"not-fetched-{cx:.0f}-{cy:.0f}")
    b.add(ink.path(ink.circle(cx, cy, 13, seed=seed, w=0.02), colour, STROKE["hair"]),
          ink.path(ink.hand_line(cx - 8, cy + 8, cx + 8, cy - 8, seed=seed + 3, bend=0.08),
                   colour, STROKE["hair"]))


def ladder(b: "Board", x: float, ys: list[float], *, seed: int, active: int = -1,
           colour: str = MUTED, r: float = 12.0, stub: float = 34.0) -> None:
    """A bus: one vertical run, one node per rung, a stub off each node.

    The run is stroked and the nodes are filled, so a rung can come as close to
    the type as the columns allow without filled ink ever entering a text box.
    """
    if len(ys) < 2:
        return
    b.add(ink.path(ink.hand_line(x, ys[0], x, ys[-1], seed=seed, bend=0.012),
                   colour, STROKE["hair"], ALPHA["ghost"]))
    for i, y in enumerate(ys):
        on = i == active
        b.chip(x, y, r + (3.0 if on else 0.0), GOLD if on else INK,
               ALPHA["full"] if on else ALPHA["soft"], seed=seed + 7 * (i + 1))
        if stub:
            b.add(ink.path(ink.hand_line(x + r + 10, y, x + r + 10 + stub, y,
                                         seed=seed + 13 * (i + 1), bend=0.06),
                           GOLD if on else colour, STROKE["hair"],
                           ALPHA["soft"] if on else ALPHA["faint"]))


class Board:
    """One panel under construction, plus the ledger of every interval it sets.

    The ledger is the contract: a panel is not finished until finish() has
    re-parsed the markup this class emitted and proved that no ink touches a
    glyph, that nothing sits above the shared chrome, and that no run fell off
    the measured type floor.
    """

    def __init__(self, w: int, h: int, title: str):
        self.w, self.h, self.title = w, h, title
        self.out: list[str] = []
        self.runs: list[tuple] = []
        self.missing = 0

    # -- ink -----------------------------------------------------------------
    def add(self, *markup) -> "Board":
        self.out.extend(markup)
        return self

    def rule(self, x1: float, x2: float, y: float, colour: str = MUTED,
             width: float = STROKE["hair"], seed: int = 7,
             opacity: float = ALPHA["ghost"]) -> "Board":
        """A divider, stroked. A filled brush rule spends a hundred points to say
        the same thing, and every one of those points is another chance to land on
        a label; hand_line says it in nine."""
        return self.add(ink.path(ink.hand_line(x1, y, x2, y, seed=seed, bend=0.01),
                                 colour, width, opacity))

    def chip(self, cx: float, cy: float, r: float, colour: str = INK,
             opacity: float = ALPHA["full"], seed: int = 13) -> "Board":
        return self.add(ink.brush_fill(ink.circle(cx, cy, r, seed=seed, w=0.03),
                                       colour, opacity))

    def box(self, x0: float, y0: float, x1: float, y1: float, colour: str = MUTED,
            width: float = STROKE["hair"], seed: int = 17,
            opacity: float = ALPHA["soft"]) -> "Board":
        return self.add(ink.path(ink.rect_path(x0, y0, x1 - x0, y1 - y0, seed=seed),
                                 colour, width, opacity))

    def spray(self, cx: float, cy: float, r: float, n: int = 18, seed: int = 19,
              colour: str = MUTED) -> "Board":
        return self.add(*ink.spray(cx, cy, r, n, seed, colour))

    # -- type ----------------------------------------------------------------
    def text(self, x: float, y: float, body, size: float = HEAD, colour: str = INK,
             family: str = ink.MONO, tracking: float = 0.0, anchor: str = "start",
             **kw) -> tuple[float, float]:
        """Set one run and record its box. Returns the x it starts and ends at."""
        s = str(body)
        size = ink.type_for(s, size)
        w = _width_of(family)(s, size, tracking)
        x0 = {"start": x, "middle": x - w / 2, "end": x - w}[anchor]
        # a baseline box: 0.80em of cap height above it, 0.24em of descender below
        self.runs.append((x0, y - 0.80 * size, x0 + w, y + 0.24 * size, size, s, x, y))
        self.out.append(M.type_line(x, y, s, size, colour, family,
                                    tracking=tracking or None, anchor=anchor, **kw))
        return x0, x0 + w

    def head(self, x: float, y: float, body, colour: str = MUTED,
             tracking: float = HEAD_TRACK) -> tuple[float, float]:
        return self.text(x, y, body, HEAD, colour, ink.MONO, tracking=tracking)

    def end(self, x: float, y: float, body, size: float = HEAD, colour: str = MUTED,
            family: str = ink.MONO, tracking: float = 0.0) -> tuple[float, float]:
        return self.text(x, y, body, size, colour, family, tracking=tracking, anchor="end")

    def kv(self, x: float, y: float, key, value, *, value_x: float = VALUE_X,
           colour: str = GOLD, key_colour: str = MUTED, size: float = HEAD,
           tracking: float = RUN_TRACK) -> None:
        """A labelled value. The gutter is measured, and the two runs are refused
        rather than allowed to print over each other."""
        if x + run_width(key, size, tracking) + GUTTER > value_x:
            raise AssertionError(
                f"{self.title}: key {key!r} needs "
                f"{x + run_width(key, size, tracking):.0f} units, the value column "
                f"opens at {value_x}")
        self.text(x, y, key, size, key_colour, ink.MONO, tracking=tracking)
        room = RIGHT - value_x
        self.text(value_x, y, fit(value, room, size, tracking), size, colour, ink.MONO,
                  tracking=tracking)

    def dash(self, x: float, y: float, *, size: float = HEAD, colour: str = MUTED,
             anchor: str = "start", gap: float = 26.0) -> None:
        """A value that was never fetched: the em dash, and the mark that says why."""
        x0, x1 = self.text(x, y, DASH, size, colour, anchor=anchor)
        cy = y - size * 0.32
        self.missing += 1
        missing_mark(self, (x1 if anchor == "start" else x0) - gap - 13 if anchor == "end"
                     else x1 + gap + 13, cy)

    def dash_end(self, x: float, y: float, *, size: float = HEAD, gap: float = 26.0) -> None:
        self.dash(x, y, size=size, anchor="end", gap=gap)

    # -- shared furniture ----------------------------------------------------
    def fit_to(self, baseline: float, pad: float = 30.0) -> None:
        """Grow the plate so a panel is exactly as tall as what it drew."""
        self.h = max(self.h, baseline + pad)

    def footnote(self, y: float) -> None:
        """The bottom line: what the marks mean, or what the screen is not."""
        if self.missing:
            note = f"{DASH} = not fetched · {self.missing} value" + \
                   ("" if self.missing == 1 else "s")
            _x0, x1 = self.text(RIGHT - 46, y, note, HEAD, MUTED, ink.MONO,
                                anchor="end", tracking=1)
            missing_mark(self, x1 + 23, y - HEAD * 0.32)
        else:
            self.end(RIGHT, y, "a snapshot, not a live clock", HEAD, MUTED, ink.MONO,
                     tracking=1)
        self.fit_to(y)

    def finish(self) -> str:
        body = "".join(self.out)
        _assert_clear(body, self.runs, self.title, self.w, self.h)
        return M.panel_doc(self.w, self.h, self.title, body)


# ── 1 · boot order ────────────────────────────────────────────────────────────
SETTINGS = (
    ("Quiet Boot", "[Disabled]"),
    ("Bootup Num-Lock", "[On]"),
    ("Wait For 'F1' If Error", "[Enabled]"),
    ("Hit 'DEL' Message Display", "[Enabled]"),
)
DRIVES = (
    ("Removable Devices", ">"),
    ("Network Stack", "[Enabled]"),
)
CHAIN = ("ORIGIN", "WindsurfAPI", "KiroStudio", "vrchat-il2cpp-re")


def setup_panel(repos: dict, tags: dict) -> str:
    """The boot chain as a bus: four rungs, two of them versioned from GitHub.

    Only two of the thirteen settings are live — the release tag on rungs two and
    three — so those carry the tag and the rest carry nothing but their place in
    the chain. A tag that came back empty is drawn as a dash: the old screen fell
    back to the literal `live`, which is exactly what a failed fetch_latest_tag
    looks like from the outside.
    """
    b = Board(W, 520, "AMIBIOS · BOOT ORDER")
    live = {name: str(name in (repos or {})) == "True" for name in CHAIN[1:3]}
    seen_tag = {name: str((tags or {}).get(name) or "") for name in CHAIN[1:3]}

    y = 96
    b.head(PAD, y, "BOOT SETTINGS")
    b.rule(PAD, RIGHT, y + 18)
    b.spray(866, 196, 40, 16, 223, MUTED)          # the empty right of the block
    y += 54
    for label, value in SETTINGS:
        b.kv(PAD, y, label, value)
        y += 36

    y += 24
    b.head(PAD, y, "HARD DISK DRIVES")
    b.rule(PAD, RIGHT, y + 18)
    y += 54
    for label, value in DRIVES:
        b.kv(PAD, y, label, value)
        y += 36

    y += 24
    b.head(PAD, y, "BOOT ORDER")
    b.rule(PAD, RIGHT, y + 18)
    y += 54
    ys: list[float] = []
    for i, name in enumerate(CHAIN):
        ys.append(y - 9)
        b.text(PAD, y, f"{i + 1:02d}", HEAD, GOLD, ink.MONO, tracking=RUN_TRACK)
        _x0, x1 = b.text(110, y, name, HEAD, INK, ink.MONO, tracking=RUN_TRACK)
        tag = seen_tag.get(name, "")
        if tag:
            b.text(x1 + 44, y, fit(tag, RIGHT - (x1 + 44), HEAD, RUN_TRACK), HEAD, GOLD,
                   ink.MONO, tracking=RUN_TRACK)
        elif name in live:
            b.dash(x1 + 44, y)
        y += 36
    ladder(b, 740, ys, seed=211, active=0)

    b.footnote(y + 44)
    return b.finish()


# ── 2 · main / status ─────────────────────────────────────────────────────────
def status_panel(work: dict, extra: dict, repos: dict, today: str) -> str:
    """The last public event, today's commits, and one honest issue count.

    Everything else this screen used to print — total stars, repo count, the year
    total, the WindsurfAPI star count and its issue count — is already on stats,
    langs and post. It is not repeated here. What is left is what only this screen
    knows: when the build was stamped, what the last public event was, and how
    many commits landed today.
    """
    work = work or {}
    extra = extra or {}
    b = Board(W, 520, "AMIBIOS · MAIN")

    date_s = (f"{today[5:7]}/{today[8:10]}/{today[2:4]}"
              if isinstance(today, str) and len(today) >= 10 else str(today or ""))
    verb = str(work.get("verb") or "")
    repo = str(work.get("repo") or "")
    msg = str(work.get("msg") or "")
    sha = str(work.get("sha") or "")
    ago = str(work.get("ago") or "")

    # left — the last public event
    b.head(PAD, 96, "LAST PUBLIC EVENT")
    b.rule(PAD, 500, 114)
    if verb and repo:
        b.text(PAD, 160, fit(f"{verb} · {repo}", 456, BIG, 1), BIG, GOLD, ink.MONO,
               tracking=1)
    else:
        b.text(PAD, 160, "no public event", BIG, MUTED, ink.SERIF, italic=True)
    note = wrap(msg, 456, HEAD, 1, limit=1)[0] if msg else ""
    b.text(PAD, 206, note, HEAD, INK, ink.SERIF) if note else b.dash(PAD, 206)
    b.kv(PAD, 254, "WHEN", ago, value_x=140)
    b.end(380, 254, "HEAD", HEAD, MUTED, ink.MONO, tracking=RUN_TRACK)
    if sha:
        b.end(500, 254, sha, HEAD, GOLD, ink.MONO, tracking=RUN_TRACK)
    else:
        b.dash_end(500, 254)

    # right — the build stamp, then today's rate
    b.head(560, 96, "BUILD")
    b.rule(560, RIGHT, 114)
    b.kv(560, 152, "BIOS", "dwgx.menu 2.9", value_x=650)
    b.kv(560, 190, "DATE", date_s, value_x=650)

    b.head(560, 248, "COMMITS TODAY")
    b.rule(560, RIGHT, 266)
    n_today = as_count(extra.get("commits_today"))
    if n_today is None:
        b.dash(560, 312, size=BIG)
    else:
        b.text(560, 312, f"{n_today:,}", BIG, GOLD, ink.MONO, tracking=1)

    b.head(560, 404, "OPEN ISSUES")
    b.rule(560, RIGHT, 422)
    b.text(560, 470, "KiroStudio", HEAD, MUTED, ink.MONO, tracking=RUN_TRACK)
    kiro = as_repo_count(repos, "KiroStudio", "open_issues_count")
    if kiro is None:
        b.dash_end(RIGHT, 470)
    else:
        b.end(RIGHT, 470, f"{kiro} open", HEAD, GOLD, ink.MONO, tracking=RUN_TRACK)

    if b.missing:
        missing_mark(b, PAD + 13, 470 - HEAD * 0.32)
        b.text(PAD + 52, 470, f"{DASH} = not fetched", HEAD, MUTED, ink.MONO, tracking=1)
    else:
        b.text(PAD, 470, "the last public event, not a clock", HEAD, MUTED, ink.MONO,
               tracking=1)
    return b.finish()


# ── 3 · devices ───────────────────────────────────────────────────────────────
SLOTS = ("Pri Master", "Pri Slave", "Sec Master", "Sec Slave", "CDROM", "Network")
COL_SLOT, COL_DEV, COL_HEAD, COL_AGE, COL_NODE, COL_BOX = 44, 220, 470, 610, 700, 812


def devices_panel(heads: list[dict]) -> str:
    """Six IDE bays, filled from the HEAD of six public repositories.

    Slot names line up with position, not with name: fetch_heads drops a
    repository that fails and the rows below it slide up, exactly as the old
    screen did. A bay that never got filled is drawn empty rather than
    substituted, and a short table says how many are missing instead of letting
    the count quietly change.
    """
    heads = [h for h in (heads or []) if isinstance(h, dict)][:len(SLOTS)]
    b = Board(W, 560, "AMIBIOS · DEVICES")

    for x, cap in ((COL_SLOT, "SLOT"), (COL_DEV, "DEVICE"), (COL_HEAD, "HEAD"),
                   (COL_AGE, "AGE"), (COL_BOX - 40, "MODE")):
        b.text(x, 96, cap, HEAD, MUTED, ink.MONO, tracking=4)
    b.rule(PAD, RIGHT, 114)

    y = 152
    for i, slot in enumerate(SLOTS):
        row = heads[i] if i < len(heads) else {}
        name = str(row.get("name") or "")
        sha = str(row.get("sha") or "")
        ago = str(row.get("ago") or "")
        b.text(COL_SLOT, y, slot, HEAD, INK, ink.MONO)
        if name:
            b.text(COL_DEV, y, fit(name, COL_HEAD - COL_DEV - 24), HEAD, INK, ink.MONO)
            b.text(COL_HEAD, y, fit(sha or DASH, 100, HEAD, 1), HEAD, GOLD, ink.MONO,
                   tracking=1)
            b.text(COL_AGE, y, fit(ago or DASH, 60), HEAD, MUTED, ink.MONO)
            b.chip(COL_NODE, y - 9, 11, GOLD, ALPHA["full"], seed=311 + 7 * i)
        else:
            b.text(COL_DEV, y, "not installed", HEAD, MUTED, ink.SERIF, italic=True)
            b.text(COL_HEAD, y, DASH, HEAD, MUTED, ink.MONO, tracking=1)
            b.text(COL_AGE, y, DASH, HEAD, MUTED, ink.MONO)
        b.box(COL_BOX - 82, y - 22, COL_BOX + 82, y + 10, GOLD if name else MUTED,
              STROKE["hair"], seed=317 + 5 * i)
        b.text(COL_BOX, y, "LBA" if name else "AUTO", HEAD, LAPIS if name else MUTED,
               ink.MONO, anchor="middle", tracking=1)
        y += 38
    b.rule(PAD, RIGHT, y + 12)

    y += 50
    b.text(PAD, y, f"{len(heads)} / {len(SLOTS)} BAYS FILLED", HEAD, GOLD, ink.MONO,
           tracking=RUN_TRACK)
    b.end(RIGHT, y, "filled from GitHub, not a local disk", HEAD, MUTED, ink.MONO,
          tracking=1)
    if len(heads) < len(SLOTS):
        gap = len(SLOTS) - len(heads)
        b.missing += gap
        _x0, x1 = b.text(PAD, y + 46, f"{DASH} = not fetched · {gap} repos did not "
                                        f"answer", HEAD, MUTED, ink.MONO, tracking=1)
        missing_mark(b, x1 + 23, y + 46 - HEAD * 0.32)
        y += 46

    msg = str((heads[0].get("msg") if heads else "") or "")
    if msg:
        size = prose_size(msg)
        for line in wrap(msg, RIGHT - PAD, size, 0, limit=2, family=ink.SERIF):
            b.text(PAD, y + 46, fit(line, RIGHT - PAD, size, 0, ink.SERIF), size, MUTED,
                   ink.SERIF)
            y += 46
    return b.finish()


# ── 4 · event log ─────────────────────────────────────────────────────────────
VERB_COLOUR = {"push": GOLD, "rel": AURORA, "open": LAPIS, "close": MUTED,
               "reopen": VIOLET, "pr": ROSE}


def eventlog_panel(lines: list[dict]) -> str:
    """The public event tape: when, how old, what kind, where, and the first line.

    Two upstream fallbacks are repaired on the way in. jst_stamp keeps the raw ISO
    string when it cannot parse, so a stamp with no colon in it never belonged on
    the tape; ago_label answers "?" when the timestamp is unreadable. Both are
    missing data, and missing data gets a dash and a mark here.
    """
    rows = [r for r in (lines or []) if isinstance(r, dict)][:ROWS]
    b = Board(W, 300, "AMIBIOS · EVENT LOG")

    if not rows:
        b.text(W / 2, 190, "no public events", BIG, MUTED, ink.SERIF, anchor="middle",
               italic=True)
        b.text(W / 2, 234, f"{DASH} the public event feed is empty or unreachable", HEAD,
               MUTED, ink.MONO, anchor="middle", tracking=1)
        missing_mark(b, W / 2 - run_width("no public events", BIG) / 2 - 34,
                     190 - BIG * 0.32)
        b.missing += 1
        b.spray(W / 2, 262, 50, 18, 401, MUTED)
        return b.finish()

    for x, cap in ((52, "TIME"), (180, "AGE"), (290, "TYPE"), (390, "SOURCE")):
        b.text(x, 96, cap, HEAD, MUTED, ink.MONO, tracking=4)
    b.end(RIGHT, 96, "NEWEST FIRST", HEAD, MUTED, ink.MONO, tracking=4)
    b.rule(52, RIGHT, 114)

    ys: list[float] = []
    for i, row in enumerate(rows):
        y = 152 + i * 58
        ys.append(y - 9)
        stamp = str(row.get("stamp") or "")
        if ":" not in stamp:
            b.dash(52, y)
        else:
            b.text(52, y, fit(stamp, 110, HEAD, 1), HEAD, INK, ink.MONO, tracking=1)
        ago = str(row.get("ago") or "")
        b.text(180, y, fit(ago, 90), HEAD, MUTED, ink.MONO) if ago not in ("", "?") \
            else b.dash(180, y)
        verb = str(row.get("verb") or "")
        b.text(290, y, fit(verb or DASH, 90, HEAD, 1), HEAD, VERB_COLOUR.get(verb, INK),
               ink.MONO, tracking=1)
        b.text(390, y, fit(str(row.get("repo") or DASH), 500), HEAD, INK, ink.MONO)
        msg = str(row.get("msg") or "")
        if msg:
            size = prose_size(msg)
            line = wrap(msg, RIGHT - 52, size, 0, limit=1, family=ink.SERIF)[0]
            b.text(52, y + 26, fit(line, RIGHT - 52, size, 0, ink.SERIF), size, MUTED,
                   ink.SERIF)
        else:
            b.dash(52, y + 26)
    ladder(b, 30, ys, seed=411, active=0, r=10, stub=0)

    b.footnote(152 + len(rows) * 58)
    return b.finish()
