"""AMIBIOS 3.31a CMOS screens for dwgx.menu. VGA 16-color, two-pane, Setup Help."""
from __future__ import annotations

import xml.sax.saxutils

AMI_BLUE = "#0000AA"
AMI_NAVY = "#000055"
AMI_CYAN = "#55FFFF"
AMI_WHITE = "#FFFFFF"
AMI_YELLOW = "#FFFF55"
AMI_GRAY = "#AAAAAA"
AMI_W, AMI_H = 960, 500


def _esc(s: str) -> str:
    return xml.sax.saxutils.escape(s)


def ami_help_wrap(text: str, width: int = 30) -> list[str]:
    words = text.split()
    lines: list[str] = []
    cur = ""
    for word in words:
        trial = (cur + " " + word).strip()
        if len(trial) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines[:12]


def ami_row(x: float, y: float, width: float, text: str, selected: bool) -> list[str]:
    parts: list[str] = []
    if selected:
        parts.append(
            f'<rect x="{x}" y="{y - 13}" width="{width}" height="18" fill="{AMI_GRAY}"/>'
        )
        fill = AMI_NAVY
    else:
        fill = AMI_WHITE
    parts.append(
        f'<text x="{x + 8}" y="{y}" font-size="13" fill="{fill}">{_esc(text)}</text>'
    )
    return parts


def ami_help_box(x: float, y: float, width: float, height: float, lines: list[str]) -> list[str]:
    parts = [
        f'<rect x="{x}" y="{y}" width="{width}" height="{height}" fill="{AMI_NAVY}" stroke="{AMI_CYAN}" stroke-width="1"/>',
        f'<text x="{x + width / 2:.0f}" y="{y + 20}" text-anchor="middle" font-size="13" fill="{AMI_YELLOW}">[ Setup Help ]</text>',
    ]
    yy = y + 44
    for line in lines:
        parts.append(
            f'<text x="{x + 14}" y="{yy}" font-size="13" fill="{AMI_WHITE}">{_esc(line)}</text>'
        )
        yy += 17
    return parts


def ami_chrome(active: str, inner: list[str]) -> str:
    w, h = AMI_W, AMI_H
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        "font-family=\"'Lucida Console','Courier New',Consolas,monospace\">",
        f'<rect width="{w}" height="{h}" fill="{AMI_BLUE}"/>',
        f'<rect x="0" y="0" width="{w}" height="26" fill="{AMI_NAVY}"/>',
        f'<text x="{w / 2:.0f}" y="18" text-anchor="middle" font-size="14" font-weight="700" fill="{AMI_WHITE}">AMIBIOS SETUP UTILITY - VERSION 3.31a</text>',
    ]
    x = 18
    for tab in ("Main", "Advanced", "Boot", "Log", "Exit"):
        tw = 12 * len(tab) + 18
        if tab == active:
            parts.append(
                f'<rect x="{x - 6}" y="30" width="{tw}" height="20" fill="{AMI_GRAY}"/>'
            )
            fill = AMI_NAVY
        else:
            fill = AMI_CYAN
        parts.append(f'<text x="{x}" y="45" font-size="14" fill="{fill}">{tab}</text>')
        x += tw + 10
    parts.append(
        f'<rect x="8" y="54" width="{w - 16}" height="{h - 90}" fill="{AMI_NAVY}" stroke="{AMI_CYAN}" stroke-width="2"/>'
    )
    parts.append(
        f'<rect x="12" y="58" width="{w - 24}" height="{h - 98}" fill="none" stroke="{AMI_CYAN}" stroke-width="1"/>'
    )
    parts.extend(inner)
    parts.append(f'<rect x="0" y="{h - 30}" width="{w}" height="30" fill="{AMI_NAVY}"/>')
    parts.append(
        f'<text x="14" y="{h - 10}" font-size="12" fill="{AMI_YELLOW}">'
        "F1:Help   Esc:Exit   ↑↓:Select Item   ←→:Select Screen   +/-:Change Values   F9:Setup Defaults   F10:Save &amp; Exit"
        "</text>"
    )
    parts.append("</svg>")
    return "".join(parts)


