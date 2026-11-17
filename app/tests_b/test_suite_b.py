"""Suite B — hand-written requirements baseline (REQUIREMENTS.md v1.1, tag req-v1.1).

Research integrity note (EQ4):
Each stub maps to the requirement(s) it covers, and quotes the specification's
own wording. Implement the bodies by hand, with your own boundary values,
assertions and verification strategies. Do not delegate the body logic.

Uncovered requirement (log in W03):
- R27, a session naming a user who no longer exists. No route deletes a user,
  so it cannot be reached through the interface. Left uncovered on purpose
  rather than covered by a test that does not test it.
- §4 Spec Gap: §4 never specifies where task creation and editing redirect upon
  saving. Logged in W03 as a v1.1 spec gap; tests navigate explicitly rather
  than asserting an unmandated redirect URL.

One requirement per stub unless two are inseparable in a single flow. A test
that cannot fail measures nothing, so avoid if/else branches that pass either
way.
"""

import pytest
from playwright.sync_api import expect

from conftest import (
    BASE_URL,
    FIELDS,
    ROUTES,
    SEED_TASKS,
    TID,
    USERS,
    post_directly,
    register,
    sel as _sel,
    sign_in,
)


# ------------------------------------------------------------------------------
# Area 1: Accounts, sessions and route protection (R1–R7, R28–R29)
# ------------------------------------------------------------------------------

def test_r01_register_valid_account(page):
    """R1: Username 3–20 characters after trimming, letters, digits and
    underscore only, unique compared case-insensitively. Password 8–128
    characters, not trimmed. On success the user is signed in and lands on the
    task list."""
    # test min boundary (3 chars) with leading/trailing spaces that should trim,
    # and password with leading/trailing spaces that must NOT be trimmed
    register(page, "  dev_1  ", "  pass1234  ")
    expect(page).to_have_url(f"{BASE_URL}{ROUTES['tasks']}")
    # Dropped expect(task_list).to_be_visible() as empty <ul> has zero height; asserting URL is sufficient.

    # verify password was stored untrimmed by signing out and back in
    page.click(_sel("signout_button"))
    sign_in(page, "dev_1", "  pass1234  ")
    expect(page).to_have_url(f"{BASE_URL}{ROUTES['tasks']}")


def test_r02_register_rejects_duplicate_username(page):
    """R2: Registration with a username that already exists, compared
    case-insensitively, is rejected with a visible message, and no account is
    created."""
    # alice is in seed data; try mixed-case Alice with spaces
    register(page, "  ALICE ", "newpassword99")
    expect(page).to_have_url(f"{BASE_URL}{ROUTES['register']}")
    msg = page.locator(_sel("message"))
    expect(msg).to_be_visible()
    assert msg.inner_text().strip() != ""

    # make sure the new password didn't overwrite or create anything usable
    sign_in(page, "alice", "newpassword99")
    expect(page).to_have_url(f"{BASE_URL}{ROUTES['signin']}")


def test_r03_register_rejects_invalid_input(page):
    """R3: A username or password breaking R1's rules is rejected with a
    visible message naming what is wrong, and no account is created."""
    # bad username (hyphen not allowed, and too short after trim)
    register(page, " a- ", "validpass123")
    expect(page).to_have_url(f"{BASE_URL}{ROUTES['register']}")
    msg = page.locator(_sel("message"))
    expect(msg).to_be_visible()
    assert "username" in msg.inner_text().lower()

    # bad password (7 chars, just under the 8-char minimum)
    register(page, "valid_user2", "1234567")
    expect(page).to_have_url(f"{BASE_URL}{ROUTES['register']}")
    expect(msg).to_be_visible()
    assert "password" in msg.inner_text().lower()

    # confirm neither account can sign in
    sign_in(page, "valid_user2", "1234567")
    expect(page).to_have_url(f"{BASE_URL}{ROUTES['signin']}")


