#!/usr/bin/env python3
"""T02 - judge model smoke test (Gemini).

Closes the mechanical half of T02 and D-007. It reports the exact model id and
version string the API returns, and whether the model is mechanically reliable
enough to be the judge.

The selection criterion is mechanical reliability ONLY: valid JSON every time,
permitted values respected, stable under repetition, acceptable latency. The
judge is never chosen, tuned, or swapped on the basis of how well it agrees
with the human reference - that would pick a judge that flatters the human and
would void EQ2. The input below is synthetic on purpose; no real scenario
exists yet, and none would be used here even if it did.

RPD cannot be read from the API. Read it in Google AI Studio and write it into
records/W01/model-candidates.md with the date you read it.

Usage
    python harness/smoke_judge.py --list
    python harness/smoke_judge.py --model gemini-2.5-flash --runs 10

Needs GEMINI_API_KEY in .env (git-ignored) or in the environment.
No third-party packages: standard library only.
"""

import argparse
import json
import os
import pathlib
import statistics
import sys
import time
import urllib.error
import urllib.request

API = "https://generativelanguage.googleapis.com/v1beta"
ROOT = pathlib.Path(__file__).resolve().parent.parent
VERDICTS = ["satisfied", "not_satisfied", "uncertain"]


def read_text_any(path):
    """Read a text file whatever encoding it was saved in.

    PowerShell's `>>` writes UTF-16 by default on Windows, and `-Encoding utf8`
    writes UTF-8 with a BOM on PowerShell 5.1, so a .env created on Windows is
    often not plain UTF-8.
    """
    raw = path.read_bytes()
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        text = raw.decode("utf-16")
    elif raw[:3] == b"\xef\xbb\xbf":
        text = raw.decode("utf-8-sig")
    else:
        text = raw.decode("utf-8", errors="replace")
    return text.lstrip("\ufeff")


def api_key():
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        env = ROOT / ".env"
        if env.exists():
            for line in read_text_any(env).splitlines():
                line = line.strip().lstrip("\ufeff")
                if line.startswith("export "):
                    line = line[7:].strip()
                if line.startswith("GEMINI_API_KEY") and "=" in line:
                    key = line.split("=", 1)[1].strip().strip("'\"")
                    # `>>` appends, so a retyped key leaves two lines. Last wins.
    if not key:
        sys.exit("GEMINI_API_KEY not found. Put it in .env as GEMINI_API_KEY=... "
                 "(.env is git-ignored) or set it in the environment.")
    key = key.strip()
    if " " in key or len(key) < 20:
        sys.exit(f"GEMINI_API_KEY looks wrong (length {len(key)}"
                 f"{', contains a space' if ' ' in key else ''}). "
                 "Check .env has one line: GEMINI_API_KEY=<key>, nothing else.")
    return key


def post(url, payload):
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode("utf-8"))


# 429 = your quota. 503 = the model is overloaded on Google's side; the error
# body says "Spikes in demand are usually temporary. Please try again later."
# Both are retryable and neither says anything about judgment quality, but they
# are different problems with different fixes, so they are counted separately.
RETRYABLE = {429: "quota", 503: "overloaded"}


def post_retrying(url, payload, attempts=5):
    """POST, backing off on 429 and 503.

    Returns (response, {429: n, 503: n}) counting retries by cause.
    """
    counts = {429: 0, 503: 0}
    delay = 6.0
    for attempt in range(1, attempts + 1):
        try:
            return post(url, payload), counts
        except urllib.error.HTTPError as e:
            if e.code not in RETRYABLE or attempt == attempts:
                raise
            counts[e.code] += 1
            wait = delay
            retry_after = e.headers.get("Retry-After") if e.headers else None
            if retry_after:
                try:
                    wait = max(wait, float(retry_after))
                except ValueError:
                    pass
            print(f"       {e.code} {RETRYABLE[e.code]}, waiting {wait:.0f}s "
                  f"(attempt {attempt}/{attempts - 1})")
            time.sleep(wait)
            delay *= 2
    raise RuntimeError("unreachable")


