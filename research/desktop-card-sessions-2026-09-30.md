# Sessions started from a one-click card in the desktop app (2026-09-30)

The evidence behind the tester's report in
[docs/spikes/desktop-worktree-hook.md](../docs/spikes/desktop-worktree-hook.md). Run by Frank
Verbruggen on Windows 10, in the Claude desktop app (Code tab).

## Sources

- The repository `claude-boot` (local, no remote), branch `draft/requirements`, commit `1a7168c`.
- The offering session: the requirements session for mlmd, which called the app's `spawn_task`
  tool to offer a card.
- The probe session `local_097112a8-0158-489e-a5c5-526fdc33002a`, titled "Probe Boot session
  handoff (OQ-13)", started from the card by the operator. Archived after the run; its transcript
  holds the output quoted below.

## What was done

A session offers a new session as a card with `spawn_task`, which takes a title, a short
description, the new session's first prompt and, optionally, a folder. The probe's prompt asked it
to report its folder, branch, worktree state and starting commit, and which session-starting tools
it could see, and to change nothing.

1. **Attempts 1 and 2**, offering session working in another project folder (`mtg-judge`): once
   with `cwd` set to `claude-boot`, once with no `cwd`. The tool answered that a card was showing
   both times. The operator saw no card, in the chat or in the Tasks pane.
2. **Attempt 3**, offering session working in `claude-boot` itself, no `cwd`. The card appeared,
   and one click started the probe session.

## What the probe reported

- Folder `claude-boot\.claude\worktrees\dazzling-hawking-4bda1f`, branch
  `claude/dazzling-hawking-4bda1f`.
- A worktree: `git rev-parse --git-dir` gave `.git/worktrees/dazzling-hawking-4bda1f`, and
  `--git-common-dir` gave `.git`.
- It started from `1a7168c`, the latest commit on `draft/requirements`, the branch the offering
  session was on. The committed files were there.
- `spawn_task` was available to it. `start_session` and `hand_off_to_session`, which other session
  tools mention, were not.

## What it shows

- A card appears only when the offering session works in the card's project folder. With another
  folder, the tool reports success and nothing is shown.
- The new session runs in its own worktree under `.claude/worktrees/`, on a new `claude/` branch
  cut from the offering session's current branch, so it sees committed work only.
- A session started from a card can offer the next card itself.
- No tool was found that starts a session without the operator's click.

Not checked: whether a project's WorktreeCreate hook is called for a card's worktree. The
probe's repository had no hook.

## Cleanup

The worktree could not be removed while its session was open (`Permission denied` on Windows).
Archiving the session released it; then `git worktree prune`, the branch deleted, and the empty
folder removed.
