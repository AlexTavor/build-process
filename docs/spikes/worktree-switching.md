# Spike: can a session move from one item's worktree to the next?

- **Assumption:** A2 in [assumptions.md](../assumptions.md).
- **Question:** a session starts in the project folder. Can it enter an item's worktree made
  beside the repository (EnterWorktree with a path), then move into the next item's worktree,
  either directly or by leaving the first one (ExitWorktree) and entering the second? Does that
  still work after `/clear`? And does EnterWorktree with a name call the project's WorktreeCreate
  hook?
- **What would be a no:** the move into the second worktree is refused in every sequence tried.
- **Where it runs:** Claude Code itself, in a throwaway repository with worktrees beside it.
  Headless runs (`claude -p`) cover the tool sequences. `/clear` exists only in an interactive
  session, so that case is checked by hand.
- **Scripts:** [worktree-switching/](worktree-switching/).

## What was done

Run on 2026-09-30, on macOS, with two Claude Code versions:

- **2.1.165**: the `claude` on PATH (`/opt/homebrew/bin/claude`). `claude --version` printed
  `2.1.165 (Claude Code)`.
- **2.1.284**: the CLI inside the desktop app
  (`~/Library/Application Support/Claude/claude-code/2.1.284/claude.app/Contents/MacOS/claude`),
  the version the app was running.

**Setup.** `setup.sh <dir>` makes `toy` with one commit on `main`, a local bare origin, and two
worktrees beside it, `toy-worktrees/w1-a` and `toy-worktrees/w2-b`, each on its own branch from
`main`. The origin was added because EnterWorktree with a name branches from `origin/main` by
default. `spike.py <sequence> <dir>` makes a fresh copy for each run and starts `claude -p` inside
`toy` with `--input-format stream-json --output-format stream-json --verbose --include-hook-events
--setting-sources project,local --permission-mode acceptEdits --allowedTools
ToolSearch,EnterWorktree,ExitWorktree,Bash(pwd),Bash(git branch:*),Bash(git worktree list:*)`.
After every move the session runs `pwd; git branch --show-current; git worktree list` with its
Bash tool. The script then prints `git worktree list` and the hook logs. Each run's raw output is
kept as `out.jsonl` in its run folder.

**Change to the method: no model.** Every `claude -p` run with the model failed with
`Failed to authenticate. API Error: 401 OAuth access token is invalid.`, on both versions, with
the inherited and with a clean environment. So `spike.py` points the CLI at a fake Messages API
on 127.0.0.1 that answers with the sequence's tool calls in order. The init line of every such run
shows `apiKeySource=ANTHROPIC_API_KEY`, the fake key. Everything else is Claude Code's own code: the
checks in EnterWorktree and ExitWorktree, the hooks, the permission questions and `/clear`. It
costs no tokens, so every sequence ran on both versions: 34 runs against the fake API, and 5
attempts with the model, all refused with the 401. Whether the model itself calls the tools as
asked was not tested. `spike.py --real` gives the same calls to the model as numbered
instructions.

**Questions and `/clear`.** `/clear` was sent as a user message on stream-json input. The desktop
app runs its CLI with the same input format: `ps` showed the app's CLI running with
`--input-format stream-json --permission-prompt-tool stdio --permission-mode auto`. With
`--approve`, `spike.py` passes `--permission-prompt-tool stdio` and answers yes to every
permission question, as the owner would in the app. Without it, `-p` refuses whatever asks.

**Added sequences.** f uses worktrees made with `git worktree add` under `toy/.claude/worktrees/`.
g is the `/clear` case. h adds a PreToolUse hook that returns allow for EnterWorktree
(`settings-allow.json`, `allow-enter.sh`). i enters by name through the WorktreeCreate hook
(`settings.json`, `worktree-create.sh`). That hook makes the worktree beside the repository, or
prints the existing one's path when its folder is already there.

