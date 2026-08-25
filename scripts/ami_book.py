"""Extra AMIBIOS / POST / DOS / NFO screens. Same VGA family, more pages."""
from __future__ import annotations

from ami import (
    AMI_CYAN,
    AMI_GRAY,
    AMI_NAVY,
    AMI_WHITE,
    AMI_YELLOW,
    _esc,
    ami_chrome,
    ami_help_box,
    ami_help_wrap,
    ami_row,
)

PNP_TABS = ("PnP", "PCI", "IRQ", "Chipset", "Health")
SYS_TABS = ("DMI", "USB", "RAID", "Memory", "ROM")


def _stars(repos: dict, name: str) -> int:
    return int((repos.get(name) or {}).get("stargazers_count") or 0)


def _open(repos: dict, name: str) -> int:
    return int((repos.get(name) or {}).get("open_issues_count") or 0)


def post_svg(repos: dict, extra: dict, public: int, stars: int, tags: dict) -> str:
    kb = stars * 16
    banks = public
    wtag = tags.get("WindsurfAPI") or "live"
    lines = [
        (AMI_YELLOW, "AMIBIOS (C)2026 dwgx, Kobe — dwgx.menu 2.9"),
        (AMI_GRAY, "BIOS Date: 08/25/26  14:54:07  Ver: 08.00.xx"),
        (AMI_WHITE, ""),
        (AMI_CYAN, "Main Processor  : Intel Ultra 9 275HX @ ROG Strix G18"),
        (AMI_CYAN, "Coprocessor     : AMD R5-5600 / RTX 3060  (Homecloud)"),
        (AMI_WHITE, ""),
        (AMI_WHITE, f"Memory Test     : {kb:,}K OK   ({stars} stars x 16)"),
        (AMI_WHITE, f"Memory Banks    : {banks} public repos detected"),
        (AMI_WHITE, ""),
        (AMI_YELLOW, "Detecting IDE Primary Master   ... ORIGIN        genesis.wiki"),
        (AMI_YELLOW, f"Detecting IDE Primary Slave    ... WindsurfAPI   {wtag}"),
        (AMI_YELLOW, f"Detecting IDE Secondary Master ... KiroStudio    {tags.get('KiroStudio') or 'live'}"),
        (AMI_YELLOW, "Detecting IDE Secondary Slave  ... vrchat-il2cpp-re"),
        (AMI_WHITE, ""),
        (AMI_GRAY, f"USB Devices     : 5    PCI Devices : 6    IRQ in use : {_open(repos,'WindsurfAPI')}"),
        (AMI_GRAY, f"Today commits   : {extra.get('commits_today') or 0}    Year : {extra.get('commits_year') or 0}"),
        (AMI_WHITE, ""),
        (AMI_YELLOW, "Press DEL to run Setup          Press F8 for BBS Popup"),
        (AMI_CYAN, "Booting from 1st device ORIGIN ..."),
    ]
    return _black_screen("AMIBIOS POST", lines, "DEL = Setup   F8 = BBS   F10 = Save")


def _black_screen(title: str, lines: list[tuple[str, str]], footer: str) -> str:
    w, h = 960, 500
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        "font-family=\"'Lucida Console','Courier New',Consolas,monospace\">",
        f'<rect width="{w}" height="{h}" fill="#000000"/>',
        f'<text x="24" y="28" font-size="14" font-weight="700" fill="{AMI_YELLOW}">{_esc(title)}</text>',
    ]
    y = 58
    for color, text in lines:
        parts.append(
            f'<text x="24" y="{y}" font-size="14" fill="{color}">{_esc(text)}</text>'
        )
        y += 20
    parts.append(f'<rect x="0" y="{h - 28}" width="{w}" height="28" fill="#111111"/>')
    parts.append(
        f'<text x="24" y="{h - 10}" font-size="12" fill="{AMI_GRAY}">{_esc(footer)}</text>'
    )
    parts.append("</svg>")
    return "".join(parts)


