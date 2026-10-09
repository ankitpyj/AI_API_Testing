import sys
import os
import json
import requests


# Project paths

ENGINE_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

AGENT_BACKEND_ROOT = os.path.dirname(ENGINE_ROOT)

PROJECT_ROOT = os.path.dirname(AGENT_BACKEND_ROOT)

TARGET_API_ROOT = os.path.join(
    PROJECT_ROOT,
    "target_api"
)

# Add the correct folders to Python's import path
for folder in [
    ENGINE_ROOT,
    AGENT_BACKEND_ROOT,
    PROJECT_ROOT
]:
    if folder not in sys.path:
        sys.path.insert(0, folder)

from bug_report.bug_report_generator import (
    generate_bug_report
)

from test_generator.rule_based_generator import (
    generate_all_tests,
    get_expected_success_response
)

from test_generator.response_validator import (
    validate_response
)

from parser.openapi_parser import (
    load_openapi,
    extract_endpoints
)

from ai_generator.ai_test_generator import (
    generate_ai_tests
)

from ai_analyzer.ai_failure_analyzer import (
    analyze_failure
)

from db_operations import (
    create_test_run,
    save_test_result,
    save_bug_report
)

BASE_URL = "http://127.0.0.1:8000"



def build_url(endpoint, path_params):
    """
    Replace path parameters with actual values.

    Example:
    /users/{user_id}
    +
    {"user_id": 1}

    becomes:
    /users/1
    """

    url = endpoint

    for name, value in path_params.items():

        url = url.replace(
            "{" + name + "}",
            str(value)
        )

    return url


def execute_test(test):
    """
    Execute one generated test case.
    """

    method = test["method"]
    endpoint = test["endpoint"]

    request_data = test["request"]

    path_params = request_data.get(
        "path_params",
        {}
    )

    query_params = request_data.get(
        "query_params",
        {}
    )

    headers = request_data.get(
        "headers",
        {}
    )

    body = request_data.get(
        "body"
    )

    # Build URL
    url = build_url(
        endpoint,
        path_params
    )

    full_url = BASE_URL + url

    print("\n" + "=" * 70)

    print(
        f"Executing {test['test_id']}"
    )

    print(
        f"Request: {method} {full_url}"
    )

    # Handle Unicode characters in body for printing
    if body:
        try:
            body_str = json.dumps(body, ensure_ascii=True)
        except:
            body_str = repr(body)
    else:
        body_str = "None"
    
    print(
        f"Body: {body_str}"
    )

    try:

        response = requests.request(
            method=method,
            url=full_url,
            params=query_params,
            headers=headers,
            json=body
        )

        print(
            f"Actual status: "
            f"{response.status_code}"
        )

        try:

            response_body = response.json()

        except ValueError:

            response_body = response.text

        try:
            response_body_str = str(response_body).encode("ascii", errors="replace").decode("ascii")
        except Exception:
            response_body_str = repr(response_body)

        print(
            f"Response: "
            f"{response_body_str}"
        )

        return {
            "test_id": test["test_id"],
            "endpoint": endpoint,
            "method": method,
            "request": request_data,
            "expected": test["expected"],
            "actual": {
                "status_code": response.status_code,
                "body": response_body
            }
        }

    except requests.RequestException as error:

        print(
            f"Request failed: {error}"
        )

        return {
            "test_id": test["test_id"],
            "endpoint": endpoint,
            "method": method,
            "request": request_data,
            "expected": test["expected"],
            "actual": {
                "status_code": None,
                "body": None,
                "error": str(error)
            }
        }
        
