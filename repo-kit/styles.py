#!/usr/bin/env python3
"""repo-kit · eight banner styles for the dwgx family.

Each style is a renderer taking a context dict and returning an SVG string for
one theme ("dark" or "light"). Motifs, grids and palettes follow
ops/PROFILE-REDESIGN-2026-10-01.md §18 (StyleForge), 1200x320 unless noted.

Design rules enforced here:
  * only the repo name may exceed 40 viewBox px;
  * the signature element is always geometry at least 40px in its small side;
  * nothing load-bearing lives below 15 viewBox px;
  * inline attributes only, no CSS, no external refs (GitHub renders SVG as <img>).
"""
from __future__ import annotations

FONT = "ui-monospace,'Cascadia Mono',Consolas,'SF Mono',monospace"
W, H = 1200, 320


def esc(value: object) -> str:
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def units(text: str) -> int:
    """Display width in monospace columns; CJK counts double."""
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
    words, rows, cur = str(text).split(), [], ""
    for word in words:
        probe = f"{cur} {word}".strip()
        if units(probe) > limit and cur:
            rows.append(cur)
            cur = word
            if len(rows) == lines:
                break
        else:
            cur = probe
    if cur and len(rows) < lines:
        rows.append(cur)
    if rows and units(rows[-1]) > limit:
        rows[-1] = clip(rows[-1], limit)
    return rows or [""]


def open_svg(width: int, height: int, label: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="{esc(label)}" '
        f'font-family="{FONT}">'
    )


def T(  # noqa: N802 - short name used everywhere below
    x: float,
    y: float,
    body: str,
    size: int = 14,
    fill: str = "#EBE4D8",
    weight: str = "400",
    anchor: str = "start",
    tracking: float | None = None,
) -> str:
    tr = f' letter-spacing="{tracking}"' if tracking else ""
    return (
        f'<text x="{x:.0f}" y="{y:.0f}" font-size="{size}" font-weight="{weight}" '
        f'fill="{fill}" text-anchor="{anchor}"{tr}>{esc(body)}</text>'
    )