def dmi_svg(hw: dict) -> str:
    inner: list[str] = [
        f'<text x="28" y="82" font-size="13" fill="{AMI_YELLOW}">DMI / SMBIOS — System Information</text>',
    ]
    rows = [
        ("Type 0  BIOS", "AMIBIOS 3.31a / dwgx.menu 2.9"),
        ("Type 1  System", "dwgx@main · Kobe · 帝王尬笑"),
        ("Type 2  Base Board", "ASUS ROG Strix G18  Ultra 9 275HX  RTX 5070 Ti"),
        ("Type 3  Chassis", "Notebook / portable"),
        ("Type 4  Processor", "Intel Ultra 9 275HX"),
        ("Type 17 Memory", "32 GB DDR5 + Homecloud 16 GB DDR4"),
        ("Type 16 Array", "MacBook Air M2 8 GB  ·  iPhone 17 / iPhone SE"),
        ("OEM String", "Homecloud Debian 13 worker · RTX 3060"),
    ]
    y = 112
    for i, (k, v) in enumerate(rows):
        inner.extend(ami_row(20, y, 600, f"{k:<22} {v}"[:78], i == 1))
        y += 22
    inner.extend(
        ami_help_box(
            636,
            72,
            308,
            360,
            ami_help_wrap(
                "DMI table of the machines you actually sit at. "
                "Type 1 is the identity string. Type 2 is the daily driver. "
                "Homecloud is the LAN worker, not a desktop toy."
            ),
        )
    )
    return ami_chrome("DMI", inner, tabs=SYS_TABS)


def irq_svg(repos: dict) -> str:
    mapping = [
        ("IRQ 0", "timer", "rtc.ok", "system"),
        ("IRQ 1", "keyboard", "VGN FLASH Ultra", "usb"),
        ("IRQ 3", "COM2", "cursorapi", "pool"),
        ("IRQ 4", "COM1", "event log", "live"),
        ("IRQ 5", "WindsurfAPI", f"{_stars(repos,'WindsurfAPI')} ★  {_open(repos,'WindsurfAPI')} open", "nic"),
        ("IRQ 7", "KiroStudio", f"{_stars(repos,'KiroStudio')} ★", "scsi"),
        ("IRQ 9", "ORIGIN", "genesis.wiki", "acpi"),
        ("IRQ 10", "vrchat-il2cpp-re", f"{_stars(repos,'vrchat-il2cpp-re')} ★", "game"),
        ("IRQ 11", "SmartCLI", "PTY + pyte", "tty"),
        ("IRQ 12", "mouse", "Dragonfly 3 / King", "usb"),
        ("IRQ 14", "YuKiKo", f"{_stars(repos,'YuKiKo')} ★", "ide"),
        ("IRQ 15", "VRCSM", f"{_stars(repos,'VRCSM')} ★", "ide"),
    ]
    inner = [
        f'<text x="28" y="82" font-size="13" fill="{AMI_YELLOW}">Interrupt Request Table</text>',
        f'<text x="28" y="106" font-size="12" fill="{AMI_CYAN}">LINE     DEVICE              NOTE                         CLASS</text>',
    ]
    y = 130
    for i, (irq, dev, note, cls) in enumerate(mapping):
        inner.extend(
            ami_row(20, y, 600, f"{irq:<8} {dev:<18} {note:<26} {cls}", i == 4)
        )
        y += 20
    inner.extend(
        ami_help_box(
            636,
            72,
            308,
            360,
            ami_help_wrap(
                "IRQ 5 is the public flagship. "
                "Open-issue counts ride the IRQ as load. "
                "COM1 is the event log. Keyboard and mice are real USB, not metaphors only."
            ),
        )
    )
    return ami_chrome("IRQ", inner, tabs=PNP_TABS)


