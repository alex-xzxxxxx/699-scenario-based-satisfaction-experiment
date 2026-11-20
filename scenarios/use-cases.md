# Use cases — UC1 to UC5, refined into 15 use cases

Written from `app/REQUIREMENTS.md` v1.0, in Week 2, before V0 exists.
Refined on 2026-11-19 into fifteen use cases, grouped under the original five
areas (D-016). The refinement splits existing flows; it adds no behaviour and
no requirement.

These are the source from which candidate scenarios are generated (T10) and
validated (T11). They live inside `scenarios/`, which is **holdout** — the
implementation model never sees this folder.

A use case is not a scenario. A use case describes what the system is for; a
scenario is one concrete, executable path through it with a known expected
outcome. Scenarios are written in Week 4 and frozen at the end of Week 5.

Each flow below cites the requirement it rests on, so that every scenario
generated later inherits a requirement ID and EQ4 has a clean unit of
comparison against the test suites.

## How the numbering works

UC1–UC5 are the five **areas** of the system. Each area holds two to four
**use cases**, numbered UC1.1, UC1.2 and so on. A scenario's `use_case` field
in `scenarios/library/` names its area (for example `UC5`), and that value
stays valid: the library was frozen and tagged `scenarios-v1` before this
refinement, so the scenario files are not edited. The table at the end of this
document places every accepted scenario in its use case.

| Area | Use cases | Requirements |
|------|-----------|--------------|
| UC1 Account registration | UC1.1, UC1.2 | R1, R2, R3, R22, R23 |
| UC2 Sessions | UC2.1, UC2.2, UC2.3, UC2.4 | R4, R5, R6, R7, R27, R28, R29 |
| UC3 Task management | UC3.1, UC3.2, UC3.3, UC3.4 | R8, R9, R10, R11, R12, R26, R22, R23 |
| UC4 Finding tasks | UC4.1, UC4.2 | R13, R14, R15, R16, R30 |
| UC5 Access control | UC5.1, UC5.2, UC5.3 | R17, R18, R19, R20, R21, R24, R25 |

---

## UC1 — Account registration

### UC1.1 — Register an account

**Actor:** a visitor with no account
**Precondition:** not signed in
**Postcondition on success:** the account exists, the visitor is signed in, and
the task list is shown

| Step | Flow | Requirement |
|------|------|-------------|
| 1 | Open the registration page | R1 |
| 2 | Enter a username of 3–20 characters, letters, digits and underscore only | R1 |
| 3 | Enter a password of 8–128 characters | R1 |
| 4 | Submit | R1 |
| 5 | Signed in, task list shown, empty for a new account | R1, R13, R16 |

**Alternate — boundary values.** A 3-character and a 20-character username are
accepted; an 8-character password is accepted. R1

**Alternate — surrounding spaces.** Leading and trailing spaces in the
username are trimmed before validation. The password is not trimmed: spaces in
it are part of the password. R1

### UC1.2 — Registration is rejected

**Actor:** a visitor with no account
**Precondition:** not signed in
**Postcondition:** no account is created; the visitor stays on the
registration page with a visible message

| Step | Flow | Requirement |
|------|------|-------------|
| 1 | Open the registration page | R1 |
| 2 | Enter a username or password that breaks a rule, or a username that is already taken | R2, R3 |
| 3 | Submit | R2, R3 |
| 4 | A visible message names what is wrong; no account is created | R2, R3, R23 |

**Alternate — username already taken.** Compared case-insensitively, so
`ALICE` is taken when `alice` exists. R2

**Alternate — username or password breaks the rules.** Too short, too long,
illegal characters such as a hyphen, or empty. R3

**Exception — the rules are bypassed.** A request sent directly to the server,
skipping the page, is still rejected and stores nothing. R22, R23

---

## UC2 — Sessions

### UC2.1 — Sign in

**Actor:** a registered user
**Precondition:** the account exists; not signed in
**Postcondition on success:** a valid session; the task list is shown

| Step | Flow | Requirement |
|------|------|-------------|
| 1 | Open the sign-in page | R4 |
| 2 | Enter the username and password | R4 |
| 3 | Submit | R4 |
| 4 | Task list shown, containing this user's tasks only | R4, R13 |

**Alternate — username typed in a different case.** Accepted; the username is
matched case-insensitively. The password is matched exactly. R4

**Alternate — wrong password.** Visible message, no session. R5

**Alternate — username does not exist.** The **same** message as a wrong
password. A different message would tell an attacker which usernames are real.
R5

### UC2.2 — Sign out

**Actor:** a signed-in user
**Precondition:** valid session
**Postcondition:** the session is no longer valid

| Step | Flow | Requirement |
|------|------|-------------|
| 1 | Sign out | R6 |
| 2 | Request the task list again | R6, R7 |
| 3 | Redirected to sign-in; no task content is returned | R7 |

**Exception — Back button after signing out.** A protected page seen while
signed in is not served from cache afterwards. R28

### UC2.3 — Reach a protected page without a valid session

