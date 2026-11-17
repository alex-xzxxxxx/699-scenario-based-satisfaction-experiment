# TaskTracker — Requirements

Version 1.1 · 16 November 2026

Build a small task-tracking web application that meets the requirements below.
Nothing outside this document is part of the specification.

---

## 1. Technical constraints

| | |
|---|---|
| Runtime | Node.js 20 or later |
| Server | Express |
| Front end | Plain HTML, CSS and JavaScript. **No front-end framework** (no React, Angular, Vue, Svelte) |
| Sessions | Server-side sessions with an HTTP-only session cookie, `sameSite: 'lax'` |
| Passwords | Stored hashed, using `node:crypto` `scrypt` with a per-user salt. Never stored or logged in plain text |
| Storage | A single JSON file on disk, `data/db.json` |
| Reading storage | **The server reads `data/db.json` from disk on every request that reads or writes data, and writes it back synchronously.** It must not hold the data in memory across requests |
| Dependencies | `express` and `express-session` only. No database, no ORM, no other runtime dependency |
| Network | The application makes no outbound network calls |
| Start | `npm start` serves the application on `http://localhost:3000` |
| Reset | `npm run reset` restores `data/db.json` to the seed data in section 5 and exits. **It must take effect on a server that is already running, without restarting it** |

Keep the code small and readable: a single `server.js` plus a handful of static
files is preferred over a layered structure.

---

## 2. Requirements

Every requirement below is observable through the browser. Each has an ID; use
these IDs in commit messages and comments where it helps.

### Accounts and sessions

| ID | Requirement |
|----|-------------|
| R1 | A visitor can register with a username and a password. Username: 3–20 characters after trimming leading and trailing whitespace, letters, digits and underscore only, unique, compared case-insensitively for uniqueness. Password: 8–128 characters, not trimmed. On success the user is signed in and lands on the task list. |
| R2 | Registration with a username that already exists, compared case-insensitively, is rejected with a visible message, and no account is created. |
| R3 | Registration with a username or password that breaks the rules in R1 is rejected with a visible message naming what is wrong, and no account is created. |
| R4 | A registered user can sign in with the correct username and password and lands on the task list. The username is matched case-insensitively; the password is matched exactly. The username is displayed as it was typed at registration. |
| R5 | Signing in with a wrong password, or with a username that does not exist, is rejected with a visible message. The two cases produce the same message. No session is created. |
| R6 | A signed-in user can sign out. Afterwards the session is no longer valid. |
| R7 | Everything other than the public set is protected. The public set is exactly: `GET /`, `GET /register`, `POST /register`, `GET /signin`, `POST /signin`, and static assets such as CSS and JavaScript files. Any other request without a valid session is redirected to `/signin`, including requests for paths that do not exist. No part of the protected content is returned. |
| R27 | If a session names a user that no longer exists in the stored data, the request is treated as unauthenticated and handled under R7. |
| R28 | Responses for protected pages carry `Cache-Control: no-store`, so that after signing out the browser's Back button does not show a page that was visible while signed in. |
| R29 | A signed-in user who requests `/signin` or `/register` is redirected to `/tasks`. |

### Tasks

| ID | Requirement |
|----|-------------|
| R8 | A signed-in user can create a task with a title (required, 1–100 characters after trimming), an optional description (up to 500 characters after trimming) and an optional due date. A new task has status `open`. |
| R9 | Creating a task with an empty or whitespace-only title is rejected with a visible message, and no task is created. |
| R10 | A user can edit the title, description and due date of their own task. The same validation as R8, R9 and R26 applies. |
| R11 | A user can mark their own task completed, and can reopen a completed task. Status is `open` or `completed`. |
| R12 | A user can delete their own task. After deletion the task no longer appears in the list, and a visible message confirms the deletion. The message survives the redirect that follows the delete and is shown once. |
| R26 | A due date, when given, must be a valid calendar date in `YYYY-MM-DD` form. Dates in the past are accepted. Anything else — a malformed string, or a well-formed but impossible date such as `2026-02-30` — is rejected with a visible message, and nothing is stored. |

