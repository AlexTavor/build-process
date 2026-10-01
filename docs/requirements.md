# mlmd: requirements (business side and adoption)

Status: proposed, v0.11 (2026-09-30). Author: Frank Verbruggen. Not yet agreed with Alex; open
items OQ-16 and OQ-17 are his to answer. "Boot" was Frank's working name for mlmd (D-8). Earlier
history of this file: the `claude-boot` repository, branch `draft/requirements`.

## 1. Purpose

These requirements cover what mlmd needs so that people other than its author can use it: how a
project starts, who takes part (a technical expert, the operator, and optionally a business
expert), who decides, how requirements stay the source of truth, and how strictly work is traced.
The engine itself (phases, gates, git, plan) is defined in [process.md](../process.md).

IDs are stable: never renumbered or reused. Withdrawn items are marked, not deleted.

## 2. Requirements

### Form and start-up
- **BR-1** mlmd can be started from one file, `BOOT.md`. Attaching it to a Claude Code prompt installs and starts the mlmd plugin, so starting from the file and starting with the plugin's commands lead to the same process. (Revised v0.9, D-12.)
- **BR-2** On first run mlmd installs its role files, templates and state file into the user's own repository; from then on the process runs from that repository.
- **BR-3** Running mlmd again on an initialised repository resumes from the recorded state.
- **BR-15** mlmd assumes no particular repository, host or project. If the folder is not a git repository, mlmd initialises it for the user; connecting a remote (e.g. GitHub) is optional and guided.

### User experience
- **BR-4** The technical expert may perform technical operations. Anything mlmd asks of a business expert (in either mode, BR-27, BR-28) needs no technical operations (terminal, git, session management); clicking a next-stage card or pasting a boot prompt counts as a decision, not a technical operation. (Revised v0.6, D-9.)
- **BR-5** mlmd adapts to the user's starting point, at least: (a) only a broad idea, (b) deep domain knowledge, (c) an existing legacy system (e.g. COBOL, PL/SQL) plus process knowledge. Case (c) is handed to PDD (Proof-Driven Development), which will be updated when the first brownfield customer arrives. (Revised v0.9, D-12.)
- **BR-6** Whatever the starting point, every path converges on a fixed set of exit files per stage. (List: pending Alex, OQ-10.)
- **BR-7** Each question is routed by role to the person able to answer it; the technical expert receives every question that has no other owner. (Revised v0.6, D-9.)

### Collaboration and authority
- **BR-8** Multiple people can collaborate on one project through the shared repository, across sessions and machines.
- **BR-9** All artifacts and all process state live in git.
- **BR-10** Every participant has a recorded role in a role register; every approval records who gave it. The register holds at least one technical expert with Claude Code knowledge (the only required role). A business expert is optional and is marked customer or team member; a project may switch between the two. (Revised v0.6, D-9.)
- **BR-16** Each project has exactly one final decider, recorded in the repository. By default this is the technical expert; it may be handed to a business expert who is a team member, never to one who is a customer. On disagreement the decider's call wins; mlmd logs the decision with its reasoning. (Revised v0.6, D-9.)

### Source of truth and change
- **BR-17** Requirements are the source of truth for the product. Code is derived from specs and tests. On conflict, the code is changed, never the requirements.
- **BR-18** Approved product and design documents (vision, behaviors, PRDs, architecture, HLDs, LLDs) may be reopened only through a change request, which flows through all downstream phases again and needs the decider's approval. New features enter this way. Standing documents (glossary, footguns, assumptions, open questions, unhandled issues) change freely, in the same commit as the work that found the change. (Revised v0.8, D-11.)
- **BR-19** Only Claude Code writes code. Humans never edit code directly; code is a side effect of the specs and tests.
- **BR-20** Traceability is 100% strict: every requirement traces to at least one spec; every spec to at least one test; every test to the code that satisfies it; nothing exists without a parent in either direction. Any gap blocks the gate. This includes an automated gate check that finds code no behavior asks for. (Revised v0.8, D-11.)

