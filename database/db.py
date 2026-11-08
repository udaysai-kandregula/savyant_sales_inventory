
import os
from pathlib import Path

import pymysql
from dotenv import load_dotenv

# Find the project root and load its .env file
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def get_db_connection():
    connection = pymysql.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        port=int(os.getenv("DB_PORT", "3306")),
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )

    return connection
