import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Optional


logger = logging.getLogger(__name__)


class Listing:
    """Represents a vehicle listing from any source."""

    def __init__(
        self,
        listing_id: str,
        source: str,
        title: str,
        url: str,
        price: str,
        year: Optional[str] = None,
        mileage: Optional[str] = None,
        location: Optional[str] = None,
        image_url: Optional[str] = None,
        description: Optional[str] = None,
        category: Optional[str] = None,
        date_posted: Optional[str] = None,
        view_count: Optional[int] = None,
    ):
        self.listing_id = listing_id
        self.source = source
        self.title = title
        self.url = url
        self.price = price
        self.year = year
        self.mileage = mileage
        self.location = location
        self.image_url = image_url
        self.description = description
        self.category = category
        self.date_posted = date_posted
        self.view_count = view_count

    def __repr__(self):
        return f"<Listing {self.source}:{self.listing_id} - {self.title}>"


class BaseScraper(ABC):
    """Abstract base class for all scrapers."""

    def __init__(self, source_name: str):
        self.source_name = source_name
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    @abstractmethod
    def scrape(self, search_config: Dict) -> List[Listing]:
        """Scrape listings based on search configuration.

        Args:
            search_config: Dictionary containing search parameters

        Returns:
            List of Listing objects found
        """
        pass

    def _extract_id_from_url(self, url: str) -> Optional[str]:
        """Extract listing ID from URL.

        Args:
            url: Listing URL

        Returns:
            Extracted ID or None
        """
        return None
