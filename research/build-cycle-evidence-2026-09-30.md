# Evidence for the build cycle, git and observability (2026-09-30)

Gathered for the discussion of skills and workflows, the HLD to LLD to implementation cycle,
observability of the process, and git handling.

## Checked on 2026-09-30

1. **`git push . HEAD:main` runs the pre-push hook.** Tested in a scratch repository. The hook
   received remote `.` and the line `HEAD -> refs/heads/main`. When it exited 1, main stayed where
   it was. So a pre-push hook on `refs/heads/main` gates the local merge procedure (build the merge
   on a detached HEAD, then `git push . HEAD:main`) as well as pushes to origin.
2. **The Claude Code desktop app puts its worktrees inside the repository**, under
   `.claude/worktrees/`. robotics-lms has three there and unshatter two. robotics-lms had to add
   `.claude` to its ESLint ignores (`eslint.config.js:15`) and to Stryker's ignore list
   (`stryker.config.json:24`). Its own script puts worktrees beside the repository instead.
3. **robotics-lms `tools/worktree.sh`:**
   - cuts branch `claude/<name>` from main;
   - refuses when origin/main has commits that local main lacks;
   - runs `npm ci` in the new worktree. Its comment: "A worktree with no node_modules cannot run a
     single gate, so the pre-push hook would fail on it and the failure would read as a code
     problem";
   - finds the worktree home from the common git directory, not `--show-toplevel`. Using the
     second would nest the next worktree inside the current one, "a bug skyline's version had
     twice";
   - places worktrees beside the checkout because "one nested inside the repo is what stryker
     would copy into its sandbox".
4. **Session history is kept per worktree folder.** robotics-lms has 10 worktree folders under
   `~/.claude/projects/`. The one transcript checked from an app worktree
   (`...robotics-lms--claude-worktrees-festive-liskov-bf5a6c`) loaded the main folder's
   `MEMORY.md`, so auto memory was not split per worktree there.

## From earlier records

- **Rules as text:** "1,472 reminders to apply a practice were followed by the agent opening that
  practice 10 times" (`~/PersonalKB/drafts/greenfield-process.md`, "What to leave out").
- **Fresh-session reviews** found 11 of one project's 15 most consequential defects, for about 15% of
  its tokens. Nine of the ten largest code defects they found were in code that takes outside
  input, stores data, or does something that can't be undone (same file, step 5).
- **A merge hook skipped 5 of 8 merges**, all of them merges committed by hand after a conflict
  (same file, step 4).
- **tiny:**
  - the plan's status went stale (2026-09-20, 2026-09-23);
  - on 2026-09-19 the owner stopped per-item sign-off: "No point is stopping for each work unit.
    Go through the plan to completion";
  - 159 design-review findings were recorded, every one marked taken;
  - on 2026-09-21 the owner asked what a review was spending tokens on.

  Source: `~/PersonalKB/workflow-codification-2026-09-26.md`, evidence 2 and 3.
- **robotics-lms:**
  - status moves at two events, LLD written and PR merged, but is written by hand. So the plan
    needs a copy ritual between main and the worktrees (`.pdd/constitution.md`);
  - a merge happens only on the owner's word, and main is the deployed tree (`CLAUDE.md`, branch
    model);
  - its phase HLDs run 93 to 768 lines (`docs/hld-p*.md`).
- **engineering-discipline's 23 skills** have broad descriptions and overlap with other skill sets
  at planning and at the start of risky work (`~/PersonalKB/drafts/superpowers-layer-plan.md`,
  v0 step 2). The same plan proposed a PreToolUse hook that refuses `--no-verify` (Build 0).

## Added later on 2026-09-30

- **Plugins can carry workflows.** From https://code.claude.com/docs/en/workflows.md, "Distribute a
  workflow in a plugin": the script goes in a `workflows/` directory at the plugin root, or in a
  location named by the `workflows` manifest field. Plugin workflows are namespaced by the plugin
  name: a plugin `acme-tools` with a script whose `meta.name` is `release-audit` runs as
  `/acme-tools:release-audit`. Project workflows in `.claude/workflows/` are shared with everyone
  who clones the repository. No plugin installed here uses the `workflows/` directory yet.
- **unshatter** merges into main on the owner's word, one word for a whole stack of work. Merge
  `fe29a26` covers milestones M18 to M27 (W157 to W236), "(owner, 2026-09-30: 'Merge into main and
  push')". Its plan marks some milestones "Owner stop" in their exit criteria (M1, M4, M5) and not
  the others. A Claude Code PreToolUse hook (`tools/merge-gate.mjs`) refuses `git merge` and
  `git push` while its registers no longer describe the tree.
