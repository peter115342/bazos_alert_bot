"""
Test script for Bazos scraper
"""

import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.scrapers.bazos import BazosScraper


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def test_bazos_scraper():
    """Test the Bazos scraper with a sample search."""
    print("\n" + "=" * 60)
    print("Testing Bazos Scraper")
    print("=" * 60 + "\n")

    # Initialize scraper
    scraper = BazosScraper("bazos_sk")

    # Test with a search URL
    search_config = {
        "name": "Test Audi A4",
        "url": "https://auto.bazos.sk/audi/?hledat=A4&rubriky=auto&hlokalita=&humkreis=25&cenaod=&cenado=20000&Submit=Hľadať&order=&crp=&kitx=ano",
    }

    print(f"Testing search: {search_config['name']}")
    print(f"URL: {search_config['url']}\n")

    # Scrape listings
    listings = scraper.scrape(search_config)

    print(f"\nFound {len(listings)} listings:\n")

    # Display first 5 listings
    for i, listing in enumerate(listings[:5], 1):
        print(f"{i}. {listing.title}")
        print(f"   ID: {listing.listing_id}")
        print(f"   Price: {listing.price}")
        print(f"   Location: {listing.location}")
        print(f"   URL: {listing.url}")
        if listing.image_url:
            print(f"   Image: {listing.image_url}")
        if listing.description:
            print(f"   Description: {listing.description[:80]}...")
        print()

    # Test with search parameters
    print("\n" + "-" * 60)
    print("Testing with search parameters")
    print("-" * 60 + "\n")

    search_config2 = {
        "name": "Test BMW",
        "search_term": "BMW",
        "category": "auto",
        "price_max": "15000",
    }

    print(f"Testing search: {search_config2['name']}")
    print(f"Search term: {search_config2['search_term']}")
    print(f"Max price: {search_config2['price_max']}\n")

    listings2 = scraper.scrape(search_config2)
    print(f"\nFound {len(listings2)} listings")

    if listings2:
        print("\nFirst listing:")
        listing = listings2[0]
        print(f"  Title: {listing.title}")
        print(f"  Price: {listing.price}")
        print(f"  URL: {listing.url}")

    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    setup_logging()
    test_bazos_scraper()