### Listing and search

| ID | Requirement |
|----|-------------|
| R13 | The task list shows the signed-in user's tasks and no others, most recently created first. Each row shows the title, status and due date if set. |
| R30 | Each task has an integer id, assigned in increasing order as tasks are created and never reused. "Most recently created first" in R13 means descending id, so the order is the same on every run. |
| R14 | The user can search their tasks by text. A task matches when the search text occurs as a substring of its title or description, ignoring case. The search text is treated as literal text, never as a pattern or expression. |
| R15 | The user can filter the list by status: `all`, `open`, or `completed`. Search and filter apply together. |
| R16 | When the list has nothing to show — whether because a search or filter matched nothing, or because the user has no tasks at all — the page shows an explicit "No tasks found" message rather than an empty area. |

### Access control

| ID | Requirement |
|----|-------------|
| R17 | A user who requests another user's task by its URL does not receive the task. The response is a 404 page, and no part of the task's content appears anywhere in it. |
| R18 | A user who submits an edit for another user's task is rejected. The task is unchanged. |
| R19 | A user who submits a delete for another user's task is rejected. The task still exists. |
| R24 | A user who submits a status toggle for another user's task is rejected. The task's status is unchanged. |
| R25 | For every route that names a task id, the response when the task belongs to another user is indistinguishable from the response when no task with that id exists — same status code, same page, same message. A user must not be able to learn which ids exist by trying them. |
| R20 | Search and filter never return another user's tasks, under any search text. |
| R21 | Authorisation is checked on the server for every request that reads or changes a task. Hiding a control in the page is not sufficient. Task identifiers are sequential; the server must not rely on them being hard to guess. |

### Validation

| ID | Requirement |
|----|-------------|
| R22 | Every validation rule in R1, R3, R8, R9, R10 and R26 is enforced on the server. Client-side checks may be added as well, but a request sent directly to the server must still be rejected. |
| R23 | A rejected request leaves stored data unchanged. |

---

## 3. Page and message conventions

These make the application testable. Follow them exactly.

- Every interactive element carries a stable `data-testid` attribute. Use these
  names: `nav-signin`, `nav-register`, `nav-signout`, `username-input`,
  `password-input`, `submit-button`, `task-title-input`, `task-description-input`,
  `task-due-input`, `task-create-button`, `task-save-button`,
  `task-delete-button`, `task-complete-toggle`, `search-input`,
  `search-submit`, `status-filter`, `task-list`, `task-row`, `empty-message`.
- Each row in the task list carries `data-testid="task-row"` and
  `data-task-id="<id>"`. A row links to that task's page; the row itself holds
  no delete or toggle control.
- `task-delete-button` and `task-complete-toggle` appear on a single task's
  page, `/tasks/:id`, not in the list.
- Every success or error message is rendered inside one container with
  `data-testid="message"`. Exactly one such container per page, and it is
  always present in the markup — empty when there is no message to show.
- The "No tasks found" text of R16 goes in `data-testid="empty-message"`, not
  in the message container.
- Messages are plain sentences in English and state what happened.

---

