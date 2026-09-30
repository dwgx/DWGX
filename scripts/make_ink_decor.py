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
import sys
import tomllib

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "repo-kit"))

import ink  # noqa: E402  (path set above, on purpose)

ASSETS = ROOT / "assets"
GROUND = "#06020f"          # the BIOS ground the existing ornaments already use
FAMILY = "crayon"           # provenance: the profile is Kobe-era crayon paper
P = ink.PALETTES[FAMILY]
INK, GOLD, AURORA = P["ink"], P["gold"], P["aurora"]
VIOLET, LAPIS, ROSE, MUTED = P["violet"], P["lapis"], P["rose"], P["muted"]

TITLE = "dwgx.menu"
DESC = "Decorative dwgx.menu panel; not live telemetry."


def doc(w: int, h: int, title: str, body: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc">'
        f'<title id="title">{ink.esc(title)}</title>'
        f'<desc id="desc">{DESC}</desc>'
        f'<rect width="{w}" height="{h}" fill="{GROUND}"/>'
        f'{body}</svg>'
    )


def chrome(x: float, y: float, left: str, right: str = "", w: int = 960) -> list[str]:
    """The `INK LAB / nn · style · palette` line every banner wears."""
    out = [ink.text(x, y, left, 12, MUTED, ink.MONO, tracking="2")]
    if right:
        out.append(ink.text(w - x, y, right, 12, MUTED, ink.MONO, anchor="end", tracking="1"))
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


# ── hero: the voice fingerprint ───────────────────────────────────────────────
def hero(profile: dict) -> str:
    w, h = 960, 300
    voice = [str(v) for v in (profile.get("voice", {}).get("lines") or [])][:4]
    ident = profile.get("identity", {})
    flag = profile.get("flagship", {})
    alias, note = str(ident.get("alias", "")), str(ident.get("note", ""))
    host = str(flag.get("url", "")).replace("https://", "")
    b: list[str] = []
    b.append(ink.path(ink.rect_path(10, 10, w - 20, h - 20, seed=3, wobble=0.03), INK, 1.6, 0.55))
    b += chrome(38, 44, "dwgx · PROFILE · 09 · crayon", f"{ident.get('from', '')} · {host}")
    b.append(ink.path(ink.hand_line(38, 58, w - 38, 58, seed=5, bend=0.01), INK, 1.2, 0.5))

    # name, set large: this is the one thing allowed to exceed 40 viewBox px
    b.append(ink.text(38, 122, str(profile.get("login", "dwgx")), 62, INK,
                      ink.SERIF, weight="600"))
    b.append(ink.path(ink.hand_line(38, 138, 38 + ink.text_width("dwgx", 62) * 1.02, 134,
                                    seed=9, bend=0.06), AURORA, 2.6))
    if alias:
        b.append(ink.text(38, 164, alias, 15, GOLD, ink.MONO, tracking="1"))
    if note:
        b.append(ink.text(38, 186, note, 14, MUTED, ink.SERIF, italic=True))

    # the fingerprint: his own lines, verbatim, one tick each
    y = 216
    for i, line in enumerate(voice):
        b += tick(40, y - 8, AURORA, 31 + i * 4)
        b.append(ink.text(62, y, line, 16, INK, ink.SERIF, italic=True, opacity=0.95))
        y += 22

    b += root_motif(812, 150, 66, 101)
    b.append(ink.text(812, 274, str(flag.get("zh_tagline", "")), 13, GOLD, ink.SERIF,
                      anchor="middle", italic=True))
    return doc(w, h, f"{TITLE} · voice fingerprint", "".join(b))



# ── boot keys ────────────────────────────────────────────────────────────────
KEYS = [("01", "MAIN"), ("02", "PROCESS"), ("03", "ORIGIN"),
        ("04", "MODULES"), ("05", "PHANTASM"), ("06", "GUESTBOOK")]


def key_cap(num: str, label: str, idx: int) -> str:
    w, h = 156, 54
    b = [ink.path(ink.rect_path(4, 4, w - 8, h - 8, seed=41 + idx * 6, wobble=0.06),
                  INK, 1.7, 0.85)]
    b.append(ink.text(16, 24, num, 12, GOLD, ink.MONO, tracking="1"))
    b.append(ink.text(w - 14, 24, label, 13, INK, ink.MONO, anchor="end", tracking="1.5"))
    b.append(ink.path(ink.hand_line(16, 34, w - 16, 34, seed=47 + idx * 6, bend=0.03),
                      INK, 1.0, 0.4))
    b.append(ink.path(ink.hand_line(16, 42, 16 + (w - 32) * (0.5 + 0.08 * idx), 42,
                                    seed=53 + idx * 6, bend=0.08), AURORA, 1.6, 0.7))
    return doc(w, h, f"{label} section link", "".join(b))


# ── section rails ────────────────────────────────────────────────────────────
RAILS = [
    ("01", "SYSTEM CONFIGURATION", "dwgx.cfg"),
    ("02", "PROCESS MEMORY", "loaded modules"),
    ("04", "EXPANSION SLOTS", "selected work"),
    ("05", "MACHINE INVENTORY", "devices"),
    ("06", "PHANTASM ARCHIVE", "touhou"),
    ("07", "ACTIVITY MEMORY", "graph / stats"),
    ("08", "BBS GUESTBOOK", "leave a trace"),
]