def pci_svg(repos: dict, tags: dict) -> str:
    devices = [
        ("00:00.0", "Host bridge", "ORIGIN", "genesis.wiki"),
        ("00:01.0", "VGA", "WindsurfAPI", tags.get("WindsurfAPI") or "live"),
        ("00:02.0", "SCSI", "KiroStudio", tags.get("KiroStudio") or "live"),
        ("00:03.0", "USB", "SmartCLI", "PTY"),
        ("00:04.0", "Gameport", "vrchat-il2cpp-re", "Unity 6"),
        ("00:05.0", "NIC", "YuKiKo", "QQ bot"),
        ("00:06.0", "SATA", "VRCSM", tags.get("VRCSM") or "cache"),
        ("00:07.0", "SMBus", "cursorapi", "key pool"),
    ]
    inner = [
        f'<text x="28" y="82" font-size="13" fill="{AMI_YELLOW}">PCI Device Enumeration</text>',
        f'<text x="28" y="106" font-size="12" fill="{AMI_CYAN}">BUS      CLASS       DEVICE              INFO</text>',
    ]
    y = 130
    for i, (bus, cls, name, info) in enumerate(devices):
        star = _stars(repos, name)
        extra = f"  ★{star}" if star else ""
        inner.extend(
            ami_row(20, y, 600, f"{bus}  {cls:<11} {name:<18} {info}{extra}", i == 1)
        )
        y += 22
    inner.extend(
        ami_help_box(
            636,
            72,
            308,
            360,
            ami_help_wrap(
                "PCI bus 0 is the public machine. "
                "VGA is WindsurfAPI because that is what the world sees first. "
                "Host bridge is ORIGIN. Do not hot-unplug under load."
            ),
        )
    )
    return ami_chrome("PCI", inner, tabs=PNP_TABS)


def smart_svg(repos: dict, tags: dict) -> str:
    stars = _stars(repos, "WindsurfAPI")
    issues = _open(repos, "WindsurfAPI")
    health = "PASSED" if issues < 50 else "WARN"
    attrs = [
        ("01 Raw Read Error Rate", "100", "050", "OK"),
        ("05 Reallocated Sectors", f"{issues:03d}", "010", "OK" if issues < 40 else "HOT"),
        ("09 Power-On Hours", "5895", "000", "OK"),
        ("12 Power Cycle Count", f"{_stars(repos,'KiroStudio'):03d}", "000", "OK"),
        ("194 Temperature", f"{min(99, 30 + (stars // 200))}", "000", "OK"),
        ("199 UDMA CRC Error", "000", "000", "OK"),
        ("241 Total LBAs Written", f"{stars}", "000", "OK"),
    ]
    inner = [
        f'<text x="28" y="82" font-size="13" fill="{AMI_YELLOW}">S.M.A.R.T.  —  WindsurfAPI as HDD 0</text>',
        f'<text x="28" y="104" font-size="13" fill="{AMI_CYAN}">Model: dwgx-WINDSURF  Firmware: {tags.get("WindsurfAPI") or "live"}  Health: {health}</text>',
        f'<text x="28" y="128" font-size="12" fill="{AMI_GRAY}">ID  ATTRIBUTE                 VALUE  THRESH  STATUS</text>',
    ]
    y = 152
    for i, (name, val, thr, st) in enumerate(attrs):
        inner.extend(ami_row(20, y, 600, f"{name:<28} {val:>5}  {thr:>5}  {st}", i == 4))
        y += 22
    inner.append(
        f'<text x="28" y="330" font-size="13" fill="{AMI_YELLOW}">Self-test: short  COMPLETED  without error</text>'
    )
    inner.extend(
        ami_help_box(
            636,
            72,
            308,
            360,
            ami_help_wrap(
                "Attribute 241 is total stars on WindsurfAPI. "
                "Reallocated sectors track open issues. "
                "This is a joke SMART page. The disk is a Node gateway, not ATA."
            ),
        )
    )
    return ami_chrome("Health", inner, tabs=PNP_TABS)


