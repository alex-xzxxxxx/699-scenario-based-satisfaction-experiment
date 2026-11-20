"""T18/T25 — the LLM judge.

Reads one evidence bundle, asks the judge model whether the scenario was
satisfied, and records the verdict. The judge sees the bundle and nothing
else: no version, no file paths, no other run (D-009, blinding).

    python -m harness.judge --bundle evidence/<run_id>          # one run
    python -m harness.judge --all --out data/verdicts.jsonl     # every bundle
    python -m harness.judge --bundle evidence/<id> --dry-run    # build the
                                                                # prompt, no call

The prompt is logs/prompts/P-003.txt and is frozen at M5. This module never
edits it, and never decides anything itself — it asks, parses and records.

Needs GEMINI_API_KEY in the environment or in .env. The key is never written
to a file, a log or a verdict record.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import sys
import time
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
PROMPT = ROOT / "logs" / "prompts" / "P-003.txt"
MODEL = "gemini-3.6-flash"          # D-010; a different modelVersion halts the run
ENDPOINT = ("https://generativelanguage.googleapis.com/v1beta/models/"
            f"{MODEL}:generateContent")

RETRYABLE = {429: "quota", 503: "overloaded"}   # D-011
MAX_TRIES = 5
VERDICTS = {"satisfied", "not_satisfied", "uncertain"}


def read_text_any(path: pathlib.Path) -> str:
    """PowerShell writes UTF-16; tolerate it (W02)."""
    raw = path.read_bytes()
    for bom, enc in ((b"\xff\xfe", "utf-16-le"), (b"\xfe\xff", "utf-16-be"),
                     (b"\xef\xbb\xbf", "utf-8-sig")):
        if raw.startswith(bom):
            return raw.decode(enc)
    return raw.decode("utf-8")


def api_key() -> str:
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if key:
        return key
    env = ROOT / ".env"
    if env.exists():
        for line in read_text_any(env).splitlines():
            if line.strip().startswith("GEMINI_API_KEY"):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit("GEMINI_API_KEY is not set, in the environment or in .env.")


def build_prompt(bundle: pathlib.Path) -> str:
    """The scenario and the trace, in the frozen prompt's two slots."""
    trace = json.loads((bundle / "trace.json").read_text(encoding="utf-8"))
    sc = trace["scenario"]
    scenario = "\n".join([
        f"Scenario {sc['id']}",
        f"Category: {sc['category']}   Severity: {sc['severity']}",
        f"Requirements: {sc['requirements']}",
        "",
        f"Preconditions: {sc['preconditions']}",
        f"User action: {sc['user_action']}",
        f"Expected behaviour: {sc['expected_behaviour']}",
        f"Expected evidence: {sc['expected_evidence']}",
    ])
    # The Markdown rendering of the same trace is what a person reads (D-009);
    # the judge is given the JSON, so that both judges work from one artefact.
    body = json.dumps({k: v for k, v in trace.items() if k != "scenario"},
                      indent=1, ensure_ascii=False)
    tpl = read_text_any(PROMPT)
    return tpl.replace("{SCENARIO}", scenario).replace("{TRACE}", body)


def parse_verdict(text: str) -> dict:
    """Pull the JSON object out of the reply. Raises if it is not usable."""
    s = text.strip()
    if s.startswith("```"):
        s = re.sub(r"^```[a-z]*\n|\n```$", "", s, flags=re.M).strip()
    start, end = s.find("{"), s.rfind("}")
    if start < 0 or end < start:
        raise ValueError("no JSON object in the reply")
    obj = json.loads(s[start:end + 1])
    v = str(obj.get("verdict", "")).strip().lower()
    if v not in VERDICTS:
        raise ValueError(f"verdict {v!r} is not one of {sorted(VERDICTS)}")
    obj["verdict"] = v
    if not isinstance(obj.get("evidence"), list) or not obj["evidence"]:
        raise ValueError("evidence must be a non-empty list")
    return obj


def ask(prompt: str, key: str) -> tuple[dict, str]:
    """One judged run. Returns (parsed verdict, the modelVersion served)."""
    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0, "responseMimeType": "application/json"},
    }).encode("utf-8")
    last = ""
    for attempt in range(1, MAX_TRIES + 1):
        req = urllib.request.Request(
            ENDPOINT, data=payload,
            headers={"Content-Type": "application/json", "x-goog-api-key": key})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                body = json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code in RETRYABLE and attempt < MAX_TRIES:
                wait = 2 ** attempt
                print(f"  {RETRYABLE[e.code]} ({e.code}); retrying in {wait}s",
                      file=sys.stderr)
                time.sleep(wait)
                continue
            raise
        served = body.get("modelVersion", "")
        if served and served != MODEL:
            raise SystemExit(
                f"halting: asked for {MODEL}, served {served}. D-011 requires "
                "the model version to be constant across a run.")
        last = body["candidates"][0]["content"]["parts"][0]["text"]
        return parse_verdict(last), served
    raise RuntimeError(f"gave up after {MAX_TRIES} attempts; last reply: {last[:200]}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bundle", help="one evidence bundle directory")
    ap.add_argument("--all", action="store_true", help="every bundle under evidence/")
    ap.add_argument("--out", default="", help="append verdicts as JSONL")
    ap.add_argument("--dry-run", action="store_true",
                    help="build the prompt and print it; make no call")
    a = ap.parse_args()

    if a.bundle:
        bundles = [pathlib.Path(a.bundle)]
    elif a.all:
        bundles = sorted(p.parent for p in (ROOT / "evidence").glob("*/trace.json"))
    else:
        return ap.print_usage() or 2

    if a.dry_run:
        print(build_prompt(bundles[0]))
        return 0

    key = api_key()
    out = open(a.out, "a", encoding="utf-8") if a.out else None
    for b in bundles:
        prompt = build_prompt(b)
        try:
            verdict, served = ask(prompt, key)
            row = {"run_id": b.name, "verdict": verdict["verdict"],
                   "evidence": verdict.get("evidence", []),
                   "reason": verdict.get("reason", ""), "model_version": served}
        except Exception as exc:  # noqa: BLE001
            # A run with no usable verdict is excluded and counted, never read
            # as satisfied (D-015).
            row = {"run_id": b.name, "verdict": None, "error": f"{type(exc).__name__}: {exc}"}
        print(f"{b.name}  {row.get('verdict') or 'NO VERDICT'}")
        if out:
            out.write(json.dumps(row, ensure_ascii=False) + "\n")
            out.flush()
    if out:
        out.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
