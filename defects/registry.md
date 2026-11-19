# Seeded defect registry

Written **before** V1, V2 and V3 are built, per `README.md` §6. Selection
began only after the library was frozen at `scenarios-v1` (D-012).

`predicted_scenarios` is recorded here before any run. It is never revised
afterwards, and the scenarios are frozen and cannot be adjusted to match.
`observed_scenarios` and the suite columns are filled in after the runs, as
results.

**Defects were chosen without reference to what suite A or suite B covers**
(§1). Whether a suite catches one is a result, recorded below after the fact.

---

## Summary

| | Defects | Critical | High | Medium | Low | Failing runs | Gate |
|---|---|---|---|---|---|---|---|
| V1 | 7 | 0 | 4 | 6 | 0 | 10 | clear |
| V2 | 3 | 4 | 0 | 0 | 0 | 4 | **FLAGGED** |
| V3 | 4 | 5 | 4 | 0 | 0 | 9 | **FLAGGED** |

**14 defects, 23 failing runs, 9 critical failures.**

Scores, assuming every scenario returns S or N:

| | Binary | Linear | Geometric |
|---|---|---|---|
| V1 | 0.787 | 0.800 | **0.832** |
| V2 | **0.915** | **0.867** | 0.808 |
| V3 | 0.809 | 0.733 | 0.665 |

```
binary      V2 > V3 > V1
linear      V2 > V1 > V3
geometric   V1 > V2 > V3
```

Three different orderings, so EQ1 has an answer under every view. **Binary
ranks V2 the healthiest version of the three at 0.915, and the critical gate
flags it as unacceptable** — V2 fails only four scenarios, and all four are
critical. That is proposal §3.7's "a single score can hide a security failure",
produced by construction.

The three versions are deliberately different in kind:

- **V1 — sloppy but safe.** Ten failures, not one of them critical. Binary
  ranks it worst; geometric ranks it best.
- **V2 — insecure but tidy.** Four failures, all critical, nothing else wrong.
  Binary and linear both rank it best; the gate condemns it.
- **V3 — broken throughout.** Nine failures including five critical.
  Geometric ranks it worst.

---

## V1 — seven defects, none critical

### D1-01 · R28 · high
- **Location** `server.js`, `render()` response headers
- **Change** The `Cache-Control: no-store` header is not set on protected responses.
- **Predicted** SES-13
- **Note** Only detectable because D-014 made the collector record response headers. Before that change this defect would have been invisible to the judge.

### D1-02 · R11 · high
- **Location** `server.js:451`, `POST /tasks/:id/toggle`
- **Change** The status is toggled on the in-memory task but `writeDb` is not called, so it reverts on the next request.
- **Predicted** TSK-15, INT-02

### D1-03 · R10 · high
- **Location** `server.js:445`, `POST /tasks/:id/edit`
- **Change** `Object.assign(t, values)` runs but `writeDb` is not called, so the edit does not survive.
- **Predicted** TSK-13, INT-02

### D1-04 · R23 · medium
- **Location** `server.js:437`, `POST /tasks/:id/edit`
- **Change** The `errors.length` branch is skipped on edit, so an empty title is accepted where creation still rejects it.
- **Predicted** TSK-20, TSK-14
- **Severity mismatch** The defect is medium by Table 8 — wrong input accepted, recoverable — but TSK-20 is a high-severity scenario, because it tests that the rule is enforced on the server rather than only in the form.

### D1-05 · R8 · medium
- **Location** `server.js:69`, `validateTask`
- **Change** `len(title) > 100` becomes `>= 100`, so the inclusive upper bound is rejected.
- **Predicted** TSK-05
- **Note** TSK-06 still passes: 101 characters are still rejected, just for the wrong reason.

### D1-06 · R26 · medium
- **Location** `server.js:72`, `validateTask`
- **Change** The `isValidDate` call is dropped, so any non-empty string is accepted as a due date.
- **Predicted** TSK-10, TSK-11

### D1-07 · R14 · medium
- **Location** `server.js:329`, `GET /tasks`
- **Change** The search matches titles only; the description clause is removed.
- **Predicted** LST-05
- **Note** LST-04 still passes — it matches on title.

## V2 — three defects, all critical, nothing else

### D2-01 · R5 · critical
- **Location** `server.js:292`, `POST /signin`
- **Change** The failure message distinguishes the two cases: "No such user." when the account is not found, "Incorrect password." when it is.
- **Predicted** SES-05
- **Note** SES-03 and SES-04 still pass: both attempts are still rejected and still create no session. Only the indistinguishability is gone, which is the whole of what SES-05 tests.

### D2-02 · R25 · critical
- **Location** `server.js:397`, `app.param('id')`
- **Change** Returns 403 when the task exists but belongs to someone else, and 404 only when no such task exists — so the two become distinguishable.
- **Predicted** ACC-01, ACC-06

### D2-03 · R7 · critical
- **Location** `server.js`, the authentication middleware guarding `/tasks`
- **Change** The guard is not applied to `GET /tasks`, so the list renders without a session.
- **Predicted** SES-08

## V3 — four defects, five critical scenarios from one of them

### D3-01 · R21 · critical
- **Location** `server.js:395`, `app.param('id')`
- **Change** `&& t.ownerId === req.user.id` is removed from the lookup, so any signed-in user reaches any task by id.
- **Predicted** ACC-01, ACC-02, ACC-03, ACC-04, ACC-06
- **Note** One dropped clause, five critical scenarios. The largest single lever in the library, and an entirely ordinary mistake.

### D3-02 · R6 · critical
- **Location** `server.js:308`, `POST /signout`
- **Change** `req.session.regenerate` is replaced by setting the flash on the existing session, so signing out leaves the session usable.
- **Predicted** SES-07, SES-13
- **Severity mismatch** Critical as a defect — it breaks sign-out — but both scenarios it fails are high. ACC-10 is **not** predicted to fail: `signIn` regenerates the session on its own (`server.js:218`), so switching accounts still works.

### D3-03 · R12 · low
- **Location** `server.js:462`, `POST /tasks/:id/delete`
- **Change** The confirmation flash is not set; the deletion happens silently.
- **Predicted** TSK-17
- **Severity mismatch** The clearest case of the kind §4 is about: a cosmetic defect, low by Table 8, failing a high-severity scenario. Scoring weights the scenario, EQ1 compares against the defect.

### D3-04 · R20 · critical
- **Location** `server.js:329`, `GET /tasks`
- **Change** When the search term is non-empty, the query runs over all tasks instead of the signed-in user's, so search reaches across accounts.
- **Predicted** ACC-08
- **Note** LST-04 and LST-05 still pass: no other account's task contains "flights" or "airlines", so a global search returns the same rows for them. Only ACC-08, which searches for a word unique to bob's task, exposes it.

---

## Results — filled in after the runs

| Defect | Observed scenarios | Suite A | Suite B |
|---|---|---|---|
| D1-01 | | | |
| D1-02 | | | |
| D1-03 | | | |
| D1-04 | | | |
| D1-05 | | | |
| D1-06 | | | |
| D1-07 | | | |
| D2-01 | | | |
| D2-02 | | | |
| D2-03 | | | |
| D3-01 | | | |
| D3-02 | | | |
| D3-03 | | | |
| D3-04 | | | |
