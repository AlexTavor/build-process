#!/bin/sh
# SessionStart hook. Logs where each session starts and why, so the log shows whether a desktop
# session runs in a worktree the WorktreeCreate hook made. Prints nothing to the session.
input=$(cat)
common=$(git -C "$CLAUDE_PROJECT_DIR" rev-parse --path-format=absolute --git-common-dir 2>/dev/null) || exit 0
root=$(dirname "$common")
log="$(dirname "$root")/$(basename "$root").log"
printf '%s SessionStart project_dir=%s input=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$CLAUDE_PROJECT_DIR" "$input" >> "$log"
exit 0
