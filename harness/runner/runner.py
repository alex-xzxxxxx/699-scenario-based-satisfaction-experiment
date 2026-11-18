"""T13 — the scenario runner.

Executes one scenario against one running version and hands the result to the
evidence collector. It performs actions and records what it saw. It never
decides whether the scenario was satisfied; that is the LLM judge's job and the
human reference's job, from the evidence alone.

    python -m harness.runner.runner --scenario ACC-01 --version V0
    python -m harness.runner.runner --all --version V0
    python -m harness.runner.runner --check          # validate, run nothing

The version name is written to data/run_manifest.jsonl and never into the
evidence bundle, because about 25 of these runs are judged blind.
"""

from __future__ import annotations

import argparse
import shutil
import sys
import traceback
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from harness.evidence import Bundle, Step, new_run_id  # noqa: E402
from harness.runner import scenario as scn  # noqa: E402
from harness.runner import steps as step_helpers  # noqa: E402

DEFAULT_URL = "http://localhost:3000"

# Response headers copied into the evidence. An allowlist, deliberately, not
# every header: D-009 keeps a bundle small enough that 540 judge calls fit the
# free tier, and a blanket copy would put server, timing and caching detail in
# front of the judge that says nothing about whether the scenario was
# satisfied. The list is not empty because R28 cannot be judged from behaviour
# alone — a page that is absent after Back and a page that was never stored
# look the same from the outside, and only the header separates them (D-014).
RECORDED_HEADERS = ("cache-control",)


def _record_response(network: list[dict], base_url: str, response) -> None:
    """Note one response. Like every other part of the runner, this records
    and does not judge: it copies the header through, it does not check it."""
    entry = {"status": response.status,
             "url": response.url.replace(base_url, "")}
    try:
        headers = response.headers
    except Exception:  # noqa: BLE001 - the response may already be gone
        headers = {}
    picked = {k: headers[k] for k in RECORDED_HEADERS if k in headers}
    if picked:
        entry["headers"] = picked
    network.append(entry)


def _playwright():
    """Imported on demand, so --check validates the library on a machine with
    only pyyaml installed."""
    try:
        from playwright.sync_api import Error, sync_playwright
    except ModuleNotFoundError:
        raise SystemExit(
            "Playwright is not installed. Running scenarios needs it:\n"
            "    pip install -r requirements.txt\n"
            "    playwright install chromium\n"
            "Validating the library (--check) needs only pyyaml."
        ) from None
    return Error, sync_playwright


@dataclass
class Context:
    """Passed to every step helper. Carries the page and the last raw result."""

    page: object
    base_url: str
    npm: str = field(default_factory=lambda: shutil.which("npm") or "npm")
    last_status: int | None = None
    last_body: str = ""


def _visible_change(before: str, after: str) -> str:
    """The text that appeared, so the trace stays compact (D-009)."""
    if after == before:
        return ""
    old = set(before.split("\n"))
    added = [ln.strip() for ln in after.split("\n")
             if ln not in old and ln.strip()]
    joined = " · ".join(added)
    return joined[:600] + ("…" if len(joined) > 600 else "")


def _body_text(page) -> str:
    try:
        return page.locator("body").inner_text()
    except Exception:  # noqa: BLE001 - playwright's Error, imported on demand
        return ""


def run_one(sc: scn.Scenario, page, base_url: str, version: str,
            console: list[str], network: list[dict], shots: bool) -> Bundle:
    bundle = Bundle(
        run_id=new_run_id(),
        scenario_id=sc.id,
        category=sc.category,
        severity=sc.severity,
        preconditions=sc.preconditions,
        user_action=sc.user_action,
        expected_behaviour=sc.expected_behaviour,
        expected_evidence=sc.expected_evidence,
        requirements=sc.requirements,
    )
    ctx = Context(page=page, base_url=base_url)

    for n, spec in enumerate(sc.steps, 1):
        name = spec["do"]
        args = {k: v for k, v in spec.items() if k != "do"}
        before = _body_text(page)
        rec = Step(n=n, action=name, detail="")
        try:
            rec.detail = step_helpers.get(name)(ctx, **args) or name
        except Exception as exc:  # noqa: BLE001
            # A step that cannot be carried out is evidence about the version,
            # not a broken experiment. Record it and keep going.
            rec.detail = f"{name}({', '.join(f'{k}={v!r}' for k, v in args.items())})"
            rec.error = f"{type(exc).__name__}: {exc}".split("\nCall log")[0][:300]
        after = _body_text(page)
        rec.url = page.url.replace(base_url, "") or "/"
        rec.changed_text = _visible_change(before, after)
        rec.http_status = ctx.last_status
        ctx.last_status = None
        if shots:
            try:
                path = bundle.screenshot_path(n, name)
                page.screenshot(path=str(path))
                rec.screenshot = path.name
            except Exception:  # noqa: BLE001
                pass
        bundle.add(rec)

    bundle.final_state = step_helpers.get("capture")(ctx, label="final")
    return bundle


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenario", help="one scenario id, e.g. ACC-01")
    ap.add_argument("--all", action="store_true", help="run the whole library")
    ap.add_argument("--check", action="store_true",
                    help="validate the library and exit without running")
    ap.add_argument("--version", default="", help="V0, V1, V2 or V3")
    ap.add_argument("--base-url", default=DEFAULT_URL)
    ap.add_argument("--no-screenshots", action="store_true")
    a = ap.parse_args()

    try:
        library = scn.load_all()
    except scn.ScenarioError as exc:
        print(f"library invalid: {exc}")
        return 2

    if a.check:
        print(f"{len(library)} scenario(s) valid.")
        for s in library:
            print(f"  {s.id:<8} {s.category:<12} {s.severity:<9} "
                  f"{len(s.steps):>2} steps  {s.requirements}")
        print(f"\nstep helpers available: {', '.join(step_helpers.known())}")
        return 0

    if not a.version:
        print("--version is required: it is recorded in the manifest so that "
              "runs can be traced back after judging.")
        return 2

    chosen = library if a.all else [s for s in library if s.id == a.scenario]
    if not chosen:
        print(f"no scenario with id {a.scenario!r}. "
              f"Known: {', '.join(s.id for s in library)}")
        return 2

    _, sync_playwright = _playwright()
    written = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for sc in chosen:
            console: list[str] = []
            network: list[dict] = []
            context = browser.new_context(base_url=a.base_url)
            page = context.new_page()
            page.on("console", lambda m: console.append(f"[{m.type}] {m.text}"))
            page.on("response",
                    lambda r: _record_response(network, a.base_url, r))
            try:
                bundle = run_one(sc, page, a.base_url, a.version,
                                 console, network, not a.no_screenshots)
            except Exception:  # noqa: BLE001
                bundle = Bundle(
                    run_id=new_run_id(), scenario_id=sc.id, category=sc.category,
                    severity=sc.severity, preconditions=sc.preconditions,
                    user_action=sc.user_action,
                    expected_behaviour=sc.expected_behaviour,
                    expected_evidence=sc.expected_evidence,
                    requirements=sc.requirements,
                )
                bundle.runner_error = traceback.format_exc(limit=2)[:600]
            finally:
                context.close()
            out = bundle.write(a.version, console, network)
            written.append((sc.id, bundle.run_id, len(bundle.steps)))
            print(f"{sc.id:<8} -> run {bundle.run_id}  "
                  f"{len(bundle.steps)} steps  {out.relative_to(out.parent.parent)}")
        browser.close()

    print(f"\n{len(written)} run(s) written. The version is in the manifest, "
          "not in the evidence.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
