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
               "violet": "#8b7fd4", "lapis": "#638aaf", "rose": "#d97757",
               "muted": "#7E9AB8"},
    "crayon": {"ink": "#f0eee6", "gold": "#e5c07b", "aurora": "#d97757",
               "violet": "#9c8272", "lapis": "#7d8590", "rose": "#c07060",
               "muted": "#8A8F98"},
    "science": {"ink": "#e8dcc8", "gold": "#e08a4c", "aurora": "#57a98a",
                "violet": "#8e9cd0", "lapis": "#7a8ab8", "rose": "#e08a63",
                "muted": "#8A97B8"},
    "sigil": {"ink": "#f0eee6", "gold": "#e5c07b", "aurora": "#1fa27d",
              "violet": "#d97757", "lapis": "#638aaf", "rose": "#e5c07b",
              "muted": "#7E9AB8"},
}
GROUND = {"dark": "#0B0A0C", "light": "#F4EFE6"}

SERIF = "Georgia,'Iowan Old Style','Times New Roman',Times,serif"
MONO = "ui-monospace,'Cascadia Mono',Consolas,'SF Mono',monospace"

# The four Art Lab palettes are tuned for a near-black ground: every "ink" role in
# them is a paper cream, which measures 1.01:1 to 1.18:1 on the light ground. These
# are the same six roles restated as pigment on paper, verified for contrast in
# styles_ink (>=4.5:1 for text roles, >=3:1 for strokes).
PAPER_PALETTES = {
    "cosmic": {"ink": "#1C2430", "gold": "#7A5D18", "aurora": "#17715A",
               "violet": "#4B4391", "lapis": "#3F6280", "rose": "#A8452C",
               "muted": "#41586B"},
    "crayon": {"ink": "#2A2320", "gold": "#7A5D18", "aurora": "#A8452C",
               "violet": "#6B5647", "lapis": "#4A5158", "rose": "#93422F",
               "muted": "#4A5158"},
    "science": {"ink": "#26221A", "gold": "#8A4A1E", "aurora": "#2F6B4F",
                "violet": "#3D4A7A", "lapis": "#4A5A8A", "rose": "#A64E2E",
                "muted": "#4A5A8A"},
    "sigil": {"ink": "#1C2430", "gold": "#7A5D18", "aurora": "#17715A",
              "violet": "#A8452C", "lapis": "#3F6280", "rose": "#7A5D18",
              "muted": "#41586B"},
}


def palette_for(family: str, light: bool) -> dict:
    table = PAPER_PALETTES if light else PALETTES
    return table.get(family) or table["cosmic"]


# Georgia-class advance widths in em. A flat 0.5em per character is wrong in both
# directions: all-caps short names get a rule that stops short, long lowercase
# names get one that dangles into empty space (measured -22% to +16%).
_WIDE = set("MWmw@%")
_NARROW = set("iljtfrI.,;:'|!()[]{}-")


def text_width(body: str, size: float) -> float:
    """Approximate advance width of `body` in a Georgia-class serif at `size`."""
    total = 0.0
    for ch in str(body):
        if ord(ch) > 0x2E7F:
            total += 1.0            # CJK glyphs are full width
        elif ch in _WIDE:
            total += 0.86
        elif ch in _NARROW:
            total += 0.31
        elif ch.isupper():
            total += 0.68
        elif ch.isdigit():
            total += 0.55
        else:
            total += 0.50
    return total * size


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
        # the closing `^ t` is what makes this mulberry32 rather than a lookalike;
        # without it the second mixing step loses its feedback
        t = ((t + ((t ^ (t >> 7)) * (61 | t))) & MASK32) ^ t
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
    """handgen.ts smoothPoly: quadratic segments that pass through every anchor.

    The last segment stops at the midpoint of the final span, exactly like the
    reference, and the anchor jitter is half a unit rather than one.
    """
    rnd = rng(seed)
    pts = [(x + (rnd() - 0.5) * 0.25, y + (rnd() - 0.5) * 0.25) for x, y in points]
    if len(pts) < 3:
        return _d(pts, close)
    out = [f"M{fmt(pts[0][0])} {fmt(pts[0][1])}"]
    span = list(zip(pts, pts[1:] + ([pts[0]] if close else [])))
    for i, (a, b) in enumerate(span):
        if not close and i == len(span) - 1:
            break
        nxt_pt = span[(i + 1) % len(span)][0]
        c = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        e = ((b[0] + nxt_pt[0]) / 2, (b[1] + nxt_pt[1]) / 2)
        out.append(f"Q{fmt(c[0])} {fmt(c[1])} {fmt(e[0])} {fmt(e[1])}")
    if close:
        out.append("Z")
    return " ".join(out)


