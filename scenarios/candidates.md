# Candidate scenarios — T10

**HOLDOUT. Never shown to the implementation model.**

Drafted from `use-cases.md` (UC1–UC5) and `app/REQUIREMENTS.md` v1.1, in the
template of Appendix B Table B1. Severity follows Table 8 and is assigned here,
before any result exists.

These are **candidates**. T11 has now validated each against the Table B4
checklist: **47 accepted, 27 rejected**, with the decision and reason for every
one recorded in `validation.md` and `validation.csv`. This file is kept as
drafted, so that what was proposed and what survived can be compared. The
library is frozen and tagged at T12, end of Week 5.

**74 candidates, for a target library of about 45.** The surplus is deliberate:
W04 records a candidate-to-approved count with a reason for every rejection,
which needs candidates that can be rejected.

## Severity, from Table 8

| Severity | Failure of this scenario would… | Linear | Geometric |
|---|---|---|---|
| Critical | expose or corrupt another user's data, or break login/security | 4 | 8 |
| High | block a main use case for the user | 3 | 4 |
| Medium | allow wrong input or produce wrong but recoverable results | 2 | 2 |
| Low | cause a cosmetic or wording problem only | 1 | 1 |

## Target distribution, from Table B3

| Category | Planned share | ≈ of 45 | Candidates | Candidate share |
|---|---|---|---|---|
| Normal | 30% | 14 | 18 | 24% |
| Failure | 25% | 11 | 16 | 22% |
| Edge | 20% | 9 | 17 | 23% |
| Adversarial / robustness | 15% | 7 | 16 | 22% |
| Integration | 10% | 5 | 7 | 9% |

The candidate mix is not the target mix. Edge and adversarial are over-weighted
and normal under-weighted, because boundary and access-control cases are easier
to enumerate from a specification than ordinary success paths. **T11 must prune
toward Table B3 rather than simply dropping whatever fails the checklist**, or
the library will over-represent the categories that were easiest to write.

Severity across the candidates: 10 critical, 20 high, 30 medium, 14 low.

Every scenario starts from seed state unless its preconditions say otherwise.
Evidence is the compact trace of D-009 — steps, actions, visible text that
changed, messages, final state — identical for the LLM judge and the human.

---

## UC1 — Register an account

| ID | Cat | Sev | Preconditions | User action | Expected behaviour | Expected evidence | Req |
|---|---|---|---|---|---|---|---|
| REG-01 | Normal | High | Signed out | Register `dev_one` / `goodpass123` | Signed in; the task list is shown | Final URL; list page; the account can sign in afterwards | R1 |
| REG-02 | Failure | Medium | Seed state | Register `alice` / `newpass1234` | Rejected; a visible message; no account created | Message text; the original alice password still works | R2 |
| REG-03 | Failure | Medium | Seed state | Register `ALICE` / `newpass1234` | Rejected; uniqueness is case-insensitive | Message text; no new account | R2 |
| REG-04 | Edge | Low | Signed out | Register `  spaced  ` / `goodpass123` | Accepted; the username is stored trimmed | The name shown is `spaced`, no spaces | R1 |
| REG-05 | Edge | Medium | Signed out | Register a 3-character username | Accepted — 3 is the lower bound | Final URL; account exists | R1 |
| REG-06 | Edge | Medium | Signed out | Register a 20-character username | Accepted — 20 is the upper bound | Final URL; account exists | R1 |
| REG-07 | Failure | Medium | Signed out | Register a 2-character username | Rejected; the message names the username | Message text; no account | R3 |
| REG-08 | Failure | Medium | Signed out | Register a 21-character username | Rejected; the message names the username | Message text; no account | R3 |
| REG-09 | Failure | Medium | Signed out | Register `bad-name` (hyphen) | Rejected; the message names the username | Message text; no account | R3 |
| REG-10 | Edge | Medium | Signed out | Register with an 8-character password | Accepted — 8 is the lower bound | Final URL; sign-in works | R1 |
| REG-11 | Failure | Medium | Signed out | Register with a 7-character password | Rejected; the message names the password | Message text; no account | R3 |
| REG-12 | Edge | Low | Signed out | Register with a password that has leading and trailing spaces | Accepted; the password is **not** trimmed | Signing in with the spaces works; without them fails | R1 |
| REG-13 | Adversarial | High | Signed out | POST `/register` directly with a 2-character username, bypassing the page | Rejected on the server; no account created | Response; no account afterwards | R22, R23 |

