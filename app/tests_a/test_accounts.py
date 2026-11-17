"""Accounts and sessions: R1–R7, R27–R29."""

import re

import pytest
from playwright.sync_api import Page, expect

from conftest import (
    message, post, read_db, read_db_bytes, register, reset_data, sign_in, sign_in_ok,
)

TASKS_URL = re.compile(r"/tasks$")
SIGNIN_URL = re.compile(r"/signin$")


# --- R1 -----------------------------------------------------------------------

def test_r1_register_signs_in_and_lands_on_task_list(page: Page):
    register(page, "dave_01", "davepass123")
    expect(page).to_have_url(TASKS_URL)
    expect(page.get_by_test_id("nav-signout")).to_be_visible()
    expect(page.get_by_test_id("nav-username")).to_have_text("dave_01")


def test_r1_username_is_trimmed_before_validation(page: Page):
    register(page, "   erin   ", "erinpass123")
    expect(page).to_have_url(TASKS_URL)
    expect(page.get_by_test_id("nav-username")).to_have_text("erin")


@pytest.mark.parametrize("username", ["abc", "a" * 20, "A_1"])
def test_r1_username_length_boundaries_accepted(page: Page, username):
    register(page, username, "goodpass123")
    expect(page).to_have_url(TASKS_URL)


@pytest.mark.parametrize("password", ["x" * 8, "y" * 128])
def test_r1_password_length_boundaries_accepted(page: Page, password):
    register(page, "frank", password)
    expect(page).to_have_url(TASKS_URL)


def test_r1_password_is_not_trimmed(page: Page, new_context):
    register(page, "gina", "  spaced pass  ")
    expect(page).to_have_url(TASKS_URL)
    other = new_context().new_page()
    sign_in(other, "gina", "spaced pass")
    expect(message(other)).to_contain_text("Incorrect username or password")
    sign_in_ok(other, "gina", "  spaced pass  ")


# --- R2 -----------------------------------------------------------------------

@pytest.mark.parametrize("username", ["alice", "ALICE", "  Alice  "])
def test_r2_duplicate_username_rejected_case_insensitively(page: Page, username):
    users_before = len(read_db()["users"])
    register(page, username, "differentpass1")
    expect(message(page)).to_contain_text("already taken")
    expect(page.get_by_test_id("nav-signout")).to_have_count(0)
    assert len(read_db()["users"]) == users_before
    # The original account is untouched.
    sign_in_ok(page, "alice")


# --- R3 -----------------------------------------------------------------------

@pytest.mark.parametrize(
    "username,password,expected",
    [
        ("ab", "goodpass123", "Username must be between 3 and 20 characters"),
        ("a" * 21, "goodpass123", "Username must be between 3 and 20 characters"),
        ("bad-name", "goodpass123", "only letters, digits and underscores"),
        ("bad name", "goodpass123", "only letters, digits and underscores"),
        ("héllo", "goodpass123", "only letters, digits and underscores"),
        ("   ", "goodpass123", "Username is required"),
        ("", "goodpass123", "Username is required"),
        ("validname", "short77", "Password must be between 8 and 128 characters"),
        ("validname", "z" * 129, "Password must be between 8 and 128 characters"),
        ("validname", "", "Password is required"),
    ],
)
def test_r3_invalid_registration_rejected_with_reason(page: Page, username, password, expected):
    users_before = len(read_db()["users"])
    register(page, username, password)
    expect(message(page)).to_contain_text(expected)
    expect(page.get_by_test_id("nav-signout")).to_have_count(0)
    assert len(read_db()["users"]) == users_before


# --- R4 -----------------------------------------------------------------------

def test_r4_sign_in_lands_on_task_list(page: Page):
    sign_in_ok(page, "alice")
    expect(page.get_by_test_id("task-list")).to_be_visible()


def test_r4_username_matched_case_insensitively_displayed_as_registered(page: Page, new_context):
    register(page, "MixedCase", "mixedpass123")
    other = new_context().new_page()
    sign_in_ok(other, "mIXEDcASE", "mixedpass123")
    expect(other.get_by_test_id("nav-username")).to_have_text("MixedCase")


def test_r4_seed_user_case_insensitive(page: Page):
    sign_in_ok(page, "BOB", "bobpass123")
    expect(page.get_by_test_id("nav-username")).to_have_text("bob")


def test_r4_password_matched_exactly(page: Page):
    sign_in(page, "alice", "ALICEPASS123")
    expect(message(page)).to_contain_text("Incorrect username or password")


# --- R5 -----------------------------------------------------------------------

def test_r5_wrong_password_and_unknown_user_give_same_message(page: Page):
    sign_in(page, "alice", "wrongpassword")
    wrong_pw = message(page).inner_text()
    expect(page).to_have_url(SIGNIN_URL)

    sign_in(page, "nobody_here", "wrongpassword")
    unknown = message(page).inner_text()

    assert wrong_pw.strip() != ""
    assert wrong_pw == unknown
    # No session was created.
    page.goto("/tasks")
    expect(page).to_have_url(SIGNIN_URL)


# --- R6 -----------------------------------------------------------------------