def run_all_tests():
        # Reset target API data before every test run
    try:
        reset_response = requests.post(
            f"{BASE_URL}/reset"
        )

        if reset_response.status_code != 200:
            print("WARNING: Could not reset test data.")

    except requests.RequestException as e:
        print(f"WARNING: Could not reset test data: {e}")
    
    
    print("Generating test cases...\n")

    all_tests = generate_all_tests()

    print(f"Rule-based tests: {len(all_tests)}")

    # Generate AI tests — reuse the same OpenAPI endpoint data
    # (generate_all_tests already loaded it internally, so we load once more
    #  here only for the AI generator; the DEBUG prints are now removed from parser)
    openapi_data = load_openapi(
        "http://127.0.0.1:8000/openapi.json"
    )
    endpoints = extract_endpoints(openapi_data)

    ai_tests = []

    for endpoint in endpoints:

        # Currently generate AI tests only for POST /users
        if (
            endpoint["path"] == "/users"
            and endpoint["method"] == "POST"
        ):

            print("\n[DEBUG] Calling AI test generator...")
            print(f"[DEBUG] Endpoint: {endpoint['method']} {endpoint['path']}")

            generated_tests = generate_ai_tests(endpoint)
            
            print(
                f"[DEBUG] AI generator returned: "
                f"{len(generated_tests)} tests"
            )
            
            # Add expected response schema to AI tests
            expected_schema = get_expected_success_response(
                endpoint,
                openapi_data
            )
            print(
                "[DEBUG] Resolved expected response schema:",
                expected_schema
            )
            print(
                "[DEBUG] POST /users endpoint:",
                endpoint
            )

            print(
                "[DEBUG] Expected schema:",
                expected_schema
            )
            
            print(
                "[DEBUG] Expected schema for AI tests:",
                expected_schema
                )
            
            for test in generated_tests:
                test["expected"]["response_schema"] = expected_schema
                
                print(
                    "[DEBUG] AI TEST EXPECTED:",
                    test["expected"]
                    )
            
            ai_tests.extend(generated_tests)

    # Give AI tests unique IDs
    for index, test in enumerate(ai_tests, start=1):
        test["test_id"] = f"AI-TC-{index}"

    print(f"AI-generated tests: {len(ai_tests)}")

    # Combine rule-based + AI tests
    all_tests.extend(ai_tests)

    print(
        f"Total tests: {len(all_tests)}"
    )

    results = []

    for test in all_tests:

        result = execute_test(test)
        

        validated_result = validate_response(
            result)

        results.append(
            validated_result
        )

    print("\n")
    print("=" * 70)
    print("TEST EXECUTION SUMMARY")
    print("=" * 70)

    passed = 0
    failed = 0
    bug_counter = 0

    for result in results:

        print(
            f"{result['test_id']} "
            f"{result['status']}"
        )

        if result["status"] == "PASS":

            passed += 1

        else:

            failed += 1

            print(
                f"Failure Reason: "
                f"{result['failure_reason']}"
            )

            # Analyze failed test using AI
            analysis = analyze_failure(
                result
            )

            result["ai_analysis"] = analysis
            
            bug_counter += 1
            bug_report = generate_bug_report(result, bug_counter=bug_counter)

            result["bug_report"] = bug_report
            
            print("\nBUG REPORT")
            print("-" * 50)

            for key, value in bug_report.items():
                print(f"{key}: {value}")

            print("\nAI FAILURE ANALYSIS")
            print("-" * 50)

            print(
                f"Summary: "
                f"{analysis['summary']}"
            )

            print(
                f"Possible Cause: "
                f"{analysis['possible_cause']}"
            )

            print(
                f"Severity: "
                f"{analysis['severity']}"
            )

            print(
                f"Recommendation: "
                f"{analysis['recommendation']}"
            )

    # Final summary
    print("\n")
    print("=" * 70)
    print("FINAL TEST EXECUTION SUMMARY")
    print("=" * 70)

    print(
        f"Total: {len(results)}"
    )

    print(
        f"Passed: {passed}"
    )

    print(
        f"Failed: {failed}"
    )
    
    # ==============================
    # SAVE TEST RUN TO DATABASE
    # ==============================
    
    pass_rate = round(
        (passed / len(results)) * 100,
        2
    ) if results else 0
    
    
    run_id = create_test_run(
        total_tests=len(results),
        passed_tests=passed,
        failed_tests=failed
    )
    
    print(
        f"Database Run ID: {run_id}"
    )
    
    
    # Save every test result
    for result in results:
        
        if result.get("test_id") == "TC-005":
            print("\n========== DEBUG DB RESULT ==========")
            print(json.dumps(result, indent=2, default=str))
            print("=====================================\n")
    
        save_test_result(
            run_id,
            result
        )
    
        if result.get("bug_report"):
            save_bug_report(
                run_id,
                result
            )
    
    
    print(
        "Test results saved to database successfully!"
    )
    
    
    return {
        "total": len(results),
        "passed": passed,
        "failed": failed,
        "pass_rate": pass_rate,
        "run_id": run_id,
        "results": results
    }
    
if __name__ == "__main__":
    run_all_tests()