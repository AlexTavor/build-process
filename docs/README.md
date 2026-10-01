# How mlmd is built

mlmd is built with its own process ([process.md](../process.md)), by hand until the plugin exists.
This folder holds the project's documents as the process defines them, so every assumption, spike
and decision is on the record.

- [assumptions.md](assumptions.md): what mlmd's design depends on that nobody has proved yet.
- [footguns.md](footguns.md): traps found on the way, where something looks like it does one
  thing and does another.
- [requirements.md](requirements.md): proposed requirements for the business side and adoption
  (roles, the decider, change requests, traceability), by Frank. Not yet agreed.
- [spikes/](spikes/): one document per spike, with the question, what would be a no, where it ran,
  what was done, and the verdict. The scripts each spike ran are in a folder next to its document.

The product is described so far in the repository's [README](../README.md) and in
[process.md](../process.md). mlmd's own Vision, behaviors and architecture documents haven't been
written yet.
