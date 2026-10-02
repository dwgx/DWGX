#!/usr/bin/env python3
"""INK LAB ornament set for the dwgx.profile README.

Replaces the hand-authored BIOS ornaments with generated hand-drawn ones. Same
engine as the repository banners (repo-kit/ink.py, a port of genesis-site's
handgen.ts), so the profile and the fleet share one drawing language:

    python scripts/make_ink_decor.py            # write assets/ink-*.svg
    python scripts/make_ink_decor.py --check    # fail if committed bytes differ

Every file is deterministic: all randomness comes from ink.seed_of(name), so
re-running produces byte-identical output and a no-op commit stays a no-op.
"""
from __future__ import annotations

import argparse
import math
import pathlib
import re
import sys
import tomllib
import xml.etree.ElementTree as ElementTree

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "repo-kit"))

import ink  # noqa: E402  (path set above, on purpose)

ASSETS = ROOT / "assets"
TITLE = "dwgx.menu"
DESC = "Decorative dwgx.menu panel; not live telemetry."

# One design system, resolved once. Nothing below names a colour, a stroke width
# or a type size as a literal: those live in repo-kit/ink.py so the profile and
# the 22 repository banners cannot drift apart.
T = ink.theme("crayon", light=False, ground="#06020f")
C, STROKE, TYPE, SPACE, ALPHA, RULES = (T["c"], T["stroke"], T["type"], T["space"],
                                        T["alpha"], T["rules"])
INK, GOLD, AURORA = C["ink"], C["gold"], C["aurora"]
VIOLET, LAPIS, ROSE, MUTED = C["violet"], C["lapis"], C["rose"], C["muted"]
GROUND = C["ground"]

# every text helper routes through here, so the CJK floor is impossible to miss
_LABEL = TYPE["label"]


def type_line(x: float, y: float, body, size: float = _LABEL, colour: str = INK,
          family: str = ink.MONO, **kw) -> str:
    """Set type at the token size, automatically raised for CJK runs."""
    return ink.text(x, y, body, ink.type_for(body, size), colour, family, **kw)


def doc(w: int, h: int, title: str, body: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc">'
        f'<title id="title">{ink.esc(title)}</title>'
        f'<desc id="desc">{DESC}</desc>'
        f'<rect width="{w}" height="{h}" fill="{GROUND}"/>'
        f'{body}</svg>'
    )

# Consolas / Cascadia Mono / SF Mono all sit near 0.6em per glyph. ink.text_width
# is a Georgia-class serif metric, so any mono run measured with it comes out
# ~20% narrow — which is how a rule ended up drawn through its own label.
MONO_EM = 0.6


def mono_width(body: str, size: float, tracking: float = 0.0) -> float:
    """Advance width of a monospaced run, including per-glyph letter-spacing."""
    n = max(len(str(body)), 1)
    return n * (size * MONO_EM + tracking)


def chrome(x: float, y: float, left: str, right: str = "", w: int = 960) -> list[str]:
    """The `INK LAB / nn · style · palette` line every banner wears."""
    out = [type_line(x, y, left, 12, MUTED, ink.MONO, tracking="2")]
    if right:
        out.append(type_line(w - x, y, right, 12, MUTED, ink.MONO, anchor="end", tracking="1"))
    return out


def tick(x: float, y: float, colour: str, seed: int, s: float = 9.0) -> list[str]:
    """A hand-drawn check: two strokes, never a glyph."""
    return [
        ink.path(ink.hand_line(x, y, x + s * 0.42, y + s * 0.5, seed=seed, bend=0.14),
                 colour, 2.2),
        ink.path(ink.hand_line(x + s * 0.42, y + s * 0.5, x + s * 1.05, y - s * 0.42,
                               seed=seed + 5, bend=0.1), colour, 2.2),
    ]


