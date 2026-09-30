#!/bin/sh
# PreToolUse hook, matcher Bash. Reads the tool input JSON on stdin. For any git push,
# merge.sh or release.sh it prints an "ask" decision; otherwise it prints nothing.
# Each call is logged to .claude/hook.log, so a run shows whether the hook was called.
cmd=$(jq -r '.tool_input.command // ""')
decision=none
if printf '%s\n' "$cmd" | grep -Eq 'git[^;&|]*[[:space:]]push|merge\.sh|release\.sh'; then
  decision=ask
  echo '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"ask","permissionDecisionReason":"mlmd trust: waits for the owner"}}'
fi
printf '%s\t%s\n' "$decision" "$cmd" >> "${CLAUDE_PROJECT_DIR:-.}/.claude/hook.log"
exit 0
