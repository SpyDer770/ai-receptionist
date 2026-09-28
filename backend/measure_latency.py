import statistics
import time

import httpx

URL = "http://127.0.0.1:8000/chat"
RUNS = 5
PAUSE_SECONDS = 6  # stays under free-tier per-minute request limits

# Read-only messages, so no appointments get created or cancelled.
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


def summarize(values):
    return f"median {statistics.median(values):7.1f}  min {min(values):7.1f}  max {max(values):7.1f}"


with httpx.Client(timeout=60) as client:
    for label, message in MESSAGES:
        samples = {"round_trip": [], "total": [], "ai": [], "db": [], "other": []}
        for i in range(RUNS):
            start = time.perf_counter()
            r = client.post(URL, json={"message": message})
            round_trip = (time.perf_counter() - start) * 1000

            if r.status_code != 200:
                print(f"  run {i + 1}: HTTP {r.status_code} {r.text[:120]}")
            else:
                samples["round_trip"].append(round_trip)
                for key, header in HEADERS.items():
                    samples[key].append(float(r.headers[header]))
            time.sleep(PAUSE_SECONDS)

        print(f"\n=== {label}: {len(samples['total'])}/{RUNS} successful runs (ms) ===")
        if samples["total"]:
            for key in ("round_trip", "total", "ai", "db", "other"):
                print(f"  {key:<11} {summarize(samples[key])}")