def root_motif(cx: float, cy: float, r: float, seed: int) -> list[str]:
    """ORIGIN as a drawing: declared boundary, hatching, rays, one spark."""
    out: list[str] = []
    out.append(ink.path(ink.ellipse(cx, cy, r, r * 0.98, seed=seed, w=0.03), INK, 2.0, 0.9))
    out.append(ink.path(ink.ellipse(cx, cy, r * 0.66, r * 0.63, seed=seed + 7, w=0.05),
                        GOLD, 1.6, 0.85))
    out += ink.hachure([(cx + math.cos(a) * r * 0.62, cy + math.sin(a) * r * 0.6)
                        for a in [i * math.tau / 11 for i in range(11)]],
                       angle_deg=-41, gap=r * 0.16, seed=seed + 11)
    out += ink.rays(cx, cy, r * 1.06, r * 1.42, 9, seed=seed + 13, bend=0.08)
    out += ink.spark(cx - r * 0.12, cy - r * 0.1, r * 0.3, seed=seed + 17, colour=GOLD)
    return [o if o.startswith("<") else ink.path(o, GOLD, 1.4, 0.55) for o in out]



# ── data panels ───────────────────────────────────────────────────────────────
# The panels below carry the page's actual data, so they get the same treatment
# as the ornaments: real ink, one type scale, and type that survives the 0.322x
# mobile scale. They live here rather than in render_profile.py so the data
# assembly and the drawing stay separate: the caller hands over plain dicts.

def panel_doc(w: int, h: int, title: str, body: str) -> str:
    """A panel: ink ground, brush frame, and the same title bar as the rails."""
    parts = [ink.brush_box(6, 6, w - 12, h - 12, width=3.2, seed=ink.seed_of(title),
                           overshoot=12, colour=INK, opacity=ALPHA["full"])]
    parts.append(type_line(26, 46, title, TYPE["label"], INK, ink.MONO, tracking="3"))
    parts.append(ink.brush_rule(26, w - 26, 60, width=STROKE["hair"], seed=11,
                                colour=INK, opacity=ALPHA["ghost"]))
    return doc(w, h, title, "".join(parts) + body)


def process_panel(rows: list, host: str, stamp: str, panel_title: str = "process.table") -> str:
    """Twelve live modules as a task board: pid, name, language, state, note.

    `rows` is a list of dicts with keys pid / name / lang / status / colour /
    note / bar. `bar` in 0..1 draws a brush progress stroke instead of a status.
    """
    w = 960
    top = 92
    row_h = 48
    h = top + len(rows) * row_h + 34
    out = [panel_doc(w, h, panel_title, "")]
    count = f"[{len(rows)} tasks]"
    out.append(type_line(w - 26, 46, count, TYPE["micro"], GOLD, ink.MONO,
                         anchor="end", tracking="2"))
    if stamp:
        # measured against the count, not guessed: two right-aligned runs used
        # to collide exactly the way the rails did
        out.append(type_line(w - 26 - mono_width(count, TYPE["micro"], 2) - 26, 46,
                             stamp, TYPE["micro"], MUTED, ink.MONO, anchor="end",
                             tracking="2"))
    for x, cap in ((26, "PID"), (108, "MODULE"), (470, "LANG"), (556, "STATE")):
        out.append(type_line(x, 84, cap, TYPE["micro"], MUTED, ink.MONO, tracking="4"))

    y = top + 22
    for r in rows:
        out.append(type_line(26, y, r["pid"], TYPE["micro"], GOLD, ink.MONO, tracking="1"))
        out.append(type_line(108, y, r["name"], TYPE["label"], INK, ink.SERIF))
        out.append(type_line(470, y, r.get("lang") or "-", TYPE["micro"], LAPIS,
                             ink.MONO, tracking="1"))
        if r.get("bar") is not None:
            frac = max(0.0, min(1.0, float(r["bar"])))
            out.append(ink.brush_rule(556, 656, y - 8, width=STROKE["body"],
                                      seed=int(frac * 1000) + 3, colour=MUTED,
                                      opacity=ALPHA["soft"], enter=0.02, exit_=0.02))
            filled = 556 + 100 * frac
            if filled > 566:
                out.append(ink.brush_rule(556, filled, y - 8, width=STROKE["body"],
                                          seed=int(frac * 1000) + 3, colour=ROSE,
                                          enter=0.02, exit_=0.04))
            out.append(type_line(668, y, f"{int(round(frac * 100))}%", TYPE["micro"],
                                 GOLD, ink.MONO, tracking="1"))
        else:
            out.append(type_line(556, y, r.get("status") or "", TYPE["micro"],
                                 r.get("colour") or GOLD, ink.MONO, tracking="2"))
        if r.get("note"):
            out.append(type_line(716, y, r["note"], TYPE["micro"], MUTED, ink.MONO,
                                 tracking="1"))
        y += row_h
    out.append(ink.brush_rule(26, w - 26, h - 40, width=STROKE["hair"], seed=17,
                              colour=INK, opacity=ALPHA["faint"]))
    out.append(type_line(26, h - 12, host, TYPE["micro"], MUTED, ink.MONO, tracking="1"))
    return doc(w, h, panel_title, "".join(out[:1]) + "".join(out[1:]))