"Entered" below means the next `pwd` printed that worktree and `git branch --show-current` printed
its branch. `<toy>` is the repository and `<wt>` is `toy-worktrees`.

| Seq | Steps | 2.1.165 | 2.1.284 |
|---|---|---|---|
| a | EnterWorktree path=w1-a, then path=w2-b | w1-a entered. w2-b refused: `Cannot enter worktree: <toy>/.claude/worktrees does not exist, so <wt>/w2-b cannot be a worktree managed by Claude Code.` The session stayed in w1-a. | Each call first asks: `Enter the worktree at "<path>"? This moves the session's working directory and write access there, and loads project configuration (CLAUDE.md, settings) from that location.` The question is a safety check for "a model-supplied worktree outside .claude/worktrees/". With no answer both calls are refused. Answered yes: same as 2.1.165. |
| b | path=w1-a, ExitWorktree keep, path=w2-b | Works. After the exit `pwd` is `<toy>` on `main`. Then w2-b entered. | Answered yes: works, with one question per entry. With no answer both entries are refused, and the exit returns `No-op: there is no active EnterWorktree session to exit.` |
| c | EnterWorktree name=w3, then path=w2-b | w3 made at `<toy>/.claude/worktrees/w3` on branch `worktree-w3` and entered. w2-b refused: `Cannot enter worktree: <wt>/w2-b is not under <toy>/.claude/worktrees. Switching from this session is limited to worktrees managed by Claude Code (created under .claude/worktrees/ of this repository).` | Same, after the question for w2-b. `git worktree list` shows w3 as `locked`. |
| d | WorktreeCreate hook; name=w4, then path=w2-b | The hook ran: one line in `hook.log` with `"name":"w4"`. w4 made at `<wt>/w4` on branch `w4` and entered. w2-b refused with the text from a. | Same. No question for w4. The question comes for w2-b, then the same refusal. |
| e | WorktreeCreate hook; `claude -p --worktree w5` | The hook ran. The session started in `<wt>/w5` on `w5`. | Same. |
| f | w6-c and w7-d made with `git worktree add` under `<toy>/.claude/worktrees/`; path=w6-c, then path=w7-d | Both entered. The direct switch works. | Same, with no question. |
| g | path=w1-a; `/clear`; path=w2-b; ExitWorktree keep; path=w2-b | After `/clear` the session id is new and `pwd` is still w1-a. The direct move is refused with the text from a. ExitWorktree keep works and returns to `<toy>`. Then w2-b entered. | Answered yes: same as 2.1.165. |
| h | b, with a PreToolUse hook that returns allow for EnterWorktree | Not run: 2.1.165 asks no question. | The hook ran and returned allow, and each entry still asked. With no answer both entries were refused. |
| i | WorktreeCreate hook; name=w1-a; `/clear`; ExitWorktree keep; name=w2-b (both already exist) | Works. The hook ran twice and printed the existing folders. `pwd`: w1-a, still w1-a after `/clear`, `<toy>` after the exit, then w2-b. | Same, with no question at any step. Also the same in auto mode. |

Other observations:

- On 2.1.284, sequence a in bypassPermissions mode asked nothing: w1-a entered, w2-b refused as
  in a. In auto mode the question still went to the owner, and the fake API received no
  classifier request.
- The WorktreeCreate hook's input had `session_id`, `transcript_path`, `cwd`, `hook_event_name`
  and `name`, and 2.1.284 adds `prompt_id`. There was no `base_ref` and no `isolation`, for
  EnterWorktree with a name and for `--worktree`.
- Worktrees made during a `-p` session were still there after the session ended.

## Verdict

