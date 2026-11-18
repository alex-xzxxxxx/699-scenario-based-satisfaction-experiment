# Run 40f98cec588ea7dc

**Scenario ACC-01** · adversarial · severity critical · R17, R21

**Preconditions.** Seed state. Task 5 belongs to bob; it is titled "Reply to supplier" and described "Confirm the delivery window". Alice does not own it.

**User action.** Signed in as alice, request bob's task by its URL.

**Expected behaviour.** The response is a 404 page, and no part of bob's task appears anywhere in it — not the title, not the description. A 404 status that still shows the title fails this scenario.

**Expected evidence.** The HTTP status, and the full visible page text, so it can be compared against bob's title and description.

## What happened

 1. **reset** — seed data restored
      - url: about:blank
 2. **sign_in** — signed in as 'alice'
      - url: /tasks
      - visible text: TaskTracker · Signed in as alice · Tasks · New task · Sign out · Your tasks · New task · Search · Status · All · Open · Completed · Search · Buy printer paper · open · Due 2026-11-20 · Renew library card · completed · Book flights · open · Due 2026-12-05 · Draft project outline · open · Due 2026-12-01
 3. **request** — requested /tasks/5 directly
      - url: /tasks
      - status: 404
 4. **goto** — requested /tasks/5
      - url: /tasks/5
      - status: 404
      - visible text: The page you requested was not found. · Not found · The page you requested was not found. · Back to your tasks
 5. **capture** — alice requesting bob's task: url http://localhost:3000/tasks/5; no task rows; message: 'The page you requested was not found.'
      - url: /tasks/5

**Final state.** final: url http://localhost:3000/tasks/5; no task rows; message: 'The page you requested was not found.'
