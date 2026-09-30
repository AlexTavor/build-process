#!/bin/sh
# Builds the throwaway repository for the desktop-worktree-hook spike.
# Usage: sh setup.sh [target folder]   (default: ~/Documents/Alex/mlmd-spike-desktop)
# The hooks log to <target>.log, next to the folder.
set -eu
here=$(cd "$(dirname "$0")" && pwd)
target=${1:-$HOME/Documents/Alex/mlmd-spike-desktop}
if [ -e "$target" ]; then echo "setup: $target already exists" >&2; exit 1; fi
mkdir -p "$target/.claude/hooks"
cp "$here"/hooks/*.sh "$target/.claude/hooks/"
chmod +x "$target"/.claude/hooks/*.sh
cp "$here/settings.json" "$target/.claude/settings.json"
cd "$target"
git init -q -b main
printf '# mlmd spike: desktop worktree hook\n\nThrowaway. See mlmd/docs/spikes/desktop-worktree-hook.md.\n' > README.md
git add -A
git -c user.name=spike -c user.email=spike@localhost commit -q -m "Spike repository"
echo "setup: $target is ready. The hooks log to $target.log"