def hachure(points, angle_deg: float = -41.0, gap: float = 4.5, seed: int = 13) -> list[str]:
    """Parallel pen strokes at `angle_deg`, clipped to the polygon by a scanline.

    Every hatch line is the set of points with a constant projection onto the
    hatch normal, so the offset advances by `gap` in that coordinate and the
    line is intersected with the polygon edge list. Clipping to the bounding box
    would spill outside an oblique shape, which is what the polygons here are.
    """
    if gap <= 0:
        return []
    rnd = rng(seed)
    rad = math.radians(angle_deg)
    dx, dy = math.cos(rad), math.sin(rad)      # along the stroke
    nx, ny = -dy, dx                            # across the strokes
    poly = list(points)
    if len(poly) < 3:
        return []
    lo = min(nx * x + ny * y for x, y in poly)
    hi = max(nx * x + ny * y for x, y in poly)

    lines: list[str] = []
    i = 0
    c = lo + gap * 0.5
    while c < hi:
        hits: list[float] = []
        for k in range(len(poly)):
            ax, ay = poly[k]
            bx, by = poly[(k + 1) % len(poly)]
            a, b = nx * ax + ny * ay, nx * bx + ny * by
            if (a - c) * (b - c) <= 0 and a != b:
                t = (c - a) / (b - a)
                hits.append(ax + (bx - ax) * t)
                hits.append(ay + (by - ay) * t)
        if len(hits) >= 4:
            # the two crossings are the ends of the stroke; drawing a fixed reach
            # from their midpoint is what sent lines flying off the shape
            jx, jy = dx * gap * 0.18 * (rnd() - 0.5), dy * gap * 0.18 * (rnd() - 0.5)
            lines.append(hand_line(hits[0] + jx, hits[1] + jy,
                                   hits[2] - jx, hits[3] - jy,
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


def spark(cx, cy, r, seed=31, colour: str = "currentColor") -> list[str]:
    """Four arms swept around the centre plus the dot in the middle, like the
    reference: five elements, not two crossed strokes. The centre dot carries an
    explicit colour because `currentColor` inside an SVG rendered as an <img>
    resolves to the document default, not to the caller's palette."""
    rnd = rng(seed)
    out = []
    for i in range(4):
        a = math.radians(90) + i * math.pi / 2 + (rnd() - 0.5) * 0.24
        reach = r * (0.86 + 0.28 * rnd())
        out.append(hand_line(cx, cy, cx + math.cos(a) * reach, cy + math.sin(a) * reach,
                             seed=seed + i, bend=0.1))
    out.append(f'<circle cx="{fmt(cx)}" cy="{fmt(cy)}" r="{fmt(r * 0.16)}" fill="{colour}"/>')
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


# ── graffiti layer ────────────────────────────────────────────────────────────
# Marker and aerosol vocabulary, used where a hand is meant to be loud rather
# than neat. Every function here is new surface: nothing above this line calls
# them, so the 22 shipped banners render byte-identical.


def overshoot(x1: float, y1: float, x2: float, y2: float, frac: float = 0.06,
              seed: int = 61, bend: float = 0.04) -> str:
    """A marker stroke that runs past both of its endpoints — the thing that
    separates a signature from a line."""
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy) or 1.0
    ux, uy = dx / length, dy / length
    return hand_line(x1 - ux * length * frac, y1 - uy * length * frac,
                      x2 + ux * length * frac, y2 + uy * length * frac,
                      seed=seed, bend=bend)


def spray(cx: float, cy: float, r: float, n: int = 26, seed: int = 67,
          colour: str = "currentColor", density: float = 1.0) -> list[str]:
    """Aerosol: dots scattered on a radius-weighted disc, denser at the centre."""
    rnd = rng(seed)
    out = []
    for i in range(n):
        a = rnd() * TAU
        # sqrt keeps the disc even instead of piling everything at the middle
        d = r * math.sqrt(rnd()) * (0.55 + 0.45 * density)
        rad = 2.0 + rnd() * 1.6      # below 2.0 the dots read as fog, not spray
        out_op = 0.25 + 0.5 * (1 - d / max(r, 0.001)) * density
        out.append(f'<circle cx="{fmt(cx + math.cos(a) * d)}" cy="{fmt(cy + math.sin(a) * d)}" '
                   f'r="{fmt(rad)}" fill="{colour}" opacity="{fmt(out_op)}"/>')
    return out


def _resample(points, step: float):
    """Walk a polyline and emit points roughly `step` apart, ends included."""
    pts = list(points)
    if len(pts) < 2:
        return pts
    out = [pts[0]]
    carry = 0.0
    for a, b in zip(pts, pts[1:]):
        dx, dy = b[0] - a[0], b[1] - a[1]
        seg = math.hypot(dx, dy)
        if seg < 1e-9:
            continue
        ux, uy = dx / seg, dy / seg
        t = carry
        while t + step <= seg:
            t += step
            out.append((a[0] + ux * t, a[1] + uy * t))
        carry = t - seg + step
    if (out[-1][0] - pts[-1][0]) ** 2 + (out[-1][1] - pts[-1][1]) ** 2 > 1e-6:
        out.append(pts[-1])
    return out


def brush(points, width: float = 6.0, seed: int = 83, enter: float = 0.16,
          exit_: float = 0.26, bow: float = 0.0, jitter: float = 0.16) -> str:
    """A marker or brush stroke with a real width envelope, returned as path data.

    Every other primitive here draws a constant-width centre line, which is why
    hand-drawn output reads as cheap: a real stroke is fat in the belly and
    dies at both ends. This walks the centre line, offsets it left and right by
    a width profile, and closes the two sides into one filled outline.

    `enter` and `exit_` are the fractions of the length spent tapering.
    `bow` bows the belly sideways, `jitter` is the per-sample width noise.
    """
    pts = _resample(points, max(2.0, width * 0.45))
    if len(pts) < 2:
        if not pts:
            return ""
        r = width * 0.5
        return f"M{fmt(pts[0][0] - r)} {fmt(pts[0][1])} a{fmt(r)} {fmt(r)} 0 1 0 " \
               f"{fmt(r * 2)} 0 a{fmt(r)} {fmt(r)} 0 1 0 {fmt(-r * 2)} 0"
    rnd = rng(seed)
    n = len(pts)
    left, right = [], []
    for i, (x, y) in enumerate(pts):
        t = i / (n - 1)
        # envelope: ramp in, hold, ramp out, with a slight belly at the middle
        head = min(1.0, t / max(enter, 1e-6))
        tail = min(1.0, (1.0 - t) / max(exit_, 1e-6))
        env = min(head, tail) ** 0.72
        belly = 1.0 + 0.16 * math.sin(math.pi * t)
        w = width * 0.5 * env * belly * (1.0 + (rnd() - 0.5) * 2 * jitter)
        # normal from the local tangent
        ax, ay = pts[max(i - 1, 0)]
        bx, by = pts[min(i + 1, n - 1)]
        dx, dy = bx - ax, by - ay
        ln = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / ln, dx / ln
        # bow is in units, not a multiple of width: multiplying by width made the
        # two sides cross and the stroke folded back on itself
        b = math.sin(math.pi * t) * min(abs(bow), width * 0.28) * (1 if bow >= 0 else -1)
        left.append((x + nx * (w + b), y + ny * (w + b)))
        right.append((x - nx * max(w - b * 0.4, 0.2), y - ny * max(w - b * 0.4, 0.2)))
    ring = left + right[::-1]
    body = " ".join(("M" if i == 0 else "L") + f"{fmt(px)} {fmt(py)}"
                    for i, (px, py) in enumerate(ring))
    return f"{body} Z"


def brush_fill(d: str, colour: str, opacity: float = 1.0) -> str:
    return f'<path d="{d}" fill="{colour}" stroke="none" opacity="{fmt(opacity)}"/>'

def brush_box(x: float, y: float, w: float, h: float, width: float = 5.0,
              seed: int = 89, overshoot: float = 10.0, colour: str = "currentColor",
              opacity: float = 1.0) -> str:
    """A box drawn the way a marker draws one: four separate tapered sides that
    overshoot the corners, instead of a closed polyline with the corners met."""
    sides = (((x, y), (x + w, y)), ((x + w, y), (x + w, y + h)),
             ((x + w, y + h), (x, y + h)), ((x, y + h), (x, y)))
    out = []
    for i, (a, b) in enumerate(sides):
        d = brush([a, b], width=width, seed=seed + i * 7, enter=0.03, exit_=0.05,
                  jitter=0.1)
        out.append(brush_fill(d, colour, opacity))
    for cx, cy, dx, dy in ((x, y, 1, 1), (x + w, y, -1, 1),
                           (x + w, y + h, -1, -1), (x, y + h, 1, -1)):
        d = brush([(cx, cy), (cx + dx * overshoot, cy + dy * overshoot * 0.24)],
                  width=width * 0.62, seed=seed + 13, enter=0.02, exit_=0.9, jitter=0.3)
        out.append(brush_fill(d, colour, opacity * 0.85))
    return "".join(out)


def brush_rule(x1: float, x2: float, y: float, width: float = 5.0, seed: int = 97,
               sag: float = 0.0, colour: str = "currentColor",
               opacity: float = 1.0, enter: float = 0.06, exit_: float = 0.08) -> str:
    """One confident horizontal mark, thick in the middle and dying at both ends."""
    d = brush([(x1, y), ((x1 + x2) / 2, y + sag), (x2, y)], width=width, seed=seed,
              enter=enter, exit_=exit_, jitter=0.12)
    return brush_fill(d, colour, opacity)



def drip(x: float, y: float, length: float, seed: int = 71, w: float = 3.4,
         colour: str = "currentColor", opacity: float = 1.0) -> list[str]:
    """One paint run: a tapering stroke that ends in a bead."""
    rnd = rng(seed)
    x0 = x + (rnd() - 0.5) * 2.0
    lean = (rnd() - 0.5) * 0.24
    pts = [(x0, y), (x0 + lean * length * 0.35, y + length * 0.45),
           (x0 + lean * length, y + length)]
    body = polyline(pts, seed=seed, close=False, roughness=0.5)
    bead = (f'<circle cx="{fmt(pts[-1][0])}" cy="{fmt(pts[-1][1] + w * 0.9)}" '
            f'r="{fmt(w * 1.1)}" fill="{colour}"/>')
    return [path(body, colour, w, opacity), bead]


def tag_underline(x1: float, x2: float, y: float, seed: int = 79,
                  colour: str = "currentColor", weight: float = 3.2) -> list[str]:
    """Two crossing strokes under a tag: the swash, then the strike."""
    mid = (x1 + x2) / 2
    sag = (x2 - x1) * 0.035
    return [
        path(smooth([(x1, y), (mid, y + sag), (x2, y - sag * 0.6)], seed=seed),
             colour, weight),
        path(overshoot(x1 + (x2 - x1) * 0.18, y + 7, x2 - (x2 - x1) * 0.06, y - 6,
                       frac=0.05, seed=seed + 3, bend=0.06), colour, weight * 0.7),
    ]


def echo(d: str, colour: str, width: float, dx: float = 2.4, dy: float = -2.0,
         factor: float = 0.35) -> str:
    """The same shape again, offset the other way — a misregistered print."""
    return (f'<path d="{d}" transform="translate({fmt(dx)} {fmt(dy)})" fill="none" '
            f'stroke="{colour}" stroke-width="{fmt(width * 0.8)}" stroke-linecap="round" '
            f'stroke-linejoin="round" opacity="{factor}"/>')


def esc(value) -> str:
    return (str(value).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))
