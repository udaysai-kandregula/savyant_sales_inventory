from database.db import get_db_connection

try:
    connection = get_db_connection()

    print("SUCCESS: MySQL connected!")

    connection.close()
    print("Database connection closed.")

except Exception as error:
    print("ERROR: MySQL connection failed!")
    print(error)