import mysql.connector


def get_db_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="ankit",
        database="ai_api_testing"
    )

    return connection