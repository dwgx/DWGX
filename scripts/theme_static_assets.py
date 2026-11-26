#!/usr/bin/env python3
"""Apply the warm-paper palette to the explicitly reviewed static SVG assets.

This is a post-generation pass, not a new asset generator. Geometry, paths,
labels, numbers, links and user-authored drawing data stay intact. Only colors,
color opacity, a paper backdrop for the formerly transparent stack, and the
exact reviewed editorial notes below may change. Running twice is a no-op.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import xml.etree.ElementTree as ET

PAPER = "#F4EFE6"
INK = "#2A2320"
CLAY = "#A8452C"
PALETTE = {PAPER.lower(), INK.lower(), CLAY.lower()}

# Deliberately literal: adding a new SVG requires reviewing it first.
STATIC_ASSETS = (
    "bbs-header.svg",
    "bbs-port-devlog.svg",
    "bbs-port-guest.svg",
    "bbs-port-patch.svg",
    "bbs-port-talk.svg",
    "exp-demo-deck.svg",
    "exp-media-aux.svg",
    "exp-ticket-blog.svg",
    "exp-ticket-genesis.svg",
    "exp-ticket-ledger.svg",
    "guestbook.svg",
    "key-del.svg",
    "key-f10.svg",
    "key-f2.svg",
    "key-f8.svg",
    "key-f9.svg",
    "marquee.svg",
    "sign-log.svg",
    "stack.svg",
    "vga.svg",
    "viewed.svg",
)

DARK_SURFACES = {"#06020f", "#0d081b", "#130f20", "#000055", "#0000aa"}
SOFT_SURFACES = {"#151020", "#181027", "#21192d", "#271e34", "#292035"}
BORDERS = {"#322846", "#403249", "#000", "#000000", "#000055", "#b4a5c8"}
ACCENTS = {"#55ffff", "#f2a6c4", "#c9a84c", "#ffff55"}
LIGHT_TEXT = {"#e6edf3", "#ffffff"}
MUTED_TEXT = {"#b4a5c8", "#aaaaaa"}
DARK_TEXT = {"#000055", "#000000", "#000"}

# These badge colors were read from stack.svg at f1f215c0. They are not a
# blanket rule for every arbitrary SVG color that might be added later.
STACK_BADGE_COLORS = {
    "#b27521", "#e0a759", "#c3356e", "#dd81a6", "#5fa532", "#93d26b",
    "#5a5a5c", "#8d8d8f", "#1c639a", "#4098dc", "#1c609a", "#4094dc",
    "#3e2591", "#6a4bd1", "#6c991d", "#a3db41", "#1d66a2", "#479ade",
    "#249322", "#49d447", "#c35a37", "#dc9a84", "#2c6ab0", "#699ed9",
    "#2d689c", "#5e9bd1", "#1d87a3", "#48bfde", "#b39543", "#d3bf89",
    "#bf6623", "#e39b65", "#357dc4", "#82b0dd", "#7a2cc2", "#ac74e0",
    "#b11f23", "#e15559", "#bc5b3d", "#d89a87", "#3f288e", "#6b4fcd",
    "#29982f", "#56d15c", "#b47d46", "#d3b08d", "#294a8d", "#5079cc",
    "#1c829a", "#40bedc", "#bf7323", "#e3a665", "#c23832", "#dd817d",
    "#2b8294", "#57bace", "#22afc1", "#65d6e4", "#3ab54a", "#7fd68a",
    "#35a4c4", "#82c9dd", "#3eb17f", "#82d3b0", "#353cc4", "#8286dd",
    "#2270c1", "#65a3e4", "#1d90a5", "#49c8df", "#298b2a", "#4fcb50",
    "#2e6d9e", "#61a0d1", "#c1332b", "#e07872", "#1c994c", "#3fdc7b",
    "#c27332", "#dda87d",
}

COMMON_BBS_NOTE = (
    "Public GitHub message board. Buttons open GitHub; no live terminal or online count.",
    "Public GitHub message board. Buttons open GitHub.",
)
READING_NOTE = (
    "A curated public reading destination, not an automatically refreshed RSS item.",
    "A curated public reading destination.",
)
TEXT_REPLACEMENTS = {
    "exp-demo-deck.svg": (
        ("A static link cover for the existing SmartCLI project demonstration, not generated execution evidence.",
         "A static link cover for the existing SmartCLI project demonstration."),
        ("Linked recording / not a live terminal", "Linked recording"),
    ),
    "exp-media-aux.svg": (
        ("Decorative equalizer: not currently playing, no live audio, no listening history.",
         "Equalizer."),
    ),
}
REMOVE_TEXT = {
    "exp-demo-deck.svg": ("CONCEPT LABELS — OPEN EXISTING DEMO",),
    "exp-media-aux.svg": ("DECORATIVE EQ / NOT LIVE AUDIO",),
}
OPEN_TAG = re.compile(r"<(?P<tag>[A-Za-z][A-Za-z0-9:-]*)(?P<attrs>\s[^<>]*?)?(?P<end>/?)>")
ATTR = re.compile(r'([\w:.-]+)=(["\'])(.*?)\2', re.DOTALL)


def set_attr(tag: str, name: str, value: str) -> str:
    pattern = re.compile(r"(?<![\w:.-])" + re.escape(name) + r'=(["\']).*?\1')
    if pattern.search(tag):
        return pattern.sub(lambda _: f'{name}="{value}"', tag, count=1)
    ending = "/>" if tag.endswith("/>") else ">"
    return tag[:-len(ending)] + f' {name}="{value}"' + ending


def recolor_tag(match: re.Match[str], *, is_stack: bool) -> str:
    raw = match.group(0)
    tag = match.group("tag")
    attrs = {name: value for name, _, value in ATTR.findall(raw)}
    changes = {}
    for attribute in ("fill", "stroke", "stop-color"):
        old = attrs.get(attribute, "").lower()
        if not old.startswith("#") or old in PALETTE:
            continue
        if attribute == "stop-color" and old == "#ffffff":
            changes[attribute] = PAPER
        elif attribute == "stroke":
            if old in BORDERS or old in DARK_SURFACES or (is_stack and old in STACK_BADGE_COLORS):
                changes[attribute] = INK
                changes["stroke-opacity"] = "0.18"
            elif old in ACCENTS:
                changes[attribute] = CLAY
                changes["stroke-opacity"] = "0.38"
            elif old in LIGHT_TEXT:
                changes[attribute] = INK
        elif attribute == "fill":
            if tag == "text":
                if old in ACCENTS:
                    changes[attribute] = CLAY
                elif old in MUTED_TEXT:
                    changes[attribute] = INK
                    changes["fill-opacity"] = "0.76"
                elif old in LIGHT_TEXT or old in DARK_TEXT:
                    changes[attribute] = INK
            elif tag == "rect":
                if old in DARK_SURFACES or (is_stack and old in STACK_BADGE_COLORS):
                    changes[attribute] = PAPER
                elif old in SOFT_SURFACES or old == "#aaaaaa":
                    changes[attribute] = INK
                    changes["fill-opacity"] = "0.055"
                elif old in ACCENTS:
                    changes[attribute] = CLAY
            elif old in ACCENTS:
                changes[attribute] = CLAY
            elif old in LIGHT_TEXT or old in MUTED_TEXT or old in DARK_TEXT:
                changes[attribute] = INK
    for name, value in changes.items():
        raw = set_attr(raw, name, value)
    return raw


def transform(name: str, source: str) -> str:
    if name not in STATIC_ASSETS:
        raise ValueError(f"Asset not reviewed: {name}")
    ET.fromstring(source)
    result = source
    if name.startswith("bbs-"):
        result = result.replace(*COMMON_BBS_NOTE)
    if name.startswith("exp-ticket-"):
        result = result.replace(*READING_NOTE)
    for before, after in TEXT_REPLACEMENTS.get(name, ()):
        result = result.replace(before, after)
    for text in REMOVE_TEXT.get(name, ()):
        pattern = re.compile(r"<text\b[^>]*>" + re.escape(text) + r"</text>")
        result = pattern.sub("", result)
    result = OPEN_TAG.sub(lambda m: recolor_tag(m, is_stack=name == "stack.svg"), result)
    if name == "stack.svg" and 'id="paper-surface"' not in result:
        root = ET.fromstring(result)
        backdrop = (
            f'<rect id="paper-surface" width="{root.attrib["width"]}" '
            f'height="{root.attrib["height"]}" fill="{PAPER}"/>'
        )
        result = result.replace("</defs>", "</defs>" + backdrop, 1)
    ET.fromstring(result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Report pending changes without writing")
    args = parser.parse_args()
    assets = Path(__file__).resolve().parents[1] / "assets"
    changed = []
    for name in STATIC_ASSETS:
        path = assets / name
        before = path.read_text(encoding="utf-8")
        after = transform(name, before)
        if after != before:
            changed.append(name)
            if not args.check:
                path.write_text(after, encoding="utf-8")
    print(f"{'pending' if args.check else 'updated'}: {len(changed)}/{len(STATIC_ASSETS)}")
    for name in changed:
        print(name)
    return int(args.check and bool(changed))


if __name__ == "__main__":
    raise SystemExit(main())

