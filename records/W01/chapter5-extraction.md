# Chapter 5 extraction — Capstone II Execution Plan

Source: Xuan Zhao, *A Satisfaction Scoring Experiment for AI-Generated Software*,
GRAD 695 final proposal, September 2026. Chapter 5 has eight subsections
(5.1–5.8). Every one is covered below.

## 5.1 Introduction
Chapter 5 is the execution plan for Capstone II: what is built, in what order,
with what resources, and how completion is judged.

## 5.2 Work Breakdown — Table 14, WP1–WP11

| WP | Activities | Deliverable | Weeks (proposal) |
|----|------------|-------------|------------------|
| WP1 | Repository and environment; choose free models; confirm thresholds | Working environment; decision log | 1–2 |
| WP2 | Requirements document; generate V0 and suite A; write suite B by hand | V0, suites A and B (tagged) | 2–3 |
| WP3 | Use cases; generate, validate, categorize scenarios; assign severity | Frozen scenario library (~45) | 3–5 |
| WP4 | Scenario runner and evidence collector; script scenarios | Runner executing all scenarios on V0 | 3–5 |
| WP5 | Seed defects; create V1–V3; defect register | V1–V3; defect register | 5–6 |
| WP6 | LLM judge module, human form, scoring engine | Judging and scoring pipeline | 5–7 |
| WP7 | Pilot five scenarios; freeze prompt, weights, analysis plan | Pilot notes; frozen release | 7 |
| WP8 | Main run: execution, both suites, 3 LLM runs, blind human evaluation | Scenario-level dataset | 8–10 |
| WP9 | Delayed re-judgment; analysis, sensitivity, error coding | Results, charts, error analysis | 10–12 |
| WP10 | Final report and presentation | Report and slides | 12–14 |
| WP11 | Dashboard, second judge model, evidence ablation | Extensions | after M6, optional |

Carried into the 13-week plan as tasks T01–T39.

## 5.3 Milestones — Table 15, M1–M8

| M | Proposal week | This plan | Acceptance criterion |
|---|---------------|-----------|----------------------|
| M1 | 2 | Weeks 1–2 | Repository and model access work; open decisions confirmed |
| M2 | 3 | Week 3 | V0 runs; suites A and B execute against it |
| M3 | 5 | Week 5 | All scenarios validated and scripted; runner executes every scenario on V0 |
| M4 | 6 | Weeks 5–6 | V1–V3 built; each seeded defect logged and confirmed by hand |
| M5 | 7 | Week 6 | Judge, form, scoring work end to end; pilot done; artifacts frozen |
| M6 | 10 | Weeks 9–10 | Every run has evidence, both suite results, three LLM judgments; human subset complete |
| M7 | 12 | Week 11 | Delayed re-judgment done; all EQ analyses complete with intervals and error coding |
| M8 | 14 | Week 13 | Report and presentation submitted |

The proposal's 14 weeks are executed in 13 (decision D-001).

## 5.4 Resources and Technical Environment — Table 16
Python; Playwright (browser automation); pytest (tests); pandas (analysis);
matplotlib (charts). All free, to install. Free model access only, $0 budget.
Private git repository. Solo: no partner, no second reviewer.

The application's own stack is **not** fixed by the proposal; set in Week 1 as
decision D-002.

## 5.5 Risks and Mitigation — Table 17
Carried as contingencies in the weekly plan: scenario scripting is the riskiest
part and is scheduled early; normal-category scenarios are scripted first; free
tier limits mean judge runs are spread over several days, not one sitting.

## 5.6 Quality Assurance, Version Control, Documentation
Decision log, prompt log, results log maintained throughout (C10). Every
artifact tagged in git. Frozen artifacts do not change after their freeze point.

## 5.7 Completion and Acceptance Criteria — Table 18 → C01–C06

| ID | Source | Commitment | Weeks |
|----|--------|------------|-------|
| C01 | 5.7 #1 | Harness components work end to end on all four application versions | 4–6 |
| C02 | 5.7 #2 | Scenario library, defect register, prompt, analysis plan frozen and tagged before the main run | 3–7 |
| C03 | 5.7 #3 | Every run has evidence, a test result or "no mapped test," and three LLM judgments | 7–8 |
| C04 | 5.7 #4 | Human subset (~25) blind; delayed re-judgment (~10) | 9, 11 |
| C05 | 5.7 #5 | All EQ1–EQ5 metrics with counts and intervals; sensitivity and error analyses | 10–11 |
| C06 | 5.7 #6 | Threats and limitations documented; final report and presentation delivered | 6, 10–13 |

Derived from 5.2 and 5.6:

| ID | Source | Commitment | Weeks |
|----|--------|------------|-------|
| C07 | 5.2 WP1, M1 | Repository and environment working; free models chosen; thresholds confirmed | 1–2 |
| C08 | 5.2 WP2, M2 | V0 generated and tagged; suites A and B execute against it | 2–3 |
| C09 | 5.2 WP5, M4 | V1–V3 built with seeded defects; each defect logged and confirmed by hand | 5–6 |
| C10 | 5.6 | Quality checks, version control, and the decision / prompt / results logs maintained | 1–13 |

## 5.8 Chapter Summary
The plan is deliberately small: one application, five use cases, ~45 scenarios,
four versions, one judge model, ~25 human-judged runs, ~540 LLM calls.

## Chapter 6 — expected contributions (K01–K04)

| ID | Source | Expected contribution | Evidence from |
|----|--------|----------------------|---------------|
| K01 | 6.3 practice | Reusable scenario format and a scoring method with a critical gate | T12, T20, T28 |
| K02 | 6.3 practice | A protocol for checking an LLM judge before trusting it | T17, T26, T27, T30 |
| K03 | 6.3 / EQ1 | Whether severity weighting changes conclusions versus binary scoring | T28, T29 |
| K04 | 6.3 / EQ2–EQ3 | How often the judge falsely accepts or rejects, and which scenarios cause it | T28, T30 |

Each is a claim **to investigate**, not a result obtained. A negative result
still satisfies the Table 18 completion criteria.