def list_models(key):
    with urllib.request.urlopen(f"{API}/models?key={key}&pageSize=200", timeout=60) as r:
        data = json.loads(r.read().decode("utf-8"))
    rows = []
    for m in data.get("models", []):
        if "generateContent" in m.get("supportedGenerationMethods", []):
            rows.append((m["name"].replace("models/", ""), m.get("version", ""),
                         m.get("displayName", "")))
    width = max((len(r[0]) for r in rows), default=10)
    print(f"{'model id'.ljust(width)}  version      display name")
    for mid, ver, disp in sorted(rows):
        print(f"{mid.ljust(width)}  {ver:<11}  {disp}")
    print(f"\n{len(rows)} models support generateContent.")
    print("Pick one and pass it with --model. RPD is not in this list - read it "
          "in Google AI Studio.")


# A synthetic item shaped like a real judging call: scenario, compact evidence,
# rubric. Deliberately unambiguous, so a wrong verdict means the model did not
# follow instructions, not that the item was hard.
ITEM = {
    "scenario": "A signed-in user creates a task with an empty title. The "
                "application must reject it with a visible message and must "
                "not create the task.",
    "evidence": [
        "step 1  open /tasks/new            -> form shown",
        "step 2  leave title empty, submit  -> stayed on /tasks/new",
        "step 3  read message container     -> (empty, no message rendered)",
        "step 4  open /tasks                -> a new row with an empty title is present",
    ],
    "rubric": "satisfied only if BOTH a visible rejection message is shown AND "
              "no task was created. Otherwise not_satisfied. Use uncertain only "
              "if the evidence does not show what happened.",
}

PROMPT = (
    "You are judging whether a software scenario was satisfied, from execution "
    "evidence alone.\n\nSCENARIO\n{scenario}\n\nRUBRIC\n{rubric}\n\n"
    "EVIDENCE\n{evidence}\n\nAnswer with JSON only."
).format(scenario=ITEM["scenario"], rubric=ITEM["rubric"],
         evidence="\n".join(ITEM["evidence"]))

SCHEMA = {
    "type": "object",
    "properties": {
        "verdict": {"type": "string", "enum": VERDICTS},
        "reason": {"type": "string"},
    },
    "required": ["verdict", "reason"],
}