**Actor:** a visitor with no valid session
**Precondition:** not signed in, or holding a session that is no longer valid
**Postcondition:** redirected to sign-in; none of the protected content is
returned

| Step | Flow | Requirement |
|------|------|-------------|
| 1 | Request any page or endpoint outside the public set, including a path that does not exist | R7 |
| 2 | Redirected to `/signin`; no protected content in the response | R7 |

**Alternate — static assets.** Stylesheets and scripts are in the public set
and load on the sign-in page. R7

**Exception — the session names a user who no longer exists.** Treated as no
session at all. R27

### UC2.4 — Open sign-in or registration while already signed in

**Actor:** a signed-in user
**Precondition:** valid session
**Postcondition:** the user is on the task list

| Step | Flow | Requirement |
|------|------|-------------|
| 1 | Request `/signin` or `/register` | R29 |
| 2 | Redirected to `/tasks` | R29 |

---

## UC3 — Task management

### UC3.1 — Create a task

**Actor:** a signed-in user
**Precondition:** valid session
**Postcondition on success:** the task exists with status `open`, owned by
this user, and appears in their list

| Step | Flow | Requirement |
|------|------|-------------|
| 1 | Open the create form | R8 |
| 2 | Enter a title of 1–100 characters; description and due date are optional | R8 |
| 3 | Submit | R8 |
| 4 | The task exists with status `open` and appears in the list | R8, R13 |

**Alternate — empty or whitespace-only title.** Visible message, no task
created. R9, R23

**Alternate — boundary lengths.** A 1-character title and a 100-character
title are accepted; 0 and 101 are rejected. A 500-character description is
accepted, 501 is rejected. Lengths are counted after trimming. R8

**Alternate — the due date.** A valid `YYYY-MM-DD` is accepted, including one
in the past. A malformed string, or an impossible date such as `2026-02-30`,
is rejected with a visible message and nothing is stored. R26

**Exception — validation bypassed.** Submitted directly to the server, an
invalid title is still rejected and nothing is stored. R22, R23

### UC3.2 — Edit a task

**Actor:** a signed-in user
**Precondition:** valid session; the user owns the task
**Postcondition on success:** the task holds the new values

| Step | Flow | Requirement |
|------|------|-------------|
| 1 | Open one of the user's own tasks | R10 |
| 2 | Change the title, description or due date | R10 |
| 3 | Save | R10 |
| 4 | The task shows the new values | R10 |

**Alternate — invalid values.** The same rules as UC3.1 apply: a blank title,
an over-long title or description, or an invalid due date is rejected with a
visible message, and the task is unchanged. R10, R23

**Exception — validation bypassed.** An invalid edit sent directly to the
server is still rejected and the task is unchanged. R22, R23

### UC3.3 — Complete and reopen a task

**Actor:** a signed-in user
**Precondition:** valid session; the user owns the task
**Postcondition:** the status is `completed`, or `open` again after reopening

| Step | Flow | Requirement |
|------|------|-------------|
| 1 | Open one of the user's own tasks | R11 |
| 2 | Mark it completed | R11 |
| 3 | The status shows `completed` | R11 |
| 4 | Reopen it; the status shows `open` | R11 |

### UC3.4 — Delete a task

**Actor:** a signed-in user
**Precondition:** valid session; the user owns the task
**Postcondition:** the task no longer exists

| Step | Flow | Requirement |
|------|------|-------------|
| 1 | Open one of the user's own tasks | R12 |
| 2 | Delete it | R12 |
| 3 | Redirected to the list; a visible message confirms the deletion, shown once | R12 |
| 4 | The task no longer appears in the list | R12, R13 |

---

## UC4 — Finding tasks

### UC4.1 — View the task list

**Actor:** a signed-in user
**Precondition:** valid session
**Postcondition:** the user sees their own tasks

| Step | Flow | Requirement |
|------|------|-------------|
| 1 | Open the task list | R13 |
| 2 | See only this user's tasks, newest first by id, each with title, status and due date | R13, R30 |

**Alternate — no tasks at all.** A new account sees an explicit "No tasks
found" message, not a blank area. R16

### UC4.2 — Search and filter tasks

**Actor:** a signed-in user
**Precondition:** valid session; the user owns some tasks
**Postcondition:** the list shows only the matching tasks

| Step | Flow | Requirement |
|------|------|-------------|
| 1 | Open the task list | R13 |
| 2 | Search by a substring of a title or description, ignoring case | R14 |
| 3 | Filter by all, open, or completed | R15 |
| 4 | Apply search and filter together | R15 |

**Alternate — search text that looks like a pattern.** Treated as literal
text, never as a pattern or expression. R14

**Alternate — missing or unknown filter value.** Treated as `all`, as the
route table in the requirements states. R15

**Alternate — nothing matches.** An explicit "No tasks found" message, not a
blank area. R16

---

## UC5 — Access control

**Actor (all three):** a signed-in user attempting to reach another user's task
**Precondition (all three):** two accounts exist, each owning at least one task

This area is the source of the critical-severity scenarios, and therefore of
the critical gate in D-005. Every flow here is an attempt that must fail.