def rail(num: str, label: str, sub: str, idx: int) -> str:
    w, h = 960, 42
    # the rules must clear the actual text, so measure it instead of guessing
    # mono runs are wider than the serif metric, and letter-spacing adds per glyph
    label_w = ink.text_width(label, 13) + 2 * len(label)
    sub_w = ink.text_width(sub, 11) + 1 * len(sub)
    num_x = w / 2 - label_w * 0.5 - 26
    left_end = num_x - 20
    right_end = w - 16 - sub_w - 16
    right_start = num_x + 26 + label_w + 20
    b = [ink.path(ink.hand_line(16, 20, left_end, 20, seed=61 + idx * 5, bend=0.012),
                  INK, 1.4, 0.75)]
    b.append(ink.path(ink.hand_line(right_start, 20, right_end, 20, seed=67 + idx * 5,
                                    bend=0.012), INK, 1.4, 0.75))
    b += ink.spark(w / 2, 20, 11, seed=71 + idx * 5, colour=GOLD)
    b.append(ink.text(num_x, 25, num, 12, GOLD, ink.MONO, tracking="1"))
    b.append(ink.text(num_x + 26, 25, label, 13, INK, ink.MONO, tracking="2"))
    b.append(ink.text(w - 16, 25, sub, 11, MUTED, ink.MONO, anchor="end", tracking="1"))
    return doc(w, h, label, "".join(b))
    ("03", "GENESIS CHAMBER", "origin"),


# ── rear I/O panel ───────────────────────────────────────────────────────────
def io_panel() -> str:
    w, h = 960, 70
    b = [ink.path(ink.rect_path(12, 10, w - 24, h - 20, seed=83, wobble=0.03), INK, 1.8, 0.85)]
    x = 30
    ports = [(46, 12), (26, 12), (34, 8), (22, 16), (40, 14), (30, 10)]
    for i, (pw, ph) in enumerate(ports):
        b.append(ink.path(ink.rect_path(x, 44 - ph, pw, ph, seed=89 + i * 4, wobble=0.07),
                          AURORA if i % 2 else INK, 1.5, 0.85))
        x += pw + 12
    b.append(ink.text(30, 24, "REAR I/O", 11, MUTED, ink.MONO, tracking="3"))
    b.append(ink.text(w - 30, 24, "dwgx@main", 11, GOLD, ink.MONO, anchor="end", tracking="1"))
    return doc(w, h, "Decorative rear I/O panel", "".join(b))


# ── phantasm danmaku ─────────────────────────────────────────────────────────
def phantasm() -> str:
    w, h = 960, 98
    b: list[str] = []
    for i in range(26):
        s = ink.seed_of(f"danmaku-{i}")
        x = 20 + (s % 920)
        y = 18 + (s >> 5) % 68
        b += ink.spark(x, y, 9 + (s >> 11) % 7, seed=s, colour=AURORA if i % 3 else GOLD)
        if i % 2 == 0:      # a short streak gives the bullet direction
            b.append(ink.path(ink.hand_line(x - 14, y + 3, x + 6, y - 2,
                                            seed=s + 3, bend=0.2), GOLD, 1.3, 0.5))
    b.append(ink.path(ink.hand_line(0, 49, w, 47, seed=97, bend=0.01), INK, 1.0, 0.28))
    b.append(ink.text(24, 90, "幻想万華鏡 · THE MEMORIES OF PHANTASM", 11, MUTED,
                      ink.MONO, tracking="3"))
    return doc(w, h, "Touhou danmaku ornament for the Phantasm feature", "".join(b))


# ── end of file ──────────────────────────────────────────────────────────────
def eof() -> str:
    w, h = 960, 136
    b = [ink.path(ink.hand_line(40, 40, w / 2 - 60, 40, seed=101, bend=0.02), INK, 1.4, 0.6)]
    b.append(ink.path(ink.hand_line(w / 2 + 60, 40, w - 40, 40, seed=103, bend=0.02),
                      INK, 1.4, 0.6))
    b.append(ink.path(ink.arrow(w / 2 - 112, 66, w / 2 - 168, 66, seed=107, head=13),
                      AURORA, 2.2))
    b.append(ink.text(w / 2, 74, "〔 返回 boot.menu 〕", 17, INK, ink.SERIF, anchor="middle"))
    b.append(ink.path(ink.hand_line(w / 2 - 120, 90, w / 2 + 120, 92, seed=109, bend=0.03),
                      GOLD, 1.4, 0.55))
    b.append(ink.text(w / 2, 116, "END OF FILE · 主机关机", 11, MUTED, ink.MONO,
                      anchor="middle", tracking="3"))
    return doc(w, h, "End of file, return to the dwgx.menu navigation", "".join(b))


# ── rubber stamps ────────────────────────────────────────────────────────────
STAMPS = [("dwgx", "PERSONAL WEB"), ("bios", "SETUP UTILITY"),
          ("ascii", "SERIAL CONSOLE"), ("touhou", "DANMAKU ARCHIVE")]


def stamp(word: str, sub: str, idx: int) -> str:
    w, h = 176, 62
    b = [ink.path(ink.rect_path(5, 5, w - 10, h - 10, seed=113 + idx * 9, wobble=0.09),
                  AURORA, 1.8, 0.8)]
    b.append(ink.path(ink.rect_path(11, 11, w - 22, h - 22, seed=119 + idx * 9, wobble=0.1),
                      AURORA, 1.0, 0.5))
    b.append(ink.text(w / 2, 36, word.upper(), 20, GOLD, ink.SERIF,
                      anchor="middle", weight="600", tracking="1"))
    b.append(ink.text(w / 2, 50, sub, 9, MUTED, ink.MONO, anchor="middle", tracking="1.5"))
    return doc(w, h, f"{word.upper()} decorative web button", "".join(b))


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
    if args.check:
        if drift:
            print("drift: " + ", ".join(drift))
            return 1
        print(f"clean: {len(files)} assets match a fresh render")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
