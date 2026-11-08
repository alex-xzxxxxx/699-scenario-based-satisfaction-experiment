# T02 — Model selection and free-tier limits

**Hard constraint (proposal §2.x, self-enhancement bias):** the implementation
model and the judge model must come from **different model families**. A model
must never judge software it wrote.

## What drives the choice

The judge makes about **540 calls** (≈45 scenarios × 4 versions × 3 runs). That
number against the daily request cap decides how many days Week 8 judging takes:

| Judge free-tier RPD | Days needed for 540 calls | Fits Week 8? |
|---------------------|---------------------------|--------------|
| 1,000 | 1 | yes |
| 200 | 3 | yes |
| 100 | 6 | tight |
| 50 | 11 | **no — plan spills into Week 9** |

So the daily cap is the number that matters, not speed or benchmark scores.
Check it **in the provider's console on the day you register**; published docs
no longer list per-model free-tier figures, and the caps change.

## Candidate routes (fill in from the console)

Decided in D-007: **Claude implements, Gemini judges.** Different families, so
the §2.x constraint is satisfied. What is left is to read the numbers.

| Role | Model | Family | Model id | Version string | RPM | RPD | TPM | Date read |
|------|-------|--------|----------|----------------|-----|-----|-----|-----------|
| Implementation | Claude | Anthropic | chat interface | _as displayed_ | — | — | — | |
| Judge | Gemini | Google | | | | | | |

Read the judge's limits in Google AI Studio, not from the documentation — the
docs no longer publish per-model free-tier figures, and the caps change.
Record the date you read them.

Also confirm the judge model supports **structured JSON output** (a response
schema or JSON response type). The judge module depends on it; free-text
answers would have to be parsed, and parse failures would become data loss.

## Required record (completion check for Week 1)

- [ ] Implementation model: exact model id and version string
- [ ] Judge model: exact model id and version string, different family
- [ ] Daily request limit for each, read from the console, with the date read
- [ ] Both API keys working — one trivial call each, saved to `logs/prompts/`
- [ ] Keys stored in `.env`, which is git-ignored

## Decision

Record the final choice as **D-007** in `logs/decision-log.md`, with the reason
and the date. The judging model cannot change after the prompt is frozen at M5
(Week 6).
