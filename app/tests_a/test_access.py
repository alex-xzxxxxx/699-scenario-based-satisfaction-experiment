"""Access control: R17–R19, R21, R24, R25."""

import pytest
from playwright.sync_api import Page, expect

from conftest import post, read_db, read_db_bytes, sign_in_ok

BOB_TASK = {
    "id": 5,
    "title": "Reply to supplier",
    "description": "Confirm the delivery window",
    "due": "2026-11-25",
}


@pytest.fixture
def alice(page: Page) -> Page:
    sign_in_ok(page, "alice")
    return page


def bob_task_from_db() -> dict:
    return next(t for t in read_db()["tasks"] if t["id"] == 5)


def assert_no_task_content(text: str) -> None:
    for value in (BOB_TASK["title"], BOB_TASK["description"], BOB_TASK["due"], "supplier", "delivery"):
        assert value not in text


# --- R17 ----------------------------------------------------------------------

@pytest.mark.parametrize("path", ["/tasks/5", "/tasks/5/edit", "/tasks/8"])
def test_r17_other_users_task_url_gives_404_without_content(alice: Page, path):
    response = alice.goto(path)
    assert response.status == 404
    html = alice.content()
    assert_no_task_content(html)
    assert "Collect parcel" not in html
    expect(alice.get_by_test_id("task-delete-button")).to_have_count(0)
    expect(alice.get_by_test_id("task-complete-toggle")).to_have_count(0)


# --- R18 / R19 / R24 ----------------------------------------------------------

def test_r18_edit_of_other_users_task_rejected(alice: Page):
    before = bob_task_from_db()
    response = post(alice, "/tasks/5/edit", {"title": "Hijacked", "description": "", "due": ""})
    assert response.status == 404
    assert bob_task_from_db() == before


def test_r18_invalid_edit_of_other_users_task_reveals_nothing(alice: Page):
    response = post(alice, "/tasks/5/edit", {"title": ""})
    assert response.status == 404
    assert "Title is required" not in response.text()


def test_r19_delete_of_other_users_task_rejected(alice: Page, new_context):
    response = post(alice, "/tasks/5/delete")
    assert response.status == 404
    assert any(t["id"] == 5 for t in read_db()["tasks"])
    bob = new_context().new_page()
    sign_in_ok(bob, "bob")
    expect(bob.locator('[data-testid="task-row"][data-task-id="5"]')).to_contain_text("Reply to supplier")


def test_r24_toggle_of_other_users_task_rejected(alice: Page):
    response = post(alice, "/tasks/5/toggle")
    assert response.status == 404
    assert bob_task_from_db()["status"] == "open"
    response = post(alice, "/tasks/6/toggle")
    assert response.status == 404
    assert next(t for t in read_db()["tasks"] if t["id"] == 6)["status"] == "completed"


def test_r18_r19_r24_rejected_requests_change_nothing(alice: Page):
    before = read_db_bytes()
    for task_id in (5, 6, 7, 8):
        post(alice, f"/tasks/{task_id}/edit", {"title": "x"})
        post(alice, f"/tasks/{task_id}/toggle")
        post(alice, f"/tasks/{task_id}/delete")
    assert read_db_bytes() == before


# --- R25 ----------------------------------------------------------------------

@pytest.mark.parametrize(
    "method,suffix,form",
    [
        ("GET", "", None),
        ("GET", "/edit", None),
        ("POST", "/edit", {"title": "x"}),
        ("POST", "/edit", {"title": ""}),
        ("POST", "/toggle", {}),
        ("POST", "/delete", {}),
    ],
)
@pytest.mark.parametrize("missing_id", ["999", "9", "0", "abc", "-1"])
def test_r25_other_users_id_indistinguishable_from_missing_id(alice: Page, method, suffix, form, missing_id):
    def fetch(task_id):
        url = f"/tasks/{task_id}{suffix}"
        if method == "GET":
            return alice.request.get(url, max_redirects=0)
        return alice.request.post(url, form=form, max_redirects=0)

    other = fetch(5)
    missing = fetch(missing_id)
    assert other.status == missing.status == 404
    assert other.text() == missing.text()


def test_r25_ids_cannot_be_probed(alice: Page):
    """Walk sequential ids: only alice's own ids respond differently."""
    found = []
    for task_id in range(1, 15):
        if alice.request.get(f"/tasks/{task_id}").status == 200:
            found.append(task_id)
    assert found == [1, 2, 3, 4]


# --- R21 ----------------------------------------------------------------------

def test_r21_hidden_controls_not_relied_on(alice: Page):
    """Even with the form markup rewritten in the page, the server refuses."""
    alice.goto("/tasks/1")
    alice.evaluate("""() => {
        document.querySelector('form[action="/tasks/1/delete"]').action = '/tasks/7/delete';
    }""")
    alice.get_by_test_id("task-delete-button").click()
    alice.wait_for_load_state()
    assert any(t["id"] == 7 for t in read_db()["tasks"])
    assert any(t["id"] == 1 for t in read_db()["tasks"])