## UC2 — Sign in, sign out, hold a session

| ID | Cat | Sev | Preconditions | User action | Expected behaviour | Expected evidence | Req |
|---|---|---|---|---|---|---|---|
| SES-01 | Normal | High | Seed state | Sign in as `alice` / `alicepass123` | The task list is shown, with alice's tasks | Final URL; the four seed titles | R4 |
| SES-02 | Edge | Medium | Seed state | Sign in as `ALICE` with the correct password | Accepted; the username is matched case-insensitively | Final URL; the displayed name is `alice` | R4 |
| SES-03 | Failure | High | Seed state | Sign in as `alice` with a wrong password | Rejected; a visible message; no session | Message text; `/tasks` still redirects to `/signin` | R5 |
| SES-04 | Failure | High | Seed state | Sign in as `no_such_user` with any password | Rejected; a visible message; no session | Message text | R5 |
| SES-05 | Adversarial | Critical | Seed state | Compare the messages from SES-03 and SES-04 | **Identical.** Neither reveals whether the account exists | The two message strings, side by side | R5 |
| SES-06 | Edge | Low | Seed state | Sign in as `alice` with the password plus a trailing space | Rejected; the password is matched exactly | Message text; no session | R4 |
| SES-07 | Normal | High | Signed in as alice | Sign out | The session is no longer valid | `/tasks` afterwards redirects to `/signin` | R6 |
| SES-08 | Adversarial | Critical | Signed out | Request `/tasks` | Redirected to `/signin`; no task content returned | Final URL; no task title anywhere in the response | R7 |
| SES-09 | Adversarial | High | Signed out | Request `/tasks/new`, `/tasks/1`, `/tasks/1/edit` in turn | Each redirects to `/signin`; no content returned | Final URL per request; no task content | R7 |
| SES-10 | Edge | Medium | Signed out | Request `/no-such-path` | Redirected to `/signin`, like any other protected path | Final URL | R7 |
| SES-11 | Normal | Low | Signed in as alice | Request `/signin` | Redirected to `/tasks` | Final URL | R29 |
| SES-12 | Normal | Low | Signed in as alice | Request `/register` | Redirected to `/tasks` | Final URL | R29 |
| SES-13 | Integration | High | Signed in as alice, task list open | Sign out, then press the browser Back button | The protected page is not shown | Final URL; `Cache-Control: no-store` on the protected response | R28 |

## UC3 — Create, edit, complete and delete a task

