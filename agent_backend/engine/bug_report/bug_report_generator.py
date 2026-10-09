def generate_bug_report(result, bug_counter=None):
    """
    Generate a structured bug report from a failed test result.
    bug_counter: optional int to produce unique BUG-XXX IDs across multiple failures.
                 Falls back to extracting the numeric part of the test_id.
    """
    if bug_counter is not None:
        bug_id = f"BUG-{bug_counter:03d}"
    else:
        # Derive a numeric suffix from the test_id (e.g. TC-007 → BUG-007)
        test_id = result.get("test_id", "TC-001")
        numeric_part = "".join(filter(str.isdigit, test_id))
        bug_id = f"BUG-{numeric_part.zfill(3)}" if numeric_part else "BUG-001"

    bug_report = {
        "bug_id": bug_id,
        "test_id": result["test_id"],
        "endpoint": result["method"] + " " + result["endpoint"],
        "severity": result["ai_analysis"]["severity"],
        "summary": result["ai_analysis"]["summary"],
        "expected": {
            "status_code": result["expected_status"],
            "schema": result["expected_schema"]
        },
        "actual": {
            "status_code": result["actual_status"],
            "body": result["actual_body"]
        },
        "possible_cause": result["ai_analysis"]["possible_cause"],
        "recommendation": result["ai_analysis"]["recommendation"],
        "status": "Open"
    }
    return bug_report