
import os
from pathlib import Path

import pymysql
from dotenv import load_dotenv

# Find the project root and load its .env file
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def get_db_connection():
    required_variables = [
        "DB_HOST",
        "DB_USER",
        "DB_PASSWORD",
        "DB_NAME"
    ]

    missing_variables = [
        variable
        for variable in required_variables
        if not os.getenv(variable)
    ]

    if missing_variables:
        raise RuntimeError(
            "Missing database configuration: "
            + ", ".join(missing_variables)
        )

    try:
        connection = pymysql.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            port=int(os.getenv("DB_PORT", "3306")),
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor
        )

        return connection

    except pymysql.MySQLError as error:
        raise RuntimeError(
            f"Database connection failed: {error}"
        ) from error
