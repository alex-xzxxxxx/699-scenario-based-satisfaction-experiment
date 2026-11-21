# Prompt log

Every prompt sent to a model, with the model, version, date, and what came back.
Required by proposal §5.6 and commitment C10. The judging prompt is frozen at
M5 (Week 6) — after that, no edit to the judging prompt is permitted, and any
attempt is recorded here as a rejected change.

## Template — copy for each entry

```
### P-00n — <purpose>
Date:            YYYY-MM-DD
Model:           <provider / model id>
Model version:   <exact version string as reported by the API>
Prompt version:  v0.n          (judging prompt only; frozen at M5)
Temperature:     <value>       (and any other sampling parameter)
Purpose:         <generation of V0 / suite A / judging run 1 / ...>
Prompt file:     logs/prompts/P-00n.txt
Output:          <where the raw response was saved>
Tokens / time:   <in, out, seconds>
Outcome:         <accepted / regenerated — and why>
```

## Entries

### P-001 — Generation of V0 and suite A
```
Date:            2026-11-16
Model:           Claude Opus 5.5 (Anthropic)
Model version:   claude-opus-5-5
                 Configured identifier, read from the chat interface. The
                 interface does not expose the serving model version, so this
                 is not an API-reported string. Recorded as a reproducibility
                 limitation in D-007 rather than presented as exact.
Prompt version:  n/a — this is the generation prompt, not the judging prompt.
                 Only the judging prompt is versioned and frozen at M5.
Temperature:     not exposed by the chat interface
Purpose:         Generate the application (V0) and its own test suite (suite A)
                 from app/REQUIREMENTS.md v1.1 and nothing else
Isolation:       A fresh session, carrying only the requirements document. No
                 repository, no folder tree, no use cases, no mention of the
                 study. The holdout rule (T05 notes, step 2) was followed.
Prompt file:     logs/prompts/P-001.txt   (saved 2026-11-17)
Output:          app/ at tag v0, commit 9fa715a
Tokens / time:   not exposed by the chat interface
Outcome:         Accepted without hand editing. V0 is the artefact under study;
                 its defects are data, not bugs to repair.
Regenerations:   UNCERTAIN — approximately one, not logged at the time.
                 See the note below.
```

**The returned specification was byte-identical to the frozen v1.1.** The model
did not alter, reinterpret or append to the requirements document it was given.
Verified by diff against the file at tag `req-v1.1`.

**The two gaps flagged in this record, as they now stand:**

1. *The prompt text is saved* (2026-11-17). It stores the instruction sent —
   "Build this application. Follow the requirements exactly." — and names the
   requirements document that followed it rather than duplicating it. That is
   sufficient for reproduction, because the document is fixed at tag
   `req-v1.1` and was returned byte-identical. Anyone can reconstruct the
   exact message from the two.
2. *The regeneration count is recorded as uncertain*, which is what this
   entry asked for. It is approximately one and was not logged at the time.
   Reported as uncertain in W03 and in the report's limitations; not stated
   as a figure.

### P-002 — Judge smoke test (T18)
```
Date:            2026-11-10
Model:           Gemini (Google)
Model version:   gemini-3.6-flash, requested and returned (D-010)
Prompt version:  not assigned — see below
Temperature:     not recorded
Purpose:         Confirm the judge API is reachable, returns parseable JSON,
                 and serves a stable model version across a run
Prompt file:     NOT RETAINED
Output:          records/W01/judge-smoke-test.json
Tokens / time:   median 3.08 s, max 11.09 s per call
Outcome:         API confirmed reachable. 15 of 25 calls returned valid JSON;
                 the other 10 were HTTP 503, not verdicts.
```

**The prompt sent in this run was not retained, and that is a gap in the
record this log exists to prevent.** It is logged here rather than omitted,
because a prompt that was sent and lost is part of the history.

