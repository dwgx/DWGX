#!/usr/bin/env python3
"""repo-kit · INK — the hand-drawn stroke engine, ported from dwgx's own Art Lab.

Source of truth: D:\\Project\\genesis\\genesis-site\\src\\scripts\\handgen.ts (owner-written,
mulberry32 seeded, two-frequency radius wobble, lift-off gap, overshoot hook,
recursive midpoint subdivision, hachure at -41 degrees). The four palettes come
from the same project's palettes.ts (cosmic / crayon / science / sigil). Ported to
Python so the repo-kit workflow needs nothing but the standard library.

Determinism: string seeds are hashed with sha256 into a numeric seed, so the same
repository renders byte-identically on every run. The banner workflow commits
every six hours; a generator that drifted would commit forever.
"""
from __future__ import annotations

import hashlib
import math

TAU = math.pi * 2
MASK32 = 0xFFFFFFFF

# palettes.ts, verbatim role names
PALETTES = {
    "cosmic": {"ink": "#f0eee6", "gold": "#e5c07b", "aurora": "#1fa27d",
               "violet": "#8b7fd4", "lapis": "#638aaf", "rose": "#d97757"},
    "crayon": {"ink": "#f0eee6", "gold": "#e5c07b", "aurora": "#d97757",
               "violet": "#8a7060", "lapis": "#6b7280", "rose": "#c07060"},
    "science": {"ink": "#e8dcc8", "gold": "#c45c26", "aurora": "#2f6b4f",
                "violet": "#3d4a7a", "lapis": "#4a5a8a", "rose": "#b85c38"},
    "sigil": {"ink": "#f0eee6", "gold": "#e5c07b", "aurora": "#1fa27d",
              "violet": "#d97757", "lapis": "#638aaf", "rose": "#e5c07b"},
}
GROUND = {"dark": "#0B0A0C", "light": "#F4EFE6"}

SERIF = "Georgia,'Iowan Old Style','Times New Roman',Times,serif"
MONO = "ui-monospace,'Cascadia Mono',Consolas,'SF Mono',monospace"


def seed_of(key: str | int) -> int:
    """Stable numeric seed. Python's hash() is salted per process, so never use it."""
    if isinstance(key, int):
        return key & MASK32
    return int.from_bytes(hashlib.sha256(key.encode("utf-8")).digest()[:4], "big")


def rng(seed: int):
    """mulberry32, byte for byte what handgen.ts ships."""
    a = seed & MASK32

    def nxt() -> float:
        nonlocal a
        a = (a + 0x6D2B79F5) & MASK32
        t = a
        t = ((t ^ (t >> 15)) * (1 | t)) & MASK32
        t = (t + ((t ^ (t >> 7)) * (61 | t)) & MASK32) & MASK32
        t ^= (t >> 14)
        return (t & MASK32) / 4294967296.0

    return nxt


def fmt(n: float) -> float:
    return round(n * 100) / 100


def _d(points: list[tuple[float, float]], close: bool) -> str:
    head = f"M{fmt(points[0][0])} {fmt(points[0][1])}"
    rest = " ".join(f"L{fmt(x)} {fmt(y)}" for x, y in points[1:])
    return head + " " + rest + (" Z" if close else "")


def polyline(points, seed=3, close=False, roughness=0.4) -> str:
    """handgen.ts polyline: every point gets a small independent jitter."""
    rnd = rng(seed ^ 0x9E37)
    j = [(x + (rnd() - 0.5) * roughness * 0.35, y + (rnd() - 0.5) * roughness * 0.35)
         for x, y in points]
    return _d(j, close)


def _radius_at(rnd, t: float, w: float, r: float) -> float:
    p1 = math.sin(t * 3 + rnd() * TAU)
    p2 = math.sin(t * 7 + rnd() * TAU)
    return r * (1 + w * 0.7 * p1 + w * 0.3 * p2)


def ellipse(cx: float, cy: float, rx: float, ry: float, seed: int = 7, w: float = 0.045,
            points: int = 11, gap: float = 0.035, overshoot: float = 0.06) -> str:
    """handgen.ts handEllipse: wobbling polygon, left open by `gap`, plus a hook."""
    rnd = rng(seed)
    end = TAU * (1 - gap)
    pts = []
    for i in range(points + 1):
        t = (i / points) * end
        rw = _radius_at(rnd, t, w, 1.0)
        pts.append((cx + math.cos(t) * rx * rw, cy + math.sin(t) * ry * rw))
    r0 = _radius_at(rnd, 0.0, w, 1.0)
    hook = (cx + math.cos(-overshoot * 0.6) * rx * r0 * 1.02,
            cy + math.sin(-overshoot * 0.6) * ry * r0 * 1.02)
    return polyline([hook, *pts], seed=seed, close=False)


