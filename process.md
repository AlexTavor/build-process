# Building software with a coding agent

*Draft, 2026-09-29, revised 2026-09-30. Replaces the Superpowers plan
(`~/PersonalKB/drafts/superpowers-layer-plan.md`). Covers requirements through release. The
document forms follow robotics-lms (`research/robotics-lms-process-2026-09-30.md`). The Vision and
the PRD per MVP follow RUP's Vision and iteration plans. The evidence for the build phases is in
`research/build-cycle-evidence-2026-09-30.md`.*

For developers who know how to build software and have not built much with an agent.

## Words

- **Phase:** a step of this process, 1a to 8.
- **MVP:** one increment of the product, with its own PRD and verdict. Each MVP runs phases 1b to 8.
- **Batch:** a group of work items in an MVP's plan, with a goal and exit criteria.
- **Work item:** one unit of work in the plan, done on its own branch.
- **Your items:** plan items only you can close: an MVP's verdict, a stop the trust level asks for.
- **Fresh session:** a session that did not write the work it is given, started from the documents.
- **The gates:** the checks that run before main moves.

## 0. Sessions

Each phase runs in its own session, and so does each spike and each work item. A session ends by
writing its output files. The next session starts by reading only those files, not the previous
conversation.

Start a new session when the phase changes, or when a spike, a work item or a review finishes.
Don't carry one conversation across phases: whatever it holds that isn't in a file is lost to every
later session.

A session works in the worktree of the item it is on (see Git), and starts with the plan view open
(see The plan).

## Documents

The agent writes the documents and keeps them current. They are how one session's findings reach
the next.

Documents change in any phase. When work turns up a change to a behavior, a rule, a term or an
assumption, the document changes in the same commit as that work. Most product decisions will
arrive after phase 1, while later work is being designed.

### Product documents

Three documents describe the product. Each answers one question.

**`docs/vision.md`: where the whole product is going.** Written in phase 1, and revised when an
MVP's verdict changes the direction. It holds:
- the problem, the users, the core;
- every feature, in a line or a short paragraph, marked with the MVP it belongs to, or with none
  yet;
- the constraints and quality levels that hold across the product: devices, speed, privacy,
  languages;
- the later features the architecture must keep possible, each with what it needs from the
  architecture.

It has no behaviors and no scenarios. A feature gets its detail when an MVP takes it on.

**`docs/behaviors.md`: what the product does.** One living spec of every behavior that is built or
being built. Behaviors are numbered across the whole product (B1, B2), and an id is never reused.
Each behavior has:
- a paragraph stating its contract: inputs, outputs, what stays true;
- a **Failure** line: what can go wrong, and what happens then;
- an **Edges** line: boundary, empty, zero and maximum cases;
- the MVP that introduced it.

A later MVP that changes a behavior edits it here, marked with who changed it and when. Git keeps
the old text.

**`docs/prd/mvp-N.md`: what this MVP is for.** One per MVP, and short:
- what the MVP is for, and what result would be a no;
- the behaviors it adds or changes, by id, one line each;
- its decisions, each marked with who made it and when. Its open questions stay in
  open-questions.md, with this MVP under "needed by";
- after it ships, its verdict. From then on it is a record and isn't edited.

**What the Vision may be used for.** The architecture may cite the Vision to keep a later feature
possible, when that costs little now and would cost a lot later. Each such choice is a decision in
architecture.md, with its cost. Nothing is built for a feature outside the current MVP: no code,
no abstraction, no scenario. Storing all data under an organization key in a product with one
customer, because a later feature serves several, is the first kind. A screen for choosing an
organization is the second.

### Standing documents

Phase 1 creates all of these, including the ones that start empty.

**`CLAUDE.md`** (project root). Claude Code loads this file into every session automatically. No
other file is loaded unless something asks for it. It holds:
- what the project is, in a few lines;
- the reading order for the other documents: vision.md, behaviors.md and the current MVP's PRD;
  open-questions.md before proposing anything; assumptions.md before relying on anything the
  documents state as fact; architecture.md before changing structure. Earlier MVPs' PRDs are
  records: read them for why something was decided, not for what the product does;
- the instruction to update the documents whenever the session finds a decision, rule, term,
  trap, assumption or issue;
