# How robotics-lms ran, against build-process.md (2026-09-30)

Read to compare with `process.md` (then `~/PersonalKB/drafts/build-process.md`, phases 0 to 3).

## Sources

- robotics-lms: `CLAUDE.md`, `README.md`, `.pdd/constitution.md`, `.githooks/pre-push`,
  `package.json` scripts, `docs/lld/TEMPLATE.md`, in full: `docs/footguns.md`,
  `docs/assumptions.md`, `docs/open-questions.md`, `docs/future.md`; in part: `docs/rules.md`,
  `docs/glossary.md`, `docs/design.md`, `docs/hld.md`, `docs/hld-p13.md` (headings).
- Git history of main (467 commits), and the first docs commit `67507da`.
- The day-1 session transcript (`2227dd7d`, 2026-08-12 to 08-13), owner turns only.
- Commits `c4c7d68`, `55d23c6`, `545f0d8` (the W17a spike).

## What robotics-lms is

v2 is a rewrite of a live v1 (built 2025-12-23 to 2026-01-04) over v1's production data. The v2
code is new, but the product, the stack (Firebase, React) and the data already existed, so the
start was not greenfield. v2 went live on 2026-09-02.

## How the start ran

All of the following happened in one session, 2026-08-12 to 08-13, which ended with a handoff.

| Time (UTC) | What happened |
| --- | --- |
| 08-12 07:33 | "Analyze this project": how it's built, where the keys are, dangers. v1's traps became footguns F1 to F9. |
| 07:55 | Owner describes the product in one message. |
| 08:14, 08:27, 08:34 | The agent asks numbered questions, and the owner answers by number in three rounds. Twice the owner answers "I am not sure what you mean, explain". A term clash (curriculum, course, class) is settled by keeping v1's terms. |
| 08:43 | "Let's do the docs/ set, and write an HLD." The design and the architecture were written together. |
| 13:10, 13:26 | Owner probes two topics: sticker storage cost, teacher sign-in. |
| 13:33 | "Run design-review." Three skills ran: design-completeness, one-meaning-per-term, design-assumptions-register. |
| 13:49 | "Commit the docs, then start scaffolding." |
| 14:24 | "Same work process, quality standards, and architectural approach as in skyline." This became W2: the rules register, the plan, the gate suite, the review workflows. |
| 15:40 | Branch model. |
| 08-13 10:58 | W3's LLD. During it the owner redesigned packs ("It doesn't have to be exactly 3, this is ridiculous"). |

The first docs commit (`67507da`) had 8 files and 643 lines: design.md with 33 requirement ids, 11
of them with a Failure line; hld.md; glossary.md; assumptions A1 to A12; footguns F1 to F10;
open questions Q1 to Q8; future.md; migration.md. **The registers came out of the phase-1 review.**
The three skills the owner ran at 13:33 are what produce the Failure and Edges lines, the glossary
and the assumptions.

Product decisions kept coming after phase 1, during the LLDs: packs (W3), Dutch as a third
language (W5), language as two axes (W5). design.md grew from 188 lines to 1197, the glossary from
86 to 314, and the assumptions from 12 to 37.

### The one spike

W17a's LLD (2026-08-23) planned a spike first, to measure animation frame rate on the slowest
classroom laptop (assumptions A14, A16, A17). The spike ran only on a development machine. On
2026-08-24 the owner waived it, and the commit says "the gating purpose has expired regardless,
since everything is built". The waiver was written into the three assumptions, with what stands in
for the measurement (the shipped frame sampler, plus a plain-look toggle a person can switch on).

What it shows: a spike that needs a device you don't have at hand gets skipped. A spike placed
inside the work item it gates doesn't gate it.

## The documents

- **`CLAUDE.md`**: a reading order, not imports. Glossary first, always. design.md, which holds
  decisions only. rules.md before code. open-questions.md before proposing anything.
  assumptions.md before relying on anything design.md states as fact. hld.md before architecture.
  future.md never. Also a **Claims** rule: "Nothing is asserted that was not read or run in the
  current session. A name, a script entry or a grep hit is a lead, not a fact."
- **`design.md`**: requirements `REQ-AAA-nn`. Each has a contract paragraph, a **Failure** line
  (what can go wrong and what happens then) and an **Edges** line. Test titles name the ids, and a
  gate checks the link. Owner rulings are marked inline, "(owner, 2026-08-31)". There is no
  separate decision log. Phase HLDs have their own Decisions sections (D-P13-n).
- **`open-questions.md`**: each question has a state. **proposed**: a default exists, and work
  proceeds on it until the owner rules. **deferred**: a decision not to decide yet, with its
  trigger. Each also has "needed by". A settled question moves into design.md.