def usb_svg(hw: dict) -> str:
    per = list(hw.get("peripheral") or [])
    mobile = list(hw.get("mobile") or [])
    inner = [
        f'<text x="28" y="82" font-size="13" fill="{AMI_YELLOW}">USB Device List</text>',
    ]
    y = 112
    items = [
        "USB 1  VGN FLASH Ultra 太陽神  (kbd)",
        "USB 2  VGN Dragonfly 3 Master 超跑紅",
        "USB 3  VGN Dragonfly King 太空银",
        "USB 4  Meta Quest 3",
        "USB 5  AirPods Pro 3 / Panasonic SL-CT790",
        "USB 6  iPhone 17  256GB  JP",
        "USB 7  iPhone SE  32GB  US origin",
        "USB 8  Apple Watch 1st  2015",
    ]
    for i, line in enumerate(items):
        inner.extend(ami_row(20, y, 600, line, i == 0))
        y += 22
    inner.append(
        f'<text x="28" y="330" font-size="12" fill="{AMI_GRAY}">{_esc(str(hw.get("mobile_comment") or ""))}</text>'
    )
    inner.extend(
        ami_help_box(
            636,
            72,
            308,
            360,
            ami_help_wrap(
                "Real peripherals from hardware.dmp. "
                "K60 is stolen, not attached. "
                "Quest 3 is VR, not a USB toy in POST — still enumerated."
            ),
        )
    )
    _ = (per, mobile)
    return ami_chrome("USB", inner, tabs=SYS_TABS)


def raid_svg(repos: dict, tags: dict) -> str:
    inner = [
        f'<text x="28" y="82" font-size="13" fill="{AMI_YELLOW}">RAID  —  Flagship Array</text>',
        f'<text x="28" y="108" font-size="13" fill="{AMI_CYAN}">Level: RAID-1  Status: DEGRADED=no  Rebuild: idle</text>',
    ]
    members = [
        ("Disk 0", "ORIGIN", "genesis.wiki", "ONLINE"),
        ("Disk 1", "WindsurfAPI", f"{tags.get('WindsurfAPI')}  ★{_stars(repos,'WindsurfAPI')}", "ONLINE"),
        ("Disk 2", "KiroStudio", f"{tags.get('KiroStudio')}  ★{_stars(repos,'KiroStudio')}", "ONLINE"),
        ("HotSpare", "SmartCLI", "PTY + pyte", "STANDBY"),
        ("HotSpare", "vrchat-il2cpp-re", f"★{_stars(repos,'vrchat-il2cpp-re')}", "STANDBY"),
    ]
    y = 140
    for i, (slot, name, note, st) in enumerate(members):
        inner.extend(
            ami_row(20, y, 600, f"{slot:<10} {name:<20} {note:<28} {st}", i == 1)
        )
        y += 24
    inner.append(
        f'<text x="28" y="300" font-size="13" fill="{AMI_YELLOW}">Stripe: none   Write cache: enabled   BBU: present</text>'
    )
    inner.extend(
        ami_help_box(
            636,
            72,
            308,
            360,
            ami_help_wrap(
                "Disk 0 is ORIGIN. Disk 1 is what people star. "
                "Hot spares are lab tools. "
                "Array stays online if one public repo is quiet."
            ),
        )
    )
    return ami_chrome("RAID", inner, tabs=SYS_TABS)


