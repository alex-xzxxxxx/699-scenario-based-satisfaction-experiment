# T11 — scenario validation

**HOLDOUT. Never shown to the implementation model.**

Every one of the 74 candidates in `candidates.md` judged against the five
items of Appendix B Table B4. Category and severity confirmed against
Table B3 and Table 8. Machine-readable in `validation.csv`.

**47 accepted, 27 rejected.** Severity was assigned when each scenario was
drafted, before any result existed, and T11 changed none of it.

## The checklist, as Table B4 states it

| # | A scenario is kept only if… |
|---|---|
| 1 | its expected behaviour is observable in the evidence |
| 2 | two readers would agree what satisfied means |
| 3 | it is not a duplicate of another scenario |
| 4 | it is traceable to the requirements document |
| 5 | it can be executed reliably by the runner |

Item 4 is why every row carries requirement ids: EQ4 compares scenario
coverage against suite A and suite B, which is only possible if each
scenario names the requirement it exercises.

## Distribution of the accepted set

| Category | Accepted | Share | Table B3 target |
|---|---|---|---|
| Normal | 14 | 30% | 30% |
| Failure | 11 | 23% | 25% |
| Edge | 9 | 19% | 20% |
| Adversarial | 9 | 19% | 15% |
| Integration | 4 | 9% | 10% |
| **Total** | **47** | | |

**Adversarial sits at 19% against a planned 15%, and this is deliberate.**
Table B3 says "about 15%". The critical gate in D-005 and the false-acceptance
measurement in EQ3 both rest entirely on this category, and pruning it to
seven scenarios to hit a round number would have cost coverage of R18, R20
or R25. Integration is correspondingly a point and a half light. Recorded
here rather than left for a reader to notice.

## Severity of the accepted set

| Severity | n | Linear | Geometric |
|---|---|---|---|
| Critical | 8 | 4 | 8 |
| High | 15 | 3 | 4 |
| Medium | 19 | 2 | 2 |
| Low | 5 | 1 | 1 |

The 8 critical scenarios are ACC-01, ACC-02, ACC-03, ACC-04, ACC-06, ACC-10, SES-05, SES-08. Every one of them
either reaches another user's data or breaks login security, which is what
Table 8 reserves the level for. Across four versions they give 32 critical
runs, comfortably above the 8 that D-005 pre-specified for the human subset.

A scenario marked critical that is not a security or data-isolation failure
would quietly break two things at once: the gate would fire on versions that
merely mishandle input, and every weighted score would shift, which is the
subject of EQ1.

## Requirement coverage

29 of the 30 requirements have at least one accepted scenario.

**R27 has none.** No route deletes a user, so a session naming a user who no
longer exists cannot be produced through the interface. Suite B leaves it
uncovered for the same reason. V0 implements it regardless, with a random
per-account token. Recorded as a gap, not papered over.

## Rejections

27 rejected. Grouped by the item that failed.

### B4#1 observable in the evidence — 1

| ID | Category | Why |
|---|---|---|
| INT-04 | integration | Exercises the harness's own reset rather than the application. Every scenario already resets, so this is not observable as application behaviour. |

### B4#3 not a duplicate — 20

| ID | Category | Why |
|---|---|---|
| ACC-05 | adversarial | R18 is covered by ACC-02; the edit page adds no distinct authorisation path. |
| ACC-07 | adversarial | Same R25 comparison as ACC-06, over POST rather than GET. Flagged as an overlap when drafted. |
| ACC-09 | adversarial | Enumerating ids is what ACC-06 already demonstrates under R25. |
| INT-03 | integration | Create then find is covered by INT-02 together with LST-04. |
| LST-03 | normal | Same user action as LST-01. Which fields a row shows is observable inside LST-01's evidence. |
| LST-06 | edge | Case-insensitivity is part of what LST-04 exercises under R14. |
| LST-10 | normal | Symmetric with LST-09. R15 is one filter; the second value adds no distinct behaviour. |
| LST-12 | integration | Search and filter combined; both mechanisms are covered by LST-04 and LST-09. |
| LST-13 | failure | Same empty state as LST-14. R16 names both causes; one run shows the behaviour. |
| REG-02 | failure | Subsumed by REG-03, which exercises the case-insensitive rule R2 actually states. |
| REG-13 | adversarial | Server-side enforcement of R22 and R23 is covered by TSK-20. |
| SES-06 | edge | The password-not-trimmed asymmetry is already the point of REG-12. |
| SES-09 | adversarial | R7 is covered by SES-08. |
| SES-10 | edge | R7 for unknown paths is covered by SES-08. |
| SES-12 | normal | Same requirement and same mechanism as SES-11; /register adds nothing over /signin. |
| TSK-07 | edge | Same trim rule as REG-04, on a different field. |
| TSK-09 | failure | Same over-length rejection mechanism as TSK-06, on a different field. |
| TSK-16 | normal | The reopen half of TSK-15. R11 is one mechanism and one run shows both directions. |
| TSK-18 | edge | The shown-once half of TSK-17. One run covers both. |
| TSK-19 | adversarial | Server-side enforcement of R22 and R23 is covered by TSK-20. |

### none - distribution — 6

| ID | Category | Why |
|---|---|---|
| LST-07 | adversarial | Distribution. Literal-text handling under R14 remains in LST-04 and LST-05. |
| LST-08 | edge | Distribution. R14 stays covered by LST-04 and LST-05. |
| REG-06 | edge | Distribution. The length boundary is exercised by REG-05. |
| REG-08 | failure | Distribution. R3 stays covered by REG-07 and REG-09. |
| REG-11 | failure | Distribution. R3 stays covered by REG-07 and REG-09. |
| TSK-12 | edge | Distribution. R26 stays covered by TSK-10 and TSK-11. |

Rejections marked *distribution* failed no checklist item. They were sound
scenarios cut to bring the set toward Table B3, and in every case the
requirement they covered remains covered by another accepted scenario. They
are separated from the checklist failures so that the two are not confused:
one is a judgment about the scenario, the other about the shape of the set.

## What T11 did not do

No scenario was rewritten. T11 accepts or rejects; changing wording would
mean re-judging something that was never drafted. Where a rejection noted a
gap worth widening — LST-04's search scope, for instance — that is a note for
T15, not an edit made here.

No decision was made by running a scenario against V0. The checklist is
answered from the scenario text and the requirements document. A scenario
kept or dropped because of how V0 behaves would be a scenario tuned to the
system it is meant to judge.

## Next

T15 scripts all 47 as YAML in `scenarios/library/`, normal cases first as the
risk register requires. T12 then freezes and tags the library.