def circle(cx: float, cy: float, r: float, **kw) -> str:
    return ellipse(cx, cy, r, r, **kw)


def hand_line(x1: float, y1: float, x2: float, y2: float, seed: int = 11,
              bend: float = 0.05) -> str:
    """handgen.ts handLine: endpoints anchored, midpoint displaced, subdivided twice."""
    rnd = rng(seed)
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / length, dx / length

    def sub(a, b, depth):
        if depth <= 0:
            return [a, b]
        mx = (a[0] + b[0]) / 2 + nx * (rnd() - 0.5) * 2 * bend * length / (2 ** depth)
        my = (a[1] + b[1]) / 2 + ny * (rnd() - 0.5) * 2 * bend * length / (2 ** depth)
        return sub(a, (mx, my), depth - 1)[:-1] + [(mx, my)] + sub((mx, my), b, depth - 1)

    return polyline(sub((x1, y1), (x2, y2), 2), seed=seed, close=False)


def smooth(points, seed: int = 5, close: bool = False) -> str:
    """handgen.ts smoothPoly: quadratic segments through every anchor."""
    rnd = rng(seed)
    pts = [(x + (rnd() - 0.5) * 0.5, y + (rnd() - 0.5) * 0.5) for x, y in points]
    if len(pts) < 3:
        return _d(pts, close)
    mid = lambda a, b: ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)  # noqa: E731
    out = [f"M{fmt(pts[0][0])} {fmt(pts[0][1])}"]
    span = list(zip(pts, pts[1:] + ([pts[0]] if close else [])))
    for i, (a, b) in enumerate(span):
        nxt_pt = span[(i + 1) % len(span)][0] if close or i + 1 < len(span) else b
        c = mid(a, b)
        e = mid(b, nxt_pt)
        out.append(f"Q{fmt(c[0])} {fmt(c[1])} {fmt(e[0])} {fmt(e[1])}")
    if close:
        out.append("Z")
    return " ".join(out)


def hachure(points, angle_deg: float = -41.0, gap: float = 4.5, seed: int = 13) -> list[str]:
    """handgen.ts hachure: parallel pen strokes clipped to a polygon's extent."""
    rnd = rng(seed)
    rad = math.radians(angle_deg)
    dx, dy = math.cos(rad), math.sin(rad)
    nx, ny = -dy, dx
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    min_x, max_x, min_y, max_y = min(xs), max(xs), min(ys), max(ys)
    diag = (max_x - min_x) + (max_y - min_y)
    c = (min_x + max_x) / 2 * dy - (min_y + max_y) / 2 * dx
    lines: list[str] = []
    i = 0
    while c < diag:
        px, py = -dy * c + dx * (min_x + max_x) / 2, dx * c + dy * (min_y + max_y) / 2
        seg = _clip_line((px - nx * diag, py - ny * diag), (px + nx * diag, py + ny * diag),
                         (min_x - 2, min_y - 2, max_x + 2, max_y + 2))
        if seg:
            jitter = gap * 0.4 * (rnd() - 0.5)
            lines.append(hand_line(seg[0][0] + dx * jitter, seg[0][1] + dy * jitter,
                                   seg[1][0] + dx * jitter, seg[1][1] + dy * jitter,
                                   seed=seed + i, bend=0.02))
        c += gap
        i += 1
    return lines


def _clip_line(p0, p1, box):
    """Liang-Barsky: return the segment inside box=(x0,y0,x1,y1) or None."""
    x0, y0, x1, y1 = box
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    t0, t1 = 0.0, 1.0
    for p, q in ((-dx, p0[0] - x0), (dx, x1 - p0[0]), (-dy, p0[1] - y0), (dy, y1 - p0[1])):
        if p == 0:
            if q < 0:
                return None
            continue
        r = q / p
        if p < 0:
            if r > t1:
                return None
            t0 = max(t0, r)
        else:
            if r < t0:
                return None
            t1 = min(t1, r)
    return ((p0[0] + t0 * dx, p0[1] + t0 * dy), (p0[0] + t1 * dx, p0[1] + t1 * dy))


def arc(cx: float, cy: float, r: float, a0: float, a1: float, seed: int = 17,
        w: float = 0.04, points: int = 9) -> str:
    rnd = rng(seed)
    pts = []
    for i in range(points + 1):
        t = a0 + (a1 - a0) * i / points
        rw = _radius_at(rnd, t, w, 1.0)
        pts.append((cx + math.cos(t) * r * rw, cy + math.sin(t) * r * rw))
    return polyline(pts, seed=seed, close=False)


