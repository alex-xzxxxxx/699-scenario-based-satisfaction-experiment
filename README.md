# Scenario Satisfaction Harness — Capstone II (CISC 699)

Xuan Zhao. Instrument for the satisfaction scoring experiment described in the
GRAD 695 proposal, *A Satisfaction Scoring Experiment for AI-Generated Software*.

The harness runs user-level scenarios against an AI-generated web application
and three seeded-defect copies of it, saves execution evidence, has an
independent LLM judge and a human judge each run, and turns those judgments
into binary and severity-weighted satisfaction scores.

## Folders

| Folder       | Holds                                                            |
|--------------|------------------------------------------------------------------|
| `harness/`   | Python: scenario runner, evidence collector, LLM judge, scoring   |
| `app/`       | The application under test. V0 generated Week 3; V1–V3 Week 5–6   |
| `scenarios/` | Scenario library. **Holdout — see the warning below**             |
| `evidence/`  | Per-run evidence under anonymized run IDs                         |
| `data/`      | Assembled datasets (judgments, test results, metrics)             |
| `analysis/`  | Analysis scripts and outputs                                      |
| `records/`   | Weekly records W01–W13, the retained evidence of work done        |
| `logs/`      | Decision log, prompt log, results log                             |
| `report/`    | Capstone II report drafts and figures                             |

## ⚠️ Holdout rule

The implementation model that generates the application **must never see**
`scenarios/`, `evidence/`, or this README. When generating V0 it receives the
requirements document and nothing else. Do not paste the repository, the
folder tree, or a file list into the implementation model's context.

Breaking this invalidates the whole study: the application would be built to
pass the exact scenarios that are supposed to judge it.

Same rule in the other direction for the hand-written baseline: suite B is
written from the requirements document, before any scenario is drafted and
before any defect is seeded, so it cannot be tuned to either.

## Setup

Harness (Python 3.11+):

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
pip freeze > requirements.lock.txt
```

Application (Node 20+), from Week 3 once V0 exists:

```bash
cd app && npm install && npm start
```

API keys go in `.env`, which is git-ignored. Never commit a key.

## Stack

| Part                | Stack                              | Fixed by                      |
|---------------------|------------------------------------|-------------------------------|
| Harness + analysis  | Python, Playwright, pandas         | Proposal §5.4 Table 16        |
| Application V0–V3   | Node/Express + plain HTML/JS       | Decision D-002, Week 1        |
| Test suites A and B | Browser-level, Playwright          | Decision D-003, Week 1        |

The proposal does not fix the application's stack. It was chosen in Week 1 and
recorded in `logs/decision-log.md`; it cannot change after V0 is tagged,
because V1–V3 are copies of V0.