**Exception — authorisation only in the UI (applies to all three).** Hiding a
button is not authorisation. Every read and write of a task is checked on the
server, and sequential ids are not a defence. R21

### UC5.1 — Read another user's task

**Postcondition:** nothing about the other user's task is revealed

| Attempt | Required outcome | Requirement |
|---------|------------------|-------------|
| Open another user's task by its URL | 404; **no part of the task's content appears anywhere in the response** | R17 |
| Compare the response for another user's id with one for an id that does not exist | Indistinguishable — same status, page and message | R25 |
| Guess a neighbouring task id after creating one's own task | Same as above; sequential ids are not a defence | R21 |
| Reach any of the above after signing out | Redirected to sign-in | R7 |

**Why R17 is written as "no part of the content appears":** a 404 status with
the task's title leaking into the page is the exact kind of defect that passes
a status-code assertion and fails a user-level scenario. Checking the status
alone would not catch it.

### UC5.2 — Change another user's task

**Postcondition:** the other user's task is unchanged and still exists

| Attempt | Required outcome | Requirement |
|---------|------------------|-------------|
| Submit an edit for another user's task | Rejected; the task is unchanged | R18 |
| Submit a delete for another user's task | Rejected; the task still exists | R19 |
| Submit a status toggle for another user's task | Rejected; the status is unchanged | R24 |

### UC5.3 — Keep each user's list and search results separate

**Postcondition:** no list or search result contains another user's task

| Attempt | Required outcome | Requirement |
|---------|------------------|-------------|
| Search for text that only another user's task contains | No results | R20 |
| Sign out, sign in as another user, open the list | Only the second user's tasks | R13, R20 |

---

## Coverage check

R1 → UC1.1 · R2 R3 → UC1.2 · R4 R5 → UC2.1 · R6 R28 → UC2.2 ·
R7 R27 → UC2.3 · R29 → UC2.4 · R8 R9 R26 → UC3.1 · R10 → UC3.2 ·
R11 → UC3.3 · R12 → UC3.4 · R13 R30 → UC4.1 · R14 R15 → UC4.2 ·
R16 → UC4.1, UC4.2 · R17 R25 → UC5.1 · R18 R19 R24 → UC5.2 ·
R20 → UC5.3 · R21 → UC5.1, UC5.2 · R22 R23 → exception flows in UC1.2,
UC3.1, UC3.2

All thirty requirements of version 1.1 are covered. No use case introduces behaviour
that is not in the requirements document; if one appears to, the requirements
document is wrong and is corrected there first, before V0 is generated.

---

## Accepted scenarios by use case

The 47 accepted scenarios in `scenarios/library/`, placed in the refined use
cases. The `use_case` field in each scenario file names the area; this table
names the use case within it. The two `cross` scenarios walk through several
use cases in one run.

| Use case | Scenarios | Count |
|----------|-----------|------:|
| UC1.1 Register an account | REG-01, REG-04, REG-05, REG-10, REG-12 | 5 |
| UC1.2 Registration is rejected | REG-03, REG-07, REG-09 | 3 |
| UC2.1 Sign in | SES-01, SES-02, SES-03, SES-04, SES-05 | 5 |
| UC2.2 Sign out | SES-07, SES-13 | 2 |
| UC2.3 Protected page without a session | SES-08 | 1 |
| UC2.4 Sign-in page while signed in | SES-11 | 1 |
| UC3.1 Create a task | TSK-01, TSK-02, TSK-03, TSK-04, TSK-05, TSK-06, TSK-08, TSK-10, TSK-11 | 9 |
| UC3.2 Edit a task | TSK-13, TSK-14, TSK-20 | 3 |
| UC3.3 Complete and reopen a task | TSK-15 | 1 |
| UC3.4 Delete a task | TSK-17 | 1 |
| UC4.1 View the task list | LST-01, LST-02, LST-14 | 3 |
| UC4.2 Search and filter tasks | LST-04, LST-05, LST-09, LST-11 | 4 |
| UC5.1 Read another user's task | ACC-01, ACC-06 | 2 |
| UC5.2 Change another user's task | ACC-02, ACC-03, ACC-04 | 3 |
| UC5.3 Separate lists and search results | ACC-08, ACC-10 | 2 |
| Across use cases | INT-01 (UC1.1, UC2.1, UC3.1, UC4.1), INT-02 (UC3.1–UC3.4) | 2 |
| **Total** | | **47** |

Every use case has at least one accepted scenario. R27 has none: a session
naming a deleted user cannot be reached through the interface, because no
route deletes a user (recorded in `scenarios/validation.md`).

---

## What happens to these next

| Week | Task | |
|------|------|--|
| 4 | T10 | Generate candidate scenarios from these flows |
| 4 | T11 | Validate each against the Appendix B checklist; assign category and severity; drop duplicates and anything not observable |
| 5 | T12 | Freeze and tag the library as a holdout set |

Target spread, from the proposal: about 40–50 scenarios across five
categories — normal, failure, edge, adversarial/robustness, integration — with
adversarial at roughly 15%, drawn mostly from UC5.
