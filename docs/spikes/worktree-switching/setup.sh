#!/bin/sh
# Make a throwaway repo <dir>/toy with one commit on main, a local bare origin,
# and two worktrees beside it: <dir>/toy-worktrees/w1-a and w2-b.
# Usage: setup.sh <dir>   (<dir> must not exist yet)
set -eu
[ ! -e "$1" ] || { echo "$1 already exists" >&2; exit 1; }
mkdir -p "$1"
dir=$(cd "$1" && pwd -P)
git init -q --bare -b main "$dir/toy-origin.git"
git init -q -b main "$dir/toy"
cd "$dir/toy"
git config user.name spike
git config user.email spike@example.invalid
echo toy > README
git add README
git commit -q -m "one commit"
git remote add origin "$dir/toy-origin.git"
git push -q -u origin main
git remote set-head origin main
git worktree add -q ../toy-worktrees/w1-a -b w1-a main
git worktree add -q ../toy-worktrees/w2-b -b w2-b main
git worktree list