def setup_svg(repos: dict, tags: dict) -> str:
    wapi = repos.get("WindsurfAPI") or {}
    wstars = int(wapi.get("stargazers_count") or 0)
    kiro = tags.get("KiroStudio") or "live"
    wtag = tags.get("WindsurfAPI") or "live"
    items = [
        ("Boot Settings Configuration", "", False, True),
        ("Quiet Boot", "[Disabled]", False, False),
        ("Bootup Num-Lock", "[On]", False, False),
        ("Wait For 'F1' If Error", "[Enabled]", False, False),
        ("Hit 'DEL' Message Display", "[Enabled]", False, False),
        ("Boot Device Priority", "", False, True),
        ("1st Boot Device", "[ORIGIN]", True, False),
        ("2nd Boot Device", f"[WindsurfAPI {wtag}]", False, False),
        ("3rd Boot Device", f"[KiroStudio {kiro}]", False, False),
        ("4th Boot Device", "[vrchat-il2cpp-re]", False, False),
        ("Hard Disk Drives", ">", False, True),
        ("Removable Devices", ">", False, False),
        ("Network Stack", "[Enabled]", False, False),
    ]
    inner: list[str] = []
    y = 84
    for label, value, selected, header in items:
        if header:
            inner.append(
                f'<text x="28" y="{y}" font-size="13" fill="{AMI_YELLOW}">{_esc(label)}</text>'
            )
            y += 22
            continue
        text = f"{label:<32} {value}".rstrip()
        inner.extend(ami_row(20, y, 600, text, selected))
        y += 20
    help_lines = ami_help_wrap(
        "Specifies the first device AMIBIOS attempts after POST. "
        "ORIGIN is the world protocol. Public face: genesis.wiki. "
        f"WindsurfAPI is 2nd ({wstars} stars, {wtag}). "
        "Use +/- to reorder. Enter opens a sub-menu. "
        "This screen is a snapshot, not a live clock."
    )
    inner.extend(ami_help_box(636, 72, 308, 320, help_lines))
    return ami_chrome("Boot", inner)


def status_svg(work: dict, extra: dict, repos: dict, today: str) -> str:
    task = "idle"
    when = "-"
    msg = "-"
    sha = "-"
    if work:
        task = f"{work.get('verb')}  {work.get('repo')}"
        when = f"{work.get('ago')} ago"
        msg = (work.get("msg") or "-")[:42]
        sha = work.get("sha") or "-"
    wstars = int((repos.get("WindsurfAPI") or {}).get("stargazers_count") or 0)
    wopen = int((repos.get("WindsurfAPI") or {}).get("open_issues_count") or 0)
    kopen = int((repos.get("KiroStudio") or {}).get("open_issues_count") or 0)
    date_s = f"{today[5:7]}/{today[8:10]}/{today[2:4]}" if len(today) >= 10 else today
    lines = [
        (28, 82, "System Overview", AMI_YELLOW),
        (44, 104, "AMIBIOS", AMI_CYAN),
        (60, 124, "Version                 : dwgx.menu 2.7", AMI_WHITE),
        (60, 144, f"Build Date              : {date_s}", AMI_WHITE),
        (44, 168, "Processor", AMI_CYAN),
        (60, 188, f"Type                    : {task}", AMI_WHITE),
        (60, 208, f"Speed                   : {extra.get('commits_today') or 0} commits/day", AMI_WHITE),
        (60, 228, "Count                   : 1", AMI_WHITE),
        (44, 252, "System Memory", AMI_CYAN),
        (60, 272, f"Size                    : {wstars} Stars  (WindsurfAPI)", AMI_WHITE),
        (44, 296, "Last Event", AMI_CYAN),
        (60, 316, f"When                    : {when}", AMI_WHITE),
        (60, 336, f"HEAD                    : {sha}", AMI_WHITE),
        (60, 356, f"Message                 : {msg}", AMI_WHITE),
        (44, 380, "OnBoard Devices", AMI_CYAN),
        (60, 400, f"WindsurfAPI IRQ         : {wopen} open", AMI_WHITE),
        (60, 420, f"KiroStudio IRQ          : {kopen} open", AMI_WHITE),
    ]
    inner: list[str] = []
    for x, y, text, fill in lines:
        if text.startswith("Type"):
            inner.extend(ami_row(20, y, 600, text, True))
        else:
            inner.append(
                f'<text x="{x}" y="{y}" font-size="13" fill="{fill}">{_esc(text)}</text>'
            )
    help_lines = ami_help_wrap(
        "System Overview. Processor Type is the latest public GitHub event. "
        "It is not a ticking clock. Speed is today's commit count. "
        "IRQ counts are open issues. "
        "Use +/- to inspect a device. F10 does nothing; this page is read-only."
    )
    inner.extend(ami_help_box(636, 72, 308, 360, help_lines))
    return ami_chrome("Main", inner)


