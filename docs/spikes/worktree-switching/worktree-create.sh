#!/bin/sh
# WorktreeCreate hook for the spike. Appends its stdin JSON to hook.log beside the repo,
# makes the worktree beside the repo (<repo>-worktrees/<name>) on a new branch <name> from main
# unless that folder already exists, and prints only the worktree's path.
input=$(cat)
cwd=$(printf '%s' "$input" | jq -r .cwd)
name=$(printf '%s' "$input" | jq -r .name)
repo=$(dirname "$(git -C "$cwd" rev-parse --path-format=absolute --git-common-dir)")
printf '%s\n' "$input" >> "$(dirname "$repo")/hook.log"
dir="$repo-worktrees/$name"
[ -d "$dir" ] || git -C "$repo" worktree add -b "$name" "$dir" main >&2 || exit 1
printf '%s\n' "$dir"
