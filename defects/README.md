# T16 — seeded defect design

**The rules below are fixed before any defect is chosen.** That ordering is the
point of this file. Choosing defects first and describing the method afterwards
would let the method drift to fit whatever was convenient, and nothing in the
write-up could rule that out. Same argument as D-004 and the `prereg-w01` tag,
applied one level down.

Nothing here names a defect. Selection begins only after the library is frozen
and tagged (T12), as D-012 requires.

---

## 1. The rule that matters most

**Defects are chosen from the requirements and from the v1.1 ambiguity list,
without reference to what suite A or suite B covers.**

The temptation is obvious: pick defects the suites miss, and the scenario
method looks good. That would answer EQ4 by construction and the result would
be worthless. Whether a given defect is caught by suite A, by suite B, by both
or by neither is **a result, recorded after the fact**, never a criterion for
selecting it.

The same applies in reverse. A defect is not rejected for being easy to catch.
If every seeded defect turns out to be caught by suite A, that is a finding
about the scenario method, and it gets reported.

## 2. What may be a seeded defect

All seven must hold:

1. **It violates one named requirement.** The registry records the R-number.
   A change that breaks nothing identifiable is a mutation, not a defect.
2. **It is reachable through the interface** by at least one scenario in the
   frozen library. A defect no method can observe repeats the mistake T11
   rejected INT-04 for.
3. **It is one localized change** — one route, one function, one condition.
   Two defects in one patch cannot be attributed separately.
4. **It is a mistake a competent developer could make.** A dropped ownership
   check, an off-by-one bound, a validation that runs in the browser but not
   on the server. Not sabotage, not a deliberate trap. External validity
   depends on this: the study claims something about reviewing real software.
5. **The application still starts and `npm run reset` still works.** A defect
   that prevents startup makes every scenario fail at once and destroys the
   run rather than testing it.
6. **It does not touch the harness contract** — the test ids in §3 or the
   routes in §4. Those are how the runner addresses the application. Changing
   them breaks every scenario for a reason that has nothing to do with the
   defect.
7. **It does not identify its own version.** No version string, no changed
   wording that exists only to mark the build. See §7.

## 3. What may not

- A defect in a requirement no frozen scenario exercises. R27 is the known
  case: nothing deletes a user, so nothing can test it.
- A defect that only manifests intermittently. Table B4 item 5 ruled out
  unreliable scenarios; the same standard applies to what they run against.
- A performance or styling change. The study measures requirement
  satisfaction, not speed or appearance.
- Anything that changes `data/db.json`'s seed content. Every scenario resets
  to the §5 state and compares against it; changing the seed changes the
  expected behaviour of scenarios that are now frozen.

## 4. Severity profiles, and why EQ1 depends on them

EQ1 asks whether the weighting scheme changes the ranking of versions. **If
the versions are built carelessly, EQ1 cannot be answered at all** — the two
schemes will simply agree, and the question has no data.

Table 8 weights:

| Severity | Linear | Geometric |
|---|---|---|
| Critical | 4 | 8 |
| High | 3 | 4 |
| Medium | 2 | 2 |
| Low | 1 | 1 |

Geometric separates critical from high by a factor of two where linear
separates them by a third. So the schemes disagree whenever one version
carries its weight in a few severe defects and another carries it in more mild
ones. The smallest disagreement:

| | Defects | Linear total | Geometric total |
|---|---|---|---|
| Version A | 1 critical | 4 | 8 |
| Version B | 1 high + 1 medium | 5 | 6 |

Linear ranks B worse; geometric ranks A worse. A more robust pair:

| | Defects | Linear total | Geometric total |
|---|---|---|---|
| Version A | 2 critical | 8 | 16 |
| Version B | 3 high | 9 | 12 |

**Requirement: the three severity profiles are fixed before any defect is
chosen, and at least one pair of versions must rank differently under the two
schemes.** Then defects are selected to fit the profiles, not the other way
round.

**This must be disclosed, and it limits the claim.** The disagreement is
constructed, not discovered. The finding can therefore never be "the two
schemes often disagree" — only "where they disagree, here is what happens to
the ranking, and here is whether the judge tracks it." Reporting a manufactured
disagreement as an empirical frequency would be a serious misreading of the
design, and the report says so in the same place it reports EQ1.

