#!/usr/bin/env python3
"""repo-kit · INK LAB — the hand-drawn banner family.

Eight compositions, one per repository class, drawn entirely with the stroke
engine in ink.py (a Python port of the owner's own Art Lab handgen.ts) and
coloured from his four Art Lab palettes.

Layout law, inherited from the previous system because it measured out:
  * only the repository name may exceed 40 viewBox px;
  * the signature element is geometry, never text, so it survives the 0.26
    mobile scale where 13 px labels have already turned to noise;
  * nothing load-bearing below 15 px — the install line and counts live in the
    README text block, which reflows natively.
"""
from __future__ import annotations

import math

import ink
from ink import MONO, SERIF

W, H = 1200, 320
TAU = math.pi * 2

STYLES = {}
DARK_ONLY = {"vt100", "scope"}


class Sheet:
    """One banner: the paper, the frame, the caption, and a place to draw."""

    def __init__(self, ctx: dict, style: str, light: bool):
        self.ctx = ctx
        self.style = style
        self.light = light
        self.family = str(ctx.get("family") or "")
        if self.family not in ink.PALETTES:
            # No family named in the spec: derive one from the repository name so
            # every project gets its own tint without 25 hand edits, and the same
            # repository always comes back the same colour.
            names = tuple(ink.PALETTES)
            roles = ("gold", "aurora", "rose", "violet", "lapis")
            self.family = names[ink.seed_of(ctx["name"]) % len(names)]
            self.derived_role = roles[ink.seed_of(ctx["name"]) % len(roles)]
        else:
            self.derived_role = str(ctx.get("accent_role") or "gold")
        # the Art Lab palettes are ink-on-slate; on paper the whole role table
        # flips to pigment, otherwise the name and the frame render at 1.01:1
        self.palette = ink.palette_for(self.family, light)
        self.ground = ink.GROUND["light" if light else "dark"]
        self.ink = self.palette["ink"]
        self.muted = self.palette["muted"]
        self.accent = self.palette.get(self.derived_role) or self.palette["gold"]
        self.seed = ink.seed_of(ctx["name"])
        self.parts: list[str] = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
            f'viewBox="0 0 {W} {H}" role="img" '
            f'aria-label="{ink.esc(ctx["name"])} — {ink.esc(ctx["tagline"])}" '
            f'font-family="{SERIF}">',
            f'<rect width="{W}" height="{H}" fill="{self.ground}"/>',
        ]

    # -- helpers ---------------------------------------------------------
    def add(self, markup: str) -> None:
        self.parts.append(markup)

    def stroke(self, d: str, colour: str | None = None, width: float = 2.0,
               ghost: bool = False) -> None:
        colour = colour or self.ink
        if ghost:
            self.add(ink.ghost(d, colour, width))
        self.add(ink.path(d, colour, width))

    def label(self, x, y, body, size=12, colour=None, anchor="start", tracking=2.0,
              family=MONO, weight="400", opacity=0.9) -> None:
        self.add(ink.text(x, y, body, size, colour or self.muted, family=family,
                          weight=weight, anchor=anchor, tracking=tracking, opacity=opacity))

    def serif(self, x, y, body, size=46, colour=None, anchor="start", italic=False,
              weight="400", opacity=1.0) -> None:
        self.add(ink.text(x, y, body, size, colour or self.ink, family=SERIF,
                          weight=weight, anchor=anchor, italic=italic, opacity=opacity))

    def caption(self) -> None:
        ctx = self.ctx
        code = {"post": "01", "vt100": "02", "seq": "03", "tree": "04",
                "iso": "05", "scope": "06", "card": "07", "pipe": "08"}.get(self.style, "00")
        family = self.family
        self.label(34, 44, f"INK LAB / {code} · {self.style} · {family}", 12)
        self.add(ink.path(ink.hand_line(34, 56, W - 34, 56, seed=self.seed + 1, bend=0.006),
                          self.muted, 1.2))

    def plate(self) -> str:
        """Hand-drawn frame with a slightly overshooting second pass."""
        x, y, w, h = 12, 12, W - 24, H - 24
        self.add(ink.path(ink.rect_path(x, y, w, h, seed=self.seed + 2, wobble=0.03),
                          self.ink, 1.6))
        self.add(ink.ghost(ink.rect_path(x + 2, y - 1, w, h, seed=self.seed + 2, wobble=0.05),
                           self.ink, 1.6, 0.22))
        return "".join(self.parts) + "</svg>"

    def title_block(self, x=34, y=150, name_size=48, limit=520) -> None:
        ctx = self.ctx
        name = str(ctx["name"])
        # GitHub allows 100-character repository names; shrink rather than let the
        # title walk off the plate, and keep the underline under the drawn text
        if len(name) * name_size * 0.5 > limit:
            name_size = max(20, int(limit / (len(name) * 0.5)))
        self.serif(x, y, name, name_size)
        width = ink.text_width(name, name_size)
        self.add(ink.path(ink.hand_line(x, y + 12, x + width, y + 12, seed=self.seed + 3,
                                        bend=0.05), self.accent, 2.4))
        words = (ctx["tagline"] or "").split(" ")
        line, lines = "", []
        budget = 46
        for word in words:
            probe = (line + " " + word).strip()
            if len(probe) > budget and line:
                lines.append(line)
                line = word
            else:
                line = probe
        lines.append(line)
        for i, text in enumerate(lines[:2]):
            self.serif(x, y + 40 + i * 26, text, 17, colour=self.ink, italic=True,
                       opacity=0.92)



    def install_line(self, x=34, y=250) -> None:
        ctx = self.ctx
        if not ctx.get("install"):
            return
        self.label(x, y, "$", 15, colour=self.accent, tracking=0)
        body = str(ctx["install"])
        if len(body) > 62:
            # keep both ends: the head says what to type, the tail says what runs
            body = f"{body[:36]} … {body[-24:]}"
        self.label(x + 18, y, body, 14, colour=self.ink, tracking=0)

    def count_block(self, x=None, y=250) -> None:
        ctx = self.ctx
        x = W - 34 if x is None else x
        if ctx.get("stars"):
            self.serif(x, y, f"★{ctx['stars']:,}", 30, colour=self.accent, anchor="end")
        meta = " · ".join(v for v in (ctx.get("lang"), ctx.get("license")) if v and v != "-")
        if meta:
            self.label(x, y + 22, meta.upper(), 11, anchor="end")
        if ctx.get("pushed"):
            self.label(x, y + 40, ctx["pushed"][:10], 11, anchor="end", opacity=0.6)


