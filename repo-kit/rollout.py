#!/usr/bin/env python3
"""repo-kit · roll the banner out to the named repositories.

    python rollout.py <repo> [<repo> ...]
    python rollout.py --dry-run <repo> ...

Per repository it stages README.md (patched), repo-kit.toml, docs/assets/banner*.svg
and .github/workflows/banner.yml, then writes one commit through the Git Data API.
No local clone, no new credential, no shell.
"""
from __future__ import annotations

import base64
import json
import shutil
import sys
import urllib.error
import shutil
import time
from pathlib import Path

KIT = Path(__file__).resolve().parent
sys.path.insert(0, str(KIT))

import build as B  # noqa: E402
import push_repo as P  # noqa: E402

OWNER = "dwgx"
WORK = Path("C:/Users/dwgx1/AppData/Local/Temp/repokit-stage")
STAGED = ("README.md", "repo-kit.toml", "docs/assets/banner.svg",
          "docs/assets/banner-light.svg", ".github/workflows/banner.yml")


def fetch_readme(repo: str, token: str) -> str | None:
    req = urllib.request.Request(
        f"{P.API}/repos/{OWNER}/{repo}/readme",
        headers={"Accept": "application/vnd.github.raw",
                 "User-Agent": "dwgx-repo-kit",
                 "Authorization": f"Bearer {token}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read().decode("utf-8")
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError):
        return None


OWNER = "dwgx"
WORK = Path("C:/Users/dwgx1/AppData/Local/Temp/repokit-stage")
STAGED = ("README.md", "repo-kit.toml", "docs/assets/banner.svg",
          "docs/assets/banner-light.svg", ".github/workflows/banner.yml")
ALLOW = KIT / "rollout.allow.txt"
MAX_PER_RUN = 3
PAUSE_BETWEEN = 8  # seconds between repository pushes


def allowed() -> set[str]:
    if not ALLOW.exists():
        return set()
    return {line.strip() for line in ALLOW.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")}


def main(argv: list[str]) -> int:
    dry = "--dry-run" in argv
    names = [a for a in argv if not a.startswith("--")]
    if not names:
        print(__doc__)
        return 2
    if not dry and len(names) > MAX_PER_RUN:
        print(f"refusing {len(names)} repositories in one run; the cap is {MAX_PER_RUN}. "
              "Run them in smaller batches.")
    if not dry:
        blocked = [r for r in names if r not in permit]
        if blocked:
            print("not in rollout.allow.txt: " + ", ".join(blocked))
            return 2
    token = B.gh_token()
    if not token:
        print("no token available", file=sys.stderr)
        return 2
    with open(KIT / "repos.toml", "rb") as fh:
        import tomllib

        conf = tomllib.load(fh)
    specs = {str(r["name"]): r for r in conf.get("repo") or []}
    WORK.mkdir(parents=True, exist_ok=True)
    status = 0
    pushed_count = 0

    for repo in names:
        if repo == "DWGX":
            print("skip DWGX (profile repository; its README is generated)")
            continue
        spec = specs.get(repo)
        if spec is None:
            print(f"NO-SPEC {repo} (add it to repo-kit/repos.toml)")
            status = 1
            continue
        stage = WORK / repo
        if stage.exists():
            shutil.rmtree(stage)
        (stage / ".github/workflows").mkdir(parents=True)
        readme = fetch_readme(repo, token)
        if readme is None:
            print(f"READ-FAIL {repo}")
            status = 1
            continue
        (stage / "README.md").write_text(readme, encoding="utf-8")

        meta: dict = {}
        history: list[int] = []
        try:
            info = B.api_get(f"/repos/{OWNER}/{repo}", token)
            meta = {"stars": info.get("stargazers_count"), "pushed": info.get("pushed_at")}
            meta["commits"] = B.count_commits(OWNER, repo, token)
            meta["releases"], meta["tag"] = B.latest_release(OWNER, repo, token)
            history = B.star_history(OWNER, repo, token)
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError) as exc:
            print(f"{repo}: live data unavailable ({exc})")

        ctx = B.build_ctx(spec, meta, history)
        style = str(spec.get("style") or "pipe")
        assets = stage / "docs/assets"
        assets.mkdir(parents=True, exist_ok=True)
        mod = B.THEMES[B.THEME]
        dark = mod.STYLES[style](ctx, False)
        (assets / "banner.svg").write_text(dark, encoding="utf-8")
        size = len(dark.encode())
        if style not in mod.DARK_ONLY:
            light = mod.STYLES[style](ctx, True)
            (assets / "banner-light.svg").write_text(light, encoding="utf-8")
            size += len(light.encode())
        (stage / "repo-kit.toml").write_text(B.export_spec(spec, OWNER), encoding="utf-8")
        shutil.copyfile(KIT / "templates/banner.yml", stage / ".github/workflows/banner.yml")
        patched = B.inject_readme(stage / "README.md", B.readme_block(spec, style, ctx))
        print(f"{repo:<24} {style:<7} {size:>7,} B  readme={'patched' if patched else 'unchanged'}")

        if dry:
            continue
        files = [p for p in STAGED if (stage / p).exists()]
        if not files:
            print(f"NOTHING-TO-PUSH {repo}")
            continue
        try:
            branch = B.api_get(f"/repos/{OWNER}/{repo}", token).get("default_branch") or "main"
            head = (P.call("GET", f"/repos/{OWNER}/{repo}/git/ref/heads/{branch}", token)
                    .get("object") or {}).get("sha")
            entries = [{"path": p, "mode": "100644", "type": "blob",
                        "content": (stage / p).read_text(encoding="utf-8")} for p in files]
            tree = P.call("POST", f"/repos/{OWNER}/{repo}/git/trees", token,
                          {"base_tree": head, "tree": entries})
            commit = P.call("POST", f"/repos/{OWNER}/{repo}/git/commits", token,
                            {"message": "feat: repo-kit banner + regeneration workflow",
                             "tree": tree.get("sha"), "parents": [head]})
            P.call("PATCH", f"/repos/{OWNER}/{repo}/git/refs/heads/{branch}", token,
                   {"sha": commit.get("sha"), "force": False})
            print(f"{repo:<24} pushed {str(commit.get('sha'))[:8]} on {branch}")
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, KeyError) as exc:
            print(f"PUSH-FAIL {repo}: {exc}")
            status = 1
    return status


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))


_ = base64  # imported for parity with the other scripts; unused here