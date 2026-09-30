#!/bin/sh
# WorktreeCreate hook. Logs the call, creates the worktree beside the repository on a new branch
# from main, and prints only its path, which is what Claude Code reads from stdout.
set -eu
input=$(cat)
field() { printf '%s' "$input" | /usr/bin/python3 -c "import json,sys; v=json.load(sys.stdin).get('$1'); print(v if v else '')"; }
cwd=$(field cwd)
name=$(field name | tr -c 'A-Za-z0-9._\n-' '-')
[ -n "$name" ] || name="unnamed-$(date +%s)"
root=$(dirname "$(git -C "${cwd:-$CLAUDE_PROJECT_DIR}" rev-parse --path-format=absolute --git-common-dir)")
log="$(dirname "$root")/$(basename "$root").log"
printf '%s WorktreeCreate %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$input" >> "$log"
dest="$(dirname "$root")/$(basename "$root")-worktrees/$name"
git -C "$root" worktree add -q -b "spike/$name" "$dest" main >> "$log" 2>&1
printf '%s created %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$dest" >> "$log"
printf '%s\n' "$dest"