- **dod's plan view** (`dod/src/dod/plankit.py`, `planspec.py`) reads `.pdd/plan.json` in PDD's
  vocabulary:
  - top level: `title`, `phases` (id, name, goal, exit_criteria), `tracks`, `items`;
  - items: id, title, phase, track, depends_on, size, risk, status, note;
  - it also reads an optional `delivers` list;
  - statuses: pending, in-progress, blocked, done, plus aliases.

  It re-reads the file on every poll and never writes to the repository. It draws the dependency
  graph and lists the ready items, the critical path and the maximum concurrency. It also flags
  dangling dependencies and cycles. robotics-lms (54 items, 15 phases) and unshatter (144 items,
  14 milestones) both use this shape.
- **dod and proof-driven-development are public** on GitHub (checked through the API).
- **How dod finds and serves plans** (`dod/README.md`, `src/dod/providers/pdd.py`, `daemon.py`,
  `~/.dod/providers/pdd.json`, `dod ls`, 2026-09-30):
  - The PDD provider treats a folder as a PDD repo when its `.pdd/` holds `config.yaml` or
    `constitution.md`. Its plan-graph view ("dag") needs no Node and no PDD CLI.
  - Projects are added by hand as `roots` in `~/.dod/providers/pdd.json`. Today that lists
    robotics-lms and tiny, with `max_depth` 0. unshatter registers through a `dod.project.json`
    that names an absolute path to the owner's dod install, and the file is git-excluded.
  - `dod ls` lists a second plan dashboard for an unshatter worktree ("unshatter-clicker-plan", "wt
    plan") beside "unshatter-plan". The ten milestones merged on 2026-09-30 had lived on a branch.
  - The always-on daemon is a launchd agent, so macOS only. dod's runtime is standard-library
    Python run through uv. The README says a kit "also serves its spec standalone, so the dashboard
    works opened directly". Nothing was tested outside macOS.
- **Claude Code's EnterWorktree tool** (its tool description, read 2026-09-30):
  - With `name`, it creates a worktree under `.claude/worktrees/` on a new branch, based on
    origin's default branch unless `worktree.baseRef` is `head`.
  - With `path`, it moves the session into an existing worktree. On the first entry from the
    launch directory, the worktree only has to appear in `git worktree list`, so one made beside
    the repository qualifies. When the session is already in a worktree, a switch must target one
    under `.claude/worktrees/`. Whether a session can move from one worktree beside the repository
    to another, for example after `/clear`, is untested.
  - ExitWorktree does not remove a worktree that was entered by `path`.
  - The tool is used only when the user or CLAUDE.md asks for worktrees.
- **Installing what a plugin needs.** Sources: https://code.claude.com/docs/en/hooks.md and
  https://code.claude.com/docs/en/plugins-reference.md, read 2026-09-30.
  - No hook event fires when a plugin is installed, enabled or updated. `Setup` fires only with
    `--init-only`, or with `--init` or `--maintenance` in `-p` mode.
  - The hooks page gives the pattern: "check for the dependency on first use and install on miss",
    for example a hook that tests for `${CLAUDE_PLUGIN_DATA}/node_modules`.
  - `${CLAUDE_PLUGIN_DATA}` is `~/.claude/plugins/data/<id>/`. It is kept across plugin updates and
    deleted on uninstall.
  - Files in a plugin's `bin/` are on the Bash tool's PATH while the plugin is enabled.
  - Command hooks time out after 600 seconds by default. `async: true` runs a hook in the
    background, and `asyncRewake: true` wakes Claude when the hook exits with code 2.
  - SessionStart fires on `startup`, `resume`, `clear`, `compact` and `fork`. Its `systemMessage` is
    shown to the user, while `additionalContext` and plain stdout go to Claude's context.
- **What dod needs to run.** From `dod/pyproject.toml` and its git tree: Python 3.10 or later
  (`requires-python = ">=3.10"`), no runtime dependencies ("stdlib-only by design"), and a web UI
  that is committed already built (`src/dod/web/*.js`). This Mac's `/usr/bin/python3` is 3.9.6, too
  old for dod.
- **The WorktreeCreate hook.** Source: https://code.claude.com/docs/en/hooks.md, read 2026-09-30.
  - It fires when a worktree is created via `--worktree`, a subagent with `isolation: "worktree"`,
    or a background session, and "replaces default git behavior".
  - Its input includes `name`, `cwd`, `base_ref` and `isolation`. Its stdout must contain only the
    created worktree's path, and any non-zero exit fails the creation.
  - WorktreeRemove fires at session exit, when a subagent finishes, and when a background session
    is deleted.
  - The page doesn't say whether the desktop app's own worktree sessions trigger the hook.