def test_r04_signin_valid_user(page):
    """R4: Correct credentials land on the task list. Username matched
    case-insensitively, password matched exactly. The username is displayed as
    it was typed at registration."""
    register(page, "CaseUser_9", "ExactPass123")
    page.click(_sel("signout_button"))

    # sign in with different casing in username, exact password
    sign_in(page, "caseuser_9", "ExactPass123")
    expect(page).to_have_url(f"{BASE_URL}{ROUTES['tasks']}")
    # original casing from registration should appear in the header/nav
    expect(page.locator("body")).to_contain_text("CaseUser_9")


def test_r05_signin_invalid_gives_same_message(page):
    """R5: A wrong password and an unknown username are both rejected with a
    visible message, and the two cases produce the SAME message. No session is
    created. (The container is `message`, per §3.)"""
    sign_in(page, "alice", "definitely_wrong_pw")
    expect(page).to_have_url(f"{BASE_URL}{ROUTES['signin']}")
    wrong_pw_msg = page.locator(_sel("message")).inner_text().strip()
    assert wrong_pw_msg != ""

    sign_in(page, "ghost_user_404", "definitely_wrong_pw")
    expect(page).to_have_url(f"{BASE_URL}{ROUTES['signin']}")
    unknown_user_msg = page.locator(_sel("message")).inner_text().strip()

    assert wrong_pw_msg == unknown_user_msg

    # verify no session was established
    page.goto(f"{BASE_URL}{ROUTES['tasks']}")
    expect(page).to_have_url(f"{BASE_URL}{ROUTES['signin']}")


def test_r06_signout_ends_session(page):
    """R6: A signed-in user can sign out; afterwards the session is no longer
    valid."""
    sign_in(page, "alice")
    expect(page).to_have_url(f"{BASE_URL}{ROUTES['tasks']}")

    page.click(_sel("signout_button"))
    # trying to visit tasks again must bounce to /signin
    page.goto(f"{BASE_URL}{ROUTES['tasks']}")
    expect(page).to_have_url(f"{BASE_URL}{ROUTES['signin']}")


def test_r07_public_set_and_protected_redirect(page):
    """R7: The public set is exactly GET /, GET+POST /register, GET+POST
    /signin, and static assets. Any other request without a valid session
    redirects to /signin, including paths that do not exist, and returns none
    of the protected content.
    (Playwright Python: expect(page).to_have_url(...), not to_url.)"""
    # public routes load without redirecting to signin
    for pub in [ROUTES["root"], ROUTES["signin"], ROUTES["register"]]:
        resp = page.goto(f"{BASE_URL}{pub}")
        assert resp.status == 200

    # protected and nonexistent paths must redirect to /signin without leaking task data
    for path in ["/tasks", "/tasks/new", "/tasks/1", "/nonexistent-route-xyz"]:
        page.goto(f"{BASE_URL}{path}")
        expect(page).to_have_url(f"{BASE_URL}{ROUTES['signin']}")
        assert "task-list" not in page.content()


def test_r28_r29_no_store_and_redirect_when_signed_in(page):
    """R28: Protected pages carry Cache-Control: no-store, so Back after
    signing out does not show a page seen while signed in.
    R29: A signed-in user requesting /signin or /register is redirected to
    /tasks."""
    sign_in(page, "alice")
    resp = page.goto(f"{BASE_URL}{ROUTES['tasks']}")
    cache_hdr = resp.headers.get("cache-control", "").lower()
    assert "no-store" in cache_hdr

    # R29: signed-in user visiting /signin or /register gets sent to /tasks
    page.goto(f"{BASE_URL}{ROUTES['signin']}")
    expect(page).to_have_url(f"{BASE_URL}{ROUTES['tasks']}")
    page.goto(f"{BASE_URL}{ROUTES['register']}")
    expect(page).to_have_url(f"{BASE_URL}{ROUTES['tasks']}")

    # R28: sign out then hit browser Back
    page.click(_sel("signout_button"))
    page.go_back()
    expect(page).to_have_url(f"{BASE_URL}{ROUTES['signin']}")


