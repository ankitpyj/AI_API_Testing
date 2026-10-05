import sys
import os

# Allow Python to find the parser module
sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from parser.openapi_parser import (
    load_openapi,
    extract_endpoints,
    resolve_schema
)


OPENAPI_URL = "http://127.0.0.1:8000/openapi.json"


def get_expected_success_status(endpoint):
    """
    Find the first successful response status code.
    """

    for response in endpoint["responses"]:
        status_code = str(response["status_code"])

        if status_code.isdigit():
            code = int(status_code)

            if 200 <= code < 300:
                return code

    return 200

def generate_valid_value(field):
    """
    Generate a valid value based on field type/format.
    """

    field_type = field.get("type")
    field_format = field.get("format")

    if field_format == "email":
        return "test@example.com"

    if field_type == "string":
        return "Test User"

    if field_type == "integer":
        return 21

    if field_type == "number":
        return 10.5

    if field_type == "boolean":
        return True

    return None


def generate_valid_path_value(field):
    """
    Generate a valid value for a path parameter.
    """

    field_name = field.get("name")
    field_type = field.get("type")

    if field_name == "user_id":
        return 1

    if field_type == "integer":
        return 1

    if field_type == "number":
        return 1.0

    if field_type == "string":
        return "1"

    return generate_valid_value(field)


def generate_wrong_type(field):
    """
    Generate a value with an intentionally incorrect type.
    """

    field_type = field.get("type")

    if field_type == "string":
        return 12345

    if field_type == "integer":
        return "not-an-integer"

    if field_type == "number":
        return "not-a-number"

    if field_type == "boolean":
        return "not-a-boolean"

    return "invalid"


def get_expected_success_response(
    endpoint,
    openapi_data
):
    """
    Get the expected successful response
    schema from the OpenAPI specification.
    """

    for response in endpoint["responses"]:

        status_code = str(
            response["status_code"]
        )

        if status_code.isdigit():

            code = int(status_code)

            if 200 <= code < 300:

                content = response.get(
                    "content",
                    {}
                )

                json_content = content.get(
                    "application/json",
                    {}
                )

                schema = json_content.get(
                    "schema"
                )

                if schema:

                    resolved_schema = resolve_schema(
                        schema,
                        openapi_data
                    )

                    return resolved_schema

    return None

def get_expected_response_for_status(
    endpoint,
    openapi_data,
    expected_status
):
    """
    Get the expected response schema
    for a specific HTTP status code.
    """

    for response in endpoint["responses"]:

        status_code = str(
            response["status_code"]
        )

        if status_code != str(expected_status):
            continue

        content = response.get(
            "content",
            {}
        )

        json_content = content.get(
            "application/json",
            {}
        )

        schema = json_content.get(
            "schema"
        )

        if schema:
            return resolve_schema(
                schema,
                openapi_data
            )

    return None

def generate_path_params(endpoint):
    """
    Generate valid values for path parameters.
    """

    path_params = {}

    for parameter in endpoint.get("parameters", []):

        if parameter.get("location") == "path":

            path_params[parameter["name"]] = (
                generate_valid_path_value(parameter)
            )

    return path_params


def generate_query_params(endpoint):
    """
    Generate valid values for query parameters.
    """

    query_params = {}

    for parameter in endpoint.get("parameters", []):

        if parameter.get("location") == "query":

            query_params[parameter["name"]] = (
                generate_valid_value(parameter)
            )

    return query_params


def create_request(endpoint, body=None):
    """
    Create a standardized HTTP request structure.
    """

    return {
        "path_params": generate_path_params(endpoint),
        "query_params": generate_query_params(endpoint),
        "headers": {},
        "body": body
    }