# --------------------------------------------------------------------- motifs


def post(ctx: dict, light: bool) -> str:
    sheet = Sheet(ctx, "post", light)
    """BIOS self-test, redrawn by hand: a checklist of parts with ticked margins."""
    sheet.caption()
    rows = ctx.get("post_rows") or []
    y = 96
    for label, status, ok in rows[:6]:
        sheet.add(ink.text(60, y, str(label)[:26], 15, sheet.ink, family=MONO, tracking=0))
        sheet.add(ink.text(430, y, str(status), 15,
                           sheet.palette["aurora"] if ok else sheet.palette["rose"],
                           family=MONO, weight="700", tracking=0))
        # the tick is a hand-drawn cross, not a glyph
        sheet.stroke(ink.hand_line(452, y - 5, 458, y + 1, seed=sheet.seed + y, bend=0.1),
                     sheet.palette["aurora"], 2.0)
        sheet.stroke(ink.hand_line(458, y + 1, 470, y - 11, seed=sheet.seed + y + 1, bend=0.1),
                     sheet.palette["aurora"], 2.0)
        y += 26
    sheet.title_block(x=520, y=140, name_size=44)
    sheet.count_block(x=1166, y=110)
    return sheet.plate()


def vt100(ctx: dict, light: bool) -> str:
    sheet = Sheet(ctx, "vt100", light)
    """A terminal window, but drawn: the frame wavers, the prompt still types."""
    sheet.caption()
    x, y, w, h = 34, 76, 520, 210
    sheet.stroke(ink.rect_path(x, y, w, h, seed=sheet.seed + 4, wobble=0.04),
                 sheet.ink, 2.0, ghost=True)
    sheet.add(ink.path(ink.hand_line(x, y + 30, x + w, y + 30, seed=sheet.seed + 5),
                       sheet.muted, 1.4))
    sheet.label(x + 16, y + 20, f"~/src/{ctx['name']}", 12)
    lines = list(ctx.get("term_lines") or [])
    for i, line in enumerate(lines[:4]):
        body, colour, _ = line
        # the tagline is already set in large italic type on the right; inside the
        # window it would simply be the same sentence twice
        if i == 1:
            body = f"# {ctx['lang']} · {ctx['license']} · {len(ctx.get('topics') or [])} topics"
        sheet.label(x + 16, y + 58 + i * 26, str(body)[:44], 13,
                    colour={"#79C0FF": sheet.palette["aurora"],
                            "#CEB27C": sheet.palette["gold"],
                            "#D6A0AC": sheet.palette["rose"],
                            "#A5AFBF": sheet.muted}.get(colour, sheet.ink), tracking=0)
    cursor_x = x + 16
    sheet.add(f'<rect x="{cursor_x}" y="{y + 210}" width="11" height="0" fill="none"/>')
    sheet.add(ink.path(ink.hand_line(cursor_x, y + 196, cursor_x + 11, y + 196,
                                     seed=sheet.seed + 6), sheet.palette["aurora"], 2.4))
    sheet.title_block(x=600, y=150, name_size=44)
    sheet.install_line(x=600, y=252)
    return sheet.plate()