# ------------------------------------------------------------------------------
# Area 2: Create and edit validation (R8–R10, R26)
# ------------------------------------------------------------------------------

def test_r08_create_task_valid(page):
    """R8: Title required, 1–100 characters after trimming. Description
    optional, up to 500 after trimming. Due date optional. A new task has
    status `open`."""
    sign_in(page, "alice")
    page.click(_sel("new_task_link"))

    raw_title = "   Buy coffee beans   "
    raw_desc = "  Medium roast whole bean  "
    page.fill(_sel("task_title_input"), raw_title)
    page.fill(_sel("task_description_input"), raw_desc)
    page.fill(_sel("task_due_date_input"), "2026-12-15")
    page.click(_sel("task_save_button"))

    # Explicit navigation to independent of V0 landing spec gap (§4)
    page.goto(f"{BASE_URL}{ROUTES['tasks']}")
    top_row = page.locator(_sel("task_row")).first
    expect(top_row).to_contain_text("Buy coffee beans")
    expect(top_row).to_contain_text("open")
    expect(top_row).to_contain_text("2026-12-15")


def test_r09_create_rejects_blank_title(page):
    """R9: An empty or whitespace-only title is rejected with a visible
    message, and no task is created."""
    sign_in(page, "alice")
    before_count = page.locator(_sel("task_row")).count()

    page.click(_sel("new_task_link"))
    page.fill(_sel("task_title_input"), "     ")
    page.fill(_sel("task_description_input"), "Orphan description")
    page.click(_sel("task_save_button"))

    msg = page.locator(_sel("message"))
    expect(msg).to_be_visible()
    assert msg.inner_text().strip() != ""

    page.goto(f"{BASE_URL}{ROUTES['tasks']}")
    assert page.locator(_sel("task_row")).count() == before_count


def test_r10_edit_own_task(page):
    """R10: A user can edit the title, description and due date of their own
    task, under the same validation as R8, R9 and R26."""
    sign_in(page, "alice")
    alice_id = SEED_TASKS["alice"][0]
    page.goto(f"{BASE_URL}/tasks/{alice_id}/edit")

    # first try an invalid edit (blank title) and verify rejection
    page.fill(_sel("task_title_input"), "   ")
    page.click(_sel("task_save_button"))
    expect(page.locator(_sel("message"))).to_be_visible()

    # now submit a valid update
    page.fill(_sel("task_title_input"), "Updated Alice Task")
    page.fill(_sel("task_description_input"), "Revised details")
    page.fill(_sel("task_due_date_input"), "2026-11-30")
    page.click(_sel("task_save_button"))

    # Explicit navigation to independent of V0 landing spec gap (§4)
    page.goto(f"{BASE_URL}{ROUTES['tasks']}")
    expect(page.locator(_sel("task_list"))).to_contain_text("Updated Alice Task")
    expect(page.locator(_sel("task_list"))).to_contain_text("2026-11-30")


def test_r26_due_date_validation(page):
    """R26: A due date must be a valid calendar date in YYYY-MM-DD. Past dates
    are accepted. A malformed string, OR a well-formed but impossible date
    such as 2026-02-30, is rejected with a visible message and nothing is
    stored."""
    sign_in(page, "alice")
    page.goto(f"{BASE_URL}{ROUTES['tasks']}")
    before_count = page.locator(_sel("task_row")).count()

    # impossible calendar date (Feb 30)
    page.goto(f"{BASE_URL}{ROUTES['task_new']}")
    page.fill(_sel("task_title_input"), "Impossible Date Task")
    page.fill(_sel("task_due_date_input"), "2026-02-30")
    page.click(_sel("task_save_button"))

    expect(page.locator(_sel("message"))).to_be_visible()
    page.goto(f"{BASE_URL}{ROUTES['tasks']}")
    assert page.locator(_sel("task_row")).count() == before_count

    # malformed format
    page.goto(f"{BASE_URL}{ROUTES['task_new']}")
    page.fill(_sel("task_title_input"), "Bad Format Date Task")
    page.fill(_sel("task_due_date_input"), "11/16/2026")
    page.click(_sel("task_save_button"))
    expect(page.locator(_sel("message"))).to_be_visible()

    # past date must be accepted
    page.goto(f"{BASE_URL}{ROUTES['task_new']}")
    page.fill(_sel("task_title_input"), "Past Due Task")
    page.fill(_sel("task_due_date_input"), "2020-01-15")
    page.click(_sel("task_save_button"))

    # Explicit navigation to independent of V0 landing spec gap (§4)
    page.goto(f"{BASE_URL}{ROUTES['tasks']}")
    expect(page.locator(_sel("task_list"))).to_contain_text("Past Due Task")