- **`future.md`**: "deliberately out of v1 ... this document is not scope, and nothing may cite
  it as a reason for anything." One paragraph per item.
- **`assumptions.md`**: columns Assumption, Falsified if, Detector / verify by, Fragility, Fallback.
  Rule R-ASSUME: a high-fragility entry goes to a spike or a decision before anything is built on
  it.
- **`footguns.md`**: columns Looks like, Actually, Anchor, Verified. Live and Retired tables, and
  the Retired table says what closed each one. Several entries are test traps: F19 and F26 are
  specs that stayed green with the code under test removed.
- **`glossary.md`**: "exactly this meaning in every document, identifier, commit message and
  conversation." Live terms, and retired terms that are barred from prose, identifiers and tests.
- **`rules.md`**: "A rule with no detector is a wish." Each rule sits in one of three tiers:
  **Gated** (a script fails on it), **Reviewed** (a person checks it, and it says so),
  **Registered** (a file must exist and be current). Each rule has Says, From (the skill or
  incident it comes from) and Detector.
- Machinery behind the rules: a 21-step gate chain, about 20 custom gate tools under `tools/`, and
  five known-gaps JSON files. This is robotics-lms's own, and the part not to carry into a process
  for other people.

## Against build-process.md

### Additions that fit what's agreed

1. **assumptions.md as a standing document from phase 1.** robotics-lms wrote A1 to A12 on day 1.
   It uses its columns, and high fragility routes to a spike or a decision. This gives phase 3
   input beyond "a list of risks".
2. **open-questions.md as its own file**, with state (proposed with a default, or deferred with a
   trigger), level (large or medium) and "needed by". Medium questions become proposed-with-default,
   so phase 1.5 doesn't block anything.
3. **A Failure and an Edges line for every behavior**, and scenarios covering them, not only the
   happy path.
4. **Rules in three tiers** (Gated, Reviewed, Registered) with Says, From, Detector, replacing
   "or nothing".
5. **Retired terms in the glossary**, and the glossary applying to identifiers and commit messages
   too.
6. **The Claims rule in CLAUDE.md.**
7. **Spikes run where the question lives** (the device, the data, the real service). If that isn't
   at hand, say so before starting and name what stands in. A waived spike is written into the
   assumption it was verifying.
8. **Documents change in any phase**, in the same commit as the work that surfaced the change. The
   draft only covers 3 to 2 to 1. In robotics-lms most product decisions after day 1 came from LLDs.
9. **The interview:** numbered questions in rounds, answered by number, "explain" when a question
   is unclear, and a term clash goes to the glossary as soon as it appears.

### Where the draft departs from robotics-lms

1. **decisions.md.** robotics-lms has none: design.md holds decisions only, marked inline with who
   and when, and git holds what changed. Recommendation: drop decisions.md. Otherwise the PRD and
   the log say the same thing in two places and drift apart.
2. **`@later` behaviors and scenarios.** robotics-lms puts later items in future.md, which is not
   scope and cannot be cited. Recommendation: do the same. Scenarios for later behaviors are work
   on things that may never be built, and the agent designs toward whatever the PRD contains.
3. **Imports rather than reading order.** At robotics-lms's sizes, glossary, rules and footguns
   come to about 54 KB (about 14k tokens) per session if imported. Whether its sessions followed
   the reading order was not checked. No change recommended.
4. **One session per phase.** robotics-lms ran requirements, architecture, the phase-1 review,
   scaffolding, process setup and two LLDs in one session. The rule is new with the draft and
   untested in practice. No change recommended.

## For phases 4 and later

What robotics-lms already has, for when the draft gets there:

- **Plan**: work items (W ids) in phases. `depends_on` means "cannot correctly start until".
  Exactly one terminal item. Status moves twice: in-progress when the LLD is written, done when the
  PR merges. The merge is the verdict. A check covers structure only.
- **A phase HLD**: Decisions, What this costs, Assumptions, Testing and gates, What the LLDs must
  decide, Build order, Glossary deltas, Deferred.
- **LLD template**:
  - a header naming the HLD section, the requirement ids, dependencies, the artifact to open and
    poke, and whether adversarial review applies;
  - a Files table ("a file missing from this table is a file that should not appear in the diff");
  - Contracts;
  - a Tests table naming rule and requirement ids;
  - Not doing.
- **Reviews**: design-review on every design document, LLDs included. Adversarial review only when
  an item reads outside input, writes stored data or changes what it means, or does something that
  cannot be undone.
- **Mutation** once per phase, on what the phase changed, with every survivor closed.
