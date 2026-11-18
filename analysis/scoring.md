# Scoring definition

Fixed before the T16 severity profiles depend on it. This is the slice of T20
that T16 cannot proceed without — how a version's four numbers are computed.
Building the engine is still T20; this says what it must compute.

---

## 1. A version does not have a score

It has a score **per judgment source**. There are four:

| Source | Runs judged | Used for |
|---|---|---|
| Human reference (T26) | ~25, blind | EQ2, EQ3 ground truth |
| LLM judge (T25) | all 188 | EQ1, EQ2, EQ3 |
| Suite A | all, by assertion | EQ4 |
| Suite B | all, by assertion | EQ4 |

The same version scores differently depending on who judged it, and that
difference **is the measurement**. EQ1 is read inside one source: does
weighting change that source's ranking of the versions. EQ2 is agreement
between two sources on the same runs.

This answers the question T16 left open — how a scenario the judge and the
human disagree about enters the total. It does not. It enters two totals, one
per source. There is no blended or consensus score anywhere in the analysis,
because a blend would destroy the disagreement EQ2 exists to measure.

## 2. The unit, and the verdict

One **run** is one (scenario, version) pair. 47 scenarios × 4 versions = 188
runs.

A verdict is binary: satisfied or not satisfied. The judge is asked for
exactly that and returns it as JSON (D-010, D-011). There is no partial
credit and no graded satisfaction. Severity already carries the weighting; a
second graded axis would double-count it and make nothing comparable to suite
A or suite B, which can only pass or fail.

## 3. The four schemes

For one version, under one source, let **F** be the set of its scenarios
judged not satisfied. Weights come from each **scenario's** severity, assigned
at T11 and frozen in `scenarios-v1` — never from the severity of whatever
defect caused the failure.

| Severity | n | Binary | Linear | Geometric |
|---|---|---|---|---|
| Critical | 8 | 1 | 4 | 8 |
| High | 15 | 1 | 3 | 4 |
| Medium | 19 | 1 | 2 | 2 |
| Low | 5 | 1 | 1 | 1 |
| **Library total** | **47** | **47** | **120** | **167** |

Satisfaction, reported as a percentage, for each scheme *w*:

```
satisfaction_w = 100 × (W_w − Σ_{s ∈ F} w(s)) / W_w
```

where `W_w` is the library total above. The critical gate is a separate
boolean, never folded in (D-005): **true if any critical-severity scenario is
in F.**

Because `W_w` is the same for every version, ranking versions by satisfaction
is exactly the inverse of ranking them by failed weight. The worked example in
`defects/README.md` §4 uses failed weight and is unaffected; in satisfaction
terms the same pair reads:

| | Scenarios failed | Binary | Linear | Geometric |
|---|---|---|---|---|
| Version A | 4 critical, 4 high, 4 medium | 74.5% | 70.0% | 66.5% |
| Version B | 2 high, 6 medium, 6 low | 70.2% | 80.0% | 84.4% |

Binary calls A the healthier version; both weighted schemes call B healthier.
That inversion is what EQ1 reports.

## 4. Runs with no verdict

Two ways a run can fail to produce one, and they are not the same.

**No evidence.** The run carries a `runner_error`, so there is no bundle to
judge. Excluded from numerator and denominator, for every source, and the
count is reported per version.

**Evidence but no usable verdict.** Only the LLM judge can do this: invalid
JSON after the D-011 retries, or a quota failure that never resolved.
Excluded for that source only, with the count reported. A missing verdict is
never silently read as *satisfied* — that would turn the judge's own failures
into evidence that the software is fine, which is the single most dangerous
rounding error available here.

A step error inside an otherwise complete run is **not** a missing verdict.
The trace records it, the judge sees it, and the judge decides what it means.
That is the runner's whole posture: it records, it does not rule.

**If any run is excluded, denominators stop matching across versions**, and a
satisfaction percentage computed on 44 scenarios is not comparable with one
computed on 47. Where exclusions exist, the four numbers are also reported on
the **common subset** — the scenarios that produced a verdict in all four
versions under that source — and that subset's size is stated beside them.

## 5. Comparing sources

The human judges about 25 runs; the judge judges 188. **A human satisfaction
score and a judge satisfaction score are only comparable on the same runs.**
Every source-to-source comparison is computed on the intersection of the runs
both judged, and the report states which runs those were.

Reporting a 25-run human score against a 188-run judge score as though the two
were the same quantity would be a straightforward error, and it is an easy one
to make because both are percentages on the same scale.

## 6. Suites A and B as sources

A suite's verdict is per assertion, not per scenario, so mapping it onto the
scenario library is not free. The rule: a scenario is *not satisfied* under
suite A if any suite A test covering one of that scenario's requirements
fails. Requirements are the join, because they are the only identifier both
sides carry.

This mapping is lossy in both directions and that is a finding, not a defect
in the method — it is part of what EQ4 now measures under D-013. The mapping
is written down before the suites are run against V1-V3, and never adjusted
afterwards.

## 7. What this does not settle

- The engine. Implementation, file formats and tests are T20.
- Confidence intervals. D-005 fixes Wilson for critical false acceptance;
  the rest of the interval reporting is T28.
- The agreement statistic for EQ2 and its ceiling. That is D-004 and T27.