def heatmap_panel(host: str, weeks: list, total: int, ramp: list, months: list) -> str:
    """The 53-week contribution grid, drawn as inked cells rather than <rect>s.

    Cells are brush-filled squares with jittered edges, so an empty week reads as
    a faint drawn mark and a busy week reads as solid, the way a hand-inked
    calendar does.
    """
    cols = len(weeks)
    cell, gap, left, top = 26, 8, 92, 96
    w = left + cols * (cell + gap) + 40
    h = top + 7 * (cell + gap) + 74
    out = [panel_doc(w, h, "contribution.memory", "")]
    out.append(type_line(w - 26, 46, f"{total:,} TOTAL", TYPE["micro"], GOLD, ink.MONO,
                         anchor="end", tracking="2"))
    last_month, last_label_x = -1, -1e9
    for col, week in enumerate(weeks):
        days = week.get("contributionDays") or []
        if not days:
            continue
        x = left + col * (cell + gap)
        month = int(str(days[0].get("date") or "")[5:7] or 0)
        # month labels collided ("SepOct") because nothing measured the previous
        # one; keep them apart by their own rendered width
        name = months[month - 1] if month else ""
        need = mono_width(name, TYPE["micro"] - 4, 1) if name else 0
        if month and (month != last_month or x - last_label_x > need + 24):
            last_month, last_label_x = month, x
            out.append(type_line(x, top - 18, name, TYPE["micro"] - 4,
                                 MUTED, ink.MONO, tracking="1"))
        for row, day in enumerate(days[:7]):
            level = int(day.get("level") or 0)
            colour = ramp[min(level, len(ramp) - 1)]
            cx, cy = x + cell / 2, top + row * (cell + gap) + cell / 2
            out.append(ink.brush_fill(
                ink.chip(cx, cy, cell * 0.46, seed=ink.seed_of(f"{col}-{row}-{level}")),
                colour))
    for row, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        out.append(type_line(left - 18, top + row * (cell + gap) + cell * 0.72, name,
                             TYPE["micro"] - 4, MUTED, ink.MONO, anchor="end"))
    ly = h - 34
    out.append(type_line(left, ly + 8, "LESS", TYPE["micro"] - 4, MUTED, ink.MONO,
                         tracking="2"))
    for i, colour in enumerate(ramp):
        cx = left + mono_width("LESS", TYPE["micro"] - 4, 2) + 26 + i * (cell + gap)
        out.append(ink.brush_fill(
            ink.chip(cx, ly, cell * 0.46, seed=ink.seed_of(f"ramp-{i}")), colour))
    out.append(type_line(left + mono_width("LESS", TYPE["micro"] - 4, 2) + 26 +
                         len(ramp) * (cell + gap) + 8, ly + 8, "MORE",
                         TYPE["micro"] - 4, MUTED, ink.MONO, tracking="2"))
    out.append(ink.brush_rule(left, w - 40, h - 16, width=STROKE["hair"], seed=19,
                              colour=INK, opacity=ALPHA["faint"]))
    out.append(type_line(w - 40, h - 16, host, TYPE["micro"] - 4, MUTED, ink.MONO,
                         anchor="end", tracking="1"))
    return doc(w, h, "contribution.memory", "".join(out))


