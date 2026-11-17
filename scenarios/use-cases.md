# Use cases — UC1 to UC5

Written from `app/REQUIREMENTS.md` v1.0, in Week 2, before V0 exists.

These are the source from which candidate scenarios are generated (T10) and
validated (T11). They live inside `scenarios/`, which is **holdout** — the
implementation model never sees this folder.

A use case is not a scenario. A use case describes what the system is for; a
scenario is one concrete, executable path through it with a known expected
outcome. Scenarios are written in Week 4 and frozen at the end of Week 5.

Each flow below cites the requirement it rests on, so that every scenario
generated later inherits a requirement ID and EQ4 has a clean unit of
comparison against the test suites.

---

## UC1 — Register an account

**Actor:** a visitor with no account
**Precondition:** not signed in
**Postcondition on success:** the account exists, the visitor is signed in, and
the task list is shown

| Step | Flow | Requirement |
|------|------|-------------|
| 1 | Open the registration page | R1 |
| 2 | Enter a username of 3–20 characters, letters, digits and underscore only | R1 |
| 3 | Enter a password of at least 8 characters | R1 |
| 4 | Submit | R1 |
| 5 | Signed in, task list shown, empty for a new account | R1, R13 |

**Alternate — username already taken.** Visible message, no account created,
still on the registration page. R2

**Alternate — username or password breaks the rules.** Too short, too long,
illegal characters, empty. Visible message naming what is wrong. No account
created. R3, R22

**Exception — the rules are bypassed.** A request sent directly to the server,
skipping the page, is still rejected and stores nothing. R22, R23

---

## UC2 — Sign in, sign out, hold a session

**Actor:** a registered user
**Precondition:** the account exists
**Postcondition on success:** a valid session; protected pages are reachable

| Step | Flow | Requirement |
|------|------|-------------|
| 1 | Open the sign-in page | R4 |
| 2 | Enter the correct username and password | R4 |
| 3 | Submit | R4 |
| 4 | Task list shown, containing this user's tasks only | R4, R13 |
| 5 | Sign out | R6 |
| 6 | The session is no longer valid | R6, R7 |

**Alternate — wrong password.** Visible message, no session. R5

**Alternate — username does not exist.** The **same** message as a wrong
password. A different message would tell an attacker which usernames are real.
R5

**Exception — no session.** Any protected page or endpoint requested without a
valid session redirects to sign-in, and none of the protected content is
returned. R7

**Exception — the session names a user who no longer exists.** Treated as no
session at all. R27

**Exception — Back button after signing out.** A protected page seen while
signed in is not served from cache afterwards. R28

**Alternate — already signed in.** Requesting the sign-in or registration page
redirects to the task list. R29

---

## UC3 — Create and edit a task

**Actor:** a signed-in user
**Precondition:** valid session
**Postcondition on success:** the task exists, owned by this user, and appears
in their list

| Step | Flow | Requirement |
|------|------|-------------|
| 1 | Open the create form | R8 |
| 2 | Enter a title of 1–100 characters; description and due date are optional | R8 |
| 3 | Submit | R8 |
| 4 | The task exists with status `open` and appears in the list | R8, R13 |
| 5 | Edit the title, description or due date | R10 |
| 6 | Mark it completed, then reopen it | R11 |
| 7 | Delete it; a visible message confirms, and it leaves the list | R12 |

**Alternate — empty or whitespace-only title.** Visible message, no task
created. The same rule applies on edit. R9, R10

**Alternate — boundary lengths.** A 1-character title and a 100-character
title are accepted; 0 and 101 are rejected. A 500-character description is
accepted, 501 is rejected. Lengths are counted after trimming. R8, R10

**Alternate — the due date.** A valid `YYYY-MM-DD` is accepted, including one
in the past. A malformed string, or an impossible date such as `2026-02-30`,
is rejected with a visible message and nothing is stored. R26

**Exception — validation bypassed.** Submitted directly to the server, an
invalid title is still rejected and nothing is stored. R22, R23

---

## UC4 — Find a task

**Actor:** a signed-in user
**Precondition:** valid session; the user owns some tasks

| Step | Flow | Requirement |
|------|------|-------------|
| 1 | Open the task list | R13 |
| 2 | See only this user's tasks, newest first by id, with title, status and due date | R13, R30 |
| 3 | Search by a substring of a title or description, ignoring case | R14 |
| 4 | Filter by all, open, or completed | R15 |
| 5 | Apply search and filter together | R15 |

**Alternate — nothing matches.** An explicit "No tasks found" message, not a
blank area. R16

**Alternate — search text that matches another user's task.** Returns nothing.
The result does not depend on what other users own. R20

---

## UC5 — Access control

**Actor:** a signed-in user attempting to reach another user's task
**Precondition:** two accounts exist, each owning at least one task

This use case is the source of the critical-severity scenarios, and therefore
of the critical gate in D-005. Every flow here is an attempt that must fail.

| Attempt | Required outcome | Requirement |
|---------|------------------|-------------|
| Open another user's task by its URL | 404; **no part of the task's content appears anywhere in the response** | R17 |
| Submit an edit for another user's task | Rejected; the task is unchanged | R18 |
| Submit a delete for another user's task | Rejected; the task still exists | R19 |
| Submit a status toggle for another user's task | Rejected; the status is unchanged | R24 |
| Compare the response for another user's id with one for an id that does not exist | Indistinguishable — same status, page and message | R25 |
| Search for text that only another user's task contains | No results | R20 |
| Guess a neighbouring task id after creating one's own task | Same as above; sequential ids are not a defence | R21 |
| Reach any of the above after signing out | Redirected to sign-in | R7 |

**Why R17 is written as "no part of the content appears":** a 404 status with
the task's title leaking into the page is the exact kind of defect that passes
a status-code assertion and fails a user-level scenario. Checking the status
alone would not catch it.

**Exception — authorisation only in the UI.** Hiding a button is not
authorisation. Every read and write of a task is checked on the server. R21

---

## Coverage check

R1 R2 R3 → UC1 · R4 R5 R6 R7 R27 R28 R29 → UC2 ·
R8 R9 R10 R11 R12 R26 → UC3 · R13 R14 R15 R16 R30 → UC4 ·
R17 R18 R19 R20 R21 R24 R25 → UC5 ·
R22 R23 → exception flows in UC1, UC3

All thirty requirements of version 1.1 are covered. No use case introduces behaviour
that is not in the requirements document; if one appears to, the requirements
document is wrong and is corrected there first, before V0 is generated.

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