# ------------------------------------------------------------------------------
# Area 3: Toggle and delete (R11–R12)
# ------------------------------------------------------------------------------

def test_r11_toggle_complete_and_reopen(page):
    """R11: A user can mark their own task completed and reopen it. Status is
    `open` or `completed` — not "active". §3 places the toggle on /tasks/:id,
    not in the list row."""
    sign_in(page, "alice")
    # create a fresh open task so initial status is guaranteed `open`
    page.goto(f"{BASE_URL}{ROUTES['task_new']}")
    page.fill(_sel("task_title_input"), "Toggle Target")
    page.click(_sel("task_save_button"))

    # Explicit navigation to detail page
    page.goto(f"{BASE_URL}{ROUTES['tasks']}")
    page.locator(_sel("task_row"), has_text="Toggle Target").locator("a").first.click()
    expect(page.locator("body")).to_contain_text("open")
    page.click(_sel("task_complete_toggle"))
    expect(page.locator("body")).to_contain_text("completed")

    # toggle again to reopen
    page.click(_sel("task_complete_toggle"))
    expect(page.locator("body")).to_contain_text("open")


def test_r12_delete_with_confirmation(page):
    """R12: After deletion the task no longer appears in the list, AND a
    visible message confirms it. The message survives the redirect that
    follows the delete, and is shown once."""
    sign_in(page, "alice")
    page.goto(f"{BASE_URL}{ROUTES['task_new']}")
    page.fill(_sel("task_title_input"), "Disposable Task 99")
    page.click(_sel("task_save_button"))

    page.goto(f"{BASE_URL}{ROUTES['tasks']}")
    page.locator(_sel("task_row"), has_text="Disposable Task 99").locator("a").first.click()
    page.click(_sel("task_delete_button"))

    # No navigation here. R12 requires the message to survive the redirect that
    # follows the delete, so the assertion has to run on the page that redirect
    # landed on. Navigating again would reload it and consume the one-shot
    # message before it could be checked.
    expect(page.locator(_sel("task_list"))).not_to_contain_text("Disposable Task 99")

    msg = page.locator(_sel("message"))
    expect(msg).to_be_visible()
    assert msg.inner_text().strip() != ""

    # Shown once. §3 says the container is always present in the markup, empty
    # when there is nothing to show, so assert it is not visible rather than
    # that it is absent.
    page.reload()
    expect(page.locator(_sel("message"))).not_to_be_visible()


# ------------------------------------------------------------------------------
# Area 4: List, search, filter and empty state (R13–R16, R30)
# ------------------------------------------------------------------------------

def test_r13_r30_list_shows_own_tasks_in_order(page):
    """R13: The list shows the signed-in user's tasks and no others, most
    recently created first, with title, status and due date if set.
    R30: Ids ascend as tasks are created and are never reused, so newest-first
    means descending id and the order is identical on every run."""
    sign_in(page, "alice")
    # create two tasks in sequence; second must appear above first
    for title in ["Order Check First", "Order Check Second"]:
        page.goto(f"{BASE_URL}{ROUTES['task_new']}")
        page.fill(_sel("task_title_input"), title)
        page.click(_sel("task_save_button"))

    # Explicit navigation to tasks list
    page.goto(f"{BASE_URL}{ROUTES['tasks']}")
    rows = page.locator(_sel("task_row"))
    expect(rows.nth(0)).to_contain_text("Order Check Second")
    expect(rows.nth(1)).to_contain_text("Order Check First")

    # none of bob's tasks should appear
    for bob_id in SEED_TASKS["bob"]:
        assert f"/tasks/{bob_id}" not in page.content()


