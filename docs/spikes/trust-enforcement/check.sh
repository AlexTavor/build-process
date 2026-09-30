#!/bin/sh
# Usage: check.sh <run dir>
# Says which commands ran, from the repo state (refs in origin.git, lines in marker.txt),
# then lists each Bash call in the session log with the start of its result.
dir=$1 o="$1/origin.git" t="$1/toy"
jq -r 'select(.type=="system" and .subtype=="init")
  | "mode \(.permissionMode), model \(.model), claude \(.claude_code_version // "?")"' "$dir/log.jsonl"
for r in t1 t2 t3 t4 t5 t6; do
  git -C "$o" rev-parse -q --verify "refs/heads/$r" >/dev/null && echo "$r: ran" || echo "$r: did not run"
done
[ "$(git -C "$o" rev-parse main)" = "$(git -C "$t" rev-parse main)" ] \
  && echo "plain git push: ran" || echo "plain git push: did not run"
for m in m1 m2 m3 m4 r1; do
  grep -q " $m\$" "$t/marker.txt" 2>/dev/null && echo "$m: ran" || echo "$m: did not run"
done
echo "--- Bash calls, with the start of each result"
jq -rs '
  (map(select(.type=="user") | .message.content[]? | select(.type=="tool_result")
       | {(.tool_use_id): .}) | add // {}) as $res
  | (.[] | select(.type=="assistant") | .message.content[]? | select(.type=="tool_use")
     | ($res[.id] // {}) as $r
     | "\(.input.command // .name)\n    \(if $r.is_error then "ERROR" else "ok" end): \(
         $r.content | if type=="array" then map(.text? // "") | join(" ") else (. // "") end
         | gsub("\\s+"; " ") | .[0:220])"),
    (.[] | select(.type=="result")
     | "--- result: \(.subtype), cost $\(.total_cost_usd), permission denials \(.permission_denials | length)\n\(.result)")
' "$dir/log.jsonl"
[ -f "$t/.claude/hook.log" ] && { echo "--- hook log"; cat "$t/.claude/hook.log"; }
exit 0
