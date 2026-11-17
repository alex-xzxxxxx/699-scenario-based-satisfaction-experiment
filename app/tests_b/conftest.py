"""Suite B fixtures — the hand-written baseline.

Everything here is plumbing taken verbatim from REQUIREMENTS.md v1.1 (tag
req-v1.1): the port, the seed credentials, the test ids, the routes. None of it
is a judgment about what to test, so none of it is part of what EQ4 measures.

The test bodies are. They are written by hand, from the requirements, before
any scenario exists and before any defect is seeded.
"""

import shutil
import subprocess
from pathlib import Path

import pytest
from playwright.sync_api import Browser, Page, sync_playwright

# §1 — the application serves on port 3000.
BASE_URL = "http://localhost:3000"

# The app directory, holding package.json. conftest.py lives in app/tests_b/.
APP_DIR = Path(__file__).resolve().parent.parent

# §5 — seed users. Passwords are these exact strings.
USERS = {
    "alice": "alicepass123",
    "bob": "bobpass123",
    "carol": "carolpass123",
}

# §3 — mandated test ids, as full selectors. sel(key) returns one.
# `save` resolves to either button: §3 names task-create-button on the create
# form and task-save-button on the edit form, and a test that submits "the
# task form" should not care which page it is on.
TID = {
    "nav_signin": '[data-testid="nav-signin"]',
    "nav_register": '[data-testid="nav-register"]',
    "nav_signout": '[data-testid="nav-signout"]',
    "signout_button": '[data-testid="nav-signout"]',
    "username": '[data-testid="username-input"]',
    "password": '[data-testid="password-input"]',
    "submit": '[data-testid="submit-button"]',
    "new_task_link": '[data-testid="new-task-link"]',
    "task_title_input": '[data-testid="task-title-input"]',
    "task_description_input": '[data-testid="task-description-input"]',
    "task_due_date_input": '[data-testid="task-due-input"]',
    "task_create_button": '[data-testid="task-create-button"]',
    "task_save_button": '[data-testid="task-save-button"], [data-testid="task-create-button"]',
    "task_delete_button": '[data-testid="task-delete-button"]',
    "task_complete_toggle": '[data-testid="task-complete-toggle"]',
    "search_input": '[data-testid="search-input"]',
    "search_submit": '[data-testid="search-submit"]',
    "status_filter": '[data-testid="status-filter"]',
    "task_list": '[data-testid="task-list"]',
    "task_row": '[data-testid="task-row"]',
    "empty_message": '[data-testid="empty-message"]',
    "message": '[data-testid="message"]',
}


def sel(key):
    """The CSS selector for a mandated test id."""
    return TID[key]


# Form field names. §3 pins the test ids but the specification never names the
# form fields, so a test that posts straight to the server (R21, R22) has to
# get them from somewhere. Recorded here as a gap in v1.1, not a change to it.
FIELDS = {
    "username": "username",
    "password": "password",
    "title": "title",
    "description": "description",
    "due": "due",
    "search": "q",
    "status": "status",
}


# §4 — every route. There is no JSON API; writes are HTML form POSTs.
ROUTES = {
    "home": "/",
    "root": "/",
    "register": "/register",
    "signin": "/signin",
    "signout": "/signout",          # POST
    "tasks": "/tasks",              # GET, with ?q= and ?status=
    "new": "/tasks/new",
    "task_new": "/tasks/new",
    "task": "/tasks/{id}",
    "edit": "/tasks/{id}/edit",
    "delete": "/tasks/{id}/delete",  # POST
    "toggle": "/tasks/{id}/toggle",  # POST
}

# §5 — seed tasks in creation order. R30 assigns ids in increasing order, so
# these are the ids after a reset. Confirm against V0 before relying on them.
SEED_TASK_DETAIL = [
    (1, "alice", "Draft project outline", "2026-12-01", "open"),
    (2, "alice", "Book flights", "2026-12-05", "open"),
    (3, "alice", "Renew library card", None, "completed"),
    (4, "alice", "Buy printer paper", "2026-11-20", "open"),
    (5, "bob", "Reply to supplier", "2026-11-25", "open"),
    (6, "bob", "Pay invoice 2291", "2026-11-18", "completed"),
    (7, "bob", "Draft budget sheet", None, "open"),
    (8, "carol", "Collect parcel", "2026-11-15", "open"),
]

# Task ids by owner, after a reset. R30 assigns ids in creation order.
SEED_TASKS = {
    "alice": [1, 2, 3, 4],
    "bob": [5, 6, 7],
    "carol": [8],
}

NPM = shutil.which("npm") or "npm"


@pytest.fixture(autouse=True)
def reset_state():
    """§6 — restore seed data before every test.

    This runs against the already-running server. It works without a restart
    because §1 requires the server to read data/db.json from disk on every
    request rather than caching it. If tests start contaminating each other,
    that requirement is what V0 has broken — which is a finding, not a bug in
    this fixture.
    """
    subprocess.run(
        [NPM, "run", "reset"],
        cwd=APP_DIR,
        check=True,
        capture_output=True,
        text=True,
    )
    yield


@pytest.fixture(scope="session")
def _browser():
    """A browser for the session. Provided here rather than by the
    pytest-playwright plugin, so the suite runs wherever Playwright itself is
    installed."""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        yield browser
        browser.close()


@pytest.fixture
def page(_browser: Browser) -> Page:
    """§6 — a fresh browser context per test, so no session survives from one
    test to the next."""
    context = _browser.new_context(base_url=BASE_URL)
    pg = context.new_page()
    yield pg
    context.close()


def sign_in(page, username, password=None):
    """Sign in through the form at /signin. Defaults to the seed password."""
    page.goto(f"{BASE_URL}{ROUTES['signin']}")
    page.fill(TID["username"], username)
    page.fill(TID["password"], password if password is not None else USERS[username])
    page.click(TID["submit"])


def register(page, username, password):
    """Register through the form at /register."""
    page.goto(f"{BASE_URL}{ROUTES['register']}")
    page.fill(TID["username"], username)
    page.fill(TID["password"], password)
    page.click(TID["submit"])


def post_directly(page, path, data=None):
    """Send a form POST straight to the server, skipping the page.

    R22 requires validation on the server, and R21 requires authorisation on
    the server, so several tests have to bypass the interface. Session cookies
    from the current page carry over.
    """
    return page.request.post(f"{BASE_URL}{path}", form=data or {})
