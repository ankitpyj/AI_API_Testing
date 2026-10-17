# AI API Testing Agent

An AI-assisted API testing tool that reads an OpenAPI specification,
generates test cases, executes requests against a target API, validates
responses, and presents test results with failure details.

> **Project status:** Prototype / ongoing development. AI-generated
> suggestions and failure explanations may be inaccurate, and support
> for API schemas or authentication may be limited.

## Problem

Testing APIs manually often involves repeatedly reading documentation,
preparing requests, trying invalid inputs, checking responses, and
recording failures. This project aims to automate parts of that
workflow.

## Key Features

-   **OpenAPI parsing:** Extracts API endpoints, HTTP methods,
    parameters, request-body details, and documented responses.
-   **Rule-based test generation:** Creates standard and negative test
    cases, such as missing required fields and invalid input types where
    supported.
-   **AI-assisted testing:** Can suggest additional test cases and help
    explain failures when the configured AI service is available.
-   **Automated execution:** Sends HTTP requests to a target API.
-   **Response validation:** Compares actual results with expected
    outcomes and marks tests as passed or failed.
-   **Failure reports:** Displays failure details, possible causes, and
    recommendations.
-   **Dashboard and history:** Provides a frontend for running tests and
    reviewing results. Persistent history depends on the configured
    database.

## Architecture

``` text
User
 |
 v
React + Vite Dashboard (default port 5173)
 |
 v
FastAPI Agent Backend (default port 5000)
 |
 v
OpenAPI Parser
 |
 v
Rule-based Test Generator + Optional AI Assistance
 |
 v
Test Executor ---------------> Target API (example: port 8000)
 |
 v
Response Validator
 |
 v
Results / Failure Analysis
 |
 v
Dashboard and (if configured) MySQL storage
```

The **agent backend** and the **target API** are different services. The
target API is the application being tested.

## Technology Stack

  -----------------------------------------------------------------------
  Component               Technology              Purpose
  ----------------------- ----------------------- -----------------------
  Frontend                React + Vite            Dashboard for running
                                                  tests and viewing
                                                  reports

  Backend                 Python + FastAPI        Coordinates the testing
                                                  workflow

  API description         OpenAPI / JSON          Describes endpoints,
                                                  parameters, request
                                                  bodies, and responses

  Test execution          Python Requests / HTTP  Sends requests to the
                          requests                target API

  Test generation         Rule-based Python logic Creates repeatable test
                                                  cases

  AI assistance           NVIDIA API via an       Optional test
                          OpenAI-compatible       suggestions and failure
                          client, if configured   explanations

  Database                MySQL, if configured    Stores test runs,
                                                  results, history, and
                                                  bug reports
  -----------------------------------------------------------------------

## Requirements

-   Python installed
-   Node.js and npm installed
-   A target API that the agent can reach over the network
-   MySQL, if persistent database features are enabled
-   An AI API key, if AI features are enabled

Check your versions:

``` powershell
python --version
node --version
npm --version
```

## Setup

The exact commands can vary depending on the folder names and
configuration in your local checkout. The examples below assume the
backend lives in `agent_backend`, the demo target API lives in
`target_api`, and the React frontend is in `frontend`.

### 1. Clone the repository

``` powershell
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd ai_api-testing_agent
```

Replace `<YOUR_GITHUB_REPOSITORY_URL>` with your repository URL.

### 2. Set up the Python environment

From the project root:

``` powershell
python -m venv agent_backend\venv
.\agent_backend\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

Install the dependencies using the requirements file that exists in your
checkout. For example, if it is inside `agent_backend`:

``` powershell
pip install -r agent_backend\requirements.txt
```

If your repository keeps `requirements.txt` at the root, use:

``` powershell
pip install -r requirements.txt
```

If Pydantic `EmailStr` is used by the target API and the dependency is
not already installed, install:

``` powershell
pip install email-validator
```

### 3. Configure environment variables

Create a local `.env` file using the variable names expected by your
backend configuration. Add your AI API key and database credentials only
if those integrations are enabled.

-   Do not commit `.env` or API keys to GitHub.
-   Keep a `.env.example` file containing placeholder values, not real
    secrets.
-   If MySQL is enabled, create the required database and configure the
    connection before starting the backend.

### 4. Start the target API

Open a new PowerShell terminal at the project root:

``` powershell
python -m uvicorn target_api.main:app --reload --port 8000
```

Check that the target API is running:

-   API root: `http://127.0.0.1:8000/`
-   Health endpoint: `http://127.0.0.1:8000/health`
-   OpenAPI specification: `http://127.0.0.1:8000/openapi.json`
-   Interactive API docs: `http://127.0.0.1:8000/docs`

These example URLs apply to the local demo target API; your endpoint
behavior may differ.

### 5. Start the agent backend

Open another terminal. Activate the environment and run the FastAPI
application using the actual module path in your repository. If the
agent entry point is `main.py` inside `agent_backend`, a typical command
is:

``` powershell
.\agent_backend\venv\Scripts\python.exe -m uvicorn main:app --reload --app-dir agent_backend --port 5000
```

If your backend entry point or module path is different, adjust this
command to match it.

### 6. Start the frontend

Open another terminal and move into the frontend directory:

``` powershell
cd frontend
npm install
npm run dev
```

Vite commonly serves the dashboard at `http://localhost:5173`. Confirm
the URL shown in your terminal. Ensure the frontend points to the
correct agent backend URL, commonly `http://127.0.0.1:5000`.

## How to Use

1.  Start the target API.
2.  Start the agent backend and frontend.
3.  Open the dashboard in your browser.
4.  Provide the target API base URL and its OpenAPI specification URL,
    if the dashboard asks for them.
5.  Generate or review the test cases.
6.  Run the tests against the target API.
7.  Inspect pass/fail status, expected and actual responses, and failure
    analysis.
8.  Review run history if persistent storage is configured.

Example local target values:

``` text
Target API URL: http://127.0.0.1:8000
OpenAPI URL:    http://127.0.0.1:8000/openapi.json
```

## Running Tests

Run the Python tests from the project root using the same virtual
environment as the backend:

``` powershell
.\agent_backend\venv\Scripts\python.exe -m pytest -v
```

If pytest is not installed in that environment, install it using your
project's dependency file or run `pip install pytest`.

## Important Notes and Limitations

-   The agent can only test target APIs that it can reach over the
    network.
-   A deployed agent generally cannot access a developer's `localhost`;
    use a reachable deployed API, run the agent in the same network, or
    configure a secure tunnel.
-   Only test APIs you own or have explicit permission to test.
-   AI output is advisory and can be incomplete or incorrect. Always
    inspect actual HTTP status codes and response bodies.
-   A failed test does not automatically prove that the target API
    contains a bug. Network, authentication, configuration, or incorrect
    expected outcomes can also cause failures.
-   A passing test only shows that the API behaved as expected for that
    test; it does not prove that the API is bug-free.
-   Authentication support, schema coverage, and AI availability may
    vary by implementation.

## Future Improvements

-   Improve AI response speed and timeout handling.
-   Expand OpenAPI schema and authentication support.
-   Improve expected-result derivation and response validation.
-   Make target API configuration easier.
-   Add more evaluation data for test accuracy, execution time, and
    failure-analysis quality.

## Contributing

Contributions and suggestions are welcome. For changes:

1.  Create a branch for your work.
2.  Make a focused change.
3.  Run the available tests.
4.  Document configuration or behavior changes.
5.  Open a pull request with a clear summary.

## License

No license is specified here. Add a `LICENSE` file before describing the
project as open source.