**Open, to settle against T20 before profiles are fixed:** the tables above
assume a version's score moves with the summed weight of the scenarios it
fails. If T20's scoring engine composes weights differently, the arithmetic
changes and the profiles must be recomputed against the real formula. The
principle does not change.

## 5. How many

Each version is **V0 plus its own defect set**, derived independently from tag
`v0`. Not cumulative: if V3 contained V1's and V2's defects as well, no
observation could be attributed to one version's set.

The count is driven by EQ3, which measures how often a judge accepts software
that is broken. Its denominator is the number of (scenario, version) pairs
where a defect actually manifests — not the number of defects, and not the 141
defective runs. A defect typically shows up in two or three scenarios, so four
to six defects per version gives roughly ten to fifteen such runs per version,
thirty to forty-five in total.

That is a workable denominator and a wide confidence interval. **Say so in the
report rather than quoting a false-acceptance rate to two decimal places.**
The number is small because every defect is placed and verified by hand, which
is also what makes the ground truth trustworthy.

## 6. The registry

One row per defect in `defects/registry.md`, written **before** the version is
built:

| Field | Written when | Notes |
|---|---|---|
| `defect_id` | at design | D1-01, D2-01, … by version |
| `version` | at design | V1, V2 or V3 |
| `requirement` | at design | the R-number violated |
| `severity` | at design | from Table 8, with the sentence justifying it |
| `location` | at design | file and function |
| `change` | at design | one sentence: what the code now does instead |
| `predicted_scenarios` | at design, **before any run** | which frozen scenarios should expose it |
| `observed_scenarios` | after the run | which actually did |
| `suite_a` / `suite_b` | after the run | caught or missed — a result, per §1 |

`predicted_scenarios` is the part worth the effort. Recording it before the run
makes the design falsifiable: a defect that no predicted scenario catches, or
one that trips scenarios nobody expected, is itself a finding about how much
scenario coverage is worth. Predictions are never revised after a run, and the
scenarios are frozen and cannot be adjusted to match.

## 7. Build and verification

Each version branches from tag `v0` so that the only difference from V0 is its
registered defects.

Before any judged run, for each of V1, V2, V3:

- `git diff v0 -- app/` shows exactly the registered changes and nothing else.
- The application starts and `npm run reset` restores the §5 seed state.
- Every one of the 47 scenarios executes without a runner error. A scenario
  that cannot run produces no evidence to judge.
- Each defect is confirmed to manifest at least once, by reading the evidence
  from its `predicted_scenarios`. **A defect assumed rather than observed is
  not ground truth**, and the whole study rests on this being right.
- No bundle contains a version word or an absolute path (already enforced by
  the collector's scrubbing, re-checked here because it is cheap).

## 8. Blinding

Evidence from V1, V2 and V3 must be indistinguishable from V0's except through
the behaviour the defect causes. Run ids are random, the version is only in
`data/run_manifest.jsonl`, and that file is never committed.

**One weakness is disclosed rather than solved.** The human reference judge has
seen V0 pass both suites and has read its evidence repeatedly. A blind bundle
in which everything behaves correctly is therefore probably V0, and the judge
may guess as much. This does not change what the evidence shows, and the
judgment is made against the scenario's expected behaviour rather than against
a remembered version — but "blind to version" is weaker here than the phrase
suggests, and the report says so.

## 9. Order of work

1. Confirm the scoring arithmetic in §4 against T20.
2. Fix the three severity profiles. Record them.
3. Only then select defects to fit the profiles, under §1-§3.
4. Register each one, including `predicted_scenarios`, before building.
5. Build V1, V2, V3 from tag `v0`.
6. Verify, per §7.
7. Tag each version.

Steps 2 and 3 are in that order on purpose, and the registry's commit dates
are what show it.

## 10. Deliberately not decided here

- Which defects. That is step 3, after the library is frozen.
- The scoring engine. That is T20.
- Whether V1, V2 and V3 differ in defect count as well as severity profile.
  Settled at step 2, once the arithmetic in §4 is confirmed.
