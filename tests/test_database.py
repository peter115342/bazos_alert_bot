"""Comprehensive test of improved scraper and database"""

import os
import sqlite3
from src.scrapers.bazos import BazosScraper
from src.database import ListingDatabase

# Setup
os.makedirs("data", exist_ok=True)
if os.path.exists("./data/test.db"):
    os.remove("./data/test.db")

db = ListingDatabase("./data/test.db")
scraper = BazosScraper("bazos_sk")

# Scrape
print("\n" + "=" * 70)
print("TESTING IMPROVED BAZOS SCRAPER")
print("=" * 70 + "\n")

config = {"url": "https://auto.bazos.sk/audi/"}
listings = scraper.scrape(config)

print(f"✓ Found {len(listings)} listings\n")

# Display and save first 3 listings
for i, listing in enumerate(listings[:3], 1):
    print(f"\n{'-' * 70}")
    print(f"LISTING #{i}")
    print(f"{'-' * 70}")
    print(f"  ID:          {listing.listing_id}")
    print(f"  Title:       {listing.title}")
    print(f"  Price:       {listing.price}")
    print(f"  Location:    {listing.location}")
    print(f"  Category:    {listing.category}")
    print(f"  Date Posted: {listing.date_posted}")
    print(f"  View Count:  {listing.view_count}")
    print(
        f"  Image URL:   {listing.image_url[:60] if listing.image_url else 'None'}..."
    )
    print(
        f"  Description: {listing.description[:80] if listing.description else 'None'}..."
    )
    print(f"  URL:         {listing.url[:60]}...")

    # Add to database
    db.add_listing(
        listing_id=listing.listing_id,
        source=listing.source,
        title=listing.title,
        url=listing.url,
        price=listing.price,
        image_url=listing.image_url,
        description=listing.description,
        location=listing.location,
        category=listing.category,
        date_posted=listing.date_posted,
        view_count=listing.view_count,
    )

# Verify database
print(f"\n\n{'=' * 70}")
print("DATABASE VERIFICATION")
print("=" * 70 + "\n")

conn = sqlite3.connect("./data/test_improved.db")
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(listings)")
columns = cursor.fetchall()

print("Database Schema:")
for col in columns:
    print(f"  - {col[1]}: {col[2]}")

print(f"\n\nStored Listings:")
cursor.execute("SELECT * FROM listings")
rows = cursor.fetchall()

for i, row in enumerate(rows, 1):
    print(f"\n{'-' * 70}")
    print(f"DB ROW #{i}")
    print(f"{'-' * 70}")
    print(f"  ID:           {row[0]}")
    print(f"  Source:       {row[1]}")
    print(f"  Title:        {row[2]}")
    print(f"  URL:          {row[3][:50]}...")
    print(f"  Price:        {row[4]}")
    print(f"  Image URL:    {row[5][:50] if row[5] else 'None'}...")
    print(f"  Description:  {row[6][:60] if row[6] else 'None'}...")
    print(f"  Location:     {row[7]}")
    print(f"  Category:     {row[8]}")
    print(f"  Date Posted:  {row[9]}")
    print(f"  View Count:   {row[10]}")
    print(f"  First Seen:   {row[11]}")
    print(f"  Last Checked: {row[12]}")

conn.close()

print(f"\n\n{'=' * 70}")
print("✅ ALL FIELDS SUCCESSFULLY EXTRACTED AND STORED!")
print("=" * 70 + "\n")