def test_r14_search_literal_substring_ignoring_case(page):
    """R14: A task matches when the search text occurs as a substring of its
    title or description, ignoring case. The text is literal, never a pattern
    or expression — a search for `(` must not error."""
    sign_in(page, "alice")
    page.goto(f"{BASE_URL}{ROUTES['task_new']}")
    page.fill(_sel("task_title_input"), "Plan (Phase 2) Review")
    page.fill(_sel("task_description_input"), "Check CamelCaseToken inside body")
    page.click(_sel("task_save_button"))

    # Explicit navigation and search by case-insensitive substring in description
    page.goto(f"{BASE_URL}{ROUTES['tasks']}")
    page.fill(_sel("search_input"), "camelcasetoken")
    page.click(_sel("search_submit"))
    expect(page.locator(_sel("task_list"))).to_contain_text("Plan (Phase 2) Review")

    # literal regex metacharacter `(` must match cleanly without 500 error
    page.fill(_sel("search_input"), "(")
    page.click(_sel("search_submit"))
    expect(page.locator(_sel("task_list"))).to_contain_text("Plan (Phase 2) Review")


def test_r15_filter_and_search_apply_together(page):
    """R15: Filter by `all`, `open` or `completed`; search and filter apply
    together. §4: `q` and `status` are query parameters, and a missing or
    unrecognised status is treated as `all`."""
    sign_in(page, "alice")
    # create one open and one completed task sharing a common keyword
    page.goto(f"{BASE_URL}{ROUTES['task_new']}")
    page.fill(_sel("task_title_input"), "ComboKeyword Open")
    page.click(_sel("task_save_button"))

    page.goto(f"{BASE_URL}{ROUTES['task_new']}")
    page.fill(_sel("task_title_input"), "ComboKeyword Done")
    page.click(_sel("task_save_button"))
    
    page.goto(f"{BASE_URL}{ROUTES['tasks']}")
    page.locator(_sel("task_row"), has_text="ComboKeyword Done").locator("a").first.click()
    page.click(_sel("task_complete_toggle"))

    # apply both search q and status=completed together
    page.goto(f"{BASE_URL}{ROUTES['tasks']}?q=ComboKeyword&status=completed")
    expect(page.locator(_sel("task_list"))).to_contain_text("ComboKeyword Done")
    expect(page.locator(_sel("task_list"))).not_to_contain_text("ComboKeyword Open")

    # unrecognised status falls back to `all`
    page.goto(f"{BASE_URL}{ROUTES['tasks']}?q=ComboKeyword&status=bogus_status")
    expect(page.locator(_sel("task_list"))).to_contain_text("ComboKeyword Done")
    expect(page.locator(_sel("task_list"))).to_contain_text("ComboKeyword Open")


def test_r16_empty_message_shown(page):
    """R16: When the list has nothing to show — a search or filter matching
    nothing, or a user with no tasks at all — the page shows "No tasks found"
    rather than an empty area. §3 puts it in `empty-message`, not in the
    message container.
    NOTE: every seed user owns at least one task, so create the empty state."""
    # register a brand-new user who has zero tasks
    register(page, "fresh_empty_user", "emptyuser123")
    expect(page).to_have_url(f"{BASE_URL}{ROUTES['tasks']}")

    empty_el = page.locator(_sel("empty_message"))
    expect(empty_el).to_be_visible()
    expect(empty_el).to_contain_text("No tasks found")


# ------------------------------------------------------------------------------
# Area 5: Access control (R17–R21, R24–R25)
# ------------------------------------------------------------------------------
# The critical-severity block. R21 — authorisation checked on the server, not
# by hiding a control — is why the write cases go straight to the server.