- **Claims:** nothing is stated as fact unless it was read or run in the current session. A name,
  a file name or a search hit is a lead, not a fact. The agent reports what it guessed as
  confidently as what it checked, and this rule is what makes it check;
- the **Trust** section (see Trust);
- three imports, each on its own line: `@docs/rules.md`, `@docs/glossary.md`, `@docs/footguns.md`.

An import pulls its file into every session, so rules and terms apply without anyone remembering
to read them. A rule in a file that no session loads is not followed. Imports cost context in
every session, so if one of these files grows long, split it by area.

**`docs/rules.md`**. The standing rules every session follows, whatever its task. Numbered (R1,
R2). Each rule has:
- **Says:** the rule.
- **From:** why it exists: a decision, or what went wrong without it.
- **Tier**, one of three:
  - **Gated:** a script fails when the rule is broken. It names the script.
  - **Reviewed:** a person checks it. It says so, and names when the check happens.
  - **Registered:** a file must exist and be current. It names the file. The check is that the
    file exists, not the judgement inside it.

Phase 1 rules come from your constraints ("no data leaves the device", "no new dependency without
a decision"). Phase 2 adds the architecture's (module boundaries, such as "the simulation imports
nothing from the view"). The product's own rules, such as a game's rules or business rules, don't
go here. They are behaviors in behaviors.md.

**`docs/glossary.md`**. Every term with a specific meaning in this project: one meaning each, and
the words not to use for it ("member; not user, customer or account"). A term means exactly this
in every document, identifier, test name, commit message and conversation. The agent drifts
between synonyms, and readers take two words for two things. Terms go in during the phase 1
interview as they come up. Phase 2 adds the names of the architecture's parts.

When a term's meaning changes, or it is replaced, it moves to a **Retired** section. Retired terms
are barred from new prose, identifiers and tests.

**`docs/footguns.md`**. Traps: something that looks like it does one thing and does another. They
can be in a library, an API, the platform, the domain, the test tools, and later the project's own
code. Example: a model whose documentation recommends a runtime that is CPU-only on Apple Silicon,
and 25 times slower there. One table:

| # | Looks like | Actually | Anchor | Verified |
| --- | --- | --- | --- | --- |

The Anchor is a link or a `file:line`. Verified is the date it was last checked. An entry is
removed when the trap is gone, not when it is understood. In phase 1 footguns come from research
and the cheapest prototype, so on a new project the file often starts empty. Spikes are the main
source.

**`docs/assumptions.md`**. Beliefs the design stands on that nobody proved. One table:

| # | Assumption | Falsified if | Detector / verify by | Fragility | Fallback |
| --- | --- | --- | --- | --- | --- |

Fragility is **high** when the design bends if the assumption is wrong, and **low** when a setting
changes. A high-fragility assumption gets a spike, or a decision that makes it not matter, before
anything is built on it (phase 3). A check that is waived is written into its entry, with what
stands in for it. Otherwise the entry reads as work still to do. Phase 1 adds beliefs about users,
the environment and the data. Phase 2 adds beliefs about scale, speed and how dependencies behave.

**`docs/open-questions.md`**. Everything not decided. The product documents and architecture.md
hold decisions only. Each question has:
- its **level** (see Ambiguity levels);
- its **state**. **Proposed:** a default exists, and work proceeds on it until you rule.
  **Deferred:** a decision not to decide yet, with the trigger that reopens it;
- **needed by:** the MVP or the work item that can't go further without an answer.

A settled question moves into the document it belongs in, and is deleted here.

**`UNHANDLED_ISSUES.md`** (project root). Anything found that needs fixing and is outside the
current task. The commit that fixes an issue deletes its entry. Create it together with the line
`UNHANDLED_ISSUES.md merge=union` in `.gitattributes`, so entries appended on different branches
merge without conflicts.

How an issue differs from a footgun: an issue gets fixed and then it's gone. A footgun stays,
because its cause can't be removed (it's in a dependency or the domain) or isn't worth removing.

**`.pdd/plan.json`** and **`.pdd/constitution.md`**: the plan and its rules (see The plan).

## The plan

**`.pdd/plan.json`** is the project's one plan, from the first session to the last. It uses PDD's
vocabulary, so dod can draw it:

