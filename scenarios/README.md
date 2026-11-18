# Scenario library — HOLDOUT

Nothing in this folder may ever be shown to the implementation model.

The library is built in Weeks 3–5 from the five use cases, validated against the
Appendix B checklist, categorized (normal / failure / edge / adversarial /
integration) and given a severity. Target: about 40–50 scenarios.

Frozen and tagged at the end of Week 5 (T12, C02). After that tag, no scenario
is added, removed, or reworded. If one has to change, the change is recorded in
`logs/decision-log.md` and reported as a threat to validity.

## Frozen — `scenarios-v1`, 17 November 2026

**47 scenarios. The library is closed.** From this tag onwards nothing here is
added, removed or reworded; a change that cannot be avoided goes in the
decision log and into the report's threats section.

| | |
|---|---|
| Scenarios | 47, from 74 candidates (T11: 27 rejected with reasons) |
| Category | normal 14 · failure 11 · edge 9 · adversarial 9 · integration 4 |
| Severity | critical 8 · high 15 · medium 19 · low 5 |
| Requirements | 29 of 30; R27 has none, for the reason in W03 |
| Steps | 363 across the library, 3 to 22 per scenario |

Every one of the 47 was executed end to end against V0 before the freeze, so
the library is known to run and not merely to validate. `validation.csv` was
brought into exact agreement with the YAML first: it had recorded one
requirement fewer than the scenario tested for ACC-01, ACC-06 and TSK-03. The
headline coverage of 29 of 30 is the same either way, because R21 and R23 are
also reached by other scenarios; what the correction fixes is which scenario
is on record as covering what.

The freeze comes before T16 by design. Seeded defects are chosen only after
this tag exists (D-012), so that no scenario can have been written to catch a
defect that was already known.
