def validate_response(result):
    """
    Validate the actual API response
    against the expected response.
    """

    expected = result["expected"]
    actual = result["actual"]

    expected_status = expected["status_code"]
    actual_status = actual["status_code"]

    # -------------------------
    # Status validation
    # -------------------------

    if actual_status == expected_status:
        status_result = "PASS"
        failure_reason = None
    else:
        status_result = "FAIL"
        failure_reason = (
            f"Expected HTTP status "
            f"{expected_status}, "
            f"but received "
            f"{actual_status}."
        )

    # -------------------------
    # Response schema validation
    # -------------------------

    expected_schema = expected.get(
        "response_schema"
    )

    actual_body = actual.get(
        "body"
    )

    if expected_schema is not None:

        if validate_schema(
            actual_body,
            expected_schema
        ):
            body_result = "PASS"
        else:
            body_result = "FAIL"
            failure_reason = (
                "Response body does not "
                "match the expected schema "
                "or expected values."
            )

    else:
        body_result = "SKIP"

    # -------------------------
    # Overall result
    # -------------------------

    if (
        status_result == "PASS"
        and body_result != "FAIL"
    ):
        overall_status = "PASS"
    else:
        overall_status = "FAIL"

    # -------------------------
    # Preserve original result
    # -------------------------

    result["status"] = overall_status
    result["failure_reason"] = failure_reason
    result["status_check"] = status_result
    result["body_check"] = body_result

    result["expected_status"] = expected_status
    result["actual_status"] = actual_status
    result["expected_schema"] = expected_schema
    result["actual_body"] = actual_body

    return result


def validate_schema(data, schema):
    """
    Validate response data against
    a simplified OpenAPI schema.
    """

    if not isinstance(data, dict):
        return False

    if schema.get("type") != "object":
        return True

    properties = schema.get(
        "properties",
        {}
    )

    required = schema.get(
        "required",
        []
    )

    # -------------------------
    # Check required fields
    # -------------------------

    for field in required:

        if field not in data:
            return False

    # -------------------------
    # Check field types
    # -------------------------

    for field_name, field_schema in properties.items():

        if field_name not in data:
            continue

        value = data[field_name]
        expected_type = field_schema.get("type")

        if expected_type == "string":

            if not isinstance(value, str):
                return False

        # Check expected example value
            if "example" in field_schema:

                if value != field_schema["example"]:
                    return False

        elif expected_type == "integer":

            if not isinstance(value, int):
                return False

        elif expected_type == "number":

            if not isinstance(value, (int, float)):
                return False

        elif expected_type == "boolean":

            if not isinstance(value, bool):
                return False

        elif expected_type == "object":

            if not isinstance(value, dict):
                return False

        elif expected_type == "array":

            if not isinstance(value, list):
                return False

    return True