```json
{
  "title": "…",
  "batches": [
    {"id": "1-2", "name": "…", "goal": "…", "exit_criteria": "…"}
  ],
  "tracks": ["DATA", "UI"],
  "items": [
    {"id": "W7", "title": "…", "batch": "1-2", "track": "DATA", "depends_on": ["W5"],
     "size": "M", "risk": "low", "delivers": ["B3", "B4"], "note": "…"}
  ]
}
```

- **Batches** are numbered by their MVP: `1-2` is MVP 1's second batch. The first batch of each MVP
  holds its requirement and architecture phases (1b to 3, and 1a for MVP 1), so progress shows
  from the first session.
- **Items** are numbered W1, W2 across the project. An id is never reused: a cut item's number
  stays unused.
- **`depends_on`** means "cannot correctly start until", not the order the plan happens to list
  things in. Leave out a dependency that another one already implies.
- **Sizes** are S, M, L or XL, never times. The agent's time estimates have no basis, and sizes are
  enough to compare items.
- **`delivers`** names the behaviors an item delivers. Every behavior of the current MVP is
  delivered by some item.
- **Your items** carry `"owner": true`: an MVP's verdict, and the stops the trust level asks for.
- **One final item.** Exactly one item has nothing depending on it: the current MVP's verdict. The
  next MVP's first items depend on it.
- **Plan edits reach main in merges of their own.** Work branches never edit plan.json. A plan
  changed on a branch shows only on that branch: robotics-lms and unshatter both ended up keeping a
  second copy of the plan in step by hand.

**Status comes from git.** Nobody writes it, except for one case:
- **done:** a merge commit on main names the item;
- **in progress:** a branch named for the item exists;
- **waiting for you:** one of your items whose dependencies are all done;
- **blocked:** the one status written by hand, in the item's `status`, with a note saying what it
  waits for;
- **pending:** everything else.

Hand-kept status went stale in tiny twice. robotics-lms moved status at two events only, the LLD
written and the merge, and still needed a copy ritual between main and its worktrees. Both of its
events are git events.

**`.pdd/constitution.md`** holds these rules. dod also uses the file to recognize the project.

**A structure check runs with the gates:**
- no cycles;
- no dependency on an item that doesn't exist;
- exactly one final item;
- every behavior of the current MVP delivered by an item;
- an LLD for every build item that has started.

**The plan view.** dod draws the plan as a dependency graph. It lists the items ready to start, the
critical path and how many items can run at once. It reads the plan and the status from main in
git, so it is right after every merge without anyone updating it.
- **Setup, in 1a:** add the repository to dod.
- **Every session:** a SessionStart hook makes sure the plan view is running and prints its
  address. In the Claude desktop app, the session opens it in the browser pane. A session that
  finishes something (a merge, a stop reached) names the items that changed.
- **On macOS** dod runs as an always-on background agent. Elsewhere, run the plan view by itself:
  dod's README says a view "works opened directly". This hasn't been tried outside macOS.

## Trust

The project's CLAUDE.md has a **Trust** section with five boxes. A checked box is a stop that waits
for you:

- [ ] **LLD:** you accept an item's LLD before its code is written.
- [ ] **Batch end:** you use a finished batch before the next one starts.
- [ ] **Merge:** an item merges into main on your word.
- [ ] **Push:** main is pushed to origin on your word.
- [ ] **Release:** a release is tagged and deployed on your word.

The more boxes are checked, the less the agent is trusted. A new project starts with every box
checked. Uncheck a box when its stops have stopped finding anything. At the far end, unshatter has
one stop left: your word that a piece of work is good, after which the agent merges, pushes and
deploys it.

How each box is enforced:
- **Merge, push and release:** permission rules in `.claude/settings.json`. A checked box is an
  `ask` rule for the command that does it (the merge script, `git push origin`, the release
  script), so Claude Code itself asks you. An unchecked box is an `allow` rule.
- **Batch end:** one of your items at the end of each batch, which the next batch's first items
  depend on. The plan view shows it as waiting for you.
- **LLD:** the session stops after the LLD's review and waits for your word, which the LLD
  records. Nothing mechanical enforces this box.