# ── hero: the signature ───────────────────────────────────────────────────────
SIGNATURE = ASSETS / "dwgx-signature.svg"
_PT = re.compile(r"[ML](-?[\d.]+) (-?[\d.]+)")


def signature_layer(x: float, y: float, width: float, colour: str,
                    opacity: float = 1.0, scale_width: float = 1.0) -> tuple[str, tuple]:
    """Drop the Owner's own hand into the composition at a known width.

    Reads assets/dwgx-signature.svg — the file sign/index.html exports — and
    normalises its ink bounding box, so a signature drawn on any canvas size
    lands at the same place in the hero. Returns the markup and the box it drew.
    """
    root = ElementTree.fromstring(SIGNATURE.read_text("utf-8"))
    ns = "{http://www.w3.org/2000/svg}"
    parts, xs, ys = [], [], []
    for el in root:
        if el.tag == f"{ns}path":
            d = el.get("d", "")
            for px, py in _PT.findall(d):
                xs.append(float(px))
                ys.append(float(py))
            parts.append((d, float(el.get("stroke-width") or 4)))
        elif el.tag == f"{ns}circle":
            xs.append(float(el.get("cx")))
            ys.append(float(el.get("cy")))
            parts.append((f'circle:{el.get("cx")}:{el.get("cy")}', float(el.get("r") or 2)))
    if not parts:
        raise SystemExit("assets/dwgx-signature.svg has no ink in it")
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    k = width / (x1 - x0)
    body = []
    for d, w in parts:
        if d.startswith("circle:"):          # a dot stroke, not a path
            _, cx, cy = d.split(":")
            body.append(f'<circle cx="{cx}" cy="{cy}" r="{w * k * scale_width:.2f}" '
                        f'fill="{colour}" stroke="none"/>')
            continue
        body.append(f'<path d="{d}" stroke-width="{w * k * scale_width:.2f}"/>')
    box = (x, y, (x1 - x0) * k, (y1 - y0) * k)
    return (f'<g transform="translate({ink.fmt(x - x0 * k)} {ink.fmt(y - y0 * k)}) '
            f'scale({ink.fmt(k)})" fill="none" stroke="{colour}" stroke-linecap="round" '
            f'stroke-linejoin="round" opacity="{ink.fmt(opacity)}">'
            + "".join(body) + "</g>", box)