def dashed_ellipse(cx, cy, rx, ry, dash_count=18, seed=23, w=0.04) -> list[str]:
    out = []
    for i in range(dash_count):
        t0 = TAU * i / dash_count
        t1 = t0 + TAU / dash_count * 0.55
        out.append(arc(cx, cy, 1.0, 0, 0, seed=seed) if False else
                   _arc_scaled(cx, cy, rx, ry, t0, t1, seed + i, w))
    return out


def _arc_scaled(cx, cy, rx, ry, t0, t1, seed, w=0.04, points=3) -> str:
    rnd = rng(seed)
    pts = []
    for i in range(points + 1):
        t = t0 + (t1 - t0) * i / points
        rw = _radius_at(rnd, t, w, 1.0)
        pts.append((cx + math.cos(t) * rx * rw, cy + math.sin(t) * ry * rw))
    return polyline(pts, seed=seed, close=False)


def rays(cx, cy, r0, r1, n, seed=29, bend=0.06) -> list[str]:
    rnd = rng(seed)
    out = []
    for i in range(n):
        a = TAU * i / n + rnd() * 0.18
        reach = r1 * (0.75 + 0.35 * rnd())
        out.append(hand_line(cx + math.cos(a) * r0, cy + math.sin(a) * r0,
                             cx + math.cos(a) * reach, cy + math.sin(a) * reach,
                             seed=seed + i * 7, bend=bend))
    return out


def spark(cx, cy, r, seed=31) -> list[str]:
    """Four-point star: two crossed strokes, each overshooting the centre."""
    out = []
    for i in range(2):
        a = math.radians(45) + i * math.pi / 2
        dx, dy = math.cos(a) * r, math.sin(a) * r
        out.append(hand_line(cx - dx, cy - dy, cx + dx * 1.12, cy + dy * 1.12,
                             seed=seed + i, bend=0.08))
    return out


def spiral(cx, cy, r0, r1, turns=1.6, seed=37, points=26, w=0.03) -> str:
    rnd = rng(seed)
    pts = []
    for i in range(points + 1):
        t = turns * TAU * i / points
        r = r0 + (r1 - r0) * i / points
        rw = _radius_at(rnd, t, w, 1.0)
        pts.append((cx + math.cos(t) * r * rw, cy + math.sin(t) * r * rw))
    return polyline(pts, seed=seed, close=False)


def arrow(x1, y1, x2, y2, seed=41, head=11.0, bend=0.04) -> str:
    """Shaft plus a hand-drawn head; the head is two short strokes, never a triangle."""
    a = math.atan2(y2 - y1, x2 - x1)
    spread = math.radians(24)
    out = [hand_line(x1, y1, x2, y2, seed=seed, bend=bend)]
    for i, s in enumerate((-spread, spread)):
        out.append(hand_line(x2, y2,
                             x2 - math.cos(a + s) * head, y2 - math.sin(a + s) * head,
                             seed=seed + i * 3, bend=0.12))
    return "".join(out)


def path(d: str, colour: str, width: float = 2.0, opacity: float = 1.0,
         cap: str = "round") -> str:
    return (f'<path d="{d}" fill="none" stroke="{colour}" stroke-width="{width}" '
            f'stroke-linecap="{cap}" stroke-linejoin="round" opacity="{opacity}"/>')


def ghost(d: str, colour: str, width: float = 2.0, factor: float = 0.3) -> str:
    """The second nervous system: the same shape drawn again, fainter and offset."""
    return (f'<path d="{d}" transform="translate(1.6 1.2)" fill="none" stroke="{colour}" '
            f'stroke-width="{width * 0.7:.1f}" stroke-linecap="round" stroke-linejoin="round" '
            f'opacity="{factor}"/>')


def rect_path(x, y, w, h, seed=43, wobble=0.05) -> str:
    """A sketched box: four separately wobbling sides, corners deliberately missed."""
    return polyline([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], seed=seed,
                    close=True, roughness=wobble * 8)


def text(x, y, body, size, colour, family=SERIF, weight="400", anchor="start",
         italic=False, tracking=None, opacity=1.0) -> str:
    tr = f' letter-spacing="{tracking}"' if tracking else ""
    it = ' font-style="italic"' if italic else ""
    op = f' opacity="{opacity}"' if opacity != 1.0 else ""
    return (f'<text x="{x:.0f}" y="{y:.0f}" font-size="{size}" font-family="{family}" '
            f'font-weight="{weight}" fill="{colour}" text-anchor="{anchor}"{tr}{it}{op}>'
            f'{esc(body)}</text>')


def esc(value) -> str:
    return (str(value).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))
