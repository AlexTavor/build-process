#!/usr/bin/env python3
"""Usage: python3 -B table.py <dir>

Prints one markdown table per variant from <dir>/<version>/<variant>-<mode>/results.json, as
spike.py writes them. Rows are the command forms, columns the modes. A cell shows one outcome
when every version agrees, else each version's outcome.
"""
import glob, json, sys

MODES = ["default", "acceptEdits", "auto", "bypassPermissions", "dontAsk"]
runs = {}
for p in glob.glob(f"{sys.argv[1]}/*/*/results.json"):
    r = json.load(open(p))
    runs[(r["claude"], r["variant"], r["requested_mode"])] = r["forms"]
versions = sorted({k[0] for k in runs})
for variant in ("rules", "hook", "both"):
    modes = [m for m in MODES if any((v, variant, m) in runs for v in versions)]
    if not modes:
        continue
    forms = next(f for (v, va, m), f in runs.items() if va == variant)
    print(f"\n{variant}, Claude Code {', '.join(versions)}\n")
    print("| Form | " + " | ".join(modes) + " |")
    print("|---" * (len(modes) + 1) + "|")
    for i, form in enumerate(forms):
        cells = []
        for m in modes:
            out = {v: runs[(v, variant, m)][i]["outcome"] for v in versions if (v, variant, m) in runs}
            same = len(set(out.values())) == 1
            cells.append(next(iter(out.values())) if same else ", ".join(f"{o} ({v})" for v, o in out.items()))
        print(f"| `{form['label']}` | " + " | ".join(cells) + " |")
