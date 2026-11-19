# Seeded defect registry

Written before building, per `README.md` §6, and **revised once during step 4**
when the first build falsified two predictions. §7 of this file records what
changed and why; the revision is dated and kept rather than overwritten.

Selection began only after the library was frozen at `scenarios-v1` (D-012),
and no defect was chosen or rejected by reference to what suite A or suite B
covers (§1).

---

## Summary

| | Defects | Critical | High | Medium | Low | Failing runs | Gate |
|---|---|---|---|---|---|---|---|
| V1 | 7 | 0 | 3 | 7 | 0 | 10 | clear |
| V2 | 3 | 4 | 2 | 0 | 0 | 6 | **FLAGGED** |
| V3 | 4 | 5 | 3 | 0 | 0 | 8 | **FLAGGED** |

**14 defects, 24 failing runs, 9 critical failures.**

| | Binary | Linear | Geometric |
|---|---|---|---|
| V1 | 0.787 | 0.808 | **0.844** |
| V2 | **0.872** | **0.817** | 0.761 |
| V3 | 0.830 | 0.758 | 0.689 |

```
binary      V2 > V3 > V1
linear      V2 > V1 > V3
geometric   V1 > V2 > V3
```

Three different orderings, so EQ1 has an answer under every view. **Binary
ranks V2 the healthiest of the three while the critical gate condemns it** —
proposal §3.7's single score hiding a security failure, produced by
construction.

- **V1 — sloppy but safe.** Ten failures, none critical. Binary ranks it worst, geometric ranks it best.
- **V2 — insecure but tidy.** Six failures, four critical. Binary and linear both rank it best; the gate condemns it.
- **V3 — broken throughout.** Eight failures, five critical. Geometric ranks it worst.

## Verification (§7)

Built on branches `defect/v1`, `defect/v2`, `defect/v3` from the commit
carrying the same `app/server.js` as tag `v0`; only `server.js` is touched.
All 47 scenarios were executed against each version and against a V0 baseline,
and each version's traces compared with V0's scenario by scenario.

| | Predicted | Manifested | Predicted but unchanged | Step errors |
|---|---|---|---|---|
| V1 | 10 | 10 | none | 0 |
| V2 | 6 | 6 | none | 0 |
| V3 | 8 | 8 | none | 0 |

Every defect manifests in every scenario predicted for it, and no scenario
predicted to change was unaffected.

### Evidence footprint is wider than the failure set

Some scenarios' evidence changed without their expected behaviour being
violated. These are recorded, not counted as failures, and **not pre-judged**
— whether they are satisfied is for the judge and the human reference to
decide, which is the measurement.

| Version | Also changed | Why |
|---|---|---|
| V2 | ACC-02, ACC-03, ACC-04 | D2-02 returns 403 where V0 returned 404. The write is still refused and bob's task is still unchanged, which is what those scenarios require. |
| V2 | SES-03, SES-04, REG-07, REG-09, REG-12 | D2-01 changed the sign-in failure message. Every one of these still refuses the attempt and creates no session. |
| V3 | INT-02 | D3-03 removed the delete confirmation. The task is still deleted, which is what INT-02's sequence requires. |

That eight of V2's fourteen changed traces are not intended failures is worth
stating plainly in the report: a defect's evidence footprint and its failure
set are different things, and only the second is ground truth.

---

## V1 — seven defects, none critical

| Id | Req | Defect severity | Location | Change | Predicted = observed |
|---|---|---|---|---|---|
| D1-01 | R11 | high | `POST /tasks/:id/toggle` | status toggled in memory, `writeDb` not called | TSK-15, INT-02 |
| D1-02 | R10 | high | `POST /tasks/:id/edit` | `Object.assign` runs, `writeDb` not called | TSK-13, INT-02 |
| D1-03 | R23 | medium | `POST /tasks/:id/edit` | the validation guard is skipped on edit | TSK-20, TSK-14 |
| D1-04 | R8 | medium | `validateTask` | `len(title) > 100` became `>= 100` | TSK-05 |
| D1-05 | R26 | medium | `validateTask` | `isValidDate` no longer called | TSK-10, TSK-11 |
| D1-06 | R14 | medium | `GET /tasks` | search matches titles only | LST-05 |
| D1-07 | R4 | medium | `POST /signin` | username matched case-sensitively | SES-02 |