def hero(profile: dict) -> str:
    """The plate a signature sits on. One hand, one swash, no confetti.

    The aerosol and the off-register second print both read as dirt at this
    size; the plate earns its weight from the frame and the mark alone.
    """
    w, h = 960, 386
    ident = profile.get("identity", {})
    flag = profile.get("flagship", {})
    host = str(flag.get("url", "")).replace("https://", "")
    alias = str(ident.get("alias", ""))

    b: list[str] = []
    b.append(ink.brush_box(14, 14, w - 28, h - 28, width=4.5, seed=3,
                           overshoot=26, colour=INK, opacity=0.55))
    b += chrome(44, 50, "dwgx · PROFILE · 09 · crayon", f"{ident.get('from', '')} · {host}")
    b.append(ink.brush_rule(44, w - 44, 64, width=3.0, seed=5, colour=INK, opacity=0.4))

    sig_x, sig_y, sig_w = 96.0, 92.0, 540.0
    main_svg, box = signature_layer(sig_x, sig_y, sig_w, INK)
    b.append(main_svg)

    # one swash, struck under the hand and dying at both ends
    under = box[1] + box[3] + 20
    b.append(ink.brush_rule(box[0] - 24, box[0] + box[2] + 30, under, width=8.0,
                           seed=137, sag=5, colour=GOLD, enter=0.1, exit_=0.3))
    b += ink.drip(box[0] + box[2] * 0.52, under + 3, 30, seed=139, w=3.6, colour=GOLD)

    # a single index mark, top right of the plate, so the corner is not empty
    # spark() hands back path data for the arms and markup for the dot
    b += [o if o.startswith("<") else ink.path(o, ROSE, 2.6) for o in
          ink.spark(w - 96, 96, 26, seed=151, colour=ROSE)]
    b.append(type_line(w - 96, 150, "SIGNED", 20, MUTED, ink.MONO, anchor="middle",
                      tracking="4"))

    if alias:
        b.append(type_line(44, 360, alias, 22, MUTED, ink.MONO, tracking="1"))
    b.append(type_line(w - 44, 360, str(flag.get("zh_tagline", "")), 38, GOLD, ink.SERIF,
                      anchor="end", italic=True))
    return doc(w, h, f"{TITLE} · signature", "".join(b))



# ── boot keys ────────────────────────────────────────────────────────────────
KEYS = [("01", "MAIN"), ("02", "PROCESS"), ("03", "ORIGIN"),
        ("04", "MODULES"), ("05", "PHANTASM"), ("06", "GUESTBOOK")]


def key_cap(num: str, label: str, idx: int) -> str:
    """A keycap: marker box, index in the corner, one confident strike."""
    w, h = 156, 58
    b = [ink.brush_box(5, 5, w - 10, h - 10, width=4.0, seed=41 + idx * 6,
                       overshoot=7, colour=INK, opacity=0.9)]
    b.append(type_line(18, 30, num, 13, GOLD, ink.MONO, tracking="1"))
    b.append(type_line(w - 16, 30, label, 14, INK, ink.MONO, anchor="end", tracking="1.5"))
    b.append(ink.brush_rule(18, w - 18, 42, width=4.4, seed=53 + idx * 6,
                            colour=AURORA, opacity=0.8, enter=0.04, exit_=0.3))
    return doc(w, h, f"{label} section link", "".join(b))


# ── section rails ────────────────────────────────────────────────────────────
RAILS = [
    ("01", "SYSTEM CONFIGURATION", "dwgx.cfg"),
    ("02", "PROCESS MEMORY", "loaded modules"),
    ("03", "GENESIS CHAMBER", "origin"),
    ("04", "EXPANSION SLOTS", "selected work"),
    ("05", "MACHINE INVENTORY", "devices"),
    ("06", "PHANTASM ARCHIVE", "touhou"),
    ("07", "ACTIVITY MEMORY", "graph / stats"),
    ("08", "BBS GUESTBOOK", "leave a trace"),
]


def rail(num: str, label: str, sub: str, idx: int) -> str:
    """A divider struck with a loaded brush.

    Every horizontal slot is measured with the mono metric and clamped, so a
    long label or a long sub can never push a rule through text or invert it.
    """
    w, h = 960, 62
    gap = 30
    num_w = mono_width(num, 22, 1)
    label_w = mono_width(label, 26, 3)
    num_x = 20
    label_x = num_x + num_w + 22
    label_end = label_x + label_w

    right_limit = w - 20
    sub_w = mono_width(sub, 22, 2)
    sub_x = right_limit - sub_w
    left_end = num_x - gap
    right_start = label_end + gap
    right_end = sub_x - gap

    def hits(seg, span):
        return max(0.0, min(seg[1], span[1]) - max(seg[0], span[0]))

    spans = ((num_x, num_x + num_w), (label_x, label_end), (sub_x, right_limit))

    def clear(a, b_):
        return all(hits((a, b_), sp) <= 0 for sp in spans)

    b = []
    if left_end > 70 and clear(20, left_end):
        b.append(ink.brush_rule(20, left_end, 31, width=6.0, seed=61 + idx * 5, sag=1.5,
                                colour=INK, opacity=0.85, enter=0.02, exit_=0.22))
    # drop the sub, not the rule, when the two collide
    if right_start + 90 >= right_end:
        sub_x = None
        right_end = right_limit - 10
    if right_end - right_start >= 90 and clear(right_start, right_end):
        b.append(ink.brush_rule(right_start, right_end, 31, width=6.0,
                                seed=67 + idx * 5, sag=-1.5, colour=INK,
                                opacity=0.85, enter=0.22, exit_=0.02))
    b.append(type_line(num_x, 40, num, 22, GOLD, ink.MONO, tracking="1"))
    b.append(type_line(label_x, 40, label, 26, INK, ink.MONO, tracking="3"))
    if sub_x is not None:
        b.append(type_line(sub_x, 40, sub, 22, MUTED, ink.MONO, tracking="2"))
    return doc(w, h, label, "".join(b))
    ("03", "GENESIS CHAMBER", "origin"),


