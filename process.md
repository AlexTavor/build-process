# Building software with a coding agent: requirements to spikes

*Draft, 2026-09-29, revised 2026-09-30. Replaces the Superpowers plan
(`~/PersonalKB/drafts/superpowers-layer-plan.md`). Covers the start of the process only:
requirements, architecture, spikes. The document forms follow robotics-lms
(`research/robotics-lms-process-2026-09-30.md`). The Vision and the PRD per MVP follow RUP's
Vision and iteration plans.*

For developers who know how to build software and have not built much with an agent.

## 0. Sessions

Each phase runs in its own session, and so does each spike. A session ends by writing its output
files. The next session starts by reading only those files, not the previous conversation.

Start a new session when the phase changes, or when a spike or a review finishes. Don't carry one
conversation across phases: whatever it holds that isn't in a file is lost to every later session.

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
- **needed by:** the MVP or the work that can't go further without an answer.

A settled question moves into the document it belongs in, and is deleted here.

**`UNHANDLED_ISSUES.md`** (project root). Anything found that needs fixing and is outside the
current task. The commit that fixes an issue deletes its entry. Create it together with the line
`UNHANDLED_ISSUES.md merge=union` in `.gitattributes`, so entries appended on different branches
merge without conflicts.

How an issue differs from a footgun: an issue gets fixed and then it's gone. A footgun stays,
because its cause can't be removed (it's in a dependency or the domain) or isn't worth removing.

## Ambiguity levels

Every open question has one of three levels:

- **Large:** answering it could change the architecture.
- **Medium:** changes behavior, but not the architecture.
- **Small:** an implementation detail. It doesn't go in the documents.

## 1. Requirements

Phase 1 covers the whole product first (1a), then one MVP (1b). Each later MVP starts at 1b (see
"Each later MVP" at the end).

### 1a. The whole product

- **Project:** before anything is written, create a folder and a git repository for this project
  and nothing else. Every document and all the code live there, and the project's sessions start
  there. Claude Code keeps CLAUDE.md, its memory and its session history per folder, so a project
  that shares a folder with other work shares all three.
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
- **Review:** a fresh session reviews the Vision, looking for:
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
- **Outputs:** the project's repository, vision.md, and the standing documents.

### 1b. An MVP

- **Ask:** "Take these features from the Vision for MVP N. Write their behaviors into behaviors.md,
  and the PRD for this MVP. Interview me about anything not settled."
- **Keep it small:** expect to push for this. The agent grows scope by default. Ask for the
  smallest set of features that shows what this MVP is for. Everything else stays in the Vision
  for a later MVP.
- A cheapest prototype (see 1a) can answer a large question here too.
- **Review:** a fresh session reviews the PRD and the behaviors it adds or changes, looking for:
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
- **Outputs:**
  - `docs/architecture.md`: the parts, the key flows, the decisions (each marked with who made it
    and when), and a **Deferred** section for technical options set aside;
  - `docs/stack.md`;
  - the high-fragility assumptions, which are phase 3's input;
  - rules for the module boundaries the architecture depends on, each with its tier;
  - glossary entries for the architecture's parts.

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

## Each later MVP

1. Write the last MVP's verdict into its PRD, and revise the Vision if the verdict changes the
   direction.
2. 1b: the new MVP's PRD, the behaviors it adds or changes, and their scenarios.
3. 1.5 for its medium questions.
4. Phase 2 as a check: walk its new and changed behaviors through the architecture. Change the
   architecture only where one can't be walked through, and record the decision.
5. Phase 3 for its new high-fragility assumptions.
