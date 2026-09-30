#!/bin/sh
# Usage: run-all.sh <dir> [--untrusted]
# Runs spike.py (fake API, no model) for each variant in every mode, on the claude on PATH and
# on the desktop app's CLI, then prints the tables. Each run's folder is <dir>/<version>/.
# --untrusted is passed on to spike.py.
set -eu
here=$(cd "$(dirname "$0")" && pwd)
app="$HOME/Library/Application Support/Claude/claude-code/2.1.284/claude.app/Contents/MacOS/claude"
for cli in claude "$app"; do
  v=$(DISABLE_AUTOUPDATER=1 "$cli" --version | cut -d' ' -f1)
  for variant in rules hook both; do
    for mode in default acceptEdits auto bypassPermissions dontAsk; do
      echo "=== $v $variant $mode"
      python3 -B "$here/spike.py" "$variant" "$mode" "$1/$v" --claude "$cli" ${2:-}
    done
  done
done
python3 -B "$here/table.py" "$1"
