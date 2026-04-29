"""
Post-deployment smoke tests.
Usage: DEPLOYMENT_URL=https://your-app.railway.app python scripts/smoke_test.py
Exit code 1 if any test fails (triggers auto-rollback in CI).
"""
import os
import sys

try:
    import httpx
except ImportError:
    print("httpx not found. Install with: pip install httpx")
    sys.exit(1)

BASE_URL = os.environ.get("DEPLOYMENT_URL", "http://localhost:8000")


def assert_status(response, expected, name: str):
    """Assert response status code matches expected (int or list of ints)."""
    if isinstance(expected, list):
        assert response.status_code in expected, (
            f"{name} failed: got {response.status_code}, expected one of {expected}"
        )
    else:
        assert response.status_code == expected, (
            f"{name} failed: got {response.status_code}, expected {expected}"
        )
    print(f"  ✅ {name}")


def smoke_test():
    client = httpx.Client(base_url=BASE_URL, timeout=15)

    print(f"Running smoke tests against: {BASE_URL}\n")

    # 1. Health check — always required
    assert_status(client.get("/health"), 200, "Health check")

    # ------------------------------------------------------------------
    # 2. Core API tests — replace with your actual endpoints
    # ------------------------------------------------------------------
    # Example:
    # r = client.post("/api/paths", json={"goal": "smoke test", "depth": "basic"})
    # assert_status(r, 200, "POST /api/paths")
    # data = r.json()
    # assert "nodes" in data and len(data["nodes"]) > 0, "Response missing 'nodes'"
    # print("  ✅ /api/paths response schema valid")
    #
    # Uncomment and adapt the block above for your core endpoint.
    # ------------------------------------------------------------------

    print(f"\n✅ All smoke tests passed ({BASE_URL})")


if __name__ == "__main__":
    try:
        smoke_test()
    except (AssertionError, Exception) as e:
        print(f"\n❌ Smoke test failed: {e}")
        sys.exit(1)
