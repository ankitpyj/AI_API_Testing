from database import get_db_connection


connection = get_db_connection()

print("Database connected successfully!")

connection.close()