# T05 — notes on the requirements document

**Not part of the specification. This file is never shown to the
implementation model.**

`app/REQUIREMENTS.md` is the only input to V0 generation. These notes record why
it says what it says, so the choices can be defended in the final report.

## What the document deliberately does not say

**How thorough the test suite should be.** Section 6 fixes the *form* of suite A
— Python, pytest, Playwright, browser-level — so that it is comparable with the
hand-written suite B (decision D-003). It does not say how many tests to write,
which requirements to cover, or to write one test per requirement.

That silence is deliberate and load-bearing. EQ4 asks what the scenarios catch
that the automated tests miss, and the premise (Liu et al., 2023) is that an
AI-written suite may be thin. If the document told the model to cover every
requirement, suite A would be artificially strong and EQ4 would be answered by
the instruction rather than by the evidence.

**Anything about scenarios, severity, defects, judging, or the study.** The
model is building an application, not taking part in an experiment. The holdout
rule depends on it.

## Requirement numbering

R1–R23, twenty-three requirements. The proposal specifies suite B as "about 20
tests, one or two per requirement" (§3.x), so the numbering gives suite B a
direct mapping and gives EQ4 a clean unit of comparison.

R17–R21 are the access-control requirements. They are the source of the
critical-severity scenarios and therefore of the critical gate (D-005), so they
are written as precise, checkable statements — R17 in particular says *no part
of the task's content appears anywhere in the response*, which can be verified
from the page text rather than from the status code alone.

## Seed data and reset

Fixed seed data plus `npm run reset` exists for EQ5, repeatability. Without a
known starting state, a scenario re-run is not the same scenario. The reset is
also what makes each test in suite A and suite B independent.

## Threat introduced by section 3

Requiring stable `data-testid` attributes makes the generated application more
testable than an AI-generated application would typically be. This is recorded
as **D-008** and must appear in the final report's threats section.

It was accepted because the proposal names scenario scripting as the riskiest
part of the project (§4.12) and schedules it early for that reason. Unstable
selectors would put Weeks 4–5 at risk for no research benefit. The constraint
applies identically to V0 and to V1–V3, so it does not favour any version, and
it does not tell the model anything about what will be tested.

## Generation protocol (T06, Week 3)

1. Freeze and commit `app/REQUIREMENTS.md` **before** generating. The commit
   date is the evidence that the requirements were not adjusted after seeing
   the output.
2. Open a **fresh session** with the implementation model. It receives
   `app/REQUIREMENTS.md` and nothing else — no repository, no folder tree, no
   file list, no mention of the study.
3. Record in `logs/prompt-log.md` as **P-001**: model id, exact version string,
   date, temperature, the prompt file, where the raw output was saved, tokens
   and seconds.
4. If the output is incomplete or does not run, record the regeneration attempt
   and why. Every attempt is logged; W03 asks for this explicitly.
5. Verify V0 runs, `npm run reset` works, and suite A executes. Then tag:
   `git tag -a v0 -m "V0 as generated from REQUIREMENTS.md v1.0"`.
6. Do not fix defects in V0 by hand. V0 is the artefact under study. Anything
   wrong with it is data, not a bug to repair. If it genuinely cannot run at
   all, regenerate and log it.

Point 6 matters: V1–V3 are copies of the tagged V0, so a hand edit to V0 after
tagging would silently change all four versions.
