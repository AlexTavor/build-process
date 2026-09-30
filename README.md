# mlmd

mlmd is a way of building software with a coding agent, written down as a process, together with a
Claude Code plugin that runs the process for you.

It's for developers who know how to build software but haven't built much with an agent. It
leaves out the engineering you already know, and covers what changes when an agent writes the
code. It's for building something new. To change an existing codebase you didn't write, see
[Proof-Driven Development](https://github.com/AlexTavor/proof-driven-development).

> **Status:** the process is a working draft ([process.md](process.md)). The plugin isn't built
> yet, so the commands below describe how it will work. Until it exists, you can follow the
> process by hand (see [Using it today](#using-it-today)).

## What changes when an agent writes the code

- **The work looks finished whether or not it's right.** The agent's reports ("all tests pass")
  come from the same session that did the work. So in mlmd, work is checked by a fresh session or
  by a script, never taken on the agent's word. In one project, reviews by fresh sessions found 11
  of its 15 most consequential defects, for about 15% of its tokens.
- **The agent fills every gap with a plausible choice, and states it as settled.** So every
  decision is marked with who made it, you read the ones the agent made, and anything undecided
  goes into a list of open questions instead of into the design.
- **A session starts with nothing but what's written down.** So the project lives in documents
  that every session reads and keeps current: the vision, the behaviors, the rules, the glossary,
  the known traps and the assumptions.
- **Rules the agent is only told about don't hold.** In one project, 1,472 reminders to apply a
  practice led the agent to open it 10 times. So a rule that matters is a check that fails, and
  every rule says what enforces it.
- **Tests the agent writes can pass without testing anything.** One set of removal tests passed on
  code that removed nothing. So before a merge, a fresh session attacks the tests ("which wrong
  implementation passes these?"), and at the end of each batch, mutation testing grades them.

## How it works

A project goes through these phases. Each one runs in its own Claude Code session and ends by
writing its results to files.

| Phase | What happens | What you do |
| --- | --- | --- |
| 1a | The Vision: the whole product, and which MVP each feature belongs to | Answer the interview, decide |
| 1b | An MVP: what it's for, its behaviors, and behavior tests in Gherkin | Keep it small |
| 1.5 | The questions that change behavior but not the architecture | Rule on the defaults |
| 2 | The architecture, then the stack | Walk each behavior through the architecture |
| 3 | Spikes for the risky assumptions | Read the verdicts |
| 4 | The build plan: work items in batches, with their dependencies | Read the plan |
| 5 | A design for each batch that changes the architecture | Answer its questions |
| 6 | Each work item: design, review, code, attack, merge | Approve the stops you kept |
| 7 | The end of a batch: mutation testing and a reading pass | Use what was built |
| 8 | The end of an MVP: its verdict, and a release | Give the verdict |

Each later MVP runs phases 1b to 8 again. [process.md](process.md) has every phase in full: what to
ask for, when it's done, and why it's there.

## Using mlmd

*Planned: the plugin isn't built yet.*

You need Claude Code (the CLI or the desktop app) and git. mlmd installs the rest itself.

**Install, once per machine:**

```
/plugin marketplace add AlexTavor/mlmd
/plugin install mlmd@mlmd
```

The first session after that installs what mlmd needs, in the background:
[uv](https://docs.astral.sh/uv/) if it's missing, and [dod](https://github.com/AlexTavor/dod),
which draws the plan. It installs nothing that needs admin rights or runs at login.

**Start a project:** in an empty folder, run `/mlmd:start`. It sets up the repository, the
documents, the plan, the trust settings and the hooks, then starts the interview about your
product.

**Everything after that:** each session opens with a status line showing what's done, what's
ready, what's waiting for you, and the address of the plan view. Then do one of these:
- start a new worktree session (the desktop app's worktree option, or `claude --worktree`), and
  mlmd gives it the next ready item;
- in a session in the project folder, run `/clear` and then `/mlmd:next`.

Say go, and the session does the item. To work on several items at once, start more sessions.
Each one takes a different item.

| Command | What it does |
| --- | --- |
| `/mlmd:start` | Sets up a new project in the current folder |
| `/mlmd:next` | Shows where the project stands, and does the next ready item |
| `/mlmd:status` | Shows the plan in the chat |
| `/mlmd:trust` | Shows and changes which steps wait for you |
| `/mlmd:release` | Tags and deploys a release |

**What you do:** answer the interviews, decide what comes to you as a question, try what's built
when an item asks you to, approve the stops you kept, and give each MVP its verdict.

**What you don't do:** keep status, track which phase you're in, make branches or worktrees, run
merges, or remember to run reviews. The first time a step runs in a project, the session tells you
in one line why the step exists.

## Trust

Five settings decide which steps wait for you:

- accepting an item's design before its code is written;
- using a finished batch before the next one starts;
- merging an item;
- pushing to origin;
- releasing.

A new project starts with all five on. Turn one off when its stops have stopped finding anything.
An operation that can't be undone on real data, such as a migration against production, always
waits for you, whatever the settings say.

## Seeing progress

The plan is one file, `.pdd/plan.json`. dod draws it as a dependency graph: what's done, what's in
progress, what's ready, what's waiting for you, and what can run in parallel. Status will come from
git, so a merged item shows as done and nobody has to keep the plan up to date. dod doesn't read
status from git yet.

## Using it today

Until the plugin exists, you can run the process by hand with Claude Code:

1. Make a folder and a git repository for the project.
2. Put [process.md](process.md) where your sessions can read it. Start with phase 1a: tell the
   session to read it and interview you for the Vision.
3. For each review, start a fresh session, give it the document, and ask it the questions the phase
   lists.
4. Merge with the procedure in process.md's Git section.

You'll be doing by hand what the plugin will do for you: the status, the worktrees, the merges and
remembering each review.

## This repository

- [process.md](process.md): the process in full.
- [research/](research/): the evidence it's drawn from.
- [docs/](docs/): how mlmd itself is being built: its assumptions, its spikes and their results,
  and the traps found on the way.
- [UNHANDLED_ISSUES.md](UNHANDLED_ISSUES.md): known issues not yet handled.

## Where it comes from

A year of solo work with Claude Code on codebases of up to about 200,000 lines: several games, a
web product, and a school's learning platform rewritten over its live data. Nothing here has been
tried with a team.

## License

MIT. See [LICENSE](LICENSE).
