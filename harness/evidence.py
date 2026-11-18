"""T14 — evidence collector.

Writes one bundle per scenario run, under an anonymized run id.

Two rules shape this module.

**The bundle must not reveal which version produced it.** About 25 runs are
judged blind by the human reference (T26), and that reference is what EQ2 and
EQ3 are measured against. A version name anywhere in the evidence — in the run
id, a path, a page URL, a log line — would end the blinding. The run id is a
random token; the mapping from run id to scenario and version lives in
`data/run_manifest.jsonl`, outside `evidence/`, and is never shown to a judge.

**The LLM judge and the human see exactly the same bundle** (D-009). If they
saw different material, EQ2 would be comparing two different tasks rather than
two judges. `trace.json` is what both receive; `trace.md` is the same content
rendered for a person to read.

The trace is deliberately compact — actions, the visible text that changed,
messages, final state. Raw page source runs to tens of thousands of tokens,
which neither fits a free judge tier across 540 calls nor can be read by a
person 25 times.
"""

from __future__ import annotations

import json
import re
import secrets
import time
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EVIDENCE_DIR = ROOT / "evidence"
MANIFEST = ROOT / "data" / "run_manifest.jsonl"

# Anything matching these is scrubbed from captured text before it is written.
# Version names are the blinding risk; absolute paths leak the machine.
_VERSION_WORD = re.compile(r"\bV[0-3]\b")
_ABS_PATH = re.compile(r"(/[\w.-]+){2,}/(app|harness|scenarios|evidence)\b[^\s\"']*")


def _scrub(text: str) -> str:
    if not text:
        return text
    text = _VERSION_WORD.sub("[version]", text)
    text = _ABS_PATH.sub("[path]", text)
    return text


def new_run_id() -> str:
    """An opaque run id. Carries no scenario, version, or ordering."""
    return secrets.token_hex(8)


@dataclass
class Step:
    n: int
    action: str
    detail: str
    url: str = ""
    changed_text: str = ""
    message: str = ""
    http_status: int | None = None
    screenshot: str = ""
    error: str = ""

    def to_public(self) -> dict:
        """The step as a judge sees it."""
        out = {"step": self.n, "action": self.action, "detail": _scrub(self.detail)}
        if self.url:
            out["url"] = self.url
        if self.http_status is not None:
            out["http_status"] = self.http_status
        if self.changed_text:
            out["visible_text"] = _scrub(self.changed_text)
        if self.message:
            out["message"] = _scrub(self.message)
        if self.screenshot:
            out["screenshot"] = self.screenshot
        if self.error:
            out["error"] = _scrub(self.error)
        return out


@dataclass
class Bundle:
    """One scenario run's evidence."""

    run_id: str
    scenario_id: str
    category: str
    severity: str
    preconditions: str
    user_action: str
    expected_behaviour: str
    expected_evidence: str
    requirements: str
    steps: list[Step] = field(default_factory=list)
    final_state: str = ""
    runner_error: str = ""
    started: float = field(default_factory=time.time)

    @property
    def dir(self) -> Path:
        return EVIDENCE_DIR / self.run_id

    def add(self, step: Step) -> None:
        self.steps.append(step)

    def screenshot_path(self, n: int, label: str) -> Path:
        safe = re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")[:40]
        self.dir.mkdir(parents=True, exist_ok=True)
        return self.dir / f"{n:02d}-{safe}.png"

    # -- what the judges receive --------------------------------------------

    def public(self) -> dict:
        """The judging view. No version, no absolute path, no run ordering."""
        return {
            "run_id": self.run_id,
            "scenario": {
                "id": self.scenario_id,
                "category": self.category,
                "severity": self.severity,
                "preconditions": self.preconditions,
                "user_action": self.user_action,
                "expected_behaviour": self.expected_behaviour,
                "expected_evidence": self.expected_evidence,
                "requirements": self.requirements,
            },
            "steps": [s.to_public() for s in self.steps],
            "final_state": _scrub(self.final_state),
            "runner_error": _scrub(self.runner_error),
        }

    def as_markdown(self) -> str:
        p = self.public()
        s = p["scenario"]
        out = [
            f"# Run {self.run_id}",
            "",
            f"**Scenario {s['id']}** · {s['category']} · severity {s['severity']}"
            f" · {s['requirements']}",
            "",
            f"**Preconditions.** {s['preconditions']}",
            "",
            f"**User action.** {s['user_action']}",
            "",
            f"**Expected behaviour.** {s['expected_behaviour']}",
            "",
            f"**Expected evidence.** {s['expected_evidence']}",
            "",
            "## What happened",
            "",
        ]
        for st in p["steps"]:
            line = f"{st['step']:>2}. **{st['action']}** — {st['detail']}"
            out.append(line)
            for key, label in (
                ("url", "url"),
                ("http_status", "status"),
                ("visible_text", "visible text"),
                ("message", "message"),
                ("error", "error"),
            ):
                if st.get(key):
                    out.append(f"      - {label}: {st[key]}")
        out += ["", f"**Final state.** {p['final_state'] or '(not recorded)'}"]
        if p["runner_error"]:
            out += ["", f"**The run did not complete.** {p['runner_error']}"]
            out += ["", "A run that could not complete is evidence too. It is "
                        "judged, not discarded."]
        return "\n".join(out) + "\n"

    # -- writing -------------------------------------------------------------

    def write(self, version: str, console: list[str], network: list[dict]) -> Path:
        """Write the bundle, and record the run in the manifest.

        `version` goes to the manifest only. It never enters the bundle.
        """
        self.dir.mkdir(parents=True, exist_ok=True)
        (self.dir / "trace.json").write_text(
            json.dumps(self.public(), indent=2) + "\n", encoding="utf-8"
        )
        (self.dir / "trace.md").write_text(self.as_markdown(), encoding="utf-8")
        if console:
            (self.dir / "console.log").write_text(
                "\n".join(_scrub(c) for c in console) + "\n", encoding="utf-8"
            )
        if network:
            with (self.dir / "network.jsonl").open("w", encoding="utf-8") as fh:
                for entry in network:
                    # Scrubbed like every other file in the bundle. Until
                    # D-014 this held only a status and a relative path and
                    # the raw write was harmless; now that response headers
                    # come through, anything the server echoes is scrubbed
                    # before it can reach a blind judge.
                    fh.write(_scrub(json.dumps(entry)) + "\n")

        MANIFEST.parent.mkdir(parents=True, exist_ok=True)
        with MANIFEST.open("a", encoding="utf-8") as fh:
            fh.write(
                json.dumps(
                    {
                        "run_id": self.run_id,
                        "scenario_id": self.scenario_id,
                        "version": version,
                        "category": self.category,
                        "severity": self.severity,
                        "started": self.started,
                        "completed": time.time(),
                        "steps": len(self.steps),
                        "runner_error": bool(self.runner_error),
                    }
                )
                + "\n"
            )
        return self.dir
