import json
import urllib.request


OPENAPI_URL = "http://127.0.0.1:8000/openapi.json"


HTTP_METHODS = {
    "get",
    "post",
    "put",
    "patch",
    "delete",
    "options",
    "head"
}


def load_openapi(url):
    """
    Fetch OpenAPI specification from the target API.
    """

    with urllib.request.urlopen(url) as response:
        data = response.read()

    return json.loads(data)


def resolve_schema(schema, openapi_data):
    """
    Resolve $ref, anyOf, and oneOf schemas.
    """

    # Handle $ref
    if "$ref" in schema:
        ref_name = schema["$ref"].split("/")[-1]

        schema = (
            openapi_data
            .get("components", {})
            .get("schemas", {})
            .get(ref_name, {})
        )

        return resolve_schema(schema, openapi_data)

    # Handle anyOf
    if "anyOf" in schema:
        for option in schema["anyOf"]:

            # Ignore null type
            if option.get("type") == "null":
                continue

            return resolve_schema(
                option,
                openapi_data
            )

    # Handle oneOf
    if "oneOf" in schema:
        for option in schema["oneOf"]:

            # Ignore null type
            if option.get("type") == "null":
                continue

            return resolve_schema(
                option,
                openapi_data
            )

    return schema


def extract_schema_details(schema, openapi_data):
    """
    Extract useful information from an OpenAPI schema.
    """

    # Resolve $ref / anyOf / oneOf
    schema = resolve_schema(
        schema,
        openapi_data
    )

    properties = schema.get(
        "properties",
        {}
    )

    required = schema.get(
        "required",
        []
    )

    fields = []

    for field_name, raw_field_data in properties.items():

        # Check whether field allows null
        nullable = False
    
        if "anyOf" in raw_field_data:
        
            for option in raw_field_data["anyOf"]:
            
                if option.get("type") == "null":
                    nullable = True
    
        field_data = resolve_schema(
            raw_field_data,
            openapi_data
        )
        
        # Create field information
        field = {
            "name": field_name,
            "type": field_data.get("type"),
            "format": field_data.get("format"),
            "required": field_name in required,
            "nullable": nullable
        }

        # Optional constraints
        if "minimum" in field_data:
            field["minimum"] = field_data["minimum"]

        if "maximum" in field_data:
            field["maximum"] = field_data["maximum"]

        if "minLength" in field_data:
            field["minLength"] = field_data["minLength"]

        if "maxLength" in field_data:
            field["maxLength"] = field_data["maxLength"]

        if "pattern" in field_data:
            field["pattern"] = field_data["pattern"]

        if "enum" in field_data:
            field["enum"] = field_data["enum"]

        fields.append(field)

    return fields


def extract_endpoints(openapi_data):

    endpoints = []

    paths = openapi_data.get("paths", {})

    for path, path_data in paths.items():

        for method, operation in path_data.items():

            if method.lower() not in HTTP_METHODS:
                continue

            endpoint = {
                "method": method.upper(),
                "path": path,
                "summary": operation.get("summary"),
                "description": operation.get("description"),
                "parameters": [],
                "request_body": None,
                "responses": []
            }

            # -------------------------
            # Parameters
            # -------------------------
            
            # Parameters can be defined at the
            # path level or operation level.
            
            path_parameters = path_data.get(
                "parameters",
                []
            )
            
            operation_parameters = operation.get(
                "parameters",
                []
            )
            
            all_parameters = (
                path_parameters +
                operation_parameters
            )
            
            for parameter in all_parameters:
            
                schema = parameter.get(
                    "schema",
                    {}
                )
            
                endpoint["parameters"].append({
                    "name": parameter.get("name"),
                    "location": parameter.get("in"),
                    "required": parameter.get(
                        "required",
                        False
                    ),
                    "type": schema.get("type"),
                    "format": schema.get("format")
                })
            
            # -------------------------
            # Request Body
            # -------------------------

            request_body = operation.get("requestBody")

            if request_body:

                content = request_body.get("content", {})

                json_content = content.get(
                    "application/json"
                )

                if json_content:

                    schema = json_content.get(
                        "schema",
                        {}
                    )

                    endpoint["request_body"] = {
                        "content_type": "application/json",
                        "required": request_body.get(
                            "required",
                            False
                        ),
                        "fields": extract_schema_details(
                            schema,
                            openapi_data
                        )
                    }

            # -------------------------
            # Responses
            # -------------------------

            for status_code, response_data in operation.get(
                "responses",
                {}
            ).items():
                
                endpoint["responses"].append({
                    "status_code": status_code,
                    "description": response_data.get("description"),
                    "content": response_data.get("content", {})
                })

            endpoints.append(endpoint)

    return endpoints


def print_endpoint_details(endpoint):

    print("\n" + "=" * 60)

    print(
        f"{endpoint['method']} {endpoint['path']}"
    )

    if endpoint["summary"]:
        print(
            f"Summary: {endpoint['summary']}"
        )

    # Parameters

    if endpoint["parameters"]:

        print("\nParameters:")

        for parameter in endpoint["parameters"]:

            print(
                f"  - {parameter['name']}"
                f" | location={parameter['location']}"
                f" | type={parameter['type']}"
                f" | required={parameter['required']}"
            )

    # Request body

    if endpoint["request_body"]:

        body = endpoint["request_body"]

        print("\nRequest Body:")

        for field in body["fields"]:

            print(
                f"  - {field['name']}"
                f" | type={field['type']}"
                f" | format={field['format']}"
                f" | required={field['required']}"
            )

    # Responses

    if endpoint["responses"]:

        print("\nExpected Responses:")

        for response in endpoint["responses"]:

            print(
                f"  - {response['status_code']}"
                f" → {response['description']}"
            )

if __name__ == "__main__":

    openapi_data = load_openapi(
        OPENAPI_URL
    )

    endpoints = extract_endpoints(
        openapi_data
    )

    for endpoint in endpoints:
        print_endpoint_details(endpoint)