def test_r6_sign_out_invalidates_session(page: Page, new_context):
    sign_in_ok(page, "alice")
    stolen = page.context.cookies()
    page.get_by_test_id("nav-signout").click()
    expect(page).to_have_url(SIGNIN_URL)
    page.goto("/tasks")
    expect(page).to_have_url(SIGNIN_URL)

    # Replaying the cookie from before sign-out gets nowhere either.
    ctx = new_context()
    ctx.add_cookies(stolen)
    replay = ctx.new_page()
    replay.goto("/tasks")
    expect(replay).to_have_url(SIGNIN_URL)
    expect(replay.get_by_text("Draft project outline")).to_have_count(0)


# --- R7 -----------------------------------------------------------------------

@pytest.mark.parametrize(
    "path",
    ["/tasks", "/tasks/1", "/tasks/new", "/tasks/1/edit", "/does-not-exist", "/tasks/999", "/signout"],
)
def test_r7_protected_get_redirects_to_signin(page: Page, path):
    response = page.request.get(path, max_redirects=0)
    assert response.status in (301, 302, 303, 307, 308)
    assert response.headers["location"].endswith("/signin")
    assert "Draft project outline" not in response.text()
    page.goto(path)
    expect(page).to_have_url(SIGNIN_URL)


@pytest.mark.parametrize(
    "path,form",
    [
        ("/tasks/new", {"title": "Sneaky"}),
        ("/tasks/1/edit", {"title": "Hacked"}),
        ("/tasks/1/toggle", {}),
        ("/tasks/1/delete", {}),
        ("/signout", {}),
        ("/", {}),
    ],
)
def test_r7_protected_post_redirects_and_changes_nothing(page: Page, path, form):
    before = read_db()
    response = post(page, path, form)
    assert response.status in (301, 302, 303, 307, 308)
    assert response.headers["location"].endswith("/signin")
    assert read_db()["tasks"] == before["tasks"]


@pytest.mark.parametrize("path", ["/", "/register", "/signin"])
def test_r7_public_pages_are_reachable_signed_out(page: Page, path):
    response = page.goto(path)
    assert response.status == 200
    expect(page).to_have_url(re.compile(re.escape(path) + "$"))


def test_r7_stylesheet_loads_on_signin_page(page: Page):
    with page.expect_response(lambda r: r.url.endswith("/style.css")) as info:
        page.goto("/signin")
    response = info.value
    assert response.status == 200
    assert "text/css" in response.headers["content-type"]


# --- R27 ----------------------------------------------------------------------

def test_r27_session_for_deleted_user_is_unauthenticated(page: Page):
    register(page, "ghost_user", "ghostpass123")
    expect(page).to_have_url(TASKS_URL)
    reset_data()  # the account no longer exists in the stored data
    page.goto("/tasks")
    expect(page).to_have_url(SIGNIN_URL)
    expect(page.get_by_test_id("nav-signout")).to_have_count(0)


def test_r27_deleted_user_session_not_inherited_by_new_account(page: Page, new_context):
    register(page, "first_one", "firstpass123")
    reset_data()
    other = new_context().new_page()
    register(other, "second_one", "secondpass12")  # may get the same numeric id
    page.goto("/tasks")
    expect(page).to_have_url(SIGNIN_URL)


# --- R28 ----------------------------------------------------------------------

def test_r28_protected_pages_are_not_cached(page: Page):
    sign_in_ok(page, "alice")
    for path in ["/tasks", "/tasks/1", "/tasks/new", "/tasks/1/edit"]:
        response = page.goto(path)
        assert "no-store" in response.headers.get("cache-control", ""), path


def test_r28_back_button_after_signout_shows_no_protected_page(page: Page):
    sign_in_ok(page, "alice")
    page.goto("/tasks/1")
    expect(page.get_by_test_id("task-title")).to_have_text("Draft project outline")
    page.get_by_test_id("nav-signout").click()
    expect(page).to_have_url(SIGNIN_URL)
    page.go_back()
    page.wait_for_load_state()
    expect(page).to_have_url(SIGNIN_URL)
    expect(page.get_by_text("Draft project outline")).to_have_count(0)


# --- R29 ----------------------------------------------------------------------

@pytest.mark.parametrize("path", ["/signin", "/register", "/"])
def test_r29_signed_in_user_redirected_to_tasks(page: Page, path):
    sign_in_ok(page, "alice")
    page.goto(path)
    expect(page).to_have_url(TASKS_URL)


# --- Session cookie (section 1) ------------------------------------------------

def test_session_cookie_is_http_only_and_lax(page: Page):
    sign_in_ok(page, "alice")
    cookies = page.context.cookies()
    assert cookies, "expected a session cookie"
    for cookie in cookies:
        assert cookie["httpOnly"] is True
        assert cookie["sameSite"] == "Lax"
    assert page.evaluate("document.cookie") == ""


def test_passwords_are_not_stored_in_plain_text(page: Page):
    register(page, "hashcheck", "plaintextcheck99")
    raw = read_db_bytes().decode()
    for pw in ["plaintextcheck99", "alicepass123", "bobpass123", "carolpass123"]:
        assert pw not in raw
