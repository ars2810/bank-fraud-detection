
from src.database import create_table, get_connection


if __name__ == "__main__":
    connection = None

    try:
        connection = get_connection()
        print("MySQL connection successful!")
        connection.close()
        connection = None

        create_table()
        print("Transactions table is ready.")

    except Exception as exc:
        print(f"Database setup failed: {exc}")

    finally:
        if connection is not None and connection.is_connected():
            connection.close()