def seq(ctx: dict, light: bool) -> str:
    sheet = Sheet(ctx, "seq", light)
    """A protocol exchange, hand-inked: two lifelines, arrows that bend."""
    sheet.caption()
    left, right = 600, 1120
    sheet.add(ink.path(ink.hand_line(left, 96, left, 268, seed=sheet.seed + 7, bend=0.02),
                       sheet.muted, 1.6))
    sheet.add(ink.path(ink.hand_line(right, 96, right, 268, seed=sheet.seed + 8, bend=0.02),
                       sheet.muted, 1.6))
    sheet.label(left, 90, "CLIENT", 11, anchor="middle")
    sheet.label(right, 90, str(ctx.get("role") or "SERVER")[:12], 11, anchor="middle")
    messages = (ctx.get("messages") or [])[:4]
    for i, entry in enumerate(messages):
        label, kind = entry[0], entry[1]
        y = 122 + i * 42
        if kind == "request":
            sheet.add(ink.path(ink.arrow(left, y, right, y, seed=sheet.seed + i * 5),
                               sheet.palette["aurora"], 2.2))
            sheet.label((left + right) / 2, y - 8, str(label)[:30], 12, anchor="middle",
                        colour=sheet.ink)
        else:
            sheet.add(ink.path(ink.arrow(right, y, left, y, seed=sheet.seed + i * 5 + 1),
                               sheet.muted, 1.6))
            sheet.label((left + right) / 2, y + 18, str(label)[:30], 11, anchor="middle",
                        opacity=0.75)
    sheet.title_block(x=34, y=150, name_size=44)
    sheet.install_line(x=34, y=268)
    return sheet.plate()


def tree(ctx: dict, light: bool) -> str:
    sheet = Sheet(ctx, "tree", light)
    """A module tree drawn as a root with branches — the elbow is a real stroke."""
    sheet.caption()
    sheet.title_block(x=34, y=112, name_size=42)
    root_y = 206
    sheet.add(ink.path(ink.circle(52, root_y - 6, 9, seed=sheet.seed + 9), sheet.accent, 2.4))
    sheet.add(ink.path(ink.hand_line(66, root_y - 6, 200, root_y - 6,
                                     seed=sheet.seed + 10), sheet.ink, 2.0))
    for i, kid in enumerate((ctx.get("children") or [])[:4]):
        y = root_y + 26 + i * 24
        sheet.add(ink.path(ink.hand_line(66, root_y - 6, 66, y - 6, seed=sheet.seed + 11 + i),
                           sheet.muted, 1.2))
        sheet.add(ink.path(ink.hand_line(66, y - 6, 92, y - 6, seed=sheet.seed + 21 + i),
                           sheet.muted, 1.2))
        sheet.label(100, y, str(kid)[:28], 13, colour=sheet.ink, tracking=0)
    sheet.count_block(x=1166, y=150)
    sheet.install_line(x=700, y=286)
    return sheet.plate()


