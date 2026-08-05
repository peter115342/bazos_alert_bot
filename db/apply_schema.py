import os
import sys
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / "scrapper" / ".env")


def main():
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL not found")
        sys.exit(1)

    schema_sql = (PROJECT_ROOT / "db" / "schema.sql").read_text(encoding="utf-8")

    conn = psycopg2.connect(database_url)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(schema_sql)

    cur.execute("""
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'public' ORDER BY table_name
    """)
    tables = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()

    print(f"✅ Schema applied. Tables: {tables}")


if __name__ == "__main__":
    main()