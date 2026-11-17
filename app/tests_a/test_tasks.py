"""Tasks: R8–R12, R26, R22, R23."""

import re

import pytest
from playwright.sync_api import Page, expect

from conftest import (
    create_task, message, post, read_db, read_db_bytes, register, row_ids, sign_in_ok,
)

DATE_ERROR = "Due date must be a valid date in the form YYYY-MM-DD"


@pytest.fixture
def alice(page: Page) -> Page:
    sign_in_ok(page, "alice")
    return page


def open_edit(page: Page, task_id: int) -> None:
    page.goto(f"/tasks/{task_id}")
    page.get_by_test_id("task-edit-link").click()
    expect(page).to_have_url(re.compile(rf"/tasks/{task_id}/edit$"))


# --- R8 -----------------------------------------------------------------------

def test_r8_create_task_with_all_fields(alice: Page):
    create_task(alice, "Write report", "Quarterly numbers", "2026-12-24")
    expect(message(alice)).to_contain_text("Task created")
    expect(alice.get_by_test_id("task-title")).to_have_text("Write report")
    expect(alice.get_by_test_id("task-description")).to_have_text("Quarterly numbers")
    expect(alice.get_by_test_id("task-due")).to_have_text("2026-12-24")
    expect(alice.get_by_test_id("task-status")).to_have_text("open")

    alice.goto("/tasks")
    row = alice.get_by_test_id("task-row").first
    expect(row).to_contain_text("Write report")
    expect(row).to_contain_text("open")
    expect(row).to_contain_text("2026-12-24")


def test_r8_create_task_with_title_only(alice: Page):
    create_task(alice, "Just a title")
    expect(alice.get_by_test_id("task-title")).to_have_text("Just a title")
    expect(alice.get_by_test_id("task-status")).to_have_text("open")
    task = read_db()["tasks"][-1]
    assert (task["title"], task["description"], task["due"], task["status"]) == ("Just a title", "", "", "open")


def test_r8_title_and_description_are_trimmed(alice: Page):
    create_task(alice, "   Padded title   ", "   padded description   ")
    expect(alice.get_by_test_id("task-title")).to_have_text("Padded title")
    task = read_db()["tasks"][-1]
    assert task["title"] == "Padded title"
    assert task["description"] == "padded description"


def test_r8_length_boundaries_accepted(alice: Page):
    create_task(alice, "T" * 100, "D" * 500)
    expect(alice.get_by_test_id("task-title")).to_have_text("T" * 100)
    # Trailing spaces do not count towards the limit.
    create_task(alice, "U" * 100 + "     ", "E" * 500 + "   ")
    expect(alice.get_by_test_id("task-title")).to_have_text("U" * 100)


@pytest.mark.parametrize(
    "title,description,expected",
    [
        ("T" * 101, "", "Title must be at most 100 characters"),
        ("Fine", "D" * 501, "Description must be at most 500 characters"),
    ],
)
def test_r8_length_limits_rejected(alice: Page, title, description, expected):
    before = read_db_bytes()
    create_task(alice, title, description)
    expect(message(alice)).to_contain_text(expected)
    assert read_db_bytes() == before


def test_r8_markup_in_title_is_shown_as_text(alice: Page):
    title = '<img src=x onerror="window.__pwned=1">'
    create_task(alice, title)
    expect(alice.get_by_test_id("task-title")).to_have_text(title)
    alice.goto("/tasks")
    expect(alice.get_by_test_id("task-row").first).to_contain_text(title)
    assert alice.evaluate("window.__pwned") is None


# --- R9 -----------------------------------------------------------------------

@pytest.mark.parametrize("title", ["", "     ", "\t  \t"])
def test_r9_empty_title_rejected(alice: Page, title):
    before = read_db_bytes()
    create_task(alice, title, "some description", "2026-12-01")
    expect(message(alice)).to_contain_text("Title is required")
    assert read_db_bytes() == before
    alice.goto("/tasks")
    assert row_ids(alice) == [4, 3, 2, 1]


# --- R26 ----------------------------------------------------------------------