**A stop whatever the boxes say:** any irreversible operation on real data, such as a migration
against production data, deleting stored data, or changing who can access what. The script that
does it asks for typed confirmation, not a keypress: one cutover script read a closed input as a
yes. The boxes trade review for speed on work that can be undone. Trusting the agent more doesn't
make an irreversible mistake cheaper.

## Git

- **One repository per project** (1a).
- **Branches and worktrees from phase 1 on.** All work happens on a branch, in a worktree of its
  own, with one session per worktree. No session checks out main. The folder the repository was
  created in doesn't stay on main either: after the first commit, detach it
  (`git switch --detach main`). While any checkout holds main, `git push . HEAD:main` is refused.
  Items that don't depend on each other run in parallel sessions, and the plan view shows which are
  ready.
- **The worktree script** makes an item's worktree:
  - cut from main, after checking that local main isn't behind origin;
  - beside the repository, not inside it. Tools that walk the repository pick up a worktree nested
    in it: robotics-lms had to exclude the desktop app's `.claude/worktrees/` from its lint and
    its mutation runs;
  - with dependencies installed and the git-ignored files the project needs to run (environment
    files) copied in. Without them the gates fail, and the failure reads as a problem in the code.
- **Names:** the branch is the item's id and a short name (`w7-catalog`), and the merge commit
  names it too. The plan view reads both.
- **Merging.** The merge script does these steps:
  1. In the item's worktree, build the merge on a detached HEAD at main:
     `git switch --detach main && git -c rerere.enabled=true merge --no-ff <branch>`. Resolve any
     conflicts there. rerere records each resolution, so a retry replays it.
  2. Run the gates on the merged tree.
  3. Move main with `git push . HEAD:main`. Git allows only a fast-forward, so if main moved in the
     meantime, go back to step 1 on the new main.
  4. Switch back to the branch. Remove the worktree once the item is done.
- **The gates** run in one pre-push hook, whenever the push targets `refs/heads/main`: types, lint,
  tests, the Gherkin scenarios, the plan's structure check, and the project's gated rules.
  `git push . HEAD:main` runs the pre-push hook too, so one hook covers local merges and pushes to
  origin. That includes a merge committed by hand after a conflict, which a merge hook once
  skipped 5 times in 8. A Claude Code PreToolUse hook refuses `--no-verify`.
- **Releases are tags on main.** Main is not the deployed tree: a deploy comes from a tag. That is
  what lets merges go ahead without you while releases still wait (see Trust).

## Tools

Each step names the one thing to run, and invokes it by name. Nothing depends on a skill starting
from its description: in one project's records, 1,472 reminders to apply a practice led the agent
to open that practice 10 times. There are three kinds:
- **Guidance, in the working session:** skills and templates. The interview, the LLD template, the
  merge procedure, handoff.
- **Checks, in a fresh session:** workflows. design-review for each design document, and the
  adversarial review before merge. Whatever judges the agent's work runs outside the session that
  made it.
- **Enforcement:** hooks and scripts. The gates in the pre-push hook, the refusal of
  `--no-verify`, the plan view at session start, and the permission rules for the trust level.

design-review's kinds, per document: the Vision, and each MVP's PRD with its behaviors, use `prd`
(`gdd` for a game). architecture.md and a batch HLD use `hld`. An LLD uses `lld`.

They ship as one Claude Code plugin: skills, workflows (in the plugin's `workflows/` folder, run as
`/<plugin>:<workflow>`), hooks and templates. engineering-discipline's skills are not part of it:
their practices are already in the documents, the review questions and the gates.

## Ambiguity levels

Every open question has one of three levels:

- **Large:** answering it could change the architecture.
- **Medium:** changes behavior, but not the architecture.
- **Small:** an implementation detail. It doesn't go in the documents.

## 1. Requirements

Phase 1 covers the whole product first (1a), then one MVP (1b). Each later MVP starts at 1b (see
"Each later MVP" at the end).

### 1a. The whole product

- **Project:** before anything is written:
  - a folder and a git repository for this project and nothing else. Every document and all the
    code live there, and the project's sessions start there. Claude Code keeps CLAUDE.md, its
    memory and its session history per folder, so a project that shares a folder with other work
    shares all three;
  - `.pdd/plan.json`, with the phases up to 3 as its first items, and `.pdd/constitution.md`. The
    repository is added to dod;
  - CLAUDE.md, with every trust box checked, and the permission rules that go with them;
  - the plugin, the worktree script and the merge script. The pre-push hook starts with the plan's
    structure check, and phase 4 adds the rest of the gates.