def generate_tests_for_endpoint(endpoint,openapi_data):

    tests = []

    # Generate path parameters
    path_params = generate_path_params(endpoint)

    # Generate query parameters
    query_params = generate_query_params(endpoint)

    # ---------------------------------------
    # If endpoint has NO request body
    # ---------------------------------------

    if not endpoint["request_body"]:

        tests.append({
            "endpoint": endpoint["path"],
            "method": endpoint["method"],
            "category": "positive",
            "description": "Valid request",
            "request": {
                "path_params": path_params,
                "query_params": query_params,
                "headers": {},
                "body": None
            },
            "expected": {
                "status_code": get_expected_success_status(
                    endpoint
                ),
                "response_schema": get_expected_success_response(
                    endpoint,
                    openapi_data)}
        })

        return tests

    fields = endpoint["request_body"]["fields"]

    # ---------------------------------------
    # 1. Valid Test
    # ---------------------------------------

    valid_body = {}

    for field in fields:

        valid_body[field["name"]] = (
            generate_valid_value(field)
        )

    tests.append({
        "endpoint": endpoint["path"],
        "method": endpoint["method"],
        "category": "positive",
        "description": "Valid request",
        "request": create_request(
            endpoint,
            valid_body
        ),
        "expected": {
        "status_code": get_expected_success_status(
        endpoint
    ),
    "response_schema": get_expected_success_response(
        endpoint,
        openapi_data
    )
    }
        })

    # ---------------------------------------
    # 2. Missing Required Field
    # ---------------------------------------

    for field in fields:

        if not field["required"]:
            continue

        body = {}

        for current_field in fields:

            if current_field["name"] == field["name"]:
                continue

            body[current_field["name"]] = (
                generate_valid_value(current_field)
            )

        tests.append({
            "endpoint": endpoint["path"],
            "method": endpoint["method"],
            "category": "negative",
            "description": (
                f"Missing required field: "
                f"{field['name']}"
            ),
            "request": create_request(
                endpoint,
                body
            ),
            "expected": {
                "status_code": 422,
                "response_schema": get_expected_response_for_status(
                endpoint,
                openapi_data,
                422
                )
            }
            
        })

    # ---------------------------------------
    # 3. Invalid Format
    # ---------------------------------------

    for field in fields:

        if field.get("format") != "email":
            continue

        body = {}

        for current_field in fields:

            if current_field["name"] == field["name"]:

                body[current_field["name"]] = (
                    "invalid-email"
                )

            else:

                body[current_field["name"]] = (
                    generate_valid_value(
                        current_field
                    )
                )

        tests.append({
            "endpoint": endpoint["path"],
            "method": endpoint["method"],
            "category": "negative",
            "description": (
                f"Invalid {field['format']}"
            ),
            "request": create_request(
                endpoint,
                body
            ),
            "expected": {
                "status_code": 422,
                "response_schema": get_expected_response_for_status(
                endpoint,
                openapi_data,
                422
                )
            }
        })

    # ---------------------------------------
    # 4. Wrong Data Type
    # ---------------------------------------

    for field in fields:

        body = {}

        for current_field in fields:

            if current_field["name"] == field["name"]:

                body[current_field["name"]] = (
                    generate_wrong_type(field)
                )

            else:

                body[current_field["name"]] = (
                    generate_valid_value(
                        current_field
                    )
                )

        tests.append({
            "endpoint": endpoint["path"],
            "method": endpoint["method"],
            "category": "negative",
            "description": (
                f"Wrong data type for "
                f"{field['name']}"
            ),
            "request": create_request(
                endpoint,
                body
            ),
            "expected": {
                "status_code": 422,
                "response_schema": get_expected_response_for_status(
                endpoint,
                openapi_data,
                422
                )
            }
        })

    # ---------------------------------------
    # 5. Null Value
    # ---------------------------------------

    for field in fields:
    
        # Skip null test if the field allows null
        if field.get("nullable") is True:
            continue
        
        body = {}
    
        for current_field in fields:
        
            if current_field["name"] == field["name"]:
            
                body[current_field["name"]] = None
    
            else:
            
                body[current_field["name"]] = (
                    generate_valid_value(
                        current_field
                    )
                )
    
        tests.append({
            "endpoint": endpoint["path"],
            "method": endpoint["method"],
            "category": "negative",
            "description": (
                f"Null value for "
                f"{field['name']}"
            ),
            "request": create_request(
                endpoint,
                body
            ),
            "expected": {
                "status_code": 422,
                "response_schema": get_expected_response_for_status(
                endpoint,
                openapi_data,
                422
                )
            }
        })

    return tests


def main():

    print("Loading OpenAPI specification...\n")

    openapi_data = load_openapi(
        OPENAPI_URL
    )

    endpoints = extract_endpoints(
        openapi_data
    )

    all_tests = []

    # Generate tests for every endpoint
    for endpoint in endpoints:

        tests = generate_tests_for_endpoint(
            endpoint,
            openapi_data
        )

        all_tests.extend(tests)

    # ---------------------------------------
    # Assign GLOBAL test IDs
    # ---------------------------------------

    for index, test in enumerate(
        all_tests,
        start=1
    ):

        test["test_id"] = (
            f"TC-{index:03}"
        )

    print(
        f"Generated {len(all_tests)} tests\n"
    )

    print("=" * 70)

    for test in all_tests:

        print(
            f"\n{test['test_id']}"
        )

        print(
            f"Endpoint: "
            f"{test['method']} "
            f"{test['endpoint']}"
        )

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
            f"Expected status: "
            f"{test['expected']['status_code']}"
        )
        print(
            f"Expected response schema: "
            f"{test['expected'].get('response_schema')}"
        )


def generate_all_tests():
    """
    Load the OpenAPI specification
    and generate all test cases.
    """

    openapi_data = load_openapi(
        OPENAPI_URL
    )

    endpoints = extract_endpoints(
        openapi_data
    )

    all_tests = []

    for endpoint in endpoints:

        tests = generate_tests_for_endpoint(
            endpoint,
            openapi_data
        )

        all_tests.extend(tests)

    # Assign global test IDs
    for index, test in enumerate(
        all_tests,
        start=1
    ):

        test["test_id"] = (
            f"TC-{index:03}"
        )

    return all_tests


if __name__ == "__main__":
    main()
    
    
    
