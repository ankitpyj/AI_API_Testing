from .bug_report_generator import generate_bug_report


failed_test = {
    "test_id": "TC-002",
    "endpoint": "/health",
    "method": "GET",

    "expected": {
        "status_code": 200,
        "body": {
            "status": "ok"
        }
    },

    "actual": {
        "status_code": 200,
        "body": {
            "status": "error"
        }
    },

    "ai_analysis": {
        "summary": "The GET /health endpoint returned an incorrect status value.",
        "possible_cause": "The application logic may be returning an error status while still using HTTP 200.",
        "severity": "Medium",
        "recommendation": "Investigate the /health endpoint implementation."
    }
}


bug_report = generate_bug_report(failed_test)


print("\nBUG REPORT")
print("=" * 50)

for key, value in bug_report.items():
    print(f"{key}: {value}")