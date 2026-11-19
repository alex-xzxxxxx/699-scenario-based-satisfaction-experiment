# T16 step 2 — severity profiles for V1, V2, V3

Fixed before any defect is chosen, per `README.md` §4. A profile is a **target
set of failing scenarios by severity**, not a set of defects. Step 3 selects
defects to meet these targets.

Scores below follow `analysis/scoring.md` and assume every scenario returns S
or N. Any Uncertain verdict moves the denominators, so these are design
targets, not predictions of the reported numbers.

---

## 1. What the library allows

A defect's reach is bounded by how many scenarios share the requirement it
breaks. Computed from the frozen library:

| Requirement | Scenarios it can fail | Severities |
|---|---|---|
| **R21** ownership check | ACC-01, ACC-02, ACC-03, ACC-04, ACC-06 | **5 critical** |
| R8 title/description bounds | 7 scenarios | 2 high, 5 medium |
| R1 registration rules | 6 scenarios | 2 high, 2 medium, 2 low |
| R13 list scoping | ACC-10, INT-01, LST-01, LST-02 | 1 critical, 2 high, 1 medium |
| R5 sign-in messages | SES-03, SES-04, SES-05 | 1 critical, 2 high |
| R23, R9, R10 | 3 each | mixed |
| R17, R18, R19, R24, R25, R7 | 1 each | **1 critical each** |
| R2, R6, R16, R28, R29, R30 | 1 each | 1 non-critical each |

Two facts drive everything below.

**One R21 defect fails five critical scenarios.** A single dropped ownership
check — entirely plausible as a real mistake — is the cheapest route to the
critical failures D-005 requires. R17, R18, R19, R24, R25 and R7 are the
precision instruments: one critical each, when five is too many.

**Low-severity failures are the most expensive thing to build.** The library
has only five low scenarios and each sits on a different requirement, so each
costs its own defect. Mediums come two per defect (R26, R14, R3, R8 bounds).

## 2. A correction to README §5

§5 estimated "a defect typically shows up in two or three scenarios, so four
to six defects per version gives roughly ten to fifteen such runs per version,
thirty to forty-five in total."

**That estimate was wrong**, and the table above is why. Most requirements are
referenced by one or two scenarios, not three. Outside the R21 lever, a defect
buys one or two failing runs, not two or three. Reaching ten failures in a
version costs six or seven defects, not four to six — and EQ3's denominator
lands near thirty across the study, not forty-five.

The estimate was made before the coupling was computed. It is corrected here
rather than quietly dropped, because the defect budget it implied was the
input to how much Week 5 and Week 6 were expected to carry.

## 3. The binding constraints

| Source | Constraint |
|---|---|
| D-005 | The human subset needs ≥8 critical-severity runs, **≥4 known-failing**. So the three versions must produce ≥4 critical failures between them. |
| README §4 | The four views must not all order the versions identically. |
| README §4 | The versions must differ in the known severity of their seeded defects. |
| README §5 | Each version is V0 plus its own set, derived independently from tag `v0`. |

The D-005 minimum is the one that nearly got missed. An earlier draft of these
profiles produced a single critical failure in the whole study, which satisfies
every stated design goal and quietly makes the Wilson interval on critical
false acceptance uncomputable.

## 4. Recommended profiles

| | Critical | High | Medium | Low | Failing runs | Defects (est.) | Gate |
|---|---|---|---|---|---|---|---|
| **V1** | 0 | 4 | 6 | 1 | 11 | ~6 | false |
| **V2** | 5 | 0 | 6 | 1 | 12 | ~5 | **TRUE** |
| **V3** | 5 | 4 | 0 | 0 | 9 | ~3 | **TRUE** |

Totals: **32 failing runs, 10 critical failures, ~14 defects.**

Resulting scores, against a notional perfect V0:

| | Binary | Linear | Geometric |
|---|---|---|---|
| V1 | 0.7660 | 0.7917 | 0.8263 |
| V2 | 0.7447 | 0.7250 | 0.6826 |
| V3 | **0.8085** | 0.7333 | 0.6647 |

**Three different orderings, healthiest first:**

```
binary      V3 > V1 > V2
linear      V1 > V3 > V2
geometric   V1 > V2 > V3
```

Every view disagrees with every other about something, which is what EQ1 needs
to have an answer.

**The case the proposal is about.** Binary ranks V3 the *healthiest* of the
three, and the critical gate flags V3 as unacceptable. Proposal §3.7: "A single
score can therefore hide a security failure." The design produces that case
rather than hoping for it.

## 5. Why not cheaper, and why not larger

| Design | Defects | Failing runs | Critical failures | Gate hides a failure |
|---|---|---|---|---|
| Lean | 7 | 16 | 5 | no |
| **Recommended** | **14** | **32** | **10** | **yes** |
| Larger | 21 | 33 | 4 | yes |

The 21-defect design is dominated: half again the build work for one more
failing run and *fewer* critical failures. Discard it.

The lean design is a real fallback if Weeks 5–6 run short. It costs 7 defects
because its V3 is a single R21 defect. Two things to accept with it: EQ3's
denominator halves to 16, and V3 rests on one defect, so if that defect does
not manifest exactly as predicted the version is empty and there is nothing to
fall back on.

## 6. What step 3 must still check

- **The cost column is an estimate from the coupling map, which is an upper
  bound on reach.** A defect breaking one clause of a requirement may fail
  fewer scenarios than the table allows — for example an R1 defect that
  mistreats usernames fails REG-04 but not REG-12. After defects are chosen,
  recompute the profile from the actual `predicted_scenarios` and confirm the
  three orderings survive. If they do not, the defects change, not the
  scoring.
- **V0's baseline is unmeasured.** The 47 scenarios have been executed against
  V0 but never judged, so V0 is not known to score 1.0. These profiles are
  deltas. If V0 already fails a scenario a profile relies on, that slot is
  already spent and the arithmetic shifts.
- **V2 and V3 both carry an R21 defect** under the recommendation. That is
  legitimate — versions are independent — but it means the same five critical
  scenarios fail in both, so the critical evidence is less varied than the
  count of ten suggests. Worth stating in the report; worth revisiting in step
  3 if a different critical lever is cheap enough to swap in.
