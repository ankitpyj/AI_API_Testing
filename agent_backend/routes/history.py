from flask import Blueprint, jsonify

from database import get_db_connection


history_bp = Blueprint(
    "history",
    __name__
)


# ==============================
# GET ALL TEST RUNS
# ==============================

@history_bp.route(
    "/test-runs",
    methods=["GET"]
)
def get_test_runs():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT
            id,
            started_at,
            total_tests,
            passed_tests,
            failed_tests
        FROM test_runs
        ORDER BY id DESC
    """

    cursor.execute(query)

    runs = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify(runs)


# ==============================
# GET TEST RESULTS
# ==============================

@history_bp.route(
    "/test-runs/<int:run_id>/results",
    methods=["GET"]
)
def get_test_results(run_id):

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT
            id,
            run_id,
            test_id,
            method,
            endpoint,
            category,
            status,
            expected_status,
            expected_body,
            actual_status,
            request_body,
            actual_body,
            failure_reason
        FROM test_results
        WHERE run_id = %s
        ORDER BY id
    """

    cursor.execute(
        query,
        (run_id,)
    )

    results = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify(results)


# ==============================
# GET BUG REPORTS
# ==============================

@history_bp.route(
    "/test-runs/<int:run_id>/bugs",
    methods=["GET"]
)
def get_bug_reports(run_id):

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT
            id,
            run_id,
            test_id,
            bug_id,
            endpoint,
            severity,
            summary,
            possible_cause,
            recommendation,
            status
        FROM bug_reports
        WHERE run_id = %s
        ORDER BY id
    """

    cursor.execute(
        query,
        (run_id,)
    )

    bugs = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify(bugs)