def dot_leader(x_from: float, x_to: float, y: float, fill: str) -> str:
    """POST's signature: middle-dot leader from a label to a fixed stop."""
    cols = int((x_to - x_from) // 9)
    return T(x_from, y, "·" * max(1, cols), size=15, fill=fill)


# --------------------------------------------------------------------------- POST


def post(ctx: dict, light: bool) -> str:
    c = (
        dict(surface="#FFFFFF", band="#F2EFE6", rule="#161C27", text="#161C27",
             muted="#6E7781", ok="#1A7F37", warn="#8C3A4A", top_rule=True)
        if light
        else dict(surface="#0F131B", band="#161C27", rule="#2A3240", text="#EBE4D8",
                  muted="#A5AFBF", ok="#7EE787", warn="#D6A0AC", top_rule=False)
    )
    name = ctx["name"]
    parts = [open_svg(W, H, f"{name} — {ctx['tagline']}"),
             f'<rect width="{W}" height="{H}" fill="{c["surface"]}"/>']
    if c["top_rule"]:
        parts.append(f'<rect width="{W}" height="4" fill="#161C27"/>')
    parts += [
        f'<rect width="{W}" height="76" fill="{c["band"]}"/>',
        f'<line x1="0" y1="76" x2="{W}" y2="76" stroke="{c["rule"]}"/>',
        T(32, 54, name, size=48, fill=c["text"], weight="700"),
        T(1168, 54, f"DWGX BIOS v{H}.{ctx.get('stars', 0)} · POST {ctx['pushed'][5:] or '--/--'}",
          size=18, fill=c["text"], anchor="end"),
    ]
    rows = ctx["post_rows"]
    for i, (label, status, ok) in enumerate(rows[:9]):
        y = 112 + i * 20
        parts += [
            T(32, y, clip(label, 26), size=15, fill=c["muted"]),
            dot_leader(32 + units(clip(label, 26)) * 9 + 8, 316, y, c["rule"]),
            T(316, y, status, size=15, fill=c["ok"] if ok else c["warn"], weight="700", anchor="end"),
        ]
    parts += [
        T(32, 296, f"Memory Test : {ctx['memory']:07d}K OK", size=20, fill=c["ok"], weight="700"),
        T(32, 314, "Press DEL to enter SETUP", size=14, fill=c["muted"]),
        "</svg>",
    ]
    return "".join(parts)


# --------------------------------------------------------------------------- VT100


def vt100(ctx: dict, light: bool) -> str:
    stroke = "#CEB27C" if light else "#2A3240"
    scan = 0.06 if light else 0.035
    frame = "#1E2532"
    parts = [open_svg(W, H, f"{ctx['name']} — terminal"),
             f'<rect width="{W}" height="{H}" fill="#0F131B"/>',
             f'<rect x="24" y="24" width="1152" height="272" rx="6" fill="#161C27" '
             f'stroke="{stroke}" stroke-width="{2 if light else 1}"/>',
             f'<path d="M24 30a6 6 0 0 1 6-6h1140a6 6 0 0 1 6 6v50h-1152z" fill="{frame}"/>',
             f'<line x1="24" y1="80" x2="1176" y2="80" stroke="{stroke}"/>']
    for cx in (44, 64, 84):
        parts.append(f'<circle cx="{cx}" cy="52" r="4" fill="#A5AFBF"/>')
    parts += [
        T(108, 58, f"dwgx — ~/src/{ctx['name']}", size=15, fill="#EBE4D8"),
        T(1156, 58, "100x28 · 0x0B", size=13, fill="#A5AFBF", anchor="end"),
    ]
    for i in range(10):
        parts.append(f'<rect x="24" y="{88 + i * 20}" width="1152" height="1" fill="#FFFFFF" fill-opacity="{scan}"/>')
    lines = ctx["term_lines"]
    for i, (body, colour, weight) in enumerate(lines):
        parts.append(T(44, 108 + i * 20, body, size=15, fill=colour, weight=weight))
    parts += [
        f'<rect x="44" y="{108 + len(lines) * 20 - 15}" width="10" height="20" fill="#79C0FF"/>',
        "</svg>",
    ]
    return "".join(parts)


# ---------------------------------------------------------------------------- SEQ


def seq(ctx: dict, light: bool) -> str:
    c = (
        dict(surface="#FFFFFF", rule="#D0D7DE", gold="#8A6D2F", muted="#6E7781",
             text="#1F2328", cyan="#0969DA")
        if light
        else dict(surface="#0F131B", rule="#2A3240", gold="#CEB27C", muted="#A5AFBF",
                  text="#EBE4D8", cyan="#79C0FF")
    )
    name = ctx["name"]
    parts = [open_svg(W, H, f"{name} — {ctx['tagline']}"),
             f'<rect width="{W}" height="{H}" fill="{c["surface"]}"/>',
             T(32, 40, f"dwgx//{name}", size=14, fill=c["muted"]),
             T(32, 92, name, size=44, fill=c["text"], weight="700"),
             T(32, 122, clip(ctx["tagline"], 46), size=16, fill=c["text"]),
             f'<line x1="32" y1="142" x2="1168" y2="142" stroke="{c["rule"]}"/>',
             T(32, 190, "$", size=14, fill=c["cyan"]),
             *[T(52, 190 + i * 20, ln, size=13, fill=c["muted"]) for i, ln in enumerate(wrap(ctx["install"], 44, 2))],
             T(900, 190, f"★{ctx['stars']:,}", size=20, fill=c["gold"], anchor="end", weight="700"),
             T(900, 214, f"{ctx['commits']:,} commits", size=13, fill=c["muted"], anchor="end"),
             T(470, 28, "CLIENT", size=13, fill=c["muted"], weight="700", anchor="middle"),
             T(1118, 28, ctx["role"], size=13, fill=c["muted"], weight="700", anchor="middle"),
             f'<line x1="470" y1="40" x2="470" y2="288" stroke="{c["gold"]}" stroke-width="2"/>',
             f'<line x1="1118" y1="40" x2="1118" y2="288" stroke="{c["gold"]}" stroke-width="2"/>']
    for i, (label, kind) in enumerate(ctx["messages"][:5]):
        y = 72 + i * 48
        rightward = i % 2 == 0
        x0, x1 = (470, 1100) if rightward else (1118, 488)
        colour = c["cyan"] if i == 0 else c["gold"]
        head = f"M{x1} {y}l-11 -6v12z"
        arrow = (
            f'<polygon points="{head}" fill="{colour}"/>'
            if kind == "request"
            else f'<polyline points="{x1 - 11} {y - 6} {x1} {y} {x1 - 11} {y + 6}" '
            f'fill="none" stroke="{colour}" stroke-width="2"/>'
        )
        parts += [
            f'<line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" stroke="{colour}" stroke-width="2"'
            + (' stroke-dasharray="6 5"' if kind == "reply" else "") + "/>",
            arrow,
            T((x0 + x1) / 2, y - 8, label, size=14, fill=c["text"] if kind == "request" else c["muted"],
              anchor="middle"),
        ]
    parts.append("</svg>")
    return "".join(parts)


# --------------------------------------------------------------------------- TREE


def tree(ctx: dict, light: bool) -> str:
    c = (
        dict(surface="#FFFFFF", panel="#F6F8FA", rule="#D0D7DE", text="#1F2328",
             muted="#57606A", accent="#8C3A4A")
        if light
        else dict(surface="#0F131B", panel="#161C27", rule="#2A3240", text="#EBE4D8",
                  muted="#A5AFBF", accent="#D6A0AC")
    )
    name = ctx["name"]
    parts = [open_svg(W, H, f"{name} — module tree"),
             f'<rect width="{W}" height="{H}" fill="{c["surface"]}"/>',
             T(32, 48, name, size=44, fill=c["text"], weight="700"),
             T(32, 72, f"dwgx//{name}", size=13, fill=c["muted"]),
             f'<line x1="32" y1="88" x2="1168" y2="88" stroke="{c["rule"]}"/>',
             f'<rect x="32" y="100" width="20" height="20" fill="{c["accent"]}"/>',
             T(64, 116, clip(name, 30), size=17, fill=c["text"], weight="700")]
    kids = ctx["children"][:6]
    spine = "M42 120v14"
    for i, kid in enumerate(kids):
        y = 148 + i * 28
        parts.append(T(84, y, clip(kid, 34), size=15, fill=c["text"]))
        spine += f"M42 {120 + i * 28}v14h42"
    parts.append(f'<path d="{spine}" fill="none" stroke="{c["rule"]}" stroke-width="1"/>')
    for i, (label, value) in enumerate(ctx["stats"][:4]):
        y = 128 + i * 40
        parts += [
            T(900, y, label, size=13, fill=c["muted"], anchor="end"),
            T(924, y, value, size=20, fill=c["accent"], weight="700"),
        ]
    parts += [T(740, 284, ctx["tagline"], size=15, fill=c["muted"]),
              T(740, 308, clip(ctx["install"], 52), size=13, fill=c["text"]), "</svg>"]
    return "".join(parts)


# ---------------------------------------------------------------------------- ISO


def iso(ctx: dict, light: bool) -> str:
    c = (
        dict(surface="#FFFFFF", tile="#D0D7DE", tile_op="0.35", top="#B6C0CC", left="#98A3B0",
             right="#7C8794", text="#1F2328", muted="#57606A", accent="#0969DA")
        if light
        else dict(surface="#0F131B", tile="#2A3240", tile_op="0.10", top="#2A3240", left="#1F2430",
                  right="#151A23", text="#EBE4D8", muted="#A5AFBF", accent="#79C0FF")
    )
    name = ctx["name"]
    parts = [open_svg(W, H, f"{name} — isometric skyline"),
             f'<rect width="{W}" height="{H}" fill="{c["surface"]}"/>',
             T(32, 92, name, size=46, fill=c["text"], weight="700")]
    for i, line in enumerate(wrap(ctx["tagline"], 40, 2)):
        parts.append(T(32, 124 + i * 24, line, size=16, fill=c["text"]))
    parts.append(T(32, 180, clip(ctx["install"], 48), size=14, fill=c["accent"]))
    ground_x, ground_y = 880, 262
    for col in range(-3, 4):
        for row in range(-2, 3):
            x = ground_x + col * 58 + row * 29
            y = ground_y + (col + row) * 15
            parts.append(
                f'<polygon points="{x},{y} {x+29},{y+15} {x},{y+30} {x-29},{y+15}" '
                f'fill="none" stroke="{c["tile"]}" fill-opacity="{c["tile_op"]}"/>'
            )
    for x, height, hero in ctx["blocks"]:
        base = ground_y + ((x - ground_x) // 58) * 15
        top = base - height
        half = 24
        shade = c["accent"] if hero else None
        parts += [
            f'<polygon points="{x-half},{base} {x},{base+15} {x},{top+15} {x-half},{top}" fill="{shade or c["left"]}"/>',
            f'<polygon points="{x+half},{base} {x},{base+15} {x},{top+15} {x+half},{top}" fill="{shade or c["right"]}"/>',
            f'<polygon points="{x-half},{top} {x},{top+15} {x+half},{top} {x},{top-15}" fill="{shade or c["top"]}"/>',
        ]
    parts += [
        T(1168, 44, f"★{ctx['stars']:,}", size=16, fill=c["accent"], weight="700", anchor="end"),
        T(1168, 66, f"{ctx['commits']:,} commits", size=13, fill=c["muted"], anchor="end"),
        T(1168, 90, f"{ctx['pushed'][:10]} · {ctx['lang']} · {ctx['license']}", size=13,
          fill=c["muted"], anchor="end"),
        f'<line x1="32" y1="300" x2="560" y2="300" stroke="{c["tile"]}"/>',
        T(32, 318, "  ".join("#" + t for t in ctx["topics"][:5]), size=12, fill=c["muted"]),
        "</svg>",
    ]
    return "".join(parts)


# --------------------------------------------------------------------------- SCOPE


def scope(ctx: dict, light: bool) -> str:
    grid, cross = "#2A3240", "#3A4450"
    parts = [open_svg(W, H, f"{ctx['name']} — activity trace"),
             f'<rect width="{W}" height="{H}" fill="#0F131B"/>',
             f'<rect x="28" y="28" width="1144" height="264" rx="2" fill="#0F131B" stroke="{grid}"/>']
    hpath = "M28 52h1144M28 76h1144M28 100h1144M28 124h1144M28 148h1144M28 196h1144M28 220h1144M28 244h1144M28 268h1144"
    vpath = "M150 28v264M272 28v264M394 28v264M516 28v264M728 28v264M850 28v264M972 28v264M1094 28v264"
    parts += [
        f'<path d="{hpath}" stroke="{grid}" stroke-opacity="0.35" fill="none"/>',
        f'<path d="{vpath}" stroke="{grid}" stroke-opacity="0.35" fill="none"/>',
        f'<path d="M28 160h1144M600 28v264" stroke="{cross}" stroke-width="2" fill="none"/>',
        f'<path d="M596 76h8M596 108h8M596 140h8M596 180h8M596 212h8M596 244h8" '
        f'stroke="{cross}" stroke-width="2" fill="none"/>',
        '<polygon points="28,154 40,160 28,166" fill="#79C0FF"/>',
        f'<line x1="28" y1="160" x2="600" y2="160" stroke="#79C0FF" stroke-opacity="0.35"/>',
    ]
    trace = ctx["trace"]
    if len(trace) < 2:
        parts.append(f'<line x1="56" y1="160" x2="1144" y2="160" stroke="#7EE787" stroke-width="2"/>')
    else:
        step = (1144 - 56) / (len(trace) - 1)
        lo, hi = min(trace), max(trace)
        span = max(1, hi - lo)
        coords = [(56 + i * step, 272 - (v - lo) / span * 224) for i, v in enumerate(trace)]
        poly = " ".join(f"{x:.0f},{y:.0f}" for x, y in coords)
        parts += [
            f'<polygon points="56,272 {poly} 1144,272" fill="#7EE787" fill-opacity="0.12"/>',
            f'<polyline points="{poly}" fill="none" stroke="#7EE787" stroke-width="2" '
            f'stroke-linejoin="round"/>',
        ]
    trig = "TRIG AUTO" if len(trace) >= 2 else "TRIG AUTO · NO SIGNAL"
    parts += [
        T(44, 52, "CH1 1.00 V/DIV", size=12, fill="#A5AFBF", tracking=1),
        T(1156, 52, "1.00 ms/DIV", size=12, fill="#A5AFBF", anchor="end", tracking=1),
        T(44, 280, trig, size=12, fill="#A5AFBF", tracking=1),
        T(48, 112, ctx["name"], size=44, fill="#EBE4D8", weight="700"),
        T(48, 136, wrap(ctx["tagline"], 30, 1)[0], size=15, fill="#EBE4D8"),
        T(1156, 136, f"★{ctx['stars']:,}", size=13, fill="#A5AFBF", anchor="end"),
        T(1156, 158, f"{ctx['commits']:,} commits · {ctx['pushed'][:10]}", size=13,
          fill="#A5AFBF", anchor="end"),
        f'<line x1="32" y1="300" x2="1168" y2="300" stroke="{grid}"/>',
        T(32, 316, clip(ctx["install"], 60), size=13, fill="#79C0FF"),
        "</svg>",
    ]
    return "".join(parts)


# --------------------------------------------------------------------------- CARD


def card(ctx: dict, light: bool) -> str:
    surface = "#FFFFFF" if light else "#EBE4D8"
    ink = "#161C27"
    paper_rule = "#D8D2C4" if light else "#C9C0AE"
    second = "#3A4250"
    muted = "#57606A"
    accent = "#8C3A4A" if light else "#D6A0AC"
    install_c = "#0969DA" if light else "#0F5C86"
    card_lines = wrap(ctx["tagline"], 34, 2)
    if len(card_lines) == 1:
        card_lines.append(ctx["lang"])
    parts = [
        open_svg(W, H, f"{ctx['name']} — index card"),
        f'<rect width="{W}" height="{H}" fill="#0F131B"/>',
        f'<rect x="54" y="38" width="1104" height="256" rx="4" fill="#000000" fill-opacity="0.25"/>',
        f'<rect x="48" y="32" width="1104" height="256" rx="4" fill="{surface}" '
        f'stroke="{ink if light else paper_rule}" stroke-width="{2 if light else 1}"/>',
        f'<circle cx="78" cy="160" r="11" fill="#0F131B" stroke="{paper_rule}"/>',
        f'<line x1="128" y1="32" x2="128" y2="288" stroke="{accent}"/>',
    ]
    rules = "".join(f"M112 {80 + i * 24}h1024" for i in range(10))
    parts.append(f'<path d="{rules}" stroke="{paper_rule}" stroke-opacity="0.55" fill="none"/>')
    parts += [
        T(152, 68, "DWGX / ARCHIVE", size=12, fill=muted, weight="700", tracking=2),
        T(1136, 68, f"NO. {ctx['topics'][0].upper() if ctx['topics'] else 'REF'} · {ctx['pushed'][:10]}",
          size=12, fill=muted, anchor="end"),
        T(152, 126, ctx["name"], size=46, fill=ink, weight="700"),
        T(1136, 126, f"★{ctx['stars']:,}", size=17, fill=ink, weight="700", anchor="end"),
        T(152, 198, card_lines[0], size=17, fill=second),
        T(152, 246, card_lines[1], size=17, fill=second),
        T(152, 270, clip(ctx["install"], 34), size=14, fill=install_c),
        T(1136, 174, f"{ctx['commits']:,} commits · {ctx['lang']}", size=13, fill=muted, anchor="end"),
        T(1136, 222, f"{ctx['license']} · {len(ctx['topics'])} topics", size=13, fill=muted, anchor="end"),
    ]
    if ctx.get("releases"):
        parts += [
            f'<g transform="rotate(-8 1050 120)">'
            f'<rect x="980" y="96" width="140" height="48" rx="3" fill="none" stroke="{accent}" stroke-width="2"/>'
            f'<text x="1050" y="126" text-anchor="middle" font-size="15" font-weight="700" '
            f'letter-spacing="3" fill="{accent}">{esc(ctx["stamp"] or "RELEASED")}</text></g>',
        ]
    parts.append("</svg>")
    return "".join(parts)


# --------------------------------------------------------------------------- PIPE


def pipe(ctx: dict, light: bool) -> str:
    c = (
        dict(surface="#FFFFFF", box="#F6F8FA", rule="#D0D7DE", text="#1F2328",
             muted="#57606A", accent="#8C3A4A", done="#1A7F37")
        if light
        else dict(surface="#0F131B", box="#161C27", rule="#2A3240", text="#EBE4D8",
                  muted="#A5AFBF", accent="#D6A0AC", done="#7EE787")
    )
    name = ctx["name"]
    parts = [open_svg(W, H, f"{name} — {ctx['tagline']}"),
             f'<rect width="{W}" height="{H}" fill="{c["surface"]}"/>',
             T(32, 38, f"dwgx//{name}", size=13, fill=c["muted"]),
             T(32, 86, name, size=44, fill=c["text"], weight="700")]
    for i, line in enumerate(wrap(ctx["tagline"], 52, 2)):
        parts.append(T(32, 114 + i * 24, line, size=16, fill=c["text"]))
    parts += [
        T(1120, 60, f"★{ctx['stars']:,}", size=18, fill=c["accent"], weight="700", anchor="end"),
        T(1120, 84, f"{ctx['commits']:,} commits", size=13, fill=c["muted"], anchor="end"),
        T(1120, 106, ctx["pushed"][:10], size=13, fill=c["muted"], anchor="end"),
    ]
    stages = ctx["stages"][:5]
    for i, stage in enumerate(stages):
        x = 32 + i * 224
        parts += [
            f'<rect x="{x}" y="170" width="196" height="46" rx="3" fill="{c["box"]}" '
            f'stroke="{c["rule"]}"/>',
            T(x + 16, 190, clip(stage, 22), size=14, fill=c["text"]),
        ]
        done = ctx["stage_progress"][i]
        for k in range(9):
            filled = k < done
            colour = c["done"] if (filled and i == len(stages) - 1) else c["accent"]
            parts.append(
                f'<rect x="{x + 16 + k * 17}" y="198" width="14" height="8" rx="1" '
                f'fill="{colour if filled else "none"}" stroke="{c["rule"] if not filled else colour}"/>'
            )
        if i < len(stages) - 1:
            parts.append(
                f'<path d="M{x + 204} 185l8 8-8 8" fill="none" stroke="{c["rule"]}" stroke-width="2"/>'
            )
    parts += [
        f'<line x1="32" y1="240" x2="1168" y2="240" stroke="{c["rule"]}"/>',
        T(32, 266, clip(ctx["install"], 60), size=14, fill=c["accent"]),
        T(1168, 266, f"{ctx['lang']} · {ctx['license']} · {ctx.get('releases', 0)} releases",
          size=13, fill=c["muted"], anchor="end"),
        "</svg>",
    ]
    return "".join(parts)


STYLES = {"post": post, "vt100": vt100, "seq": seq, "tree": tree, "iso": iso,
          "scope": scope, "card": card, "pipe": pipe}
# VT100 and SCOPE are emissive instruments: one dark asset in both themes.
DARK_ONLY = {"vt100", "scope"}