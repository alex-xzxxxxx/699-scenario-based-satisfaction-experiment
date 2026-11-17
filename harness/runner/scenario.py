"""Scenario loading and validation.

A scenario is a YAML file carrying the Appendix B Table B1 fields plus the
steps that execute it. FR1 requires scenarios to be stored with id, use case,
category, severity, steps, expected behaviour and expected evidence; this
module is where that requirement is enforced rather than assumed.

Validation here is structural only — does the file carry the required fields,
are the category and severity from the fixed vocabularies, does every step name
a helper that exists. The Table B4 judgments (is it observable, would two
readers agree, is it a duplicate, is it traceable, can it run reliably) are
T11's work and belong to a person.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from . import steps as step_helpers

LIBRARY = Path(__file__).resolve().parent.parent.parent / "scenarios" / "library"

CATEGORIES = {"normal", "failure", "edge", "adversarial", "integration"}
SEVERITIES = {"critical", "high", "medium", "low"}

# Table 8. Assigned when the scenario is written, before any result exists.
LINEAR_WEIGHT = {"critical": 4, "high": 3, "medium": 2, "low": 1}
GEOMETRIC_WEIGHT = {"critical": 8, "high": 4, "medium": 2, "low": 1}

REQUIRED = (
    "id", "use_case", "category", "severity", "preconditions",
    "user_action", "expected_behaviour", "expected_evidence",
    "requirements", "steps",
)


class ScenarioError(ValueError):
    pass


@dataclass
class Scenario:
    id: str
    use_case: str
    category: str
    severity: str
    preconditions: str
    user_action: str
    expected_behaviour: str
    expected_evidence: str
    requirements: str
    steps: list[dict]
    path: Path | None = None

    @property
    def linear_weight(self) -> int:
        return LINEAR_WEIGHT[self.severity]

    @property
    def geometric_weight(self) -> int:
        return GEOMETRIC_WEIGHT[self.severity]


def _fault(path: Path, msg: str) -> ScenarioError:
    return ScenarioError(f"{path.name}: {msg}")


def parse(data: dict, path: Path) -> Scenario:
    missing = [f for f in REQUIRED if f not in data or data[f] in (None, "")]
    if missing:
        raise _fault(path, f"missing required field(s): {', '.join(missing)}")

    category = str(data["category"]).strip().lower()
    if category not in CATEGORIES:
        raise _fault(path, f"category {category!r} is not one of {sorted(CATEGORIES)}")

    severity = str(data["severity"]).strip().lower()
    if severity not in SEVERITIES:
        raise _fault(path, f"severity {severity!r} is not one of {sorted(SEVERITIES)}")

    raw_steps = data["steps"]
    if not isinstance(raw_steps, list) or not raw_steps:
        raise _fault(path, "steps must be a non-empty list")

    parsed: list[dict] = []
    for i, s in enumerate(raw_steps, 1):
        if isinstance(s, str):
            s = {"do": s}
        if not isinstance(s, dict) or "do" not in s:
            raise _fault(path, f"step {i} must be a mapping with a 'do' key")
        name = s["do"]
        try:
            step_helpers.get(name)
        except KeyError as exc:
            raise _fault(path, f"step {i}: {exc}") from None
        parsed.append(s)

    if path.stem != data["id"]:
        raise _fault(path, f"file name must match the scenario id {data['id']!r}")

    return Scenario(
        id=data["id"],
        use_case=str(data["use_case"]),
        category=category,
        severity=severity,
        preconditions=str(data["preconditions"]).strip(),
        user_action=str(data["user_action"]).strip(),
        expected_behaviour=str(data["expected_behaviour"]).strip(),
        expected_evidence=str(data["expected_evidence"]).strip(),
        requirements=str(data["requirements"]).strip(),
        steps=parsed,
        path=path,
    )


def load(path: str | Path) -> Scenario:
    path = Path(path)
    return parse(yaml.safe_load(path.read_text(encoding="utf-8")) or {}, path)


def load_all(directory: str | Path = LIBRARY) -> list[Scenario]:
    directory = Path(directory)
    found = sorted(directory.glob("*.yaml")) + sorted(directory.glob("*.yml"))
    scenarios = [load(p) for p in found]
    seen: dict[str, Path] = {}
    for s in scenarios:
        if s.id in seen:
            raise ScenarioError(f"duplicate scenario id {s.id!r}")
        seen[s.id] = s.path
    return scenarios
