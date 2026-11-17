# TaskTracker

A small task-tracking web application (Express, plain HTML/CSS, JSON-file storage),
built to `REQUIREMENTS.md` v1.1.

## Install

Requires Node.js 20 or later.

```sh
npm install
```

## Seed

```sh
npm run reset
```

Restores `data/db.json` to the seed data (users `alice` / `alicepass123`,
`bob` / `bobpass123`, `carol` / `carolpass123`, and their eight tasks). The server
reads the file on every request, so this also works while the server is running.
If `data/db.json` is missing when the server starts, it is created from the seed.

## Start

```sh
npm start
```

Serves the application on <http://localhost:3000>.

## Test

The suite in `tests_a/` uses Python, `pytest` and Playwright's synchronous API, and
drives a real Chromium against the running server.

```sh
pip install pytest playwright
python -m playwright install chromium

npm start            # in one terminal
python -m pytest tests_a   # in another, from this directory
```

Each test runs `npm run reset` before it starts and uses a fresh browser context.
Set `TASKTRACKER_URL` to test a server at a different address.

## Layout

| File | Purpose |
|------|---------|
| `server.js` | The whole application: routes, validation, rendering |
| `db.js` | Read/write `data/db.json`, password hashing (scrypt), seed data |
| `reset.js` | `npm run reset` |
| `public/style.css` | Stylesheet |
| `tests_a/` | Browser test suite |

## Notes

- Form inputs carry no browser-side validation attributes (`required`, `maxlength`,
  `type="date"`), so every rule is checked, and testable, on the server (R22). The due
  date is a text field taking `YYYY-MM-DD`.
- A task that belongs to another user and a task id that does not exist get the same
  404 page on every task route (R25). Ownership is checked before input validation, so
  an invalid edit to someone else's task does not reveal that it exists.
- Sessions record the user's id plus a random per-account token. After `npm run reset`
  (or any removal of the account) such a session no longer matches a stored user and is
  treated as signed out (R27), even if a later account reuses the same numeric id.
- As the specification notes, R2 reveals whether a username is taken while R5 does not.
  That tension is left as specified.
