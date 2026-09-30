#!/bin/sh
# Usage: setup.sh <dir> <rules|hook|both>   (<dir> must not exist yet)
# Makes <dir>/origin.git (bare) and <dir>/toy, a repo with one commit pushed to origin/main
# and one commit not pushed, two scripts that append a line to toy/marker.txt, and the
# project settings for the variant.
set -eu
here=$(cd "$(dirname "$0")" && pwd)
dir=$1 variant=$2
[ ! -e "$dir" ] || { echo "$dir already exists" >&2; exit 1; }
mkdir -p "$dir" && dir=$(cd "$dir" && pwd -P)
g() { git -c user.name=spike -c user.email=spike@example.invalid -c commit.gpgsign=false "$@"; }
git init -q --bare -b main "$dir/origin.git"
git init -q -b main "$dir/toy" && cd "$dir/toy"
mkdir -p scripts .claude
for s in merge release; do
  printf '#!/bin/sh\necho "%s $1" >> "$(dirname "$0")/../marker.txt"\n' "$s" > "scripts/$s.sh"
done
chmod +x scripts/*.sh
echo marker.txt > .gitignore
g add -A && g commit -qm one
git remote add origin "$dir/origin.git"
git push -q -u origin main
echo two > two.txt && g add two.txt && g commit -qm two
cp "$here/settings-$variant.json" .claude/settings.json
cp "$here/trust-hook.sh" .claude/trust-hook.sh
