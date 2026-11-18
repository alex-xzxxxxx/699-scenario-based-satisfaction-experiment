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

**What a version scores is not a property of its defects.** D-005 computes
four schemes per version — binary, linear 4-3-2-1, geometric 8-4-2-1, and the
critical gate as a separate flag — over the **scenarios the version fails**,
weighted by **each scenario's own severity**, which T11 assigned and `v0`
froze. A defect is only the cause. The lever this section controls is
therefore *which frozen scenarios a version breaks*, and the library already
fixes what each is worth:

| Severity | Scenarios in the library | Binary | Linear | Geometric |
|---|---|---|---|---|
| Critical | 8 | 1 | 4 | 8 |
| High | 15 | 1 | 3 | 4 |
| Medium | 19 | 1 | 2 | 2 |
| Low | 5 | 1 | 1 | 1 |

The eight critical scenarios are ACC-01, ACC-02, ACC-03, ACC-04, ACC-06,
ACC-10, SES-05 and SES-08. Four of them turn on the ownership check in R21, so
a single defect there moves a version's critical count by four at once. That
is the largest single lever in the library and it is easy to pull by accident.

### The comparison EQ1 actually makes

Proposal §3.7, closing sentence: **EQ1 asks which of the views — binary,
linear, geometric, critical gate — best separates the seeded-defect versions
from V0, and which best matches the known severity of their defects.**

That is not "does weighting change the answer". It is a comparison of four
views against a reference, and **the reference is the seeded defects
themselves**. Two things follow, and both are constraints on this file rather
than on the analysis:

1. **The views must disagree somewhere.** If all four order the versions
   identically, "which separates best" has no discriminating case and EQ1
   returns nothing. The disagreement has to be built in.
2. **The defect severities must vary across versions.** "Matches the known
   severity of their defects" is only testable if the versions differ in that
   known severity. This is why §6 records a defect's own Table 8 severity:
   it is EQ1's ground truth, not bookkeeping.

Note which views split in the proposal's own illustration. One version fails
a single critical scenario, another fails five low ones; binary *and* linear
both rank the first higher, and only geometric reverses. So the useful
requirement is that the views disagree — not specifically that binary
inverts against the weighted pair.

Binary counts failures; the weighted schemes care what failed. They part
company when one version fails fewer but more severe scenarios than another
(the table below assumes every scenario returned S or N; any Uncertain
verdict changes the denominators, per `analysis/scoring.md` §3):

| | Scenarios failed | Binary | Linear | Geometric |
|---|---|---|---|---|
| Version A | 4 critical, 4 high, 4 medium | 12 | 36 | 56 |
| Version B | 2 high, 6 medium, 6 low | 14 | 24 | 26 |

Binary ranks B worse. Both weighted schemes rank A worse. That inversion is
the observation EQ1 exists to make, and it survives realistic counts — these
are the ten-to-fifteen failing runs per version that §5 arrives at
independently.

A secondary question is whether the two weighted schemes agree with each
other. They part company less easily, since geometric only doubles the gap
above medium:

| | Scenarios failed | Linear | Geometric |
|---|---|---|---|
| Version A | 2 critical | 8 | 16 |
| Version B | 3 high | 9 | 12 |

**Requirement: the three profiles are fixed before any defect is chosen; the
four views must not all order the versions identically; and the versions must
differ in the known severity of their seeded defects.** Which views split is
not prescribed — binary against the weighted pair, or geometric against the
other three as in the proposal's illustration, both give EQ1 its
discriminating case.

Because the profiles are expressed as target sets of failing scenarios, and
`predicted_scenarios` in §6 records the same thing per defect, the two must
agree before a version is built. A defect set whose predictions do not add up
to its version's profile means one of the two is wrong.

**This is constructed, and it bounds the claim.** The inversion is designed in,
not discovered. EQ1 may therefore never report that weighting "often" changes
conclusions — only that where it does, here is what happens to the ranking and
whether the judge tracks it. Reporting a manufactured inversion as an empirical
frequency would misread the design, and the report says so where it reports
EQ1.

**Still open, to settle before profiles are fixed:** whether T20 sums scenario
weights as assumed above, and how a scenario the judge and the human disagree
about enters the total. The principle is unaffected; the arithmetic is not.

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
| `severity` | at design | the **defect's** own Table 8 severity, with the sentence justifying it. This is EQ1's ground truth — the "known severity" the four views are judged against — so it is load-bearing, not a label. Distinct from the severities of the scenarios it breaks, which are what §4 scores. They usually agree; where they do not, say so in the row, because a low-severity defect that breaks a critical scenario is exactly the case that separates the views |
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

1. Confirm the scoring arithmetic in §4 against T20. T20 does not exist yet,
   so this means settling how a version's four totals are computed before the
   profiles depend on them — a slice of T20 pulled earlier than planned.
2. Fix the three profiles, as target sets of failing scenarios by severity,
   with the binary inversion of §4 present. Record them.
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
