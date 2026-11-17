"""Listing, search and filter: R13–R16, R20, R30."""

import re

import pytest
from playwright.sync_api import Page, expect

from conftest import (
    ALICE_TASKS, BOB_TASKS, CAROL_TASKS, create_task, register, row_ids, search, sign_in_ok,
)


@pytest.fixture
def alice(page: Page) -> Page:
    sign_in_ok(page, "alice")
    return page


# --- R13 / R30 ---------------------------------------------------------------

def test_r13_list_shows_own_tasks_newest_first(alice: Page):
    assert row_ids(alice) == [4, 3, 2, 1]
    titles = alice.get_by_test_id("task-row-title").all_inner_texts()
    assert titles == [ALICE_TASKS[i] for i in (4, 3, 2, 1)]


def test_r13_each_row_shows_title_status_and_due(alice: Page):
    row4 = alice.locator('[data-testid="task-row"][data-task-id="4"]')
    expect(row4).to_contain_text("Buy printer paper")
    expect(row4).to_contain_text("open")
    expect(row4).to_contain_text("2026-11-20")
    row3 = alice.locator('[data-testid="task-row"][data-task-id="3"]')
    expect(row3).to_contain_text("completed")
    expect(row3.get_by_test_id("task-row-due")).to_have_count(0)


@pytest.mark.parametrize(
    "user,password,expected",
    [("bob", "bobpass123", [7, 6, 5]), ("carol", "carolpass123", [8])],
)
def test_r13_other_users_see_only_their_tasks(page: Page, user, password, expected):
    sign_in_ok(page, user, password)
    assert row_ids(page) == expected


def test_r13_row_links_to_task_page(alice: Page):
    alice.locator('[data-testid="task-row"][data-task-id="2"] a').click()
    expect(alice).to_have_url(re.compile(r"/tasks/2$"))
    expect(alice.get_by_test_id("task-title")).to_have_text("Book flights")


def test_r30_ids_increase_and_are_never_reused(alice: Page):
    create_task(alice, "Newest")
    expect(alice).to_have_url(re.compile(r"/tasks/9$"))
    alice.get_by_test_id("task-delete-button").click()
    create_task(alice, "After delete")
    expect(alice).to_have_url(re.compile(r"/tasks/10$"))
    alice.goto("/tasks")
    assert row_ids(alice) == [10, 4, 3, 2, 1]


def test_r30_order_stable_across_users_creating(page: Page, new_context):
    sign_in_ok(page, "alice")
    bob = new_context().new_page()
    sign_in_ok(bob, "bob")
    create_task(page, "A1")   # id 9
    create_task(bob, "B1")    # id 10
    create_task(page, "A2")   # id 11
    page.goto("/tasks")
    assert row_ids(page) == [11, 9, 4, 3, 2, 1]


# --- R14 ----------------------------------------------------------------------

@pytest.mark.parametrize(
    "q,expected",
    [
        ("book", [2]),            # title
        ("BOOK", [2]),            # case-insensitive
        ("AIRLINES", [2]),        # description only
        ("draft", [1]),           # alice's only; bob's "Draft budget sheet" excluded
        ("r", [4, 3, 2, 1]),
        ("two", [4, 2]),          # "two reams", "two airlines"
        ("A4, two", [4]),
        ("outline", [1]),
    ],
)
def test_r14_search_title_and_description(alice: Page, q, expected):
    search(alice, q)
    assert row_ids(alice) == expected
    expect(alice.get_by_test_id("search-input")).to_have_value(q)


@pytest.mark.parametrize("q", [".*", "^Book", "B..k", "[a-z]+", "(", "\\", "%", "_", "*"])
def test_r14_search_text_is_literal(alice: Page, q):
    search(alice, q)
    expect(alice.get_by_test_id("task-list")).to_have_count(1)
    assert row_ids(alice) == []
    expect(alice.get_by_test_id("empty-message")).to_have_text("No tasks found")


def test_r14_literal_special_characters_match(alice: Page):
    create_task(alice, "Cost (approx.) 50% [maybe]*")
    search(alice, "(approx.) 50% [maybe]*")
    assert row_ids(alice) == [9]


def test_r14_search_via_query_string(alice: Page):
    alice.goto("/tasks?q=PRINTER")
    assert row_ids(alice) == [4]


# --- R15 ----------------------------------------------------------------------

@pytest.mark.parametrize(
    "status,expected",
    [("all", [4, 3, 2, 1]), ("open", [4, 2, 1]), ("completed", [3])],
)
def test_r15_filter_by_status(alice: Page, status, expected):
    search(alice, "", status)
    assert row_ids(alice) == expected
    expect(alice.get_by_test_id("status-filter")).to_have_value(status)


def test_r15_search_and_filter_combine(alice: Page):
    search(alice, "r", "completed")
    assert row_ids(alice) == [3]
    search(alice, "book", "completed")
    assert row_ids(alice) == []
    search(alice, "book", "open")
    assert row_ids(alice) == [2]


@pytest.mark.parametrize("query", ["status=bogus", "status=", "status=OPEN", "status=all"])
def test_r15_unrecognised_status_means_all(alice: Page, query):
    alice.goto(f"/tasks?{query}")
    assert row_ids(alice) == [4, 3, 2, 1]


# --- R16 ----------------------------------------------------------------------

def test_r16_no_match_shows_empty_message(alice: Page):
    search(alice, "zzz-nothing")
    expect(alice.get_by_test_id("empty-message")).to_have_text("No tasks found")
    expect(alice.get_by_test_id("message")).not_to_contain_text("No tasks found")


def test_r16_filter_with_no_match_shows_empty_message(page: Page):
    sign_in_ok(page, "carol")
    search(page, "", "completed")
    expect(page.get_by_test_id("empty-message")).to_have_text("No tasks found")


def test_r16_user_with_no_tasks_sees_empty_message(page: Page):
    register(page, "emptyuser", "emptypass123")
    expect(page.get_by_test_id("empty-message")).to_have_text("No tasks found")
    assert row_ids(page) == []


def test_r16_empty_after_deleting_last_task(page: Page):
    sign_in_ok(page, "carol")
    page.goto("/tasks/8")
    page.get_by_test_id("task-delete-button").click()
    expect(page.get_by_test_id("empty-message")).to_have_text("No tasks found")


def test_r16_empty_message_absent_when_tasks_shown(alice: Page):
    expect(alice.get_by_test_id("empty-message")).to_have_count(0)


# --- R20 ----------------------------------------------------------------------

OTHER_TITLES = list(BOB_TASKS.values()) + list(CAROL_TASKS.values())


@pytest.mark.parametrize(
    "q", ["supplier", "invoice", "parcel", "budget", "delivery window", "2291", "", " ", "a", "e"],
)
@pytest.mark.parametrize("status", ["all", "open", "completed"])
def test_r20_search_never_returns_other_users_tasks(alice: Page, q, status):
    alice.goto(f"/tasks?q={q}&status={status}")
    assert set(row_ids(alice)) <= set(ALICE_TASKS)
    text = alice.get_by_test_id("task-list").inner_text()
    for title in OTHER_TITLES:
        assert title not in text
