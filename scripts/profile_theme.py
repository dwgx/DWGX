"""Select the profile palette without changing the profile layout."""
from pathlib import Path
import tomllib

ROOT = Path(__file__).resolve().parents[1]
THEME = tomllib.loads((ROOT / "profile.toml").read_text(encoding="utf-8")).get("theme", "paper")
if THEME not in {"paper", "classic"}:
    raise ValueError(f"Unknown profile theme: {THEME!r}")
CLASSIC_REF = "97e5ac3682f43248e9a78fd6206ba83ec199c185"
CLASSIC_STATIC_ASSETS = (
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
