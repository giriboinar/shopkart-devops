#!/usr/bin/env python3
"""5x festival-traffic SPIKE SIMULATION (local only).

What this really is: a small threaded HTTP load script against a LOCAL
deployment (docker-compose or kind port-forward on localhost:8000).
It is NOT a real festival, NOT real users, and NOT production traffic.

Usage:
  python3 loadtest/spike.py            # baseline then 5x load
  BASE_URL=http://localhost:8000 python3 loadtest/spike.py

The script prints request counts, success rate and average latency for a
baseline round and a 5x round, so you can watch the HPA scale the
Deployment up (kubectl get hpa -n shopkart) and back down afterwards.
"""
import concurrent.futures
import os
import statistics
import time
import urllib.request

BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000")


def hit(_):
    start = time.time()
    try:
        with urllib.request.urlopen(BASE_URL + "/products", timeout=10) as r:
            return r.status, time.time() - start
    except Exception:
        return 0, time.time() - start


def round(name, workers, total):
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        results = list(pool.map(hit, range(total)))
    ok = sum(1 for s, _ in results if s == 200)
    lat = [t for _, t in results if t]
    print(f"{name}: {ok}/{total} OK, avg latency {statistics.mean(lat):.3f}s")
    return ok


if __name__ == "__main__":
    print("Baseline round (10 workers, 100 requests):")
    round("baseline", 10, 100)
    print("Spike round — 5x workers (50 workers, 500 requests):")
    round("spike-5x", 50, 500)
    print("Done. Check HPA scaling with: kubectl get hpa -n shopkart")