def chipset_svg(langs: list[dict]) -> str:
    inner = [
        f'<text x="28" y="82" font-size="13" fill="{AMI_YELLOW}">Chipset Features  —  language northbridge</text>',
    ]
    y = 114
    total = sum(int(x.get("size") or 0) for x in langs) or 1
    for i, lang in enumerate(langs[:8]):
        pct = int(lang["size"]) * 100 // total
        bar = "█" * max(1, pct // 5) + "░" * max(0, 20 - pct // 5)
        inner.extend(
            ami_row(
                20,
                y,
                600,
                f"{str(lang['name']):<16} {bar}  {pct:3d}%",
                i == 0,
            )
        )
        y += 22
    inner.extend(
        ami_help_box(
            636,
            72,
            308,
            360,
            ami_help_wrap(
                "Byte-weighted languages from public repos. "
                "HTML/CSS stripped. "
                "C# high means IL2CPP dump, not that JS stopped being flagship."
            ),
        )
    )
    return ami_chrome("Chipset", inner, tabs=PNP_TABS)


def memmap_svg(repos: dict) -> str:
    rows = [
        ("00000-9FFFF", "Conventional", "dwgx.cfg / identity"),
        ("A0000-BFFFF", "VGA", "WindsurfAPI viewport"),
        ("C0000-C7FFF", "Option ROM", "幻想万華鏡"),
        ("C8000-DFFFF", "Unused", "reserved"),
        ("E0000-EFFFF", "BIOS Ext", "KiroStudio gateway"),
        ("F0000-FFFFF", "System BIOS", "AMIBIOS 3.31a"),
        ("100000-7FFFFF", "Extended", f"{_stars(repos,'WindsurfAPI')} stars mapped"),
        ("800000-FFFFFF", "High mem", "ORIGIN world protocol"),
    ]
    inner = [
        f'<text x="28" y="82" font-size="13" fill="{AMI_YELLOW}">Memory Map</text>',
        f'<text x="28" y="106" font-size="12" fill="{AMI_CYAN}">RANGE           REGION         OWNER</text>',
    ]
    y = 130
    for i, (rng, region, owner) in enumerate(rows):
        inner.extend(ami_row(20, y, 600, f"{rng:<16} {region:<14} {owner}", i == 1))
        y += 22
    inner.extend(
        ami_help_box(
            636,
            72,
            308,
            360,
            ami_help_wrap(
                "A0000 is the public surface. "
                "C0000 is the Touhou option ROM. "
                "High memory is ORIGIN. Conventional is the cfg you already rewrote."
            ),
        )
    )
    return ami_chrome("Memory", inner, tabs=SYS_TABS)


def optionrom_svg() -> str:
    inner = [
        f'<text x="28" y="82" font-size="13" fill="{AMI_YELLOW}">Option ROM  —  VGA BIOS shadow</text>',
        f'<text x="28" y="110" font-size="13" fill="{AMI_WHITE}">C000:0000  幻想万華鏡  The Memories of Phantasm</text>',
        f'<text x="28" y="134" font-size="13" fill="{AMI_CYAN}">Publisher : 滿福神社</text>',
        f'<text x="28" y="156" font-size="13" fill="{AMI_CYAN}">Episodes  : 18   Format : BDRip</text>',
        f'<text x="28" y="178" font-size="13" fill="{AMI_CYAN}">License   : 東方Project 二次創作</text>',
        f'<text x="28" y="210" font-size="13" fill="{AMI_YELLOW}">Shadowing : Enabled     Size : 32 KB mapped</text>',
        f'<text x="28" y="232" font-size="13" fill="{AMI_WHITE}">INT 10h hook installed. Featured GIF is the framebuffer.</text>',
        f'<text x="28" y="270" font-size="13" fill="{AMI_GRAY}">This ROM is personality, not a KPI.</text>',
    ]
    inner.extend(
        ami_help_box(
            636,
            72,
            308,
            360,
            ami_help_wrap(
                "Option ROM at C000. "
                "Keep the 東方 clip. "
                "Do not replace it with a stats card."
            ),
        )
    )
    return ami_chrome("ROM", inner, tabs=SYS_TABS)


def dir_svg(repos: dict) -> str:
    names = [
        "WindsurfAPI",
        "KiroStudio",
        "vrchat-il2cpp-re",
        "YuKiKo",
        "SmartCLI",
        "VRCSM",
        "cursorapi",
        "JSM",
        "THIzaKaYaDEVCosole",
        "fuckopencode",
        "SaoMoLa",
        "DWGX",
    ]
    lines = [(AMI_YELLOW, " Volume in drive C is DWGX"), (AMI_YELLOW, " Directory of C:\\dwgx"), (AMI_WHITE, "")]
    for name in names:
        r = repos.get(name) or {}
        stars = int(r.get("stargazers_count") or 0)
        pushed = str(r.get("pushed_at") or "")[:10]
        lang = r.get("language") or "-"
        lines.append(
            (
                AMI_WHITE,
                f"{name:<22} {stars:>5} ★  {lang:<10}  {pushed}",
            )
        )
    lines.append((AMI_WHITE, ""))
    lines.append((AMI_CYAN, f"       {len(names)} file(s)    {sum(_stars(repos, n) for n in names)} stars listed"))
    return _black_screen("C:\\dwgx> dir /o:s", lines, "COMMAND.COM  ·  dir of public flagships")


def nfo_svg(stars: int, public: int, tags: dict) -> str:
    gold, pink, dim = "#c9a84c", "#f2a6c4", "#8b949e"
    lines = [
        (gold, "      ▄▄▄▄▄▄▄  ▄     ▄  ▄▄▄▄▄▄▄  ▄     ▄"),
        (gold, "      █     █  █  █  █  █        ▀▄   ▄▀"),
        (gold, "      █     █  █  █  █  █  ▄▄▄     █ █"),
        (gold, "      █     █  █  █  █  █    █     █ █"),
        (gold, "      ▀▄▄▄▄▄▀   ▀▄▀▄▀   ▀▄▄▄▄▀     ▀▄▀"),
        (pink, "              . d w g x . p r e s e n t s ."),
        (dim, ""),
        (AMI_WHITE, f"  group     dwgx"),
        (AMI_WHITE, f"  pack      dwgx.menu 2.9"),
        (AMI_WHITE, f"  os        windows + debian13 + m2"),
        (AMI_WHITE, f"  supplier  WindsurfAPI {tags.get('WindsurfAPI')}  /  KiroStudio {tags.get('KiroStudio')}"),
        (AMI_WHITE, f"  rating    {stars} stars  /  {public} public"),
        (AMI_WHITE, "  nfo       maybe I'm dwgx"),
        (dim, ""),
        (pink, "  帝王尬笑"),
    ]
    w, h = 960, 500
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        "font-family=\"'Lucida Console','Courier New',Consolas,monospace\">",
        f'<rect width="{w}" height="{h}" fill="#06020f"/>',
        f'<rect x="8" y="8" width="{w-16}" height="{h-16}" fill="none" stroke="{gold}" stroke-width="2"/>',
    ]
    y = 48
    for color, text in lines:
        parts.append(
            f'<text x="48" y="{y}" font-size="16" fill="{color}">{_esc(text)}</text>'
        )
        y += 26
    parts.append("</svg>")
    return "".join(parts)