# ── rear I/O panel ───────────────────────────────────────────────────────────
def io_panel() -> str:
    """Rear I/O: a panel with real ports, each one a filled mark."""
    w, h = 960, 104
    b = [ink.brush_box(12, 10, w - 24, h - 20, width=4.0, seed=83, overshoot=14,
                       colour=INK, opacity=0.85)]
    x = 34
    ports = [(80, 26), (50, 26), (62, 18), (42, 34), (72, 30), (56, 22),
             (86, 24), (46, 30)]
    for i, (pw, ph) in enumerate(ports):
        b.append(ink.brush_box(x, 82 - ph, pw, ph, width=3.4, seed=89 + i * 4,
                               overshoot=5, colour=AURORA if i % 2 else INK, opacity=0.9))
        x += pw + 28
    b.append(type_line(34, 44, "REAR I/O", 22, MUTED, ink.MONO, tracking="4"))
    b.append(type_line(w - 34, 44, "dwgx@main", 22, GOLD, ink.MONO, anchor="end",
                      tracking="2"))
    b.append(ink.brush_rule(34, w - 34, 64, width=3.2, seed=97, colour=INK, opacity=0.3))
    return doc(w, h, "Decorative rear I/O panel", "".join(b))


# ── phantasm danmaku ─────────────────────────────────────────────────────────
def phantasm() -> str:
    """Touhou danmaku as brush ticks crossing the band, not as dots."""
    w, h = 960, 126
    b: list[str] = []
    for i in range(30):
        s_ = ink.seed_of(f"danmaku-{i}")
        x = 26 + (s_ % 900)
        y = 26 + (s_ >> 5) % 62
        ln = 16 + (s_ >> 11) % 26
        tilt = -22 + (s_ >> 17) % 44
        d = ink.brush([(x, y + ln / 2), (x + ln, y - ln / 2)], width=6.0,
                      seed=s_, enter=0.05, exit_=0.42, jitter=0.2)
        b.append(ink.brush_fill(d, AURORA if i % 3 else GOLD, 0.5 + (i % 4) * 0.12))
    b.append(ink.brush_rule(24, w - 24, 74, width=2.6, seed=97, colour=INK, opacity=0.35))
    b.append(type_line(24, 116, "幻想万華鏡 · THE MEMORIES OF PHANTASM", 26, MUTED,
                      ink.MONO, tracking="4"))
    return doc(w, h, "Touhou danmaku ornament for the Phantasm feature", "".join(b))