@pytest.mark.parametrize(
    "due",
    ["2026-02-30", "2027-02-29", "2026-13-01", "2026-00-10", "2026-04-31",
     "2026-1-5", "12/01/2026", "2026/12/01", "tomorrow", "2026-12-01T00:00", " 2026-12-01", "0000-01-01"],
)
def test_r26_invalid_due_date_rejected(alice: Page, due):
    before = read_db_bytes()
    create_task(alice, "Dated task", "", due)
    expect(message(alice)).to_contain_text(DATE_ERROR)
    assert read_db_bytes() == before


@pytest.mark.parametrize("due", ["2028-02-29", "2000-02-29", "2001-01-01", "2026-12-31"])
def test_r26_valid_due_dates_accepted_including_past(alice: Page, due):
    create_task(alice, "Dated task", "", due)
    expect(message(alice)).to_contain_text("Task created")
    expect(alice.get_by_test_id("task-due")).to_have_text(due)


# --- R10 ----------------------------------------------------------------------

def test_r10_edit_own_task(alice: Page):
    open_edit(alice, 2)
    expect(alice.get_by_test_id("task-title-input")).to_have_value("Book flights")
    alice.get_by_test_id("task-title-input").fill("Book train tickets")
    alice.get_by_test_id("task-description-input").fill("Cheaper than flying")
    alice.get_by_test_id("task-due-input").fill("2026-12-10")
    alice.get_by_test_id("task-save-button").click()
    expect(alice).to_have_url(re.compile(r"/tasks/2$"))
    expect(message(alice)).to_contain_text("Task updated")
    expect(alice.get_by_test_id("task-title")).to_have_text("Book train tickets")
    expect(alice.get_by_test_id("task-description")).to_have_text("Cheaper than flying")
    expect(alice.get_by_test_id("task-due")).to_have_text("2026-12-10")


def test_r10_edit_can_clear_optional_fields(alice: Page):
    open_edit(alice, 1)
    alice.get_by_test_id("task-description-input").fill("")
    alice.get_by_test_id("task-due-input").fill("")
    alice.get_by_test_id("task-save-button").click()
    expect(message(alice)).to_contain_text("Task updated")
    task = next(t for t in read_db()["tasks"] if t["id"] == 1)
    assert task["description"] == "" and task["due"] == ""


def test_r10_edit_keeps_status(alice: Page):
    open_edit(alice, 3)  # completed
    alice.get_by_test_id("task-title-input").fill("Renew library card soon")
    alice.get_by_test_id("task-save-button").click()
    expect(alice.get_by_test_id("task-status")).to_have_text("completed")


@pytest.mark.parametrize(
    "field,value,expected",
    [
        ("task-title-input", "   ", "Title is required"),
        ("task-title-input", "x" * 101, "Title must be at most 100 characters"),
        ("task-description-input", "y" * 501, "Description must be at most 500 characters"),
        ("task-due-input", "2026-02-30", DATE_ERROR),
        ("task-due-input", "next week", DATE_ERROR),
    ],
)
def test_r10_edit_validation(alice: Page, field, value, expected):
    before = read_db_bytes()
    open_edit(alice, 1)
    alice.get_by_test_id(field).fill(value)
    alice.get_by_test_id("task-save-button").click()
    expect(message(alice)).to_contain_text(expected)
    assert read_db_bytes() == before
    alice.goto("/tasks/1")
    expect(alice.get_by_test_id("task-title")).to_have_text("Draft project outline")


# --- R11 ----------------------------------------------------------------------

def test_r11_complete_and_reopen(alice: Page):
    alice.goto("/tasks/1")
    expect(alice.get_by_test_id("task-status")).to_have_text("open")
    alice.get_by_test_id("task-complete-toggle").click()
    expect(alice.get_by_test_id("task-status")).to_have_text("completed")
    alice.goto("/tasks")
    expect(alice.locator('[data-testid="task-row"][data-task-id="1"]')).to_contain_text("completed")

    alice.goto("/tasks/1")
    alice.get_by_test_id("task-complete-toggle").click()
    expect(alice.get_by_test_id("task-status")).to_have_text("open")


