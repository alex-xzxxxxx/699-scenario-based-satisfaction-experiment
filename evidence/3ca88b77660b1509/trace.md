# Run 3ca88b77660b1509

**Scenario ACC-06** · adversarial · severity critical · R25, R21

**Preconditions.** Seed state. Task 5 belongs to bob. No task has id 999999.

**User action.** Signed in as alice, request bob's task id and a non-existent id by the same routes, and compare the two responses.

**Expected behaviour.** The two responses are indistinguishable — same status, same page, same message. If they differ in any way, alice can discover which task ids exist by trying them.

**Expected evidence.** Both status codes and both bodies for each pair of requests, and whether each pair matched.

## What happened

 1. **reset** — seed data restored
      - url: about:blank
 2. **sign_in** — signed in as 'alice'
      - url: /tasks
      - visible text: TaskTracker · Signed in as alice · Tasks · New task · Sign out · Your tasks · New task · Search · Status · All · Open · Completed · Search · Buy printer paper · open · Due 2026-11-20 · Renew library card · completed · Book flights · open · Due 2026-12-05 · Draft project outline · open · Due 2026-12-01
 3. **compare_responses** — compared GET /tasks/5 against /tasks/999999 — status 404 vs 404 (same), body identical
      - url: /tasks
      - status: 404
 4. **compare_responses** — compared GET /tasks/5/edit against /tasks/999999/edit — status 404 vs 404 (same), body identical
      - url: /tasks
      - status: 404
 5. **compare_responses** — compared POST /tasks/5/toggle against /tasks/999999/toggle — status 404 vs 404 (same), body identical
      - url: /tasks
      - status: 404
 6. **capture** — after the comparisons: url http://localhost:3000/tasks; 4 task row(s): Buy printer paper · open · Due 2026-11-20 | Renew library card · completed | Book flights · open · Due 2026-12-05 | Draft project outline · open · Due 2026-12-01
      - url: /tasks

**Final state.** final: url http://localhost:3000/tasks; 4 task row(s): Buy printer paper · open · Due 2026-11-20 | Renew library card · completed | Book flights · open · Due 2026-12-05 | Draft project outline · open · Due 2026-12-01
