#!/bin/sh
# WorktreeRemove hook. Logs the call and removes the worktree folder. It keeps the branch: in mlmd
# the branch is what records an item's work.
set -eu
input=$(cat)
field() { printf '%s' "$input" | /usr/bin/python3 -c "import json,sys; v=json.load(sys.stdin).get('$1'); print(v if v else '')"; }
path=$(field path)
cwd=$(field cwd)
root=$(dirname "$(git -C "${cwd:-$CLAUDE_PROJECT_DIR}" rev-parse --path-format=absolute --git-common-dir)")
log="$(dirname "$root")/$(basename "$root").log"
printf '%s WorktreeRemove %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$input" >> "$log"
if [ -n "$path" ]; then git -C "$root" worktree remove --force "$path" >> "$log" 2>&1 || true; fi