The consequence is narrow but real. This run cannot answer whether the judge
was offered the three verdicts proposal §3.7 defines. All 15 parseable
responses returned `not_satisfied`; none returned `satisfied` and none
returned `uncertain`. With the prompt gone there is no way to tell whether
that reflects the evidence it was shown, a two-value vocabulary, or a
one-value one.

This was a connectivity test, so a single repeated input and a single verdict
are what it was built to produce, and `stable_under_repetition` is the result
it was after. It is not evidence that the judging prompt is sound, and it was
never meant to be.

### P-003 — Judging prompt (T18, T25)
```
Date:            2026-11-20
Model:           Gemini (Google)
Model version:   gemini-3.6-flash requested; the runner halts if another is served (D-011)
Prompt version:  v0.1 — validated 2026-11-20, all three verdicts reachable
Temperature:     0
Purpose:         Decide, from one evidence bundle, whether a scenario was satisfied
Prompt file:     logs/prompts/P-003.txt
Caller:          harness/judge.py
Output:          one JSON object: verdict, the evidence cited, the reason
```

Written to close the gap P-002 records. It offers the three verdicts of
proposal §3.7, defines Uncertain as insufficient evidence rather than a middle
grade, and requires the judge to cite what it read, per §3.8.

**Validated 2026-11-20, on the student's machine.** Four calls, each on an
input chosen to warrant one verdict, and every one came back as intended:

| Input | Verdict | Why it was expected |
|---|---|---|
| ACC-01 on V1 | `satisfied` | V1's defects are R11, R10, R23, R8, R26, R14, R4 — none touches ACC-01's R17/R21, so it behaves as V0 does here |
| ACC-01 on V2 | `not_satisfied` | D2-02 returns 403 rather than 404: refused, but no longer indistinguishable |
| ACC-01 on V3 | `not_satisfied` | D3-01 dropped the ownership check |
| `records/W06/prompt-validation/uncertain-fixture` | `uncertain` | a real trace truncated so the page text the scenario asks for was never captured |

All three verdicts of §3.7 are therefore reachable, which is exactly what
P-002 could not establish. Two failure modes are ruled out: a prompt that
cannot return `satisfied` would have scored every version zero, and one that
cannot return `uncertain` would have removed §3.7's protection against
guessing across all 540 judged runs, in both cases while looking healthy.

The satisfied case was taken on V1 rather than V0 by accident, and is the
better test. **V1 is a defective build, and the judge still found this
scenario satisfied on it**, which shows it rules on the scenario rather than
on the version. A V0 run could not have shown that.

Noted for EQ2 rather than as a problem: V2 is the arguable case — a 403 is
still a refusal, so a reviewer could call it satisfied — and the model called
it `not_satisfied`. Whether the human reference agrees is a result either way,
and the human judgment must be made without reference to this verdict.

What was checked without the API key: the prompt builds from a real bundle at
4,700 bytes with no version word and no absolute path in it, and the reply
parser accepts bare JSON, fenced JSON and JSON with prose around it while
rejecting an unknown verdict, an empty evidence list and a non-JSON reply.

Frozen at M5 (Week 6). After that, no edit, and any attempt is recorded here
as a rejected change.

**Before T25**, the judging prompt is written, saved as `logs/prompts/P-003.txt`,
logged here as P-003 with `Prompt version: v0.1`, and must satisfy §3.7 and
§3.8:

- offer all three verdicts — Satisfied, Not satisfied, Uncertain — and define
  Uncertain as insufficient evidence rather than as a middle grade;
- require the judge to cite the specific evidence supporting its decision;
- be validated against inputs that are known to warrant each of the three,
  so that all three are demonstrably reachable. A prompt that cannot return
  `satisfied` scores every version at zero, and a prompt that cannot return
  `uncertain` removes the protection §3.7 added on purpose.

Frozen at M5 (Week 6). After that, no edit, and any attempt is recorded here
as a rejected change.
