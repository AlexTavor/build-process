#!/bin/sh
# PreToolUse hook for sequence h: log the call beside the repo and approve it.
input=$(cat)
cwd=$(printf '%s' "$input" | jq -r .cwd)
repo=$(dirname "$(git -C "$cwd" rev-parse --path-format=absolute --git-common-dir)")
printf '%s\n' "$input" >> "$(dirname "$repo")/pretooluse.log"
echo '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"allow","permissionDecisionReason":"spike: approve EnterWorktree"}}'
