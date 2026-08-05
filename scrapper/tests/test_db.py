import os
import sys
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")


def main():
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL not found. Check your .env file in the project root.")
        sys.exit(1)

    print("Connecting to database...")
    conn = psycopg2.connect(database_url)
    conn.autocommit = True
    cur = conn.cursor()

    print("Creating temporary test table...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS _connection_test (
            id SERIAL PRIMARY KEY,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)

    cur.execute(
        "INSERT INTO _connection_test (message) VALUES (%s) RETURNING id",
        ("Hello from Bazos alert bot test script!",),
    )
    inserted_id = cur.fetchone()[0]
    print(f"Inserted import os
import sys
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")


def main():
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL not found. Check your .env file in the project root.")
        sys.exit(1)

    print("Connecting to database...")
    conn = psycopg2.connect(database_url)
    conn.autocommit = True
    cur = conn.cursor()

    print("Creating temporary test table...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS _connection_test (
            id SERIAL PRIMARY KEY,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)

    cur.execute(
        "INSERT INTO _connection_test (message) VALUES (%s) RETURNING id",
        ("Hello from Bazos alert bot test script!",),
    )
    inserted_id = cur.fetchone()[0]
    print(f"Inserted row with id={inserted_id}")

    cur.execute("SELECT id, message, created_at FROM _connection_test WHERE id = %s", (inserted_id,))
    row = cur.fetchone()
    print(f"Read back: id={row[0]}, message='{row[1]}', created_at={row[2]}")

    cur.execute("DROP TABLE _connection_test")

    cur.close()
    conn.close()
    print("\n✅ SUCCESS - database connection, write, and read all work.")


if __name__ == "__main__":
    main()row with id={inserted_id}")

    cur.execute("SELECT id, message, created_at FROM _connection_test WHERE id = %s", (inserted_id,))
    row = cur.fetchone()
    print(f"Read back: id={row[0]}, message='{row[1]}', created_at={row[2]}")

    cur.execute("DROP TABLE _connection_test")

    cur.close()
    conn.close()
    print("\n✅ SUCCESS - database connection, write, and read all work.")


if __name__ == "__main__":
    main()