def test_r11_reopen_seeded_completed_task(alice: Page):
    alice.goto("/tasks/3")
    expect(alice.get_by_test_id("task-status")).to_have_text("completed")
    alice.get_by_test_id("task-complete-toggle").click()
    expect(alice.get_by_test_id("task-status")).to_have_text("open")


# --- R12 ----------------------------------------------------------------------

def test_r12_delete_shows_confirmation_once(alice: Page):
    alice.goto("/tasks/2")
    alice.get_by_test_id("task-delete-button").click()
    expect(alice).to_have_url(re.compile(r"/tasks$"))
    expect(message(alice)).to_contain_text("deleted")
    assert row_ids(alice) == [4, 3, 1]
    expect(alice.get_by_test_id("task-list")).not_to_contain_text("Book flights")

    alice.reload()
    expect(message(alice)).to_have_text("")
    assert row_ids(alice) == [4, 3, 1]

    alice.goto("/tasks/2")
    assert alice.get_by_role("heading").first.inner_text() == "Not found"


def test_r12_list_rows_hold_no_delete_or_toggle_controls(alice: Page):
    alice.goto("/tasks")
    expect(alice.get_by_test_id("task-delete-button")).to_have_count(0)
    expect(alice.get_by_test_id("task-complete-toggle")).to_have_count(0)
    first = alice.get_by_test_id("task-row").first
    expect(first.locator("a")).to_have_attribute("href", "/tasks/4")


# --- R22 / R23: server-side validation of direct requests ---------------------

@pytest.mark.parametrize(
    "form,expected",
    [
        ({"title": ""}, "Title is required"),
        ({"description": "no title field"}, "Title is required"),
        ({"title": "ok", "due": "2026-02-30"}, DATE_ERROR),
        ({"title": "z" * 101}, "Title must be at most 100 characters"),
        ({"title": "ok", "description": "d" * 501}, "Description must be at most 500 characters"),
    ],
)
def test_r22_create_validation_enforced_on_server(alice: Page, form, expected):
    before = read_db_bytes()
    response = post(alice, "/tasks/new", form)
    assert response.status >= 400
    assert expected in response.text()
    assert read_db_bytes() == before


def test_r22_edit_validation_enforced_on_server(alice: Page):
    before = read_db_bytes()
    response = post(alice, "/tasks/1/edit", {"title": " ", "due": "2026-02-30"})
    assert response.status >= 400
    assert "Title is required" in response.text()
    assert read_db_bytes() == before


@pytest.mark.parametrize(
    "form,expected",
    [
        ({"username": "x", "password": "goodpass123"}, "Username must be between 3 and 20"),
        ({"username": "bad!name", "password": "goodpass123"}, "only letters, digits and underscores"),
        ({"username": "fine_name", "password": "short"}, "Password must be between 8 and 128"),
        ({"username": "fine_name"}, "Password is required"),
        ({"username": "Carol", "password": "goodpass123"}, "already taken"),
    ],
)
def test_r22_registration_validation_enforced_on_server(page: Page, form, expected):
    before = read_db_bytes()
    response = post(page, "/register", form)
    assert response.status >= 400
    assert expected in response.text()
    assert read_db_bytes() == before


def test_r23_rejected_requests_leave_data_unchanged(page: Page):
    before = read_db_bytes()
    register(page, "ALICE", "anotherpass1")
    register(page, "no", "anotherpass1")
    sign_in_ok(page, "alice")
    create_task(page, "   ")
    create_task(page, "Valid", "", "2026-02-30")
    post(page, "/tasks/5/edit", {"title": "Hijack"})
    post(page, "/tasks/5/delete")
    post(page, "/tasks/5/toggle")
    assert read_db_bytes() == before


def test_new_user_can_create_and_see_own_task(page: Page):
    register(page, "newbie", "newbiepass1")
    create_task(page, "First task")
    page.goto("/tasks")
    assert len(row_ids(page)) == 1
    expect(page.get_by_test_id("task-row")).to_contain_text("First task")