D1-03's severity differs from its scenario's: medium as a defect — wrong input
accepted, recoverable — but TSK-20 is high, because it tests that the rule
holds on the server and not only in the form.

## V2 — three defects, four critical scenarios

| Id | Req | Defect severity | Location | Change | Predicted = observed |
|---|---|---|---|---|---|
| D2-01 | R5 | critical | `POST /signin` | the failure message names which of the two went wrong | SES-05 |
| D2-02 | R25 | critical | `app.param('id')` | 403 when the task exists but belongs to someone else | ACC-01, ACC-06 |
| D2-03 | R7 | critical | the R7 public set | `GET /tasks` added to the public set | SES-08, SES-07, SES-13 |

## V3 — four defects, five critical scenarios from one of them

| Id | Req | Defect severity | Location | Change | Predicted = observed |
|---|---|---|---|---|---|
| D3-01 | R21 | critical | `app.param('id')` | `&& t.ownerId === req.user.id` removed | ACC-01, ACC-02, ACC-03, ACC-04, ACC-06 |
| D3-02 | R28 | high | the R28 header middleware | `Cache-Control: no-store` no longer set | SES-13 |
| D3-03 | R12 | low | `POST /tasks/:id/delete` | the confirmation flash is not set | TSK-17 |
| D3-04 | R20 | critical | `GET /tasks` | a non-empty search runs over all tasks | ACC-08 |

One dropped clause in D3-01 fails five critical scenarios — the largest single
lever in the library, and an ordinary mistake.

D3-02 is only visible because D-014 made the collector record response
headers. Before that change this defect would have been invisible to the judge.

D3-03 is the case §4 is about: a cosmetic defect, low by Table 8, failing a
high-severity scenario. Scoring weights the scenario; EQ1 compares against the
defect.

---

## §7 — the step 4 revision

Two defects in the first build reached much further than predicted, and both
were replaced on 19 November, before any judged run.

**Replaced: R6, sign-out does not destroy the session.** Intended to fail
SES-07 and SES-13. It failed those and also broke ACC-10, INT-01, REG-01,
REG-04, REG-05, REG-10 and REG-12, because a still-valid session makes R29
redirect `/signin` to `/tasks`, so the harness's `sign_in` helper finds no
form and times out. **Ten scenarios hit a 30-second Playwright timeout,
including ACC-02, ACC-03 and ACC-04** — which meant three of V3's five
critical scenarios were failing on a broken setup rather than on the ownership
defect they exist to test. That corrupts the evidence V3 is for, and breaks
§7's requirement that all 47 execute without a runner error.

There is no narrow version of this defect. Any sign-out that leaves the
session usable breaks every scenario that signs out and back in, because of
the R29 redirect. Replaced by the R28 header defect, which fails SES-13
cleanly.

**Replaced: R2, username uniqueness case-sensitive.** Same shape, one
scenario: REG-03 registers "ALICE", the duplicate is now accepted, the account
is signed in, and the scenario's later `/signin` navigation is redirected to
`/tasks`, so the fill timed out. Replaced by the R4 case-sensitive sign-in
defect, which fails SES-02 with no navigation side effect.

**The general lesson, for the report.** A defect that changes authentication
state breaks the harness's navigation, not just the scenario under test. The
failure looks like a scenario failure and is not one. Nothing in the
admissibility criteria of §2 catches this; the criterion it most resembles is
"one localized change", and both defects were exactly that. Found only by
building and running, which is the argument for step 4 existing at all.

---

## Results — filled in after judging

| Defect | Suite A | Suite B |
|---|---|---|
| D1-01 | | |
| D1-02 | | |
| D1-03 | | |
| D1-04 | | |
| D1-05 | | |
| D1-06 | | |
| D1-07 | | |
| D2-01 | | |
| D2-02 | | |
| D2-03 | | |
| D3-01 | | |
| D3-02 | | |
| D3-03 | | |
| D3-04 | | |