**Yes, with one condition.** A session cannot move straight from one worktree beside the
repository into another. Once it is in a worktree, EnterWorktree with a path accepts only targets
under `<repo>/.claude/worktrees/` (a, c, d, on both versions). It can move by leaving first:
ExitWorktree with action keep, then EnterWorktree (b). That still works after `/clear`. The
session stays in the worktree, and ExitWorktree still takes it back to the project folder (g, i).
That `/clear` was sent headless, on the stream-json input the desktop app also uses. Whether the
app's own `/clear` and the terminal's `/clear` behave the same was not checked. The steps for that
are below.

The two ways in differ on 2.1.284, the version the desktop app runs. EnterWorktree with a path
outside `.claude/worktrees/` asks the owner on every entry. An allow rule for EnterWorktree does
not stop the question, and neither does a PreToolUse hook that returns allow (h). Of the modes
tried (acceptEdits, auto, bypassPermissions), only bypassPermissions skipped it. **EnterWorktree
with a name goes through the project's WorktreeCreate hook** (d, i, on both versions), as
`--worktree` does (e). The worktree the hook returns is entered with no question, even though it
is beside the repository.

What it means for mlmd:

- Worktrees stay beside the repository. Moving them under `.claude/worktrees/` is not needed, and
  neither is a new session per item.
- The loop is sequence i, and it works on both versions with no question. After `/clear`,
  `/mlmd:next` calls ExitWorktree with action keep, then EnterWorktree with the item's worktree
  name. mlmd's WorktreeCreate hook makes the worktree beside the repository, or prints the
  existing worktree's path when its folder is already there.
- In a session that is not in a worktree, ExitWorktree changes nothing and returns
  `No-op: there is no active EnterWorktree session to exit.` (seen on 2.1.284). So `/mlmd:next`
  can call it every time.
- EnterWorktree with a path also works after ExitWorktree, but on 2.1.284 the owner answers a
  question on every move.
- If worktrees ever move under `.claude/worktrees/`, a direct switch by path works there, with no
  question and no ExitWorktree (f).
- The hook gets the name and `cwd` but no base branch, so it picks the base itself. Worktree names
  must fit EnterWorktree's name rule: segments of letters, digits, dots, underscores and dashes,
  at most 64 characters in all.
- The terminal CLI here is 2.1.165 and the desktop app runs 2.1.284. Only 2.1.284 asks the
  question.

Still open:

- `/clear` typed in an interactive session. The owner's steps are below.
- A run with the real model. After the owner logs in again (`claude auth login`), run
  `spike.py <sequence> <dir> --real`.

**Manual check of `/clear`.** Run from the mlmd repository.

1. In a terminal:

   ```sh
   docs/spikes/worktree-switching/setup.sh /tmp/wt-manual
   mkdir /tmp/wt-manual/toy/.claude
   cp docs/spikes/worktree-switching/settings.json docs/spikes/worktree-switching/worktree-create.sh /tmp/wt-manual/toy/.claude/
   cd /tmp/wt-manual/toy && claude --version && claude
   ```

   Trust the folder when asked, so the project's hook can run.
2. Ask: "Work in a worktree: use the EnterWorktree tool with name w1-a, then run pwd and
   git branch --show-current." Expected: `/private/tmp/wt-manual/toy-worktrees/w1-a` and `w1-a`.
3. Type `/clear`.
4. Ask: "Run pwd. Then use the EnterWorktree tool with path
   /private/tmp/wt-manual/toy-worktrees/w2-b." Write down the `pwd` and the exact result.
   Headless, `pwd` was still w1-a and the move was refused.
5. Ask: "Use the ExitWorktree tool with action keep and run pwd. Then use the EnterWorktree tool
   with name w2-b and run pwd and git branch --show-current." Headless, this printed `toy`, then
   `toy-worktrees/w2-b` and `w2-b`.
6. Write down any permission question, and the output of `cat /tmp/wt-manual/hook.log`. It should
   have one line for each EnterWorktree with a name.
7. Repeat steps 2 to 6 in the desktop app, in a session opened on a fresh copy
   (`setup.sh /tmp/wt-manual-app` and the same `.claude` files), with the paths changed to match.
