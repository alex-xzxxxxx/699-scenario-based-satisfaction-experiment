"""Shared fixtures for the TaskTracker browser test suite.

The application must already be running on http://localhost:3000 (`npm start`).
Before every test the data is restored with `npm run reset`, run as a
subprocess against that running server, and every test gets a fresh browser
context, so no session survives from one test to the next.
"""

import json
import os
import re
import subprocess
from pathlib import Path

import pytest
from playwright.sync_api import Browser, Page, expect, sync_playwright

BASE_URL = os.environ.get("TASKTRACKER_URL", "http://localhost:3000")
APP_DIR = Path(__file__).resolve().parent.parent
DB_PATH = APP_DIR / "data" / "db.json"

SEED_PASSWORDS = {"alice": "alicepass123", "bob": "bobpass123", "carol": "carolpass123"}
ALICE_TASKS = {  # id -> title, from section 5
    1: "Draft project outline",
    2: "Book flights",
    3: "Renew library card",
    4: "Buy printer paper",
}
BOB_TASKS = {5: "Reply to supplier", 6: "Pay invoice 2291", 7: "Draft budget sheet"}
CAROL_TASKS = {8: "Collect parcel"}


def reset_data() -> None:
    subprocess.run(
        ["npm", "run", "--silent", "reset"],
        cwd=APP_DIR,
        check=True,
        capture_output=True,
        timeout=60,
    )


def read_db_bytes() -> bytes:
    return DB_PATH.read_bytes()


def read_db() -> dict:
    return json.loads(read_db_bytes())


@pytest.fixture(autouse=True)
def seed():
    reset_data()
    yield


@pytest.fixture(scope="session")
def _browser():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        yield browser
        browser.close()


@pytest.fixture
def new_context(_browser: Browser):
    """Factory for extra, isolated browser contexts within one test."""
    contexts = []

    def make():
        ctx = _browser.new_context(base_url=BASE_URL)
        contexts.append(ctx)
        return ctx

    yield make
    for ctx in contexts:
        ctx.close()


@pytest.fixture
def page(new_context) -> Page:
    return new_context().new_page()


# --- helpers ----------------------------------------------------------------


def message(page: Page):
    return page.get_by_test_id("message")


def sign_in(page: Page, username: str, password: str | None = None) -> None:
    page.goto("/signin")
    page.get_by_test_id("username-input").fill(username)
    page.get_by_test_id("password-input").fill(
        password if password is not None else SEED_PASSWORDS[username.lower()]
    )
    page.get_by_test_id("submit-button").click()


def sign_in_ok(page: Page, username: str, password: str | None = None) -> None:
    sign_in(page, username, password)
    expect(page).to_have_url(re.compile(r"/tasks$"))


def register(page: Page, username: str, password: str) -> None:
    page.goto("/register")
    page.get_by_test_id("username-input").fill(username)
    page.get_by_test_id("password-input").fill(password)
    page.get_by_test_id("submit-button").click()


def create_task(page: Page, title: str, description: str = "", due: str = "") -> None:
    page.goto("/tasks/new")
    page.get_by_test_id("task-title-input").fill(title)
    page.get_by_test_id("task-description-input").fill(description)
    page.get_by_test_id("task-due-input").fill(due)
    page.get_by_test_id("task-create-button").click()


def row_ids(page: Page) -> list[int]:
    rows = page.get_by_test_id("task-row")
    return [int(rows.nth(i).get_attribute("data-task-id")) for i in range(rows.count())]


def search(page: Page, q: str = "", status: str = "all") -> None:
    page.goto("/tasks")
    page.get_by_test_id("search-input").fill(q)
    page.get_by_test_id("status-filter").select_option(status)
    page.get_by_test_id("search-submit").click()
    page.wait_for_load_state()


def post(page: Page, path: str, form: dict | None = None):
    """POST directly to the server with the page's cookies, bypassing the UI."""
    return page.request.post(path, form=form or {}, max_redirects=0)