## 4. Routes

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/` | Home. Signed in: redirect to `/tasks`. Signed out: links to sign in and register |
| GET, POST | `/register` | Registration form and submission |
| GET, POST | `/signin` | Sign-in form and submission |
| POST | `/signout` | End the session |
| GET | `/tasks` | Task list. Search and filter are query parameters on a GET form: `q` is the search text, `status` is `all`, `open` or `completed`. A missing or unrecognised `status` is treated as `all`; a missing `q` means no search |
| GET, POST | `/tasks/new` | Create form and submission |
| GET | `/tasks/:id` | One task |
| GET, POST | `/tasks/:id/edit` | Edit form and submission |
| POST | `/tasks/:id/delete` | Delete |
| POST | `/tasks/:id/toggle` | Mark completed or reopen |

---

## 5. Seed data

`npm run reset` writes exactly this state. Password hashes use a fresh random
salt each time, so the bytes of `data/db.json` differ between resets; the
behaviour it describes does not.

Users, with passwords shown here in plain text for setup only; they are stored
hashed:

| Username | Password |
|----------|----------|
| `alice` | `alicepass123` |
| `bob` | `bobpass123` |
| `carol` | `carolpass123` |

Tasks, created in this order, so that ids ascend down the table and the
newest-first ordering of R13 and R30 is deterministic:

| Owner | Title | Description | Due | Status |
|-------|-------|-------------|-----|--------|
| alice | Draft project outline | Sections and rough word counts | 2026-12-01 | open |
| alice | Book flights | Compare two airlines before booking | 2026-12-05 | open |
| alice | Renew library card | | | completed |
| alice | Buy printer paper | A4, two reams | 2026-11-20 | open |
| bob | Reply to supplier | Confirm the delivery window | 2026-11-25 | open |
| bob | Pay invoice 2291 | | 2026-11-18 | completed |
| bob | Draft budget sheet | Include travel and printing | | open |
| carol | Collect parcel | | 2026-11-15 | open |

---

## 6. Also deliver

An automated test suite for the application, written as **Python** files using
`pytest` and Playwright's synchronous API, driving the application through a
real browser at `http://localhost:3000`. Place it in `app/tests_a/`.

Each test starts from the seed state. A test resets by running `npm run reset`
as a subprocess before it begins, against the already-running server — which
works because of the storage rules in section 1. Each test uses a fresh browser
context, so no session survives from one test to the next.

Include a short `app/README.md` saying how to install, seed, start and test.

---

## 7. Out of scope

No password reset, no email, no roles or administrators, no pagination, no file
upload, no API tokens, no deployment configuration, no Docker, no CI
configuration, no analytics, no styling beyond what is needed to read the pages.
There is no notion of a task being overdue.

---

## Changes from version 1.0

Version 1.0 left behaviour undefined in places where two competent
implementations would reasonably differ. Because section 1 states that nothing
outside this document is part of the specification, each of those gaps would
have produced disagreement between the two test suites and the scoring, for
reasons that had nothing to do with the application's quality.

**Clarified, no change of intent:** R1 and R8 now say that input is trimmed
before validation · R1 and R4 state how case is treated on registration and
sign-in · R7 names the public set exactly, so that stylesheets load on the
sign-in page · R12 says the confirmation survives the redirect · R13 is pinned
to a deterministic order by R30 · R14 says the search text is literal, not a
pattern · R16 covers a user with no tasks, not only an empty search ·
section 3 says the message container is always present and that "No tasks
found" lives in `empty-message` · section 4 names the query parameters ·
section 5 notes that reset is behaviourally, not byte, identical.

**New requirements:** R24 toggle authorisation, which no requirement covered ·
R25 indistinguishable responses for another user's id and a non-existent id ·
R26 due-date validation, which R22 referred to but R8 never defined · R27
sessions naming a deleted user · R28 no caching of protected pages · R29
redirect away from sign-in when already signed in · R30 deterministic ids
and ordering.

**New constraints in section 1:** the server reads storage from disk per
request, so that `npm run reset` takes effect on a running server — without
this, every test after the first would run against contaminated state · a
128-character password ceiling · `sameSite: 'lax'` on the session cookie.

**Deliberately left as they are:** R2 reveals whether a username exists while
R5 conceals it. That is a real tension in the specification rather than an
oversight, and it is reported rather than resolved.

**Still deliberately unspecified:** how thorough the test suite in section 6
should be. Section 6 fixes its form so that it is comparable with the
hand-written suite, and says nothing about coverage.
