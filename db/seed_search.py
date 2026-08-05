import os
import sys
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / "scrapper" / ".env")


def main():
    database_url = os.environ.get("DATABASE_URL")
    conn = psycopg2.connect(database_url)
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO searches (name, source, url, price_min, price_max, max_pages, active)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """,
        (
            "Fiat Panda", "bazos_sk",
            "https://auto.bazos.sk/?hledat=Panda&rubriky=auto&hlokalita=&humkreis=25&cenaod=2000&cenado=15000&Submit=H%C4%BEada%C5%A5&order=&crp=&kitx=ano",
            2000, 15000, 1, True,
        ),
    )
    new_id = cur.fetchone()[0]
    cur.close()
    conn.close()
    print(f"Inserted search with id={new_id}")


if __name__ == "__main__":
    main()