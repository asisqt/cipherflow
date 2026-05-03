#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# CipherFlow Docker Smoke Test
# ═══════════════════════════════════════════════════════════════════════════════
# Builds and runs the backend container locally, validates endpoints,
# then tears down. Used for pre-push verification.
#
# Usage: ./scripts/docker-test.sh
# ═══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

IMAGE="cipherflow-smoke-test"
CONTAINER="cipherflow-smoke"
PORT=8099

echo "Building image..."
docker build -t $IMAGE . > /dev/null 2>&1

echo "Starting container on port $PORT..."
docker run -d --name $CONTAINER -p $PORT:8000 $IMAGE > /dev/null

echo "Waiting for startup..."
sleep 5

PASS=0
FAIL=0

check() {
    code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "http://localhost:$PORT$1")
    if [ "$code" = "$2" ]; then
        echo "  ✓ $1 → $code"
        PASS=$((PASS + 1))
    else
        echo "  ✗ $1 → $code (expected $2)"
        FAIL=$((FAIL + 1))
    fi
}

echo "Running smoke tests..."
check "/" "200"
check "/api/v1/health" "200"
check "/api/v1/ready" "200"
check "/docs" "200"

echo "Cleaning up..."
docker stop $CONTAINER > /dev/null 2>&1
docker rm $CONTAINER > /dev/null 2>&1

echo "────────────────────────"
echo "Results: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ] && echo "✓ Smoke test passed" || echo "✗ Smoke test failed"
exit $FAIL
