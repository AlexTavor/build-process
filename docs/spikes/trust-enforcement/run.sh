#!/bin/sh
# Usage: SPIKE_DIR=<throwaway dir> run.sh <rules|hook|both> <mode>
# Builds a fresh toy repo in $SPIKE_DIR/<variant>-<mode>, runs one headless session there
# with only the toy project's settings, then prints check.sh's report.
set -eu
here=$(cd "$(dirname "$0")" && pwd)
variant=$1 mode=$2
dir=${SPIKE_DIR:?set SPIKE_DIR to a throwaway directory}/$variant-$mode
rm -rf "$dir" && sh "$here/setup.sh" "$dir" "$variant"
toy=$(cd "$dir/toy" && pwd -P)
cd "$toy"
# env -i: nothing from a parent Claude Code session (such as CLAUDECODE) reaches this one.
env -i HOME="$HOME" PATH="$PATH" USER="$USER" SHELL=/bin/sh TMPDIR="${TMPDIR:-/tmp}" \
  claude -p "$(sed "s|TOY|$toy|g" "$here/prompt.txt")" \
  --permission-mode "$mode" --setting-sources project,local \
  --strict-mcp-config --no-session-persistence --model sonnet --max-budget-usd 2 \
  --output-format stream-json --verbose > "$dir/log.jsonl" 2> "$dir/stderr.txt" \
  || echo "claude exited with $?"
sh "$here/check.sh" "$dir"
