"""Compare verdicts from different judgment sources on the same runs.

A first cut of what T27 needs. It joins the sources on run_id, shows where
they agree, and reveals the version last — from the manifest, which is the
only place it lives.

    python -m harness.compare --judge data/verdicts.jsonl \\
                              --human data/human-verdicts.jsonl \\
                              --manifest data/run_manifest.jsonl

Each verdict file is JSONL, one object per line:

    {"run_id": "1caea6087d5e641a", "verdict": "satisfied", "note": "..."}

D-015 governs what this may and may not do. Sources are compared only on the
runs they both judged, a missing verdict is never read as satisfied, and no
blended score is produced anywhere.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

from harness.judge import read_text_any   # tolerates a UTF-16 file (W02)

VERDICTS = {"satisfied", "not_satisfied", "uncertain"}
SHORT = {"satisfied": "SAT", "not_satisfied": "NOT", "uncertain": "UNC"}


def load(path: str, label: str) -> dict[str, dict]:
    """One JSONL file of verdicts, keyed by run_id.

    Says what is wrong in a sentence rather than raising: this is run in front
    of people, and a stack trace mid-demo tells them nothing.
    """
    if not path:
        return {}
    p = pathlib.Path(path)
    if not p.exists():
        raise SystemExit(
            f"No {label} verdicts at {path}.\n"
            f"  Expected one JSON object per line:\n"
            f'    {{"run_id": "<the id>", "verdict": "satisfied", "note": "..."}}\n'
            f"  verdict is satisfied, not_satisfied or uncertain.\n"
            f"  Write it in an editor and save as UTF-8; PowerShell redirection\n"
            f"  produces UTF-16, which is read here but is worth avoiding.")
    rows = {}
    for n, line in enumerate(read_text_any(p).splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            r = json.loads(line)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"{path} line {n} is not valid JSON: {exc.msg}\n  {line[:120]}")
        if "run_id" not in r:
            raise SystemExit(f"{path} line {n} has no run_id:\n  {line[:120]}")
        v = r.get("verdict")
        if v is not None and v not in VERDICTS:
            print(f"warning: {path} line {n} has verdict {v!r}, not one of "
                  f"{sorted(VERDICTS)} — it will be excluded", file=sys.stderr)
        rows[r["run_id"]] = r
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--judge", default="", help="JSONL of LLM judge verdicts")
    ap.add_argument("--human", default="", help="JSONL of human verdicts")
    ap.add_argument("--manifest", default="data/run_manifest.jsonl")
    ap.add_argument("--reveal", action="store_true",
                    help="show the version column (read from the manifest)")
    a = ap.parse_args()

    judge, human = load(a.judge, "judge"), load(a.human, "human")
    man = load(a.manifest, "manifest") if pathlib.Path(a.manifest).exists() else {}

    both = sorted(set(judge) & set(human))
    only_j = sorted(set(judge) - set(human))

    if not both:
        print("No run was judged by both sources; there is nothing to compare.")
        print(f"  judge: {len(judge)} run(s)   human: {len(human)} run(s)")
        return 1

    scen = {rid: man.get(rid, {}).get("scenario_id", "?") for rid in both}
    ver = {rid: man.get(rid, {}).get("version", "?") for rid in both}

    head = f"{'run':<18}{'scenario':<10}"
    if a.reveal:
        head += f"{'version':<9}"
    head += f"{'judge':<7}{'human':<7}agree"
    print(head)
    print("-" * len(head))

    agree = 0
    counted = 0
    for rid in both:
        j = judge[rid].get("verdict")
        h = human[rid].get("verdict")
        # A missing or unusable verdict is excluded and counted, never read as
        # satisfied (D-015).
        usable = j in VERDICTS and h in VERDICTS
        same = usable and j == h
        if usable:
            counted += 1
            agree += same
        row = f"{rid:<18}{scen[rid]:<10}"
        if a.reveal:
            row += f"{ver[rid]:<9}"
        row += (f"{SHORT.get(j, '--'):<7}{SHORT.get(h, '--'):<7}"
                f"{'yes' if same else ('no' if usable else 'excluded')}")
        print(row)

    print()
    if counted:
        print(f"Agreement on the {counted} run(s) both judged usably: "
              f"{agree}/{counted} = {agree / counted:.0%}")
    excluded = len(both) - counted
    if excluded:
        print(f"Excluded, no usable verdict from one side: {excluded}")
    if only_j:
        print(f"Judged by the model but not by the human: {len(only_j)} "
              "— not comparable, left out (D-015 §5)")
    if counted < 20:
        print("\nToo few runs for an agreement statistic. This is a "
              "demonstration of the comparison, not a result; EQ2 needs the "
              "human subset of about 25.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
