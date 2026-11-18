# Scoring definition

**Authority: proposal §3.7 and Table 8.** This file restates that definition
for implementation and records what follows from it. Where the two ever
differ, the proposal wins and this file is wrong.

Fixed before the T16 severity profiles depend on it. Building the engine is
still T20; this says what it must compute.

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
difference **is the measurement**. EQ1 is read inside one source. EQ2 is
agreement between two sources on the same runs.

This answers the question T16 left open — how a scenario the judge and the
human disagree about enters the total. It does not. It enters two totals, one
per source. There is no blended or consensus score anywhere in the analysis,
because a blend would average away the disagreement EQ2 exists to measure
while still looking like a result.

## 2. The unit, and the three verdicts

One **run** is one (scenario, version) pair. 47 scenarios × 4 versions = 188
runs.

A verdict is **ternary**, per §3.7: Satisfied (S), Not satisfied (N), or
**Uncertain (U)**. A scenario scores `s = 1` if S and `s = 0` if N. U is left
out of the score entirely and reported separately as an **uncertainty rate**.

U is not a failure of the judge. §3.8 requires that the judge "may answer
Uncertain when the evidence is insufficient", and the reason §3.7 gives for
excluding it is precise: *so that an evaluator cannot inflate or deflate a
score by guessing*. A judge forced to choose on thin evidence produces a
number that looks like a measurement and is not one.

There is no partial credit within S or N. Severity already carries the
weighting, and suites A and B can only pass or fail, so a graded axis would
have nothing to compare against.

## 3. The formulas

For one version under one source, let **J** be the scenarios judged S or N —
*not* the whole library — and let `w(i)` be scenario *i*'s severity weight,
assigned at T11 and frozen in `scenarios-v1`.

```
S_bin = |{i ∈ J : S}| / |J|

S_w   = Σ_{i ∈ J} w(i)·s(i) / Σ_{i ∈ J} w(i)      ( = Σ_{i ∈ S} w(i) / Σ_{i ∈ J} w(i) )

uncertainty rate = |{i : U}| / |{i : S, N or U}|
```

Weights, from Table 8, with this library's composition:

| Severity | n | Linear | Geometric |
|---|---|---|---|
| Critical | 8 | 4 | 8 |
| High | 15 | 3 | 4 |
| Medium | 19 | 2 | 2 |
| Low | 5 | 1 | 1 |
| **All 47 judged** | **47** | **120** | **167** |

The last row is the denominator only when every scenario returns S or N. **It
is not a constant.** Each U, and each run that produced no verdict, removes
that scenario's weight from the denominator as well as the numerator, so the
denominator is a property of the version-and-source, not of the library.

The critical gate stays a separate boolean (D-005): **true if any
critical-severity scenario is judged N.** A critical scenario judged U does
not raise the gate and does not lower it — it is reported in the uncertainty
rate, where a reader can see it.

## 4. Runs with no verdict, which is not the same as U

| Case | Cause | Effect |
|---|---|---|
| **U** | The judge looked and found the evidence insufficient | A verdict. Excluded from the score, counted in the uncertainty rate |
| **No evidence** | `runner_error`: no bundle exists to judge | Excluded for every source; counted and reported per version |
| **No usable verdict** | Invalid JSON after D-011 retries, or an unresolved quota failure | Excluded for the LLM judge only; counted and reported separately from U |

The three are reported separately because they mean different things. U is
the instrument working as designed; the other two are the instrument failing,
and a reader must be able to tell which.

**A missing verdict is never read as S.** Treating the judge's own failures as
evidence that the software is fine would bias precisely the direction EQ3 is
built to detect.

Because the denominator already moves with exclusions, the scores stay
well-defined. What they stop being is *comparable*: a version scored over 44
scenarios is not measured on the same instrument as one scored over 47. Where
exclusions differ across versions, the numbers are also reported on the
**common subset** — scenarios returning S or N in all four versions under that
source — with the subset size stated beside them.

## 5. Comparing sources

The human judges about 25 runs; the judge judges 188. **A human score and a
judge score are only comparable on the same runs.** Every source-to-source
comparison is computed on the intersection of the runs both judged, and the
report states which runs those were.

Both come out as proportions on the same scale, which makes comparing a
25-run score with a 188-run score an easy and invisible mistake.

## 6. Suites A and B as sources

A suite's verdict is per assertion, not per scenario. The mapping: a scenario
is **N** under suite A if any suite A test covering one of that scenario's
requirements fails, **S** otherwise. Requirements are the join, because they
are the only identifier both sides carry.

**A suite can never return U.** An assertion has no way to say the evidence
was insufficient — it passes or it fails. That asymmetry is itself part of
what EQ4 measures under D-013: the uncertainty rate is a column the suites
structurally cannot have, and the comparison has to be read knowing that.

The mapping is written down before the suites run against V1–V3, and never
adjusted afterwards.

## 7. What this does not settle

- The engine. Implementation, file formats and tests are T20.
- Confidence intervals. D-005 fixes Wilson for critical false acceptance; the
  rest is T28.
- The agreement statistic for EQ2 and its ceiling. D-004 and T27.
- **Whether the judge prompt currently offers U at all.** §3.8 requires it;
  the T18 smoke test recorded only `not_satisfied`. To be checked before T25.