def iso(ctx: dict, light: bool) -> str:
    sheet = Sheet(ctx, "iso", light)
    """An isometric stack, hand-built: hatched blocks standing on a scribbled ground."""
    sheet.caption()
    sheet.title_block(x=34, y=140, name_size=44)
    base = 268
    for i in range(7):
        x = 640 + i * 74
        h = 40 + (i * 37) % 90
        top = [(x - 26, base - h), (x, base - h - 14), (x + 26, base - h), (x, base - h + 14)]
        side = [(x + 26, base - h), (x, base - h + 14), (x, base + 14), (x + 26, base)]
        sheet.add(ink.path(ink.polyline(top, seed=sheet.seed + i * 3, close=True),
                           sheet.accent if i == 3 else sheet.ink, 1.8))
        sheet.add(ink.path(ink.polyline(side, seed=sheet.seed + 40 + i * 3, close=True),
                           sheet.muted, 1.4))
        if i % 2 == 0:
            for line in ink.hachure(side, angle_deg=-41, gap=9, seed=sheet.seed + 60 + i):
                sheet.add(ink.path(line, sheet.muted, 1.0))
    sheet.add(ink.path(ink.hand_line(600, base + 20, 1166, base + 20,
                                     seed=sheet.seed + 70, bend=0.01), sheet.muted, 1.2))
    sheet.count_block(x=1166, y=110)
    return sheet.plate()


def scope(ctx: dict, light: bool) -> str:
    sheet = Sheet(ctx, "scope", light)
    """A scope trace, hand-plotted: sample points, no grid, one wandering curve."""
    sheet.caption()
    trace = ctx.get("trace") or []
    points = []
    if len(trace) >= 2:
        lo, hi = min(trace), max(trace)
        span = max(1, hi - lo)
        for i, value in enumerate(trace):
            x = 560 + i * (600 / max(1, len(trace) - 1))
            y = 250 - (value - lo) / span * 150
            points.append((x, y))
        sheet.add(ink.path(ink.smooth(points, seed=sheet.seed + 8),
                           sheet.palette["aurora"], 2.4))
        for p in points[::4]:
            sheet.add(ink.path(ink.circle(p[0], p[1], 3, seed=int(p[0])), sheet.accent, 1.6))
    else:
        sheet.add(ink.path(ink.hand_line(560, 200, 1160, 200, seed=sheet.seed + 8),
                           sheet.muted, 1.6))
        sheet.label(860, 188, "NO SIGNAL", 11, anchor="middle")
    sheet.add(ink.path(ink.hand_line(544, 96, 544, 268, seed=sheet.seed + 9), sheet.muted, 1.0))
    sheet.add(ink.path(ink.hand_line(544, 200, 1160, 200, seed=sheet.seed + 10), sheet.muted, 1.0))
    sheet.title_block(x=34, y=150, name_size=44)
    sheet.install_line(x=34, y=250)
    return sheet.plate()