### Stages, sessions and handoffs
- **BR-11** The process is a sequence of stages. Each stage has one AI role, declared inputs, declared exit files, and a decider gate (approve / revise / reject).
- **BR-12** Each stage ends in a handoff committed to the repository: stage report, STATUS line, gate decision. The next stage reads only the handoff and its declared inputs.
- **BR-13** Work is split across many agents, each with a small context and a single role.
- **BR-14** ~~Defined stages so far: S1 meaning extraction; S2 per-area clarification.~~ Revised v0.8 (D-11): the stages are mlmd's phases 1a-8 as defined in Alex's process.md; S1 and S2 are withdrawn.
- **BR-21** ~~Boot is self-contained and independent of any other process framework.~~ Withdrawn by D-8: Boot and mlmd are the same product.
- **BR-22** Each stage runs in its own session; within a stage, work runs as subagents. A stage ends by committing its handoff, then offering the next stage as a one-click card. Where cards are unavailable (CLI, web, or a card fails to appear), mlmd gives a copy-paste boot prompt of at most three lines. (D-1, D-6.)
- **BR-24** Each stage session works on its own branch. At the gate the stage branch is merged into the project's working branch; the decider's gate approval authorises that merge. The next stage is offered only after the merge, so it starts from the approved state. (D-6.)
- **BR-25** mlmd works in Claude Code Desktop, CLI and web, with the copy-paste boot prompt as the common fallback. (D-6.)
- **BR-26** ~~mlmd keeps one home session per project; stage sessions report back to it.~~ Revised v0.11 (D-14): there is no home session. The project overview comes from the plan and git (status derived from merges), shown as a status line at every session start and in the dod plan view, the same for every collaborator.
- **BR-27** Customer mode: the business expert is consulted, not on the team. mlmd collects their input through interviews and verdicts; the technical expert records it and decides. (D-9.)
- **BR-28** Team mode: the business expert takes part in interviews, gates and summaries, all in plain language. (D-9.)
- **BR-31** The agent may make a provisional decision so work can continue; it is marked as the agent's, and the final decider confirms or overturns each one at the next gate. (D-11.)
- **BR-32** Several people can work on one project at once, each with a role from the register (BR-10). Concurrent work follows standard GitHub practice: each piece of work on its own branch, merged through pull requests. (D-11, D-13.)
- **BR-33** Only the final decider may change the project's trust settings (which steps wait for a person). (D-11.)
- **BR-34** Windows 10 is a supported platform for mlmd, including dod, uv and the hooks. Frank tests on Windows. (D-12.)
- **BR-35** Terms: the **operator** is the person running mlmd on a project. On a one-person project the operator, the technical expert and the final decider are the same person. On a multi-person team the technical expert is a software engineer or software architect. (D-13.)
- **BR-30** A new project starts with the business expert, if any, in customer mode (BR-27). (D-10.)
- **BR-29** Adoption: a newcomer with Claude Code knowledge can start a project with mlmd without anyone explaining it to them; every phase states in one line why it exists. (D-9.)
- **BR-23** Token usage is measured and recorded per stage and per subagent, and reported to the user in each stage report. There is no fixed budget: mlmd keeps cost low by design (small contexts, only the files a phase needs, subagents only where they pay off, short reports). (Revised v0.10, D-13.)

## 3. Open questions
- **OQ-10** Full stage list, exit files per stage, and PDD details. Owner: Alex.
- **OQ-11** ~~Token budgets per stage/subagent~~ Closed by D-13.
- **OQ-12** Definition of done / verification criteria (tests, traceability, mutation or coverage thresholds). Owner: Alex (PDD).
- **OQ-13** ~~Verify that a Desktop session can reliably offer the next-stage session as a one-click chip, and what the fallback is outside Desktop.~~ Closed by D-6.
- **OQ-14** ~~Should stage sessions report back to one home session?~~ Closed by D-7.
- **OQ-16** Who owns the process (the final decider on mlmd itself, as distinct from each project's decider in BR-16). **Proposed** (Frank agrees; Alex's 2026-09-30 reply did not address it — he clarified that mlmd's "owner" means the operator of mlmd, i.e. a project's operator, not the process owner): split by area — Alex owns the engine (phases, gates, git); Frank owns adoption and the business side (onboarding, explanation, roles, business-expert modes, change requests); cross-area disagreements go to a tie-break both agree on in advance.
- **OQ-18** ~~Default business-expert mode for a new project~~ Closed by D-10.
- **OQ-17** Where these requirements and mlmd's work items are managed. mlmd is a public repository both can PR to; Alex is unsure GitHub is the right place for requirements and tasks and will decide next. Awaiting Alex.
- **OQ-20** ~~Terminology: operator vs technical expert vs final decider~~ Closed by D-13 (BR-35).
- **OQ-19** ~~How concurrent collaborators avoid clashing~~ Closed by D-13.
- **OQ-15** ~~Which session is the home session~~ Closed by D-14 (no home session).

