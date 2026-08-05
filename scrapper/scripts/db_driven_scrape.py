"""
Read active searches from the DB, scrape each one, and save new listings.

Usage (run from the scrapper/ project root):
    uv run python scripts/db_driven_scrape.py
"""

import psycopg2.extras
import sys
from pathlib import Path

from src.db.connect import get_connection
from src.scrapers import BazosScraper

# todo meanwhile, Add the project root (parent of scripts/) to Python's import path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

def fetch_active_searches(cur):
    """Return all active search rows from the DB."""
    cur.execute("SELECT * FROM searches WHERE active = true")
    return cur.fetchall()


def build_search_config(search):
    """Turn a DB search row into the config dict BazosScraper expects."""
    return {
        "source": search["source"],
        "url": search["url"],
        "search_term": search["search_term"],
        "price_min": search["price_min"],
        "price_max": search["price_max"],
        "location": search["location"],
        "max_pages": search["max_pages"] or 1,
    }


def scrape_search(search):
    """Run the scraper for a single search row. Returns a list of Listing objects."""
    config = build_search_config(search)
    scraper = BazosScraper(search["source"])
    return scraper.scrape(config)


def listing_exists(cur, listing):
    """Check whether this listing is already in the DB."""
    cur.execute(
        "SELECT 1 FROM listings WHERE id = %s AND source = %s",
        (listing.listing_id, listing.source),
    )
    return cur.fetchone() is not None


def touch_listing(cur, listing):
    """Update last_checked for a listing we've already seen."""
    cur.execute(
        "UPDATE listings SET last_checked = NOW() WHERE id = %s AND source = %s",
        (listing.listing_id, listing.source),
    )


def insert_listing(cur, listing, search_id):
    """Insert a brand new listing into the DB."""
    cur.execute(
        """
        INSERT INTO listings
        (id, source, search_id, title, url, price, image_url, description,
         location, category, date_posted, view_count)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            listing.listing_id,
            listing.source,
            search_id,
            listing.title,
            listing.url,
            listing.price,
            listing.image_url,
            listing.description,
            listing.location,
            listing.category,
            listing.date_posted,
            listing.view_count,
        ),
    )


def save_listing(cur, listing, search_id):
    """Save one listing: insert if new, otherwise just update last_checked.
    Returns True if it was a new listing, False if it already existed."""
    if listing_exists(cur, listing):
        touch_listing(cur, listing)
        return False
    else:
        insert_listing(cur, listing, search_id)
        return True


def process_search(cur, search):
    """Scrape one search and save all its listings. Returns (new_count, existing_count)."""
    print(f"\n--- Search '{search['name']}' (id={search['id']}) ---")

    try:
        listings = scrape_search(search)
    except Exception as e:
        print(f"  ERROR scraping: {e}")
        return 0, 0

    print(f"  Found {len(listings)} listing(s) on the page")

    new_count = 0
    existing_count = 0

    for listing in listings:
        is_new = save_listing(cur, listing, search["id"])
        if is_new:
            new_count += 1
            print(f"  NEW: {listing.title} - {listing.price}")
        else:
            existing_count += 1

    return new_count, existing_count


def main():
    conn = get_connection()
    conn.autocommit = True
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    print("Reading active searches from DB...")
    active_searches = fetch_active_searches(cur)
    print(f"Found {len(active_searches)} active search(es)")

    total_new = 0
    total_existing = 0

    for search in active_searches:
        new_count, existing_count = process_search(cur, search)
        total_new += new_count
        total_existing += existing_count

    cur.close()
    conn.close()

    print(f"\nDone. New listings: {total_new}, already existed: {total_existing}")


if __name__ == "__main__":
    main()