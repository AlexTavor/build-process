# Spike: does the desktop app call mlmd's WorktreeCreate hook?

- **Assumption:** A3 in [assumptions.md](../assumptions.md).
- **Question:** when a session starts with the desktop app's worktree option, does the app call
  the project's WorktreeCreate hook? And do the session's diff, the sync with the base branch and
  archiving still work with a worktree the hook made beside the repository?
- **What would be a no:** the app makes its own worktree without calling the hook.
- **Where it runs:** the Claude desktop app, in a throwaway repository whose hook writes a log
  line every time it runs. Only the operator can start a desktop session there, so the operator
  clicks and the log shows what happened.
- **Scripts:** [desktop-worktree-hook/](desktop-worktree-hook/).

## What was done

**Setup.** `sh desktop-worktree-hook/setup.sh` made a throwaway repository,
`~/Documents/Alex/mlmd-spike-desktop`, with one commit on main and no remote. Its
`.claude/settings.json` has three hooks, and each writes a line to
`~/Documents/Alex/mlmd-spike-desktop.log`:
- WorktreeCreate logs its input, creates the worktree beside the repository on a new branch from
  main, and prints the path;
- WorktreeRemove logs its input and removes the worktree folder;
- SessionStart logs where the session started.

Before the real run, the hooks were run by hand in a scratch copy, with their JSON input piped in.
They created and removed a worktree beside the repository and logged each step.

**Attempt 1, 2026-09-30, desktop app on Claude Code 2.1.284** (the transcript's `version` field;
entrypoint `claude-desktop`). The operator started a session in the repository and asked it to run
`pwd` and `git branch --show-current` and to create `hello.txt`. The results:
- The log has one line, a SessionStart with `cwd` set to the repository itself. There is no
  WorktreeCreate and no WorktreeRemove.
- The session ran `pwd` in the repository and was on `main`. It wrote `hello.txt` into the
  repository, where it is untracked.
- `git worktree list` shows only the repository, and there is no `.claude/worktrees/` folder.
- The app's session record (`get_session`) has no worktree fields. A worktree session from the app
  in robotics-lms has `worktreePath`, `worktreeName` and `sourceBranch`.

This session didn't run in a worktree, so the attempt says nothing about the hook yet. The cause:
the new-session dialog has a worktree checkbox, and it wasn't checked (operator, 2026-09-30). A
second attempt, with the checkbox checked, follows.

**Attempt 2, 2026-09-30, same app, worktree checkbox checked.** The session didn't start. The app
showed this error (copied by the operator):

```
WorktreeCreate hook failed: "$CLAUDE_PROJECT_DIR"/.claude/hooks/worktree-create.sh: shell-init: error retrieving current directory: getcwd: cannot access parent directories: Operation not permitted
shell-init: error retrieving current directory: getcwd: cannot access parent directories: Operation not permitted
/bin/sh: /Users/alextavor/Documents/Alex/mlmd-spike-desktop/.claude/hooks/worktree-create.sh: Operation not permitted
```

The log has no new line, `git worktree list` shows no new worktree, and there is no
`.claude/worktrees/` folder. Two things follow:
- The desktop app does call the WorktreeCreate hook from its worktree checkbox. The error names the
  hook.
- The process that runs the hook isn't allowed into `~/Documents`. It can't read its own working
  folder (`getcwd`) or the script, and both fail with "Operation not permitted", which is how macOS
  refuses access to a protected folder. Sessions themselves work in `~/Documents`: attempt 1's
  SessionStart hook ran from the same folder and wrote its line.

**Attempt 3** uses the same setup outside `~/Documents`, in `~/mlmd-spike-home`, to tell apart "the
hook's process can't reach `~/Documents`" from "the hook can't run from the app at all".

**Reported by another tester, 2026-09-30, not reproduced here.** A session can offer a new
session as a one-click card. The tester reported:
- the new session gets its own worktree under `.claude/worktrees/<name>`, on branch
  `claude/<name>`;
- the worktree is made from the latest commit on the current branch;
- the new session sees only committed files;
- the new session can offer the next session the same way;
- the card appears only if the offering session is working in the same project folder;
- no tool is available to start a session directly.

Not yet known: whether this path calls the project's WorktreeCreate hook, and whether "the same
project folder" includes a session working in a worktree beside the repository.

## Verdict

*Not yet run.*