- **Ask:** "Interview me about the whole product until you can write vision.md. Ask numbered
  questions, a few per round. Mark every decision you write with who made it and when: me, or you
  so work could continue. Add each term to the glossary as it comes up. Anything not decided goes
  into open-questions.md with its level, never into the documents as settled."
- **The interview:** answer by number. Say "explain" when a question is unclear. When you and the
  agent use a word differently, settle it in the glossary before going on.
- **Cheapest prototype (optional):** some large questions can only be answered by trying something:
  whether it's fun, whether an interaction feels right, whether the output is useful. For each such
  question, build the cheapest thing that answers it, in whatever tool is fastest. Before building
  it, write down what result would be a no. Each prototype has its own document,
  `docs/prototypes/<name>.md`, which stands alone: the question, what would be a no, what was
  built, how it was judged, the verdict, and where what was built can still be found (a commit or
  a link). A decision that follows from a prototype cites it. The code is thrown away. Say so when
  asking for it; otherwise the agent will reuse it as a base.
- **Review:** design-review of the Vision, in a fresh session, looking for:
  - a feature marked with no MVP, and not marked "none yet" either;
  - a term used with two meanings, or two terms for one thing;
  - a belief the product depends on that nobody chose. Each one goes into assumptions.md;
  - a large question about a later feature that is neither answered nor listed among what the
    architecture must keep possible.
- **You:** answer, decide, reject. Read every decision marked as the agent's.
- **Done when:**
  - every feature is marked with its MVP, or with none yet;
  - every large question about a later feature is answered, or listed in the Vision among what the
    architecture must keep possible;
  - every decision is marked with who made it;
  - the review's findings are settled.
- **Outputs:** the project's repository, the plan shown in dod, vision.md, and the standing
  documents.

### 1b. An MVP

- **Ask:** "Take these features from the Vision for MVP N. Write their behaviors into behaviors.md,
  and the PRD for this MVP. Interview me about anything not settled."
- **Keep it small:** expect to push for this. The agent grows scope by default. Ask for the
  smallest set of features that shows what this MVP is for. Everything else stays in the Vision
  for a later MVP.
- A cheapest prototype (see 1a) can answer a large question here too.
- **Review:** design-review of the PRD and the behaviors it adds or changes, in a fresh session,
  looking for:
  - a behavior without its Failure or Edges line;
  - a term used with two meanings, or two terms for one thing;
  - a belief the design depends on that nobody chose. Each one goes into assumptions.md;
  - a behavior or scenario for a feature outside this MVP.
- **You:** answer, decide, reject. Read every decision marked as the agent's, and every rule.
- **Done when:**
  - no large question about this MVP is open;
  - any new large question about a later feature is answered, or added to the Vision's list of
    what the architecture must keep possible;
  - every decision is marked with who made it;
  - every behavior this MVP adds or changes has its contract, Failure and Edges;
  - every term the documents use with a specific meaning is in the glossary;
  - the review's findings are settled.
- **Outputs:**
  - `docs/prd/mvp-N.md`;
  - the behaviors this MVP adds or changes, in behaviors.md;
  - `features/*.feature`: behavior tests in Gherkin, each scenario tagged with its behavior's id
    (`@B7`), covering the Failure and Edges lines as well as the normal case.

**Why Gherkin:** it doesn't depend on the stack, runners exist for most languages (Cucumber for
JS/Java, behave for Python, godog for Go, Reqnroll for .NET), and developers already know it. The
scenarios can run once phase 2 has written the step definitions that bind them to the system.

## 1.5 Refinement

Answer the medium questions in open-questions.md. Each one has a default that work proceeds on
until you rule. Because they don't affect the architecture, this can run before phase 2, alongside
it, or after it.

## 2. Architecture, then stack

The agent is lead architect: it proposes an architecture that covers every behavior in
behaviors.md, and keeps possible the later features the Vision lists for it.

- **You:** walk the behaviors through the architecture one at a time: "B7: which parts take part,
  in what order, what state changes?" If a behavior can't be walked through, the architecture is
  incomplete. The walk-throughs of behaviors that cross more than one part go into
  architecture.md as its key flows.
