# Demo — one use case, end to end

For the question: *show one use case, how the AI tests it, how a human
reviews it, and how the two are compared.*

**Use case UC5.1 — Read another user's task.** Scenario **ACC-01**, adversarial,
critical, requirements R17 and R21.

Chosen because the same scenario comes out three different ways across the
versions, so one scenario demonstrates agreement and disagreement:

| Version | What the application does | |
|---|---|---|
| V0 | another user's task returns 404, same as one that does not exist | the correct behaviour |
| V3 | the ownership check is gone — alice reads bob's task | clearly wrong |
| V2 | returns 403 instead of 404 — still refused, but now distinguishable | **arguable** |

V2 is the one worth dwelling on. The write is refused, so a reasonable
reviewer could call it satisfied; R17 is about a response that reveals
nothing, so a reasonable reviewer could call it failed. That disagreement is
the thing this project measures, and it is better demonstrated than described.

---

## Before the demo: validate the prompt (once)

The judging prompt is `logs/prompts/P-003.txt`. It has never been run. Before
using it in front of anyone, confirm all three verdicts are reachable —
a prompt that cannot return `satisfied` scores every version zero, and one
that cannot return `uncertain` silently removes the protection proposal §3.7
added on purpose.

```
python -m harness.judge --bundle <ACC-01 run on V0>                  # expect satisfied
python -m harness.judge --bundle <ACC-01 run on V3>                  # expect not_satisfied
python -m harness.judge --bundle records/W06/prompt-validation/uncertain-fixture
                                                                     # expect uncertain
```

The third is a deliberately truncated trace: the run stops after sign-in, so
the page text ACC-01 asks for was never captured. It is a prompt fixture, not
experimental data, and is kept out of `evidence/` for that reason.

If any of the three comes back wrong, the prompt is wrong — fix it now. After
M5 it is frozen and an edit becomes a recorded threat to validity.

---

## 1. Show the scenario — written before anything ran

Open `scenarios/library/ACC-01.yaml`.

The point to make: **the expected behaviour is prose, not an assertion.**

> The response is a 404 page, and no part of bob's task appears anywhere in
> it — not the title, not the description. A 404 status that still shows the
> title fails this scenario.

A test suite cannot hold that. It can assert `status == 404`, and it would
pass an application that returns 404 with bob's title still on the page.
That gap is what the project is about.

Mention that the library is frozen at tag `scenarios-v1` and was written
before the defective versions existed, so nothing here was written to catch a
defect that was already known.

## 2. Run it against V0 — the AI executing the test

```
git checkout feature/week01-v1
npm --prefix app run reset
cd app && node server.js          # leave running, second terminal
python -m harness.runner.runner --scenario ACC-01 --version V0
```

Point out what the runner does **not** do: it never decides whether the
scenario passed. Sixteen step helpers act and record; none of them assert. If
the runner decided, there would be nothing left for the judge and the human
to disagree about, and the central measurement would have no data.

## 3. Run it against a defective version

```
git checkout defect/v3
npm --prefix app run reset
cd app && node server.js
python -m harness.runner.runner --scenario ACC-01 --version V3
```

V3 has one dropped clause — `&& t.ownerId === req.user.id` — which fails five
critical scenarios at once. Registered in `defects/registry.md` before the
version was built.

## 4. Open the evidence

```
evidence/<run_id>/trace.md
```

Three things to point at:

- The run id is a random token. The version appears nowhere in the bundle —
  only in `data/run_manifest.jsonl`, which is never committed.
- `trace.md` and `trace.json` are the same content. The person reads the
  first, the judge is given the second.
- Every step carries what was on screen, so a reviewer can check the claim
  rather than take it.

## 5. The AI judges it

```
python -m harness.judge --bundle evidence/<run_id>
```

Returns one JSON object: the verdict, the evidence it cites, and why. It is
given the scenario and the trace, nothing else — no version, no other run, no
knowledge of what the other judge said.

## 6. The human judgment — done before the demo, not during it

**Do this the day before, not live.** Reading a trace properly takes several
minutes of silence, which is a poor thing to watch, and rushing it produces a
judgment that is not worth comparing against.

For each of the three runs, read `trace.md` and record one line:

```
data/human-verdicts.jsonl
{"run_id": "1caea6087d5e641a", "verdict": "satisfied",     "note": "404, and no part of bob's task on the page"}
{"run_id": "ee16eeb5cd02990c", "verdict": "not_satisfied", "note": "bob's title shown to alice"}
{"run_id": "<the V2 run>",     "verdict": "...",           "note": "..."}
```

Blind means blind: do not open `data/run_manifest.jsonl`, and do not run the
judge first. The human reference is what the model is measured against, so a
judgment made after seeing the model's answer measures nothing.

Judge V2 honestly rather than diplomatically. If a 403 reads as satisfying
R17 to you, record `satisfied` — a disagreement with the model there is a
result, not a mistake.

## 7. Compare — this is the part to spend time on

```
python -m harness.compare --judge data/verdicts.jsonl \
                          --human data/human-verdicts.jsonl
```

```
run               scenario  judge  human  agree
-----------------------------------------------
1caea6087d5e641a  ACC-01    SAT    SAT    yes
ee16eeb5cd02990c  ACC-01    NOT    NOT    yes
7b3f...           ACC-01    SAT    NOT    no
```

Then, and only then, reveal which version each run was:

```
python -m harness.compare --judge ... --human ... --reveal
```

Four things to draw out:

1. **The version column comes last, from the manifest.** It is the only place
   the mapping exists, and it is never committed. The blinding is a property
   of the artefacts, not a promise.
2. **Agreement on the clear cases is the uninteresting part.** Both judges
   calling V0 satisfied and V3 not satisfied says the instrument works.
3. **The V2 row is the experiment.** Whatever it shows — agreement or not —
   that is the kind of case EQ2 counts, and it is why the measurement needs a
   human reference at all rather than a rule.
4. **The tool refuses to give an agreement statistic on three runs.** It
   prints the comparison and then says the sample is too small. EQ2 needs the
   subset of about 25, judged blind and judged again fourteen days later —
   and the agreement with that earlier self is the ceiling the model is held
   to, rather than a borrowed κ of 0.61.

Where suite A and suite B stand on the same scenario can be added by hand for
the demo; the mapping from assertions to a per-scenario verdict is set out in
`analysis/scoring.md` §6 and is not automated yet.

---

## What this shows, in one line each

- **Scenario** — a requirement written as expected behaviour, in prose, frozen before the versions existed.
- **AI testing** — the harness executes and records; it rules on nothing.
- **AI review** — the judge reads the evidence and returns one of three verdicts, citing what it read.
- **Human review** — the same evidence, blind to version, by the researcher.
- **Comparison** — four sources on the same run: two judges and two conventional test suites.

## What this demo cannot show yet

The agreement statistic and the scoring. Those need the full run of 47
scenarios across four versions — 188 runs — and the human subset of about 25.
This demonstrates the loop on one scenario, not the result.