def smoke(key, model, runs, sleep):
    url = f"{API}/models/{model}:generateContent?key={key}"
    payload = {
        "contents": [{"parts": [{"text": PROMPT}]}],
        "generationConfig": {
            "temperature": 0,
            "responseMimeType": "application/json",
            "responseSchema": SCHEMA,
        },
    }

    results, latencies, errors = [], [], []
    versions = []
    retried = {429: 0, 503: 0}
    failed = {429: 0, 503: 0, "other": 0}

    for i in range(1, runs + 1):
        if i > 1 and sleep:
            time.sleep(sleep)
        t0 = time.time()
        try:
            resp, retries = post_retrying(url, payload)
            for code, n in retries.items():
                retried[code] += n
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")[:160].replace("\n", " ")
            failed[e.code if e.code in failed else "other"] += 1
            errors.append(f"run {i}: HTTP {e.code} {body}")
            print(f"  run {i:>2}  HTTP {e.code} gave up after retries")
            continue
        except Exception as e:                      # noqa: BLE001
            failed["other"] += 1
            errors.append(f"run {i}: {type(e).__name__} {e}")
            print(f"  run {i:>2}  {type(e).__name__}")
            continue
        dt = time.time() - t0
        latencies.append(dt)

        versions.append(resp.get("modelVersion"))
        try:
            text = resp["candidates"][0]["content"]["parts"][0]["text"]
            obj = json.loads(text)
            verdict = obj["verdict"]
            ok = verdict in VERDICTS and isinstance(obj.get("reason"), str)
        except Exception as e:                      # noqa: BLE001
            errors.append(f"run {i}: unparseable response ({e})")
            print(f"  run {i:>2}  {dt:5.2f}s  INVALID")
            results.append(None)
            continue

        results.append(verdict if ok else None)
        print(f"  run {i:>2}  {dt:5.2f}s  {verdict}")

    valid = [r for r in results if r]
    distinct = sorted(set(valid))
    seen_versions = sorted({v for v in versions if v})
    rerouted = bool(seen_versions) and seen_versions != [model]
    report = {
        "checked": time.strftime("%Y-%m-%d %H:%M:%S %z"),
        "model_requested": model,
        "model_versions_returned": seen_versions,
        "rerouted": rerouted,
        "served_model_stable_within_run": len(seen_versions) <= 1,
        "runs": runs,
        "seconds_between_calls": sleep,
        "valid_json": f"{len(valid)}/{runs}",
        "verdicts": {v: valid.count(v) for v in distinct},
        "stable_under_repetition": len(distinct) == 1,
        "retries_that_recovered": {"429_quota": retried[429],
                                   "503_overloaded": retried[503]},
        "calls_lost_after_retries": {"429_quota": failed[429],
                                     "503_overloaded": failed[503],
                                     "other": failed["other"]},
        "latency_seconds": {
            "median": round(statistics.median(latencies), 2) if latencies else None,
            "max": round(max(latencies), 2) if latencies else None,
        },
        "errors": errors,
        "rpd": "READ IN GOOGLE AI STUDIO - not available from the API",
    }

    print("\n" + json.dumps(report, indent=2))

    out = ROOT / "records" / "W01" / "judge-smoke-test.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"\nwritten to {out.relative_to(ROOT)}")

    print("\nPass requires all of:")
    print(f"  valid JSON {runs}/{runs} ..................... "
          f"{'PASS' if len(valid) == runs else 'FAIL'}")
    print(f"  same verdict every run ............... "
          f"{'PASS' if len(distinct) == 1 else 'FAIL'}")
    print(f"  no unrecovered errors ................ "
          f"{'PASS' if not errors else 'FAIL'}")
    print(f"  one served model throughout .......... "
          f"{'PASS' if len(seen_versions) <= 1 else 'FAIL'}")
    print("  RPD high enough for 540 calls ........ read it in AI Studio")
    if retried[429] or retried[503]:
        print(f"\n  Recovered by retry: {retried[429]} quota (429), "
              f"{retried[503]} overload (503).")
    if failed[503]:
        print(f"\n  {failed[503]} call(s) still failed with 503 after retries. "
              "503 is Google's\n  capacity, not your quota - a busy model, or "
              "free-tier requests being\n  shed under load. A quieter or older "
              "model may behave far better.")
    if failed[429]:
        print(f"\n  {failed[429]} call(s) still failed with 429 after retries. "
              "That is your daily\n  quota, and no amount of pacing fixes it.")
    if rerouted:
        print(f"\n  NOTE  you requested '{model}' but the API served "
              f"{seen_versions}.\n  The requested id does not pin the model. "
              "judge.py must record modelVersion\n  on every one of the 540 "
              "calls and stop if it ever changes mid-run.")
    print("\n540 calls = 45 scenarios x 4 versions x 3 runs.")
    print("  RPD 1000 -> 1 day   250 -> 3 days   100 -> 6 days   50 -> 11 days")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true", help="list models and exit")
    ap.add_argument("--model", default="gemini-2.5-flash")
    ap.add_argument("--runs", type=int, default=10)
    ap.add_argument("--sleep", type=float, default=7.0,
                    help="seconds between calls; free tiers throttle per minute")
    a = ap.parse_args()
    key = api_key()
    if a.list:
        list_models(key)
    else:
        print(f"model: {a.model}   runs: {a.runs}   "
              f"{a.sleep}s between calls\n")
        smoke(key, a.model, a.runs, a.sleep)


if __name__ == "__main__":
    main()
