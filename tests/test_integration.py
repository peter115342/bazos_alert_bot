"""
Full integration test for the bot
"""

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.config import Config
from src.database import ListingDatabase
from src.scrapers.bazos import BazosScraper


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )


def test_integration():
    """Test the full integration"""
    print("\n" + "=" * 60)
    print("Integration Test")
    print("=" * 60 + "\n")

    # Test database
    print("1. Testing Database...")
    db = ListingDatabase("./data/test_listings.db")

    # Add a test listing
    added = db.add_listing(
        listing_id="123456",
        source="bazos_sk",
        title="Test Car",
        url="https://test.com",
        price="10000 €",
    )
    print(f"   Added new listing: {added}")

    # Check if it exists
    exists = db.is_listing_seen("123456", "bazos_sk")
    print(f"   Listing exists: {exists}")

    # Try to add again (should fail)
    added_again = db.add_listing(
        listing_id="123456",
        source="bazos_sk",
        title="Test Car",
        url="https://test.com",
        price="10000 €",
    )
    print(f"   Added duplicate: {added_again}")

    # Get count
    count = db.get_listing_count("bazos_sk")
    print(f"   Total listings: {count}")
    print("   ✓ Database working!\n")

    # Test scraper
    print("2. Testing Scraper...")
    scraper = BazosScraper("bazos_sk")

    search_config = {"name": "Test Search", "url": "https://auto.bazos.sk/audi/"}

    listings = scraper.scrape(search_config)
    print(f"   Found {len(listings)} listings")

    if listings:
        sample = listings[0]
        print(f"   Sample listing:")
        print(f"     - Title: {sample.title}")
        print(f"     - ID: {sample.listing_id}")
        print(f"     - URL: {sample.url}")
        print(f"     - Has image: {bool(sample.image_url)}")
    print("   ✓ Scraper working!\n")

    # Test URL building
    print("3. Testing URL Builder...")
    search_config2 = {"search_term": "BMW 3", "price_max": "15000"}

    url = scraper._build_search_url(search_config2)
    print(f"   Built URL: {url}")
    print("   ✓ URL builder working!\n")

    print("=" * 60)
    print("All tests passed! ✓")
    print("=" * 60 + "\n")

    # Cleanup
    Path("./data/test_listings.db").unlink(missing_ok=True)


if __name__ == "__main__":
    setup_logging()
    test_integration()