def devices_svg(heads: list[dict]) -> str:
    slots = [
        "Pri Master",
        "Pri Slave",
        "Sec Master",
        "Sec Slave",
        "CDROM",
        "Network",
    ]
    inner: list[str] = [
        f'<text x="28" y="82" font-size="13" fill="{AMI_YELLOW}">Standard CMOS Setup  -  IDE Devices</text>',
        f'<text x="28" y="108" font-size="12" fill="{AMI_CYAN}">TYPE            DEVICE              LBA/SHA     AGE     MODE</text>',
        f'<line x1="28" y1="116" x2="620" y2="116" stroke="{AMI_CYAN}" stroke-width="1"/>',
    ]
    y = 138
    for i, slot in enumerate(slots):
        row = heads[i] if i < len(heads) else {}
        name = str(row.get("name") or "Not Installed")
        sha = str(row.get("sha") or "-")
        age = str(row.get("ago") or "-")
        mode = "LBA" if row else "AUTO"
        line = f"{slot:<15} {name:<18} {sha:<9} {age:<7} {mode}"
        inner.extend(ami_row(20, y, 600, line, i == 0))
        y += 22
    inner.append(
        f'<text x="28" y="292" font-size="13" fill="{AMI_GRAY}">Floppy Drive A:     Not Installed</text>'
    )
    inner.append(
        f'<text x="28" y="314" font-size="13" fill="{AMI_GRAY}">Floppy Drive B:     Not Installed</text>'
    )
    inner.append(
        f'<text x="28" y="336" font-size="13" fill="{AMI_GRAY}">Boot Sector Virus Protection     [Disabled]</text>'
    )
    inner.append(
        f'<text x="28" y="368" font-size="12" fill="{AMI_CYAN}">Halt On: All Errors     Base Memory: 640K     Extended: {len(heads)} Devices</text>'
    )
    msg = (heads[0].get("msg") if heads else "") or ""
    help_lines = ami_help_wrap(
        "Pri Master is HEAD of the first listed public repository. "
        f"LBA is the short SHA. Last commit: {msg[:90] or 'none'}. "
        "Filled from GitHub, not from a local disk."
    )
    inner.extend(ami_help_box(636, 72, 308, 360, help_lines))
    return ami_chrome("Advanced", inner)


def eventlog_svg(lines: list[dict]) -> str:
    inner: list[str] = [
        f'<text x="28" y="82" font-size="13" fill="{AMI_YELLOW}">Event Log</text>',
        f'<text x="28" y="104" font-size="13" fill="{AMI_GRAY}">Event Log Valid              [Yes]</text>',
        f'<text x="28" y="124" font-size="13" fill="{AMI_GRAY}">View Event Log               [Enter]</text>',
        f'<text x="28" y="156" font-size="12" fill="{AMI_CYAN}">TIME     AGE    TYPE     SOURCE              DESCRIPTION</text>',
        f'<line x1="28" y1="164" x2="930" y2="164" stroke="{AMI_CYAN}" stroke-width="1"/>',
    ]
    y = 184
    if not lines:
        inner.append(
            f'<text x="28" y="{y}" font-size="13" fill="{AMI_GRAY}">(no public events)</text>'
        )
    for i, row in enumerate(lines[:11]):
        line = (
            f"{str(row.get('stamp') or '--:--'):<8} "
            f"{str(row.get('ago') or '?'):<6} "
            f"{str(row.get('verb') or ''):<8} "
            f"{str(row.get('repo') or ''):<18} "
            f"{str(row.get('msg') or '')[:40]}"
        )
        inner.extend(ami_row(20, y, 920, line, i == 0))
        y += 20
    return ami_chrome("Log", inner)
