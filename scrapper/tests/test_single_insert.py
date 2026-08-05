import os
import sys
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
load_dotenv(PROJECT_ROOT / ".env")

from scrapers import BazosScraper  # noqa: E402


CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS listings (
    id TEXT NOT NULL,
    source TEXT NOT NULL,
    title TEXT,
    url TEXT,
    price TEXT,
    image_url TEXT,
    description TEXT,
    location TEXT,
    category TEXT,
    date_posted TEXT,
    view_count INTEGER,
    first_seen TIMESTAMP NOT NULL DEFAULT NOW(),
    last_checked TIMESTAMP NOT NULL DEFAULT NOW(),
    notified BOOLEAN NOT NULL DEFAULT FALSE,
    PRIMARY KEY (id, source)
)
"""


def main():
    search_config = {
        "source": "bazos_sk",
        "url": "https://auto.bazos.sk/?hledat=Panda&rubriky=auto&hlokalita=&humkreis=25&cenaod=2000&cenado=15000&Submit=H%C4%BEada%C5%A5&order=&crp=&kitx=ano",
        "max_pages": 1,
    }

    scraper = BazosScraper(search_config["source"])
    print("Scraping...")
    listings = scraper.scrape(search_config)

    if not listings:
        print("No listings found - nothing to insert.")
        return

    listing = listings[0]
    print(f"First listing: {listing.title} - {listing.price}")

    database_url = os.environ.get("DATABASE_URL")
    conn = psycopg2.connect(database_url)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(CREATE_TABLE_SQL)

    cur.execute(
        """
        INSERT INTO listings
        (id, source, title, url, price, image_url, description,
         location, category, date_posted, view_count)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLimport os
import sys
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
load_dotenv(PROJECT_ROOT / ".env")

from src.scrapers import BazosScraper  # noqa: E402


CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS listings (
    id TEXT NOT NULL,
    source TEXT NOT NULL,
    title TEXT,
    url TEXT,
    price TEXT,
    image_url TEXT,
    description TEXT,
    location TEXT,
    category TEXT,
    date_posted TEXT,
    view_count INTEGER,
    first_seen TIMESTAMP NOT NULL DEFAULT NOW(),
    last_checked TIMESTAMP NOT NULL DEFAULT NOW(),
    notified BOOLEAN NOT NULL DEFAULT FALSE,
    PRIMARY KEY (id, source)
)
"""


def main():
    search_config = {
        "source": "bazos_sk",
        "url": "https://auto.bazos.sk/?hledat=Panda&rubriky=auto&hlokalita=&humkreis=25&cenaod=2000&cenado=15000&Submit=H%C4%BEada%C5%A5&order=&crp=&kitx=ano",
        "max_pages": 1,
    }

    scraper = BazosScraper(search_config["source"])
    print("Scraping...")
    listings = scraper.scrape(search_config)

    if not listings:
        print("No listings found - nothing to insert.")
        return

    listing = listings[0]
    print(f"First listing: {listing.title} - {listing.price}")

    database_url = os.environ.get("DATABASE_URL")
    conn = psycopg2.connect(database_url)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(CREATE_TABLE_SQL)

    cur.execute(
        """
        INSERT INTO listings
        (id, source, title, url, price, image_url, description,
         location, category, date_posted, view_count)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id, source) DO NOTHING
        """,
        (
            listing.listing_id, listing.source, listing.title, listing.url,
            listing.price, listing.image_url, listing.description,
            listing.location, listing.category, listing.date_posted, listing.view_count,
        ),
    )

    cur.close()
    conn.close()
    print("Inserted (or already existed).")


if __name__ == "__main__":
    main()ICT (id, source) DO NOTHING
        """,
        (
            listing.listing_id, listing.source, listing.title, listing.url,
            listing.price, listing.image_url, listing.description,
            listing.location, listing.category, listing.date_posted, listing.view_count,
        ),
    )

    cur.close()
    conn.close()
    print("Inserted (or already existed).")


if __name__ == "__main__":
    main()