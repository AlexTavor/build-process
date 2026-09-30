# Unhandled issues

Issues found outside the task that found them. One entry per issue, appended at the end. The
commit that fixes an issue deletes its entry.

## Superseded drafts in PersonalKB don't say they are superseded

- Date: 2026-09-30
- Where: `~/PersonalKB/drafts/greenfield-process.md`, `~/PersonalKB/drafts/superpowers-layer-plan.md`
- What is wrong: `process.md` supersedes both. The first was replaced by the 2026-09-29 restart,
  and the second by the decision not to build on Superpowers. Neither file says so.
- What it breaks: a session that finds them can take a dropped plan for the current one.
- Branch: main
