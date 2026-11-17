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
Prompt file:     logs/prompts/P-001.txt   [NOT YET SAVED — see below]
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

**Two gaps in this record, both to close before M2 is claimed complete:**

1. *The prompt text itself is not saved.* `logs/prompts/P-001.txt` does not
   exist. Copy the exact message sent to the model into that file. Without it,
   the generation is not reproducible by anyone else, which is the one
   reproducibility claim that does not depend on model determinism.
2. *The regeneration count is a recollection, not a record.* W03 asks for it
   explicitly. Check the session history and record the actual number; if it
   cannot be recovered, both this entry and W03 say so rather than stating a
   figure. An uncertain number reported as uncertain is defensible. An
   uncertain number reported as "1" is not.
