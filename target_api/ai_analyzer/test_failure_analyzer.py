import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_analyzer.ai_failure_analyzer import (
    analyze_failure
)


# Simulated failed test
failed_test = {
    "test_id": "TC-002",
    "endpoint": "/health",
    "method": "GET",
    "status": "FAIL",

    "expected_status": 200,
    "actual_status": 200,

    "expected_schema": {
        "type": "object",
        "properties": {
            "status": {
                "type": "string",
                "example": "ok"
            }
        },
        "required": [
            "status"
        ]
    },

    "actual_body": {
        "status": "error"
    },

    "failure_reason": (
        "Response body does not match "
        "the expected schema or expected values."
    )
}


# Analyze failure
analysis = analyze_failure(
    failed_test
)


print("\nAI FAILURE ANALYSIS")
print("=" * 60)

print(
    f"\nSummary:\n"
    f"{analysis['summary']}"
)

print(
    f"\nPossible Cause:\n"
    f"{analysis['possible_cause']}"
)

print(
    f"\nSeverity:\n"
    f"{analysis['severity']}"
)

print(
    f"\nRecommendation:\n"
    f"{analysis['recommendation']}"
)