| ID | Cat | Sev | Preconditions | User action | Expected behaviour | Expected evidence | Req |
|---|---|---|---|---|---|---|---|
| TSK-01 | Normal | High | Signed in as alice | Create a task with a title only | The task exists with status `open` and appears in the list | The row; its status | R8 |
| TSK-02 | Normal | Medium | Signed in as alice | Create a task with title, description and due date | All three are stored and shown | The row; the detail page | R8 |
| TSK-03 | Failure | High | Signed in as alice | Create with an empty title | Rejected; a visible message; no task created | Message text; the row count is unchanged | R9 |
| TSK-04 | Failure | Medium | Signed in as alice | Create with a whitespace-only title | Rejected; a visible message; no task created | Message text; row count unchanged | R9 |
| TSK-05 | Edge | Medium | Signed in as alice | Create with a 100-character title | Accepted — 100 is the upper bound | The row; the full title | R8 |
| TSK-06 | Failure | Medium | Signed in as alice | Create with a 101-character title | Rejected; no task created | Message text; row count unchanged | R8, R22 |
| TSK-07 | Edge | Low | Signed in as alice | Create with a title surrounded by spaces | Accepted; the title is stored trimmed | The row shows no leading or trailing space | R8 |
| TSK-08 | Edge | Medium | Signed in as alice | Create with a 500-character description | Accepted — 500 is the upper bound | The detail page | R8 |
| TSK-09 | Failure | Low | Signed in as alice | Create with a 501-character description | Rejected; no task created | Message text; row count unchanged | R8, R22 |
| TSK-10 | Failure | Medium | Signed in as alice | Create with due date `2026-02-30` | Rejected — well-formed but not a real date; nothing stored | Message text; row count unchanged | R26 |
| TSK-11 | Failure | Medium | Signed in as alice | Create with due date `11/16/2026` | Rejected — wrong format; nothing stored | Message text; row count unchanged | R26 |
| TSK-12 | Edge | Low | Signed in as alice | Create with due date `2020-01-15` | Accepted — past dates are allowed | The row; the date shown | R26 |
| TSK-13 | Normal | High | Signed in as alice | Edit her own task's title | The new title is stored and shown | The row before and after | R10 |
| TSK-14 | Failure | Medium | Signed in as alice | Edit her own task to a blank title | Rejected; the task is unchanged | Message text; the original title still shown | R10, R23 |
| TSK-15 | Normal | High | Signed in as alice, task is `open` | Mark it completed from `/tasks/:id` | Status becomes `completed` | Status before and after | R11 |
| TSK-16 | Normal | Medium | Signed in as alice, task is `completed` | Reopen it | Status becomes `open` | Status before and after | R11 |
| TSK-17 | Normal | High | Signed in as alice | Delete her own task | It leaves the list and a visible message confirms | The list before and after; message text | R12 |
| TSK-18 | Edge | Low | Immediately after TSK-17 | Reload the list page | The confirmation is gone — shown once | The message container, empty on reload | R12 |
| TSK-19 | Adversarial | High | Signed in as alice | POST a 101-character title straight to the server | Rejected server-side; no task created | Response; row count unchanged | R22, R23 |
| TSK-20 | Adversarial | High | Signed in as alice | POST a blank title to her own task's edit route | Rejected server-side; the task is unchanged | Response; the stored task before and after | R22, R23 |

## UC4 — Find a task

| ID | Cat | Sev | Preconditions | User action | Expected behaviour | Expected evidence | Req |
|---|---|---|---|---|---|---|---|
| LST-01 | Normal | High | Signed in as alice | Open the task list | Only alice's four seed tasks are shown | The rows; no bob or carol title | R13 |
| LST-02 | Normal | Medium | Signed in as alice | Create two tasks, then open the list | The newer of the two is above the older | Row order; task ids | R13, R30 |
| LST-03 | Normal | Low | Signed in as alice | Open the task list | Each row shows title, status, and due date where one is set | A row with a due date and one without | R13 |
| LST-04 | Normal | Medium | Signed in as alice | Search for a substring of a task title | Only matching tasks are listed | The rows; the search term | R14 |
| LST-05 | Normal | Medium | Signed in as alice | Search for a substring of a task description | The task matches on its description | The rows | R14 |
| LST-06 | Edge | Medium | Signed in as alice | Search using different case from the stored text | Matches — case is ignored | The rows | R14 |
| LST-07 | Adversarial | Medium | Signed in as alice | Search for `(` | Treated as literal text; no error page | HTTP status; the rows or the empty message | R14 |
| LST-08 | Edge | Low | Signed in as alice | Search for a phrase containing a space | Matched as a substring, spaces included | The rows | R14 |
| LST-09 | Normal | Medium | Signed in as alice | Filter by `open` | Only `open` tasks are listed | The rows and their statuses | R15 |
| LST-10 | Normal | Medium | Signed in as alice | Filter by `completed` | Only `completed` tasks are listed | The rows and their statuses | R15 |
| LST-11 | Edge | Low | Signed in as alice | Request `?status=not_a_status` | Treated as `all` | The rows — the full list | R15 |
| LST-12 | Integration | Medium | Signed in as alice, with one open and one completed task sharing a word | Apply that word as search and `completed` as filter | Only the completed one is listed | The rows | R15 |
| LST-13 | Failure | Low | Signed in as alice | Search for text no task contains | "No tasks found" is shown, not a blank area | The empty message element and its text | R16 |
| LST-14 | Edge | Low | A freshly registered user with no tasks | Open the task list | "No tasks found" is shown | The empty message element | R16 |

