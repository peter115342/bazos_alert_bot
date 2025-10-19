import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional
from contextlib import contextmanager


logger = logging.getLogger(__name__)


class ListingDatabase:
    def __init__(self, db_path: str = "./data/listings.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()

    def _init_database(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS listings (
                    id TEXT PRIMARY KEY,
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
                    first_seen TIMESTAMP NOT NULL,
                    last_checked TIMESTAMP NOT NULL
                )
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_source 
                ON listings(source)
            """)

            conn.commit()
            logger.info(f"Database initialized at {self.db_path}")

    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def is_listing_seen(self, listing_id: str, source: str = "mobile_de") -> bool:
        """
        Check if a listing has been seen before.

        Args:
            listing_id: Unique identifier for the listing
            source: Source platform (e.g., 'mobile_de')

        Returns:
            True if listing exists in database, False otherwise
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id FROM listings WHERE id = ? AND source = ?",
                (listing_id, source),
            )
            result = cursor.fetchone()
            return result is not None

    def add_listing(
        self,
        listing_id: str,
        source: str = "mobile_de",
        title: Optional[str] = None,
        url: Optional[str] = None,
        price: Optional[str] = None,
        image_url: Optional[str] = None,
        description: Optional[str] = None,
        location: Optional[str] = None,
        category: Optional[str] = None,
        date_posted: Optional[str] = None,
        view_count: Optional[int] = None,
    ) -> bool:
        """
        Add a new listing to the database.

        Args:
            listing_id: Unique identifier for the listing
            source: Source platform
            title: Vehicle title
            url: Listing URL
            price: Vehicle price
            image_url: URL to listing image
            description: Listing description
            location: Location of the listing
            category: Category of the listing
            date_posted: Date when listing was posted
            view_count: Number of views

        Returns:
            True if added successfully, False if already exists
        """
        if self.is_listing_seen(listing_id, source):
            logger.debug(f"Listing {listing_id} already exists in database")
            return False

        now = datetime.utcnow().isoformat()

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO listings 
                (id, source, title, url, price, image_url, description, location, 
                 category, date_posted, view_count, first_seen, last_checked)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    listing_id,
                    source,
                    title,
                    url,
                    price,
                    image_url,
                    description,
                    location,
                    category,
                    date_posted,
                    view_count,
                    now,
                    now,
                ),
            )
            conn.commit()
            logger.info(f"Added new listing {listing_id} from {source}")
            return True

    def update_last_checked(self, listing_id: str, source: str = "mobile_de"):
        """
        Update the last_checked timestamp for a listing.

        Args:
            listing_id: Unique identifier for the listing
            source: Source platform
        """
        now = datetime.utcnow().isoformat()

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE listings 
                SET last_checked = ?
                WHERE id = ? AND source = ?
            """,
                (now, listing_id, source),
            )
            conn.commit()

    def get_listing_count(self, source: Optional[str] = None) -> int:
        """
        Get the total number of listings in the database.

        Args:
            source: Optional source filter

        Returns:
            Number of listings
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if source:
                cursor.execute(
                    "SELECT COUNT(*) FROM listings WHERE source = ?", (source,)
                )
            else:
                cursor.execute("SELECT COUNT(*) FROM listings")

            result = cursor.fetchone()
            return result[0] if result else 0

    def cleanup_old_listings(self, days: int = 30, source: Optional[str] = None):
        """
        Remove listings older than specified days.

        Args:
            days: Age threshold in days
            source: Optional source filter
        """
        from datetime import timedelta

        cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()

        with self._get_connection() as conn:
            cursor = conn.cursor()
            if source:
                cursor.execute(
                    "DELETE FROM listings WHERE first_seen < ? AND source = ?",
                    (cutoff, source),
                )
            else:
                cursor.execute("DELETE FROM listings WHERE first_seen < ?", (cutoff,))
            deleted = cursor.rowcount
            conn.commit()
            logger.info(f"Cleaned up {deleted} old listings")