def beep_svg() -> str:
    lines = [
        (AMI_YELLOW, "BIOS Beep Codes  —  dwgx.menu"),
        (AMI_WHITE, ""),
        (AMI_WHITE, "1 short            POST OK, boot ORIGIN"),
        (AMI_WHITE, "2 short            WindsurfAPI listening"),
        (AMI_WHITE, "1 long 2 short     video / README render fail"),
        (AMI_WHITE, "1 long 3 short     no Glama / PR closed by deleting fork"),
        (AMI_WHITE, "continuous         labeled-issue noise on the cover (fixed)"),
        (AMI_WHITE, "no beep            Homecloud tunnel 1033"),
        (AMI_WHITE, ""),
        (AMI_CYAN, "If you hear 1 long 3 short: re-open the PR. Do not delete the fork."),
    ]
    return _black_screen("BEEP.ROM", lines, "speaker: PC beep  ·  not a clock")


def render_book(payload: dict) -> dict[str, str]:
    repos = payload["repos"]
    extra = payload["extra"]
    tags = payload["tags"]
    hw = payload["hardware"]
    langs = payload.get("langs") or []
    public = payload["public"]
    stars = payload["stars"]
    return {
        "post.svg": post_svg(repos, extra, public, stars, tags),
        "dmi.svg": dmi_svg(hw),
        "irq.svg": irq_svg(repos),
        "pci.svg": pci_svg(repos, tags),
        "smart.svg": smart_svg(repos, tags),
        "usb.svg": usb_svg(hw),
        "raid.svg": raid_svg(repos, tags),
        "chipset.svg": chipset_svg(langs),
        "memmap.svg": memmap_svg(repos),
        "optionrom.svg": optionrom_svg(),
        "dir.svg": dir_svg(repos),
        "nfo.svg": nfo_svg(stars, public, tags),
        "beep.svg": beep_svg(),
    }
