import statistics
import time

import httpx

URL = "http://127.0.0.1:8000/chat"
RUNS = 15  # 15 per message x 4 messages = 60 total requests
PAUSE_SECONDS = 5

# Read-only / side-effect-free messages, so no appointments get created.
MESSAGES = [
    ("greeting", "Hello"),
    ("faq", "What are your working hours?"),
    ("book (missing fields)", "Book an appointment tomorrow at 5 PM"),
    ("get appointment (DB read)", "Show my appointment 6"),
]

HEADERS = {
    "total": "X-Latency-Total-Ms",
    "ai": "X-Latency-AI-Ms",
    "db": "X-Latency-DB-Ms",
    "other": "X-Latency-Other-Ms",
}


def percentile(values, pct):
    """Nearest-rank percentile — no external dependency needed."""
    if not values:
        return float("nan")
    ordered = sorted(values)
    k = max(0, min(len(ordered) - 1, int(round(pct / 100 * (len(ordered) - 1)))))
    return ordered[k]


def summarize(values):
    return {
        "n": len(values),
        "min": min(values),
        "max": max(values),
        "avg": statistics.mean(values),
        "median": statistics.median(values),
        "p95": percentile(values, 95),
    }


def print_summary(label, values):
    s = summarize(values)
    print(
        f"  {label:<11} n={s['n']:<3} min={s['min']:8.1f}  max={s['max']:8.1f}  "
        f"avg={s['avg']:8.1f}  median={s['median']:8.1f}  p95={s['p95']:8.1f}"
    )


all_results = {"round_trip": [], "total": [], "ai": [], "db": [], "other": []}

with httpx.Client(timeout=60) as client:
    for label, message in MESSAGES:
        samples = {"round_trip": [], "total": [], "ai": [], "db": [], "other": []}
        failures = 0
        for i in range(RUNS):
            start = time.perf_counter()
            r = client.post(URL, json={"message": message})
            round_trip = (time.perf_counter() - start) * 1000

            if r.status_code != 200:
                failures += 1
                print(f"  run {i + 1}: HTTP {r.status_code} {r.text[:120]}")
            else:
                samples["round_trip"].append(round_trip)
                for key, header in HEADERS.items():
                    samples[key].append(float(r.headers[header]))
            time.sleep(PAUSE_SECONDS)

        print(f"\n=== {label}: {len(samples['total'])}/{RUNS} successful, {failures} failed ===")
        for key in ("round_trip", "total", "ai", "db", "other"):
            if samples[key]:
                print_summary(key, samples[key])
                all_results[key].extend(samples[key])

print("\n\n=== COMBINED ACROSS ALL SCENARIOS ===")
for key in ("round_trip", "total", "ai", "db", "other"):
    if all_results[key]:
        print_summary(key, all_results[key])
print(f"\nTotal successful requests: {len(all_results['total'])}")