def card(ctx: dict, light: bool) -> str:
    sheet = Sheet(ctx, "card", light)
    """An index card drawn on the sheet: a rule, a margin, a hand-ruled stamp."""
    sheet.caption()
    sheet.title_block(x=34, y=120, name_size=42)
    sheet.add(ink.path(ink.hand_line(34, 168, 470, 170, seed=sheet.seed + 11, bend=0.02),
                       sheet.palette["rose"], 2.0))
    rows = [("LANG", ctx.get("lang")), ("LICENSE", ctx.get("license")),
            ("RELEASES", str(ctx.get("releases") or 0)), ("PUSHED", ctx["pushed"][:10])]
    y = 212
    for key, value in rows:
        sheet.label(34, y, key, 11)
        sheet.label(200, y, str(value)[:24], 13, colour=sheet.ink, tracking=0)
        y += 24
    stamp_x, stamp_y = 900, 150
    sheet.add(ink.ghost(ink.circle(stamp_x, stamp_y, 62, seed=sheet.seed + 12), sheet.accent, 2.0))
    sheet.add(ink.path(ink.circle(stamp_x, stamp_y, 56, seed=sheet.seed + 13), sheet.accent, 1.2))
    for arm in ink.spark(stamp_x, stamp_y, 26, seed=sheet.seed + 14, colour=sheet.accent):
        sheet.add(arm if arm.startswith("<circle") else ink.path(arm, sheet.accent, 2.0))
    sheet.label(stamp_x, stamp_y + 84, "dwgx archive", 11, anchor="middle")
    sheet.count_block(x=1166, y=252)
    return sheet.plate()


def pipe(ctx: dict, light: bool) -> str:
    sheet = Sheet(ctx, "pipe", light)
    """A conveyor drawn by hand: five stations, each a sketched box and a ticked bar."""
    sheet.caption()
    sheet.title_block(x=34, y=124, name_size=44)
    stages = (ctx.get("stages") or [])[:5]
    progress = (ctx.get("stage_progress") or [])[:5]
    x = 34
    for i, stage in enumerate(stages):
        w = 196
        sheet.stroke(ink.rect_path(x, 202, w, 62, seed=sheet.seed + 20 + i, wobble=0.05),
                     sheet.ink, 1.8)
        sheet.label(x + 14, 226, str(stage)[:18], 12, colour=sheet.ink, tracking=0)
        done = 9 if i == len(stages) - 1 else (int(progress[i]) if i < len(progress) else 3)
        for k in range(9):
            bx = x + 14 + k * 20
            sheet.add(ink.path(ink.hand_line(bx, 250, bx + 13, 250,
                                             seed=sheet.seed + 30 + i * 9 + k, bend=0.12),
                               sheet.accent if k < done else sheet.muted,
                               2.4 if k < done else 0.9))
        if i < len(stages) - 1:
            sheet.add(ink.path(ink.arrow(x + w + 4, 233, x + w + 26, 233,
                                         seed=sheet.seed + 60 + i, head=8), sheet.muted, 1.4))
        x += w + 30
    sheet.install_line(x=34, y=292)
    if ctx.get("releases"):
        note = f"{ctx['releases']} releases"
        sheet.label(1126, 118, note, 12, anchor="end", tracking=0)
        sheet.add(ink.path(ink.hand_line(1020, 112, 1126, 112, seed=sheet.seed + 77,
                                         bend=0.05), sheet.accent, 1.8))
    return sheet.plate()


STYLES.update({"post": post, "vt100": vt100, "seq": seq, "tree": tree, "iso": iso,
               "scope": scope, "card": card, "pipe": pipe})


def render(style: str, ctx: dict, light: bool) -> str:
    return STYLES[style](ctx, light)


def _wrap_sheet(style: str):
    """The renderers take (Sheet, light); the public entry takes (ctx, light)."""
    inner = STYLES[style]
    return lambda ctx, light: inner(Sheet(ctx, style, light), light)


def units(text: str) -> int:
    return sum(2 if ord(ch) > 0x2E7F else 1 for ch in str(text))


def clip(text: str, limit: int) -> str:
    text = str(text)
    if units(text) <= limit:
        return text
    out, used = "", 0
    for ch in text:
        w = 2 if ord(ch) > 0x2E7F else 1
        if used + w > limit - 1:
            return out + "…"
        out += ch
        used += w
    return out


def wrap(text: str, limit: int, lines: int = 2) -> list[str]:
    rows, cur = [], ""
    for word in str(text).split(" "):
        probe = (cur + " " + word).strip()
        if len(probe) > limit and cur:
            rows.append(cur)
            cur = word
            if len(rows) == lines:
                break
        else:
            cur = probe
    if cur and len(rows) < lines:
        rows.append(cur)
    return rows or [""]


_ = TAU
