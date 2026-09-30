#!/usr/bin/env bash
# repo-kit · roll the banner out to the named repositories.
#
#   rollout.sh <repo> [<repo> ...]
#
# Each repository gets two new files and one commit:
#   repo-kit.toml                  the spec for its own banner
#   .github/workflows/banner.yml   fetches the generator and refreshes on a schedule
#
# It always works on a fresh shallow clone under the temp dir, never on a local
# working copy, so a half-finished branch in D:\Project is never touched.
set -uo pipefail

KIT="D:/Project/DWGX/repo-kit"
WORK="${TMPDIR:-/tmp}/repokit-rollout"
mkdir -p "$WORK"
status=0

for repo in "$@"; do
  [ "$repo" = "DWGX" ] && { echo "skip DWGX (profile repo, README is generated)"; continue; }
  dir="$WORK/$repo"
  rm -rf "$dir"
  if ! git clone --depth 1 -q "https://github.com/dwgx/$repo.git" "$dir"; then
    echo "CLONE-FAIL $repo"; status=1; continue
  fi
  branch=$(git -C "$dir" rev-parse --abbrev-ref HEAD)
  if ! python "$KIT/build.py" "$repo" --out "$dir" --flat --inject --export "$dir" \
        >"$dir/.repokit.log" 2>&1; then
    echo "RENDER-FAIL $repo"; sed -n '1,5p' "$dir/.repokit.log"; status=1; continue
  fi
  rm -f "$dir/.repokit.log"
  mkdir -p "$dir/.github/workflows"
  cp "$KIT/templates/banner.yml" "$dir/.github/workflows/banner.yml"
  if ! git -C "$dir" diff --quiet || [ -n "$(git -C "$dir" status --porcelain)" ]; then
    git -C "$dir" add -A
    git -C "$dir" -c user.name=dwgx -c user.email=dwgx@users.noreply.github.com \
      commit -q -m "feat: repo-kit banner + regeneration workflow"
    if git -C "$dir" push -q origin "HEAD:$branch"; then
      size=$(stat -c%s "$dir/docs/assets/banner.svg" 2>/dev/null || echo 0)
      echo "OK $repo ($branch, banner ${size} B)"
    else
      echo "PUSH-FAIL $repo ($branch)"; status=1
    fi
  else
    echo "NOCHANGE $repo ($branch)"
  fi
done
exit $status