## 4. Decision log
| ID | Date | Decision | Reasoning |
|----|------|----------|-----------|
| D-1 | 2026-09-30 | Session model C: one sidebar session per stage, subagents within. | Balances a smooth experience (one click) with small contexts and readable per-stage history. Subagent token use must be monitored (BR-23). |
| D-2 | 2026-09-30 | One final decider per project. | Disagreements need a deterministic resolution. |
| D-3 | 2026-09-30 | Requirements are the source of truth; only Claude Code writes code. | Code is a derived artifact of specs and tests. |
| D-4 | 2026-09-30 | Traceability is 100% strict. | Every artifact must justify its existence and every requirement must be proven. |
| D-5 | 2026-09-30 | ~~Boot lives in its own repository, independent of other frameworks.~~ Superseded by D-8. | Reusable by anyone in their own repositories. |
| D-6 | 2026-09-30 | Next stage is offered as a one-click card, with a copy-paste boot prompt as fallback; each stage works on its own branch, merged at the gate. | Probe (OQ-13): a card appears and starts a session only when the offering session works in the same project folder; the new session runs in its own worktree/branch from the latest commit, so only committed handoffs are visible; a stage session can offer the next card itself; direct session start is not available. |
| D-7 | 2026-09-30 | ~~Stage sessions report back to one home session.~~ Reversed by D-14. | Owner wants one overview across stages; messaging between sessions is available. Cost kept low by short reports. |
| D-8 | 2026-09-30 | Boot and mlmd are one product; use the name mlmd. BR-21 withdrawn, D-5 superseded. | Frank and Alex are building the same thing and had no shared name; Alex's name is kept. |
| D-9 | 2026-09-30 | The primary user is a technical expert with Claude Code knowledge, the only required role; the business expert is optional, as customer or team member. BR-4, BR-7, BR-10, BR-16 revised; BR-27..BR-29 added; T1 closed. | Alex's process is proven on a real product; the gap is adoption. Whether the business expert is a customer (Alex's view) or a team member (Frank's) varies by project, so mlmd supports both. |
| D-10 | 2026-09-30 | Default business-expert mode is customer. | Owner's decision; matches Alex's proven practice, with team mode as an opt-in. |
| D-11 | 2026-09-30 | Resolve tensions T2, T3, T4, T6, T8, T12 with Alex's process: agent decisions confirmed at gates (BR-31); change requests only for product/design documents (BR-18); orphan-code gate (BR-20); concurrent collaborators (BR-32, OQ-19); only the decider changes trust (BR-33); adopt mlmd phases, withdraw S1/S2 (BR-14). | Owner's decisions, all within the business/adoption area (OQ-16 proposal). They keep Alex's proven flow where it does not conflict with one decider and strict traceability. |
| D-12 | 2026-09-30 | From Alex's reply: legacy systems go to PDD (BR-5); BOOT.md installs and starts the plugin (BR-1); Windows is supported, Frank tests (BR-34); plugin work is coordinated as shared work items, both PR to the public mlmd repo (T13). | Alex's answers to Frank's questions 2-5. PDD will be revised when a brownfield customer arrives, since its ceremony may be outdated. |
| D-13 | 2026-09-30 | No fixed token budget, keep cost low by design (BR-23); concurrent work via standard GitHub branches, PRs and merges (BR-32); operator = technical expert = final decider on one-person projects, technical expert is a software engineer or architect on teams (BR-35). | Owner's decisions. Fixed budgets would stop useful work; GitHub practice is known to every technical expert; one shared term set avoids drift with Alex's wording. |
| D-14 | 2026-09-30 | No home session; overview from plan + git at every session start and in dod (BR-26). Reverses D-7. | Costs no tokens, survives closed or archived sessions, works identically for a team, and is already part of mlmd's engine. |
