# Run f8b935f47365c0fd

**Scenario TSK-03** · failure · severity high · R9, R23

**Preconditions.** Seed state, signed in as alice, who owns four tasks.

**User action.** Open the create form, leave the title empty, and submit.

**Expected behaviour.** The submission is rejected with a visible message, and no task is created — alice still owns four.

**Expected evidence.** The message text, and the number of task rows in alice's list before and after the attempt.

## What happened

 1. **reset** — seed data restored
      - url: about:blank
 2. **sign_in** — signed in as 'alice'
      - url: /tasks
      - visible text: TaskTracker · Signed in as alice · Tasks · New task · Sign out · Your tasks · New task · Search · Status · All · Open · Completed · Search · Buy printer paper · open · Due 2026-11-20 · Renew library card · completed · Book flights · open · Due 2026-12-05 · Draft project outline · open · Due 2026-12-01
 3. **goto** — requested /tasks
      - url: /tasks
      - status: 200
 4. **capture** — list before: url http://localhost:3000/tasks; 4 task row(s): Buy printer paper · open · Due 2026-11-20 | Renew library card · completed | Book flights · open · Due 2026-12-05 | Draft project outline · open · Due 2026-12-01
      - url: /tasks
 5. **goto** — requested /tasks/new
      - url: /tasks/new
      - status: 200
      - visible text: Title · Description (optional) · Due date (optional, YYYY-MM-DD) · Create task Cancel
 6. **fill** — filled title with ''
      - url: /tasks/new
 7. **fill** — filled description with 'Orphan description'
      - url: /tasks/new
 8. **click** — clicked create
      - url: /tasks/new
      - visible text: Title is required.
 9. **capture** — immediately after submitting: url http://localhost:3000/tasks/new; no task rows; message: 'Title is required.'
      - url: /tasks/new
10. **goto** — requested /tasks
      - url: /tasks
      - status: 200
      - visible text: Your tasks · Search · Status · All · Open · Completed · Search · Buy printer paper · open · Due 2026-11-20 · Renew library card · completed · Book flights · open · Due 2026-12-05 · Draft project outline · open · Due 2026-12-01
11. **capture** — list after: url http://localhost:3000/tasks; 4 task row(s): Buy printer paper · open · Due 2026-11-20 | Renew library card · completed | Book flights · open · Due 2026-12-05 | Draft project outline · open · Due 2026-12-01
      - url: /tasks

**Final state.** final: url http://localhost:3000/tasks; 4 task row(s): Buy printer paper · open · Due 2026-11-20 | Renew library card · completed | Book flights · open · Due 2026-12-05 | Draft project outline · open · Due 2026-12-01
