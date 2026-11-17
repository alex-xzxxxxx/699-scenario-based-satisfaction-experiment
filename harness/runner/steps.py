"""T13 — reusable step helpers.

A scenario is data: a list of steps naming helpers in this registry. Adding a
scenario in Week 5 should mean writing YAML, not Python.

**No helper asserts anything.** Every one performs an action and records what
it saw. Whether the scenario was satisfied is decided later, by the LLM judge
and by the human reference, from the evidence alone. A runner that decided for
itself would leave EQ2 nothing to measure, and would quietly become a third
test suite rather than an execution harness.

That is also why a step that fails to act — a missing element, a timeout — is
recorded and the run continues where it can. A scenario that could not be
carried out is evidence about the version, not a broken experiment.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent.parent / "app"

# §3 of the requirements fixes these. A scenario names the key; only this map
# knows the selector, so a markup change is one edit here.
TESTID = {
    "nav_signin": "nav-signin",
    "nav_register": "nav-register",
    "nav_signout": "nav-signout",
    "username": "username-input",
    "password": "password-input",
    "submit": "submit-button",
    "new_task_link": "new-task-link",
    "title": "task-title-input",
    "description": "task-description-input",
    "due": "task-due-input",
    "create": "task-create-button",
    "save": "task-save-button",
    "delete": "task-delete-button",
    "toggle": "task-complete-toggle",
    "search": "search-input",
    "search_submit": "search-submit",
    "status_filter": "status-filter",
    "task_list": "task-list",
    "task_row": "task-row",
    "empty": "empty-message",
    "message": "message",
}

# §5 seed accounts.
USERS = {
    "alice": "alicepass123",
    "bob": "bobpass123",
    "carol": "carolpass123",
}

_REGISTRY: dict[str, callable] = {}


def step(name):
    def wrap(fn):
        _REGISTRY[name] = fn
        return fn

    return wrap


def get(name):
    if name not in _REGISTRY:
        raise KeyError(
            f"unknown step '{name}'. Known steps: {', '.join(sorted(_REGISTRY))}"
        )
    return _REGISTRY[name]


def known() -> list[str]:
    return sorted(_REGISTRY)


def _sel(key: str) -> str:
    if key not in TESTID:
        raise KeyError(f"unknown test id key '{key}'")
    return f'[data-testid="{TESTID[key]}"]'


def _text(ctx, key: str) -> str:
    loc = ctx.page.locator(_sel(key))
    return loc.inner_text().strip() if loc.count() else ""


# --- navigation and state ---------------------------------------------------


@step("reset")
def reset(ctx, **_):
    """Restore seed data. Works against a running server because §1 requires a
    disk read per request."""
    subprocess.run(
        [ctx.npm, "run", "--silent", "reset"],
        cwd=APP_DIR, check=True, capture_output=True, timeout=60,
    )
    return "seed data restored"


@step("goto")
def goto(ctx, path: str, **_):
    resp = ctx.page.goto(f"{ctx.base_url}{path}")
    ctx.last_status = resp.status if resp else None
    return f"requested {path}"


@step("back")
def back(ctx, **_):
    ctx.page.go_back()
    return "pressed the browser Back button"


@step("reload")
def reload(ctx, **_):
    ctx.page.reload()
    return "reloaded the page"


# --- accounts ---------------------------------------------------------------


@step("register")
def register(ctx, username: str, password: str, **_):
    ctx.page.goto(f"{ctx.base_url}/register")
    ctx.page.fill(_sel("username"), username)
    ctx.page.fill(_sel("password"), password)
    ctx.page.click(_sel("submit"))
    return f"registered {username!r}"


@step("sign_in")
def sign_in(ctx, user: str = "", username: str = "", password: str = "", **_):
    name = username or user
    pw = password if password else USERS.get(name.lower(), "")
    ctx.page.goto(f"{ctx.base_url}/signin")
    ctx.page.fill(_sel("username"), name)
    ctx.page.fill(_sel("password"), pw)
    ctx.page.click(_sel("submit"))
    return f"signed in as {name!r}"


@step("sign_out")
def sign_out(ctx, **_):
    ctx.page.click(_sel("nav_signout"))
    return "signed out"


# --- forms ------------------------------------------------------------------


@step("fill")
def fill(ctx, field: str, value: str = "", **_):
    ctx.page.fill(_sel(field), value)
    shown = value if len(value) <= 60 else f"{value[:57]}… ({len(value)} chars)"
    return f"filled {field} with {shown!r}"


@step("select")
def select(ctx, field: str, value: str, **_):
    ctx.page.select_option(_sel(field), value)
    return f"set {field} to {value!r}"


@step("click")
def click(ctx, target: str, **_):
    ctx.page.click(_sel(target))
    return f"clicked {target}"


@step("open_task")
def open_task(ctx, title: str, **_):
    """Open a task's page from the list by its title."""
    ctx.page.locator(_sel("task_row"), has_text=title).locator("a").first.click()
    return f"opened the task titled {title!r} from the list"


# --- straight to the server -------------------------------------------------


@step("post")
def post(ctx, path: str, fields: dict | None = None, **_):
    """Submit directly, bypassing the page. R21 and R22 require the server to
    enforce authorisation and validation on its own."""
    resp = ctx.page.request.post(f"{ctx.base_url}{path}", form=fields or {})
    ctx.last_status = resp.status
    ctx.last_body = resp.text()
    return f"posted to {path} without using the page"


@step("request")
def request(ctx, path: str, **_):
    """Fetch a path and record the status, without navigating."""
    resp = ctx.page.request.get(f"{ctx.base_url}{path}")
    ctx.last_status = resp.status
    ctx.last_body = resp.text()
    return f"requested {path} directly"


@step("compare_responses")
def compare_responses(ctx, path_a: str, path_b: str, method: str = "get",
                      fields: dict | None = None, **_):
    """Fetch two paths and record whether the responses differ.

    R25 is about indistinguishability, which is a property of a pair of
    responses rather than of one. The helper records the comparison; it does
    not rule on it.
    """
    call = ctx.page.request.get if method == "get" else ctx.page.request.post
    kw = {} if method == "get" else {"form": fields or {}}
    a = call(f"{ctx.base_url}{path_a}", **kw)
    b = call(f"{ctx.base_url}{path_b}", **kw)
    same_status = a.status == b.status
    same_body = a.text() == b.text()
    ctx.last_status = a.status
    return (
        f"compared {method.upper()} {path_a} against {path_b} — "
        f"status {a.status} vs {b.status} ({'same' if same_status else 'DIFFERENT'}), "
        f"body {'identical' if same_body else 'DIFFERENT'}"
    )


# --- observation ------------------------------------------------------------


@step("capture")
def capture(ctx, label: str = "state", **_):
    """Record what is on screen. The judge reads this; the runner does not."""
    rows = ctx.page.locator(_sel("task_row"))
    parts = [f"url {ctx.page.url}"]
    if rows.count():
        titles = [rows.nth(i).inner_text().strip().replace("\n", " · ")
                  for i in range(min(rows.count(), 12))]
        parts.append(f"{rows.count()} task row(s): " + " | ".join(titles))
    else:
        parts.append("no task rows")
    for key, name in (("message", "message"), ("empty", "empty message")):
        txt = _text(ctx, key)
        if txt:
            parts.append(f"{name}: {txt!r}")
    return f"{label}: " + "; ".join(parts)


@step("note")
def note(ctx, text: str, **_):
    """Record something the scenario needs stated but no action produces."""
    return text