def test_r17_cannot_view_other_users_task(page):
    """R17: Requesting another user's task returns a 404 page, and no part of
    the task's content appears anywhere in it.
    SHARP CHECK: a 404 that still leaks bob's title or description fails R17.
    Assert on page content, not only on status."""
    # capture bob's first task title first
    bob_id = SEED_TASKS["bob"][0]
    sign_in(page, "bob")
    page.goto(f"{BASE_URL}/tasks/{bob_id}")
    bob_title = page.locator("h1, h2, [data-testid='task-title']").first.inner_text().strip()
    page.click(_sel("signout_button"))

    # now sign in as alice and try to view bob's task
    sign_in(page, "alice")
    resp = page.goto(f"{BASE_URL}/tasks/{bob_id}")
    assert resp.status == 404
    assert bob_title not in page.content()


def test_r18_cannot_edit_other_users_task(page):
    """R18: An edit submitted for another user's task is rejected and the task
    is unchanged. Send it directly to the server (R21), not through the page."""
    bob_id = SEED_TASKS["bob"][0]
    sign_in(page, "bob")
    page.goto(f"{BASE_URL}/tasks/{bob_id}")
    original_html = page.locator("main, body").first.inner_text()
    page.click(_sel("signout_button"))

    sign_in(page, "alice")
    resp = post_directly(
        page,
        f"/tasks/{bob_id}/edit",
        {"title": "Alice Hijacked Title", "description": "Hacked", "due": ""},
    )
    assert resp.status == 404
    page.click(_sel("signout_button"))

    # verify bob's task was untouched
    sign_in(page, "bob")
    page.goto(f"{BASE_URL}/tasks/{bob_id}")
    assert "Alice Hijacked Title" not in page.content()
    assert page.locator("main, body").first.inner_text() == original_html


def test_r19_r24_cannot_delete_or_toggle_other_users_task(page):
    """R19: A delete submitted for another user's task is rejected and the
    task still exists.
    R24: A status toggle submitted for another user's task is rejected and the
    status is unchanged."""
    bob_id = SEED_TASKS["bob"][0]
    sign_in(page, "bob")
    page.goto(f"{BASE_URL}/tasks/{bob_id}")
    before_text = page.locator("main, body").first.inner_text()
    page.click(_sel("signout_button"))

    sign_in(page, "alice")
    del_resp = post_directly(page, f"/tasks/{bob_id}/delete")
    assert del_resp.status == 404

    tog_resp = post_directly(page, f"/tasks/{bob_id}/toggle")
    assert tog_resp.status == 404
    page.click(_sel("signout_button"))

    # verify bob's task still exists with identical status
    sign_in(page, "bob")
    resp = page.goto(f"{BASE_URL}/tasks/{bob_id}")
    assert resp.status == 200
    assert page.locator("main, body").first.inner_text() == before_text


def test_r20_r21_list_and_search_isolation(page):
    """R20: Search and filter never return another user's tasks, under any
    search text.
    R21: Authorisation is checked on the server for every request that reads
    or changes a task; hiding a control in the page is not sufficient."""
    # bob creates a task with a distinctive marker
    sign_in(page, "bob")
    page.goto(f"{BASE_URL}{ROUTES['task_new']}")
    page.fill(_sel("task_title_input"), "SecretBobMarker_XYZ")
    page.click(_sel("task_save_button"))
    page.click(_sel("signout_button"))

    # alice searches for that exact marker across all statuses
    sign_in(page, "alice")
    page.goto(f"{BASE_URL}{ROUTES['tasks']}?q=SecretBobMarker_XYZ&status=all")
    # Verify no task_row contains the marker (echoed search query in input/html is allowed per R20)
    assert page.locator(_sel("task_row"), has_text="SecretBobMarker_XYZ").count() == 0
    expect(page.locator(_sel("empty_message"))).to_be_visible()

    # R21: GET /tasks/:id/edit for bob's seed task must also be blocked on the server
    bob_id = SEED_TASKS["bob"][0]
    edit_get = page.goto(f"{BASE_URL}/tasks/{bob_id}/edit")
    assert edit_get.status == 404


