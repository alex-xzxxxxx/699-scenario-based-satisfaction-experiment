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

(none yet — the first will be P-001, the V0 generation prompt, Week 3)
