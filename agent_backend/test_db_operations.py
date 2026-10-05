from db_operations import create_test_run


run_id = create_test_run(
    total_tests=34,
    passed_tests=33,
    failed_tests=1
)

print("Test run created successfully!")
print("Run ID:", run_id)