## UC5 — Access control

Every flow here is an attempt that must be refused. This is where the
critical-severity scenarios come from, and therefore the critical gate in D-005.

| ID | Cat | Sev | Preconditions | User action | Expected behaviour | Expected evidence | Req |
|---|---|---|---|---|---|---|---|
| ACC-01 | Adversarial | Critical | Signed in as alice | Open bob's task by its URL | 404; **no part of the task's content anywhere in the response** | Status; the full page text checked against bob's title and description | R17 |
| ACC-02 | Adversarial | Critical | Signed in as alice | POST an edit to bob's task, straight to the server | Rejected; bob's task is unchanged | Response; bob's task before and after | R18, R21 |
| ACC-03 | Adversarial | Critical | Signed in as alice | POST a delete to bob's task | Rejected; the task still exists | Response; the task still present for bob | R19, R21 |
| ACC-04 | Adversarial | Critical | Signed in as alice | POST a toggle to bob's task | Rejected; the status is unchanged | Response; the status before and after | R24, R21 |
| ACC-05 | Adversarial | Critical | Signed in as alice | Open bob's task edit page | 404; no content and no editable fields | Status; page text | R18, R21 |
| ACC-06 | Adversarial | Critical | Signed in as alice | Request bob's task id and a non-existent id, and compare | **Indistinguishable** — same status, same page, same message | The two responses, compared byte for byte | R25 |
| ACC-07 | Adversarial | Critical | Signed in as alice | POST edit, toggle and delete to bob's id and to a non-existent id, and compare each pair | Indistinguishable in every pair | The response pairs | R25 |
| ACC-08 | Adversarial | High | Signed in as alice; bob owns a task with a unique marker word | Search for that marker | No task row matches. An echoed search term in the input is not a match | The task rows; the empty message | R20 |
| ACC-09 | Adversarial | High | Signed in as alice | Request `/tasks/1` through `/tasks/10` in turn | Only alice's own ids return a task; the rest are indistinguishable 404s | Status and title per id | R21, R25 |
| ACC-10 | Integration | Critical | alice signed in with tasks visible | Sign out, sign in as bob, open the task list | Only bob's tasks are shown; none of alice's | The rows before and after the switch | R13, R20 |

## Integration across use cases

| ID | Cat | Sev | Preconditions | User action | Expected behaviour | Expected evidence | Req |
|---|---|---|---|---|---|---|---|
| INT-01 | Integration | High | Signed out | Register, create a task, sign out, sign in again | The task is still there and belongs to that account | The row after signing back in | R1, R8, R13 |
| INT-02 | Integration | Medium | Signed in as alice | Create a task, edit it, complete it, reopen it, delete it | Each step takes effect and the last removes it | State after each step | R8–R12 |
| INT-03 | Integration | Medium | Signed in as alice | Create a task, then find it by search and by status filter | Found both ways | The rows from each query | R8, R14, R15 |
| INT-04 | Integration | High | Seed state | Run `npm run reset`, then sign in and open the list | Three accounts and eight tasks, exactly as section 5 describes | The rows for each user | §5 |

---

## Notes for T11

**Known overlaps to resolve.** ACC-06 and ACC-07 both test R25 and may merge.
ACC-09 overlaps both. TSK-06 and TSK-19 both reject a 101-character title, one
through the page and one straight to the server — keep both only if the
server-side path is judged a distinct risk. LST-04 and LST-05 differ only in
which field matches.

**Thin areas.** R27 has no scenario, for the reason in W03: no route deletes a
user. Integration is at the planned 10% but every candidate is a long multi-step
run, which is where the runner is most likely to be fragile — Table B4 item 5.

**Distribution after the planned merges** lands near the Table B3 shares. T11
should recount rather than trust this table, and record the final counts in W04.

**Nothing here was written against V0's observed behaviour.** Each scenario
traces to a use case flow and a requirement id. The threat recorded in W03
stands: the author had seen V0 pass both suites before drafting these.
