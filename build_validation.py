import sys
# # pyrefly: ignore [missing-import]
# from fastapi.testclient import TestClient
# # pyrefly: ignore [missing-import]
# from src.api.hockeyplayoffapi.main import app

# client = TestClient(app)


def validate_app_build():
    """Validate the FastAPI application build."""
    try:
        # 1. Import your FastAPI app instance
        # Change 'app.main' if your folder/file name is different
        from src.api.hockeyplayoffapi.main import app
        from fastapi.testclient import TestClient

        # print("⚡ Compiling application and OpenAPI schema...")
        # schema = app.openapi()
        # if not schema:
        #     raise ValueError("Failed to compile OpenAPI schema.")

        print("🔍 Testing health endpoint layout...")
        # 2. Initialize the TestClient with your app
        client = TestClient(app)

        # 3. Request the specific /health/live endpoint
        response = client.get("/health")

        # 4. Assert the status code is 200 OK
        if response.status_code != 200:
            raise ValueError(
                f"Endpoint failed with status code: {response.status_code}"
            )

        # 5. Assert the JSON body matches exactly what your method returns
        expected_body = {"status": "alive"}
        if response.json() != expected_body:
            raise ValueError(f"Unexpected response body: {response.json()}")

        print("✅ Success! App compiled and '/health' validated perfectly.")
        sys.exit(0)

    except Exception as e:
        print(f"❌ Validation failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    validate_app_build()
