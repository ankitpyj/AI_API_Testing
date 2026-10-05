import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from parser.openapi_parser import (
    load_openapi,
    extract_endpoints
)

from ai_generator.ai_test_generator import (
    generate_ai_tests
)


# Load OpenAPI specification
openapi_data = load_openapi(
    "http://127.0.0.1:8000/openapi.json"
)


# Extract all API endpoints
endpoints = extract_endpoints(
    openapi_data
)


# Find POST /users
api_info = None

for endpoint in endpoints:

    if (
        endpoint["path"] == "/users"
        and endpoint["method"] == "POST"
    ):
        api_info = endpoint
        break


# Make sure endpoint was found
if api_info is None:
    print("POST /users endpoint not found")
    exit()


# Generate AI tests
tests = generate_ai_tests(
    api_info
)


print("\nAI GENERATED TESTS")
print("=" * 60)


for index, test in enumerate(
    tests,
    start=1
):

    print(f"\nAI-TC-{index}")

    print(
        f"Category: "
        f"{test['category']}"
    )

    print(
        f"Description: "
        f"{test['description']}"
    )

    print(
        f"Request: "
        f"{test['request']}"
    )

    print(
        f"Expected Status: "
        f"{test['expected']['status_code']}"
    )