- **Later features:** each one the Vision lists for the architecture gets a decision: what keeps it
  possible and what that costs now, or a decision not to, with what adding it later would cost.
- **Then the stack:** what supports the requirements and the architecture as they stand. Any
  constraint known up front (platform, language, hosting) belongs in phase 1, not here.
- **Assumptions:** every belief the architecture or the stack depends on that nobody proved goes
  into assumptions.md, with its fragility.
- **Step definitions:** choose the test runner and write the step definitions that bind the Gherkin
  steps to the system. Watch for steps that assert nothing: if a scenario's steps only log or
  return, it passes against any implementation. A fresh session checks them by asking "which wrong
  implementation passes these?"
- **Review:** design-review of architecture.md, kind `hld`, in a fresh session.
- **Outputs:**
  - `docs/architecture.md`: the parts, the key flows, the decisions (each marked with who made it
    and when), and a **Deferred** section for technical options set aside;
  - `docs/stack.md`;
  - the high-fragility assumptions, which are phase 3's input;
  - rules for the module boundaries the architecture depends on, each with its tier;
  - glossary entries for the architecture's parts;
  - the worktree script, now installing the stack's dependencies.

## 3. Spikes

Every high-fragility assumption gets a spike, or a decision that makes it not matter, before
anything is built on it. It could be a mechanism, a part of the stack, an integration. One session
per spike, doing the minimum needed to answer its question.

- **Before starting:** state the question, what result would be a no, and where the spike has to
  run: the device, the data or the real service the question is about. A result from anywhere else
  answers a different question. If that place isn't at hand, say so now and name what will stand
  in. A spike planned inside the work it gates tends to be skipped once that work is built.
- **Output:** `docs/spikes/<name>.md` with the question, where it ran, what was done, and the
  verdict. The assumption's entry gets the verdict. The spike code is thrown away unless the
  verdict says to keep it. Any trap the spike found goes in footguns.md.
- **Waived:** a spike that won't run is written into its assumption, with what stands in for it.
- **Feedback:** a verdict that changes the architecture goes back to 2. One that changes a behavior
  goes back to 1. Either way, the documents change in the same commit as the verdict.
- **A likely spike:** can the Gherkin steps drive this stack? This is hard for real-time systems and
  games, where state is continuous and timing matters.

## 4. Plan the build

After phase 3 for MVP 1, and after the phase 2 check for a later MVP.

- **Ask:** "Plan MVP N's build in .pdd/plan.json: work items in batches, each with what it cannot
  correctly start until, its size, its risk and the behaviors it delivers. Give each batch a goal
  and exit criteria that can be checked. End with the MVP's verdict as the one final item."
- **Size items for review:** an item is small enough when its LLD can be reviewed in one sitting.
  A file that will obviously grow past a few hundred lines is a reason to split the item now, not
  after the code exists.
- **Your items:** the MVP's verdict, and a stop at the end of each batch while that trust box is
  checked.
- **The gates:** before the first build item, the pre-push hook runs types, lint, tests, the Gherkin
  scenarios, the plan's structure check and the gated rules. Try each check once on the real
  failure it exists for. A check counts once it has been seen to fail on a real case, not only on a
  planted example: in one project a boundary check passed a module that broke its rule, until a
  review noticed.
- **You:** read the plan in dod: the batches, what each item delivers, what can run in parallel.
- **Done when:** every behavior of the MVP is delivered by an item, the structure check passes, and
  each gate has been seen to fail on a real case.

## 5. Batch design

Only for a batch that adds or changes architecture: new parts, new stored data, new flows between
parts. Any other batch goes straight to its items, whose LLDs are written against
architecture.md.

- **Ask for `docs/hld/<batch>.md`:**
  - what the batch builds and why;
  - its decisions, each marked with who made it and when;
  - what can go wrong, with a guard for each;
  - what it costs;
  - its key flows;
  - what the LLDs must decide;
  - its changes to the glossary, the rules and the assumptions;
  - what it defers.
- **Review:** design-review, kind `hld`, in a fresh session. A finding that would overturn one of
  your decisions comes to you as a question.