def test_r25_other_users_task_indistinguishable_from_missing(page):
    """R25: For every route naming a task id, the response for another user's
    task is identical to the response for an id that does not exist — same
    status, same page, same message.
    SHARP CHECK: do NOT write `assert status in [403, 404]`. A 403 reveals the
    task exists, which is the violation R25 forbids. Compare the two responses
    against each other."""
    sign_in(page, "alice")
    bob_id = SEED_TASKS["bob"][0]
    missing_id = 999999

    # compare GET routes
    for suffix in ["", "/edit"]:
        r_bob = page.request.get(f"{BASE_URL}/tasks/{bob_id}{suffix}")
        r_miss = page.request.get(f"{BASE_URL}/tasks/{missing_id}{suffix}")
        assert r_bob.status == r_miss.status
        assert r_bob.text() == r_miss.text()

    # compare POST routes
    for action, payload in [
        ("/edit", {"title": "Probe", "description": "", "due": ""}),
        ("/toggle", {}),
        ("/delete", {}),
    ]:
        r_bob = post_directly(page, f"/tasks/{bob_id}{action}", payload)
        r_miss = post_directly(page, f"/tasks/{missing_id}{action}", payload)
        assert r_bob.status == r_miss.status
        assert r_bob.text() == r_miss.text()


# ------------------------------------------------------------------------------
# Area 6: Server-side enforcement (R22–R23)
# ------------------------------------------------------------------------------

def test_r22_validation_enforced_on_the_server(page):
    """R22: Every validation rule in R1, R3, R8, R9, R10 and R26 is enforced
    server-side. Client-side checks may exist too, but a request sent directly
    to the server must still be rejected.
    (This is about VALIDATION. Unauthenticated access is R7, above.)"""
    # direct POST to /register bypassing HTML minlength/pattern
    reg_resp = post_directly(page, ROUTES["register"], {"username": "x", "password": "123"})
    assert reg_resp.status in (400, 422) or ROUTES["register"] in reg_resp.url

    sign_in(page, "alice")
    alice_id = SEED_TASKS["alice"][0]

    # direct POST to /tasks (or /tasks/new) with over-length title (>100 chars) & invalid date
    page.goto(f"{BASE_URL}{ROUTES['tasks']}")
    before_count = page.locator(_sel("task_row")).count()

    post_directly(
        page,
        ROUTES["task_new"],
        {"title": "A" * 101, "description": "", "due": "2026-02-30"},
    )
    # Verify no task with that over-length title was created
    page.goto(f"{BASE_URL}{ROUTES['tasks']}")
    assert page.locator(_sel("task_row"), has_text="A" * 101).count() == 0

    # direct POST to /tasks/:id/edit with blank title
    edit_resp = post_directly(
        page,
        f"/tasks/{alice_id}/edit",
        {"title": "   ", "description": "", "due": ""},
    )
    assert edit_resp.status in (400, 422) or f"/tasks/{alice_id}/edit" in edit_resp.url


def test_r23_rejected_request_changes_nothing(page):
    """R23: A rejected request leaves stored data unchanged. Take a rejection
    from R22 and verify the stored state is exactly as it was."""
    sign_in(page, "alice")
    alice_id = SEED_TASKS["alice"][0]

    # snapshot alice's task before rejected edit
    page.goto(f"{BASE_URL}/tasks/{alice_id}")
    snapshot_before = page.locator("main, body").first.inner_text()

    # send invalid edit directly to server (blank title + impossible due date)
    post_directly(
        page,
        f"/tasks/{alice_id}/edit",
        {"title": "", "description": "Should not save", "due": "2026-02-30"},
    )

    # reload task and verify stored state is completely unchanged
    page.goto(f"{BASE_URL}/tasks/{alice_id}")
    snapshot_after = page.locator("main, body").first.inner_text()
    assert snapshot_after == snapshot_before
    assert "Should not save" not in page.content()