# ── end of file ──────────────────────────────────────────────────────────────
def eof() -> str:
    """Shutdown: two struck rules, a brush arrow back to the boot menu, the sign-off."""
    w, h = 960, 176
    b = [ink.brush_rule(40, w / 2 - 130, 46, width=5.0, seed=101, sag=2,
                        colour=INK, opacity=0.6, enter=0.02, exit_=0.2),
         ink.brush_rule(w / 2 + 130, w - 40, 46, width=5.0, seed=103, sag=-2,
                        colour=INK, opacity=0.6, enter=0.2, exit_=0.02)]
    b.append(ink.path(ink.arrow(w / 2 - 150, 92, w / 2 - 250, 92, seed=107, head=22),
                      GOLD, 4.0))
    b.append(type_line(w / 2, 102, "〔 返回 boot.menu 〕", 38, INK, ink.SERIF, anchor="middle"))
    b.append(ink.brush_rule(w / 2 - 170, w / 2 + 170, 130, width=4.0, seed=109,
                            colour=GOLD, opacity=0.55))
    b.append(type_line(w / 2, 158, "END OF FILE · 主机关机", 22, MUTED, ink.MONO,
                      anchor="middle", tracking="4"))
    return doc(w, h, "End of file, return to the dwgx.menu navigation", "".join(b))


# ── rubber stamps ────────────────────────────────────────────────────────────
STAMPS = [("dwgx", "PERSONAL WEB"), ("bios", "SETUP UTILITY"),
          ("ascii", "SERIAL CONSOLE"), ("touhou", "DANMAKU ARCHIVE")]


def stamp(word: str, sub: str, idx: int) -> str:
    """A rubber stamp: hit slightly off square and rocked a few degrees."""
    w, h = 176, 62
    b = [ink.brush_box(6, 6, w - 12, h - 12, width=6.4, seed=113 + idx * 9,
                       overshoot=8, colour=AURORA, opacity=0.85),
         ink.brush_box(14, 14, w - 28, h - 28, width=3.0, seed=131 + idx * 9,
                       overshoot=4, colour=AURORA, opacity=0.4)]
    b.append(type_line(w / 2, 36, word.upper(), 22, GOLD, ink.SERIF,
                      anchor="middle", weight="600", tracking="1"))
    b.append(type_line(w / 2, 52, sub, 14, MUTED, ink.MONO, anchor="middle", tracking="1"))
    tilt = -3.4 + idx * 2.1                      # a hand never hits a stamp square
    body = "".join(b)
    return doc(w, h, f"{word.upper()} decorative web button",
               f'<g transform="rotate({tilt:.1f} {w / 2} {h / 2})">{body}</g>')


def build(profile: dict) -> dict[str, str]:
    out = {
        "ink-hero.svg": hero(profile),
        "ink-io.svg": io_panel(),
        "ink-phantasm.svg": phantasm(),
        "ink-eof.svg": eof(),
    }
    for i, (num, label) in enumerate(KEYS):
        out[f"ink-key-0{i + 1}.svg"] = key_cap(num, label, i)
    for i, (num, label, sub) in enumerate(RAILS):
        out[f"ink-rail-0{i + 1}.svg"] = rail(num, label, sub, i)
    for i, (word, sub) in enumerate(STAMPS):
        out[f"ink-stamp-{word}.svg"] = stamp(word, sub, i)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if any committed asset differs from a fresh render")
    args = ap.parse_args()
    profile = tomllib.loads((ROOT / "profile.toml").read_text("utf-8"))
    files = build(profile)
    drift: list[str] = []
    for name, svg in sorted(files.items()):
        path = ASSETS / name
        if args.check:
            if not path.exists() or path.read_text("utf-8") != svg:
                drift.append(name)
            continue
        path.write_text(svg, encoding="utf-8")
        print(f"{name:<22} {len(svg.encode('utf-8')):>6} B")
    stale = sorted(p.name for p in ASSETS.glob("ink-*.svg") if p.name not in files)
    if args.check:
        if drift or stale:
            if drift:
                print("drift: " + ", ".join(drift))
            if stale:
                print("stale (no longer produced): " + ", ".join(stale))
            return 1
        print(f"clean: {len(files)} assets match a fresh render")
    elif stale:
        for name in stale:
            (ASSETS / name).unlink()
            print(f"removed stale {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
