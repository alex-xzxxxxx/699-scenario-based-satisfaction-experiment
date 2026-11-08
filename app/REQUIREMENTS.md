# TaskTracker — Requirements

Version 1.0 · 8 November 2026

Build a small task-tracking web application that meets the requirements below.
Nothing outside this document is part of the specification.

---

## 1. Technical constraints

| | |
|---|---|
| Runtime | Node.js 20 or later |
| Server | Express |
| Front end | Plain HTML, CSS and JavaScript. **No front-end framework** (no React, Angular, Vue, Svelte) |
| Sessions | Server-side sessions with an HTTP-only session cookie |
| Passwords | Stored hashed, using `node:crypto` `scrypt` with a per-user salt. Never stored or logged in plain text |
| Storage | A single JSON file on disk, `data/db.json` |
| Dependencies | `express` and `express-session` only. No database, no ORM, no other runtime dependency |
| Network | The application makes no outbound network calls |
| Start | `npm start` serves the application on `http://localhost:3000` |
| Reset | `npm run reset` restores `data/db.json` to the seed data in section 5 and exits |

Keep the code small and readable: a single `server.js` plus a handful of static
files is preferred over a layered structure.

---

## 2. Requirements

Every requirement below is observable through the browser. Each has an ID; use
these IDs in commit messages and comments where it helps.

### Accounts and sessions

| ID | Requirement |
|----|-------------|
| R1 | A visitor can register with a username and a password. Username: 3–20 characters, letters, digits and underscore only, unique, case-insensitive for the uniqueness check. Password: at least 8 characters. On success the user is signed in and lands on the task list. |
| R2 | Registration with a username that already exists is rejected with a visible message, and no account is created. |
| R3 | Registration with a username or password that breaks the rules in R1 is rejected with a visible message naming what is wrong, and no account is created. |
| R4 | A registered user can sign in with the correct username and password and lands on the task list. |
| R5 | Signing in with a wrong password, or with a username that does not exist, is rejected with a visible message. The two cases produce the same message. No session is created. |
| R6 | A signed-in user can sign out. Afterwards the session is no longer valid. |
| R7 | A request to any page or endpoint that is not the home, sign-in or registration page, made without a valid session, is redirected to the sign-in page. Nothing of the protected content is returned. |

### Tasks

| ID | Requirement |
|----|-------------|
| R8 | A signed-in user can create a task with a title (required, 1–100 characters), an optional description (up to 500 characters) and an optional due date. A new task has status `open`. |
| R9 | Creating a task with an empty or whitespace-only title is rejected with a visible message, and no task is created. |
| R10 | A user can edit the title, description and due date of their own task. The same validation as R8 and R9 applies. |
| R11 | A user can mark their own task completed, and can reopen a completed task. Status is `open` or `completed`. |
| R12 | A user can delete their own task. After deletion the task no longer appears in the list, and a visible message confirms the deletion. |

### Listing and search

| ID | Requirement |
|----|-------------|
| R13 | The task list shows the signed-in user's tasks and no others, most recently created first. Each row shows the title, status and due date if set. |
| R14 | The user can search their tasks by text. The search matches a substring of the title or the description, ignoring case. |
| R15 | The user can filter the list by status: all, open, or completed. Search and filter apply together. |
| R16 | When a search or filter returns no tasks, the page shows an explicit "No tasks found" message rather than an empty area. |

### Access control

| ID | Requirement |
|----|-------------|
| R17 | A user who requests another user's task by its URL does not receive the task. The response is a 404 page, and no part of the task's content appears anywhere in it. |
| R18 | A user who submits an edit for another user's task is rejected. The task is unchanged. |
| R19 | A user who submits a delete for another user's task is rejected. The task still exists. |
| R20 | Search and filter never return another user's tasks, under any search text. |
| R21 | Authorisation is checked on the server for every request that reads or changes a task. Hiding a control in the page is not sufficient. Task identifiers may be sequential; the server must not rely on them being hard to guess. |

### Validation

| ID | Requirement |
|----|-------------|
| R22 | Every validation rule in R1, R3, R8, R9 and R10 is enforced on the server. Client-side checks may be added as well, but a request sent directly to the server must still be rejected. |
| R23 | A rejected request leaves stored data unchanged. |

---

## 3. Page and message conventions

These make the application testable. Follow them exactly.

- Every interactive element carries a stable `data-testid` attribute. Use these
  names: `nav-signin`, `nav-register`, `nav-signout`, `username-input`,
  `password-input`, `submit-button`, `task-title-input`, `task-description-input`,
  `task-due-input`, `task-create-button`, `task-save-button`,
  `task-delete-button`, `task-complete-toggle`, `search-input`,
  `status-filter`, `task-list`, `task-row`, `empty-message`.
- Each row in the task list carries `data-testid="task-row"` and
  `data-task-id="<id>"`.
- Every success or error message is rendered inside one container with
  `data-testid="message"`. Exactly one message container per page.
- Messages are plain sentences in English and state what happened.

---

## 4. Routes

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/` | Home. Signed in: redirect to `/tasks`. Signed out: links to sign in and register |
| GET, POST | `/register` | Registration form and submission |
| GET, POST | `/signin` | Sign-in form and submission |
| POST | `/signout` | End the session |
| GET | `/tasks` | Task list, with search and filter as query parameters |
| GET, POST | `/tasks/new` | Create form and submission |
| GET | `/tasks/:id` | One task |
| GET, POST | `/tasks/:id/edit` | Edit form and submission |
| POST | `/tasks/:id/delete` | Delete |
| POST | `/tasks/:id/toggle` | Mark completed or reopen |

---

## 5. Seed data

`npm run reset` writes exactly this state.

Users, with passwords shown here in plain text for setup only; they are stored
hashed:

| Username | Password |
|----------|----------|
| `alice` | `alicepass123` |
| `bob` | `bobpass123` |
| `carol` | `carolpass123` |

Tasks, created in this order so that the newest-first ordering of R13 is
deterministic:

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
real browser at `http://localhost:3000`. Place it in `app/tests_a/`. Each test
resets the application state before it runs, by invoking the reset in section 1.

Include a short `app/README.md` saying how to install, seed, start and test.

---

## 7. Out of scope

No password reset, no email, no roles or administrators, no pagination, no file
upload, no API tokens, no deployment configuration, no Docker, no CI
configuration, no analytics, no styling beyond what is needed to read the pages.