- **Done when:** the review's findings are settled. Where the batch changes the architecture,
  architecture.md changes in the same commit.

## 6. Work items

Each item runs in its own worktree, in its own session.

1. **LLD**, `docs/lld/W<id>-<name>.md`, from the template:
   - a header: the behaviors it delivers, what it depends on, what you'll open to see it work, and
     whether its code gets the adversarial review (step 4), with the reason;
   - **Files:** every file it adds or changes, with what the file is responsible for and what it
     exports. A file missing from this table should not appear in the diff;
   - **Contracts:** the types that cross a module boundary, and what happens to invalid input. It
     fails or reaches the user, never quietly;
   - **Tests:** each test file, what it pins, and the behavior and rule ids it covers;
   - **Not doing:** what a reader would expect here and won't find, and where it happens instead.
2. **Design review** of every LLD, kind `lld`, in a fresh session. The findings are fixed in the LLD
   before any code. If the LLD box is checked, the session then waits for your word.
3. **Implementation**, in the worktree. The gates run between edits, and each verified step is a
   commit.
4. **Adversarial review before merge**, in a fresh session. It attacks:
   - the tests, always: "which wrong implementation passes these?";
   - the code, when the item reads outside input, writes stored data or changes what stored data
     means, or does something that can't be undone.

   What it finds is fixed before the merge.
5. **Merge**, by the merge procedure, as the trust level says. The item is done when its merge is
   on main.

**Why these reviews:** in one project, reviews by fresh sessions found 11 of its 15 most
consequential defects, for about 15% of its tokens. Nine of the ten largest code defects they found
were in those three kinds of code. And agent-written tests can pass without testing anything: one
set of removal tests passed on code that removed nothing.

## 7. End of a batch

- **You:** use what the batch built. If the batch-end box is checked, the next batch waits for your
  item. What you find becomes items in the plan.
- **Mutation testing** on what the batch changed in the modules that hold data or make decisions.
  A tool (Stryker, for TypeScript) makes small changes to the code and reruns the tests, and a
  change no test notices is a gap. Read every survivor the same day. Each one is a missing test,
  dead code, or a change that makes no difference, and each is closed.
- **A reading pass** for failures that leave no trace: swallowed errors, work started and never
  finished, success reported for nothing written.
- **Once no session can read the whole codebase:** a check for duplicated code. The agent writes a
  new helper where one already exists.
- **Done when:** the batch's exit criteria are met.

**Why:** a mutation run found a fault in code the current model wrote: an unreadable save was
marked writable, so one refused read would have written a new save over the player's. A reading
pass found two hangs that no check could see.

## 8. End of an MVP, and release

- **The verdict:** you use the MVP against what it was for, and against the result its PRD said
  would be a no. The verdict goes into its PRD and closes the MVP's final item.
- **Release:** a tag on main, deployed from the tag. If the release box is checked, you first read
  the code that handles outside input, permissions and stored data. A platform built by prompting
  alone, with an earlier model, went to production accepting any Google account as admin and
  running HTML stored in its content. Reading found both.
- **After release,** what users report becomes items.

## Each later MVP

1. Revise the Vision if the last MVP's verdict changes the direction.
2. 1b: the new MVP's PRD, the behaviors it adds or changes, and their scenarios.
3. 1.5 for its medium questions.
4. Phase 2 as a check: walk its new and changed behaviors through the architecture. Change the
   architecture only where one can't be walked through, and record the decision.
5. Phase 3 for its new high-fragility assumptions.
6. Phases 4 to 8 for its build.

## Tooling this process needs

Parts of this process rely on tools that don't exist yet:
- **dod:**
  - `batches` and `batch` as names for its `phases` and `phase`;
  - status derived from git;
  - the plan read from main instead of from a checkout;
  - your items shown as waiting for you;
  - adding a project in one step. Today a project is added by hand to dod's PDD provider config.
- **The plugin:**
  - skills: the interview, the LLD template, the merge procedure, handoff;
  - workflows: design-review and adversarial review, which exist today as copies installed from
    the author's workflows repository;
  - hooks: the plan view at session start, the refusal of `--no-verify`;
  - templates for the documents.
- **Scripts:** the worktree script, the merge script, the plan's structure check, and the pre-push
  hook that runs the gates.
