"""Section 3 page and message conventions, section 4 routes, section 5 seed."""

import re

import pytest
from playwright.sync_api import Page, expect

from conftest import message, read_db, register, row_ids, sign_in_ok

SIGNED_OUT_PAGES = ["/", "/signin", "/register"]
SIGNED_IN_PAGES = ["/tasks", "/tasks?q=zzz", "/tasks/new", "/tasks/1", "/tasks/1/edit", "/tasks/999", "/nope"]


@pytest.mark.parametrize("path", SIGNED_OUT_PAGES)
def test_exactly_one_message_container_signed_out(page: Page, path):
    page.goto(path)
    expect(page.get_by_test_id("message")).to_have_count(1)
    expect(page.get_by_test_id("nav-signin")).to_be_visible()
    expect(page.get_by_test_id("nav-register")).to_be_visible()
    expect(page.get_by_test_id("nav-signout")).to_have_count(0)


@pytest.mark.parametrize("path", SIGNED_IN_PAGES)
def test_exactly_one_message_container_signed_in(page: Page, path):
    sign_in_ok(page, "alice")
    page.goto(path)
    expect(page.get_by_test_id("message")).to_have_count(1)
    expect(page.get_by_test_id("nav-signout")).to_be_visible()
    expect(page.get_by_test_id("nav-signin")).to_have_count(0)


def test_message_container_empty_when_no_message(page: Page):
    page.goto("/signin")
    expect(message(page)).to_have_text("")
    sign_in_ok(page, "alice")
    expect(message(page)).to_have_text("")


def test_form_test_ids_present(page: Page):
    page.goto("/signin")
    for tid in ("username-input", "password-input", "submit-button"):
        expect(page.get_by_test_id(tid)).to_have_count(1)
    page.goto("/register")
    for tid in ("username-input", "password-input", "submit-button"):
        expect(page.get_by_test_id(tid)).to_have_count(1)

    sign_in_ok(page, "alice")
    for tid in ("search-input", "search-submit", "status-filter", "task-list"):
        expect(page.get_by_test_id(tid)).to_have_count(1)
    page.goto("/tasks/new")
    for tid in ("task-title-input", "task-description-input", "task-due-input", "task-create-button"):
        expect(page.get_by_test_id(tid)).to_have_count(1)
    page.goto("/tasks/1/edit")
    for tid in ("task-title-input", "task-description-input", "task-due-input", "task-save-button"):
        expect(page.get_by_test_id(tid)).to_have_count(1)
    page.goto("/tasks/1")
    for tid in ("task-delete-button", "task-complete-toggle"):
        expect(page.get_by_test_id(tid)).to_have_count(1)


def test_home_signed_out_links(page: Page):
    page.goto("/")
    page.get_by_test_id("nav-register").click()
    expect(page).to_have_url(re.compile(r"/register$"))
    page.get_by_test_id("nav-signin").click()
    expect(page).to_have_url(re.compile(r"/signin$"))


def test_signed_in_unknown_path_is_404(page: Page):
    sign_in_ok(page, "alice")
    response = page.goto("/definitely/not/here")
    assert response.status == 404


def test_search_form_is_get_with_q_and_status(page: Page):
    sign_in_ok(page, "alice")
    page.get_by_test_id("search-input").fill("book")
    page.get_by_test_id("status-filter").select_option("open")
    page.get_by_test_id("search-submit").click()
    expect(page).to_have_url(re.compile(r"/tasks\?q=book&status=open$"))


def test_seed_state(page: Page):
    db = read_db()
    assert [u["username"] for u in db["users"]] == ["alice", "bob", "carol"]
    assert [t["id"] for t in db["tasks"]] == list(range(1, 9))
    for user, pw, ids in [("alice", "alicepass123", [4, 3, 2, 1]),
                          ("bob", "bobpass123", [7, 6, 5]),
                          ("carol", "carolpass123", [8])]:
        ctx_page = page
        ctx_page.context.clear_cookies()
        sign_in_ok(ctx_page, user, pw)
        assert row_ids(ctx_page) == ids


def test_registered_user_message_and_sign_out_message(page: Page):
    register(page, "msgcheck", "msgcheck123")
    expect(message(page)).not_to_have_text("")
    page.get_by_test_id("nav-signout").click()
    expect(message(page)).to_contain_text("signed out")
