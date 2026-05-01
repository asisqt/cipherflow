"""
CipherFlow Performance Benchmark
====================================
Measures API throughput, latency percentiles, and error rates.
Useful for baseline performance testing before and after changes.

Usage:
    python scripts/benchmark.py http://localhost:8000
    python scripts/benchmark.py http://168.144.1.246 --requests 500
"""

import argparse
import json
import time
import statistics
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed


def get_token(base_url: str) -> str:
    """Authenticate and return JWT token."""
    data = json.dumps({"username": "admin", "password": "cipherflow-secret"}).encode()
    req = urllib.request.Request(
        f"{base_url}/api/v1/auth/token",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())["access_token"]


def send_request(base_url: str, token: str, request_id: int) -> dict:
    """Send a single process request and measure latency."""
    payload = json.dumps({
        "id": f"bench-{request_id:06d}",
        "data": {
            "name": f"  Benchmark User {request_id}  ",
            "email": f"user{request_id}@benchmark.test",
            "password": "bench-secret-password",
            "credit_card": "4111-1111-1111-1111",
        },
    }).encode()

    req = urllib.request.Request(
        f"{base_url}/api/v1/process",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
    )

    start = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            resp.read()
            latency = (time.perf_counter() - start) * 1000
            return {"status": "success", "latency_ms": latency, "code": resp.status}
    except urllib.error.HTTPError as e:
        latency = (time.perf_counter() - start) * 1000
        return {"status": "error", "latency_ms": latency, "code": e.code}
    except Exception as e:
        latency = (time.perf_counter() - start) * 1000
        return {"status": "error", "latency_ms": latency, "code": 0}


def run_benchmark(base_url: str, total_requests: int, concurrency: int) -> None:
    """Execute benchmark and print results."""
    print(f"CipherFlow Performance Benchmark")
    print(f"Target:      {base_url}")
    print(f"Requests:    {total_requests}")
    print(f"Concurrency: {concurrency}")
    print(f"{'─' * 48}")

    print("Authenticating...", end=" ")
    token = get_token(base_url)
    print("OK")

    print(f"Running benchmark...")
    results = []
    start_time = time.perf_counter()

    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        futures = {
            pool.submit(send_request, base_url, token, i): i
            for i in range(total_requests)
        }
        for future in as_completed(futures):
            results.append(future.result())

    elapsed = time.perf_counter() - start_time
    latencies = [r["latency_ms"] for r in results]
    successes = sum(1 for r in results if r["status"] == "success")
    errors = total_requests - successes

    latencies.sort()
    p50 = latencies[int(len(latencies) * 0.50)]
    p90 = latencies[int(len(latencies) * 0.90)]
    p95 = latencies[int(len(latencies) * 0.95)]
    p99 = latencies[min(int(len(latencies) * 0.99), len(latencies) - 1)]

    print(f"{'─' * 48}")
    print(f"Results:")
    print(f"  Total time:    {elapsed:.2f}s")
    print(f"  Throughput:    {total_requests / elapsed:.1f} req/s")
    print(f"  Success:       {successes}/{total_requests} ({successes/total_requests*100:.1f}%)")
    print(f"  Errors:        {errors}")
    print(f"{'─' * 48}")
    print(f"Latency:")
    print(f"  Mean:          {statistics.mean(latencies):.1f}ms")
    print(f"  Median (p50):  {p50:.1f}ms")
    print(f"  p90:           {p90:.1f}ms")
    print(f"  p95:           {p95:.1f}ms")
    print(f"  p99:           {p99:.1f}ms")
    print(f"  Min:           {min(latencies):.1f}ms")
    print(f"  Max:           {max(latencies):.1f}ms")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CipherFlow Performance Benchmark")
    parser.add_argument("url", help="Base URL of the API")
    parser.add_argument("--requests", type=int, default=100, help="Total requests")
    parser.add_argument("--concurrency", type=int, default=10, help="Concurrent workers")
    args = parser.parse_args()
    run_benchmark(args.url, args.requests, args.concurrency)
