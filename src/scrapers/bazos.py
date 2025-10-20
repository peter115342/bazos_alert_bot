import logging
import re
from typing import Dict, List, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from .base import BaseScraper, Listing


logger = logging.getLogger(__name__)


class BazosScraper(BaseScraper):
    """Scraper for Bazos.sk and Bazos.cz vehicle listings."""

    BASE_URLS = {
        "bazos_sk": "https://auto.bazos.sk",
        "bazos_cz": "https://auto.bazos.cz",
    }

    def __init__(self, source_name: str):
        super().__init__(source_name)
        self.base_url = self.BASE_URLS.get(source_name)
        if not self.base_url:
            raise ValueError(f"Unknown Bazos source: {source_name}")

        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "sk,cs;q=0.9,en;q=0.8",
            }
        )

    def scrape(self, search_config: Dict) -> List[Listing]:
        """Scrape Bazos listings based on search configuration.

        Args:
            search_config: Dictionary containing:
                - url: Full search URL (optional)
                - search_term: Search query (optional)
                - category: Category (default: auto)
                - price_max: Maximum price (optional)
                - price_min: Minimum price (optional)
                - max_pages: Maximum number of pages to scrape (default: 1)
                - order: Sort order (4 = by views ascending)

        Returns:
            List of Listing objects
        """
        url = search_config.get("url")

        if not url:
            url = self._build_search_url(search_config)

        if not url:
            self.logger.error("No URL or search parameters provided")
            return []

        max_pages = search_config.get("max_pages", 3)

        all_listings = []

        for page_num in range(max_pages):
            page_url = self._get_page_url(url, page_num)
            self.logger.info(f"Scraping page {page_num + 1}/{max_pages}: {page_url}")

            try:
                response = self.session.get(page_url, timeout=30)
                response.raise_for_status()
                response.encoding = "utf-8"

                soup = BeautifulSoup(response.text, "html.parser")
                listings = self._parse_listings(soup)

                if not listings:
                    self.logger.info(f"No more listings found on page {page_num + 1}")
                    break

                all_listings.extend(listings)
                self.logger.info(
                    f"Found {len(listings)} listings on page {page_num + 1}"
                )

            except requests.exceptions.RequestException as e:
                self.logger.error(f"Error fetching Bazos page {page_num + 1}: {e}")
                break
            except Exception as e:
                self.logger.error(
                    f"Error parsing Bazos page {page_num + 1}: {e}", exc_info=True
                )
                break

        self.logger.info(f"Total listings found: {len(all_listings)}")
        return all_listings

    def _build_search_url(self, search_config: Dict) -> Optional[str]:
        """Build search URL from configuration parameters.

        Args:
            search_config: Search configuration dictionary

        Returns:
            Constructed URL or None
        """
        from urllib.parse import quote

        search_term = search_config.get("search_term", "")
        price_min = search_config.get("price_min", "")
        price_max = search_config.get("price_max", "")
        location = search_config.get("location", "")
        radius = search_config.get("radius", "25")
        order = search_config.get("order", "")

        if not search_term:
            return None

        url = f"{self.base_url}/?hledat={quote(search_term)}"

        if price_min:
            url += f"&cenaod={price_min}"
        if price_max:
            url += f"&cenado={price_max}"
        if location:
            url += f"&hlokalita={quote(location)}"
        if radius:
            url += f"&humkreis={radius}"
        if order:
            url += f"&order={order}"

        url += "&rubriky=auto&kitx=ano"

        return url

    def _get_page_url(self, base_url: str, page_num: int) -> str:
        """Generate URL for a specific page.

        Bazos pagination: page 1 = base_url, page 2 = /20/, page 3 = /40/, etc.

        Args:
            base_url: The base search URL
            page_num: Page number (0-indexed)

        Returns:
            URL for the specific page
        """
        if page_num == 0:
            return base_url

        offset = page_num * 20

        if "/?" in base_url:
            parts = base_url.split("/?")
            return f"{parts[0]}/{offset}/?{parts[1]}"
        else:
            return base_url

    def _parse_listings(self, soup: BeautifulSoup) -> List[Listing]:
        """Parse listing items from search results page.

        Args:
            soup: BeautifulSoup object of the page

        Returns:
            List of Listing objects
        """
        listings = []

        listing_divs = soup.find_all("div", class_="inzeratynadpis")

        self.logger.debug(f"Found {len(listing_divs)} listing divs")

        for div in listing_divs:
            try:
                listing = self._parse_listing_item(div)
                if listing:
                    listings.append(listing)
            except Exception as e:
                self.logger.debug(f"Error parsing listing item: {e}")
                continue

        return listings

    def _parse_listing_item(self, div) -> Optional[Listing]:
        """Parse a single listing from a div element.

        Args:
            div: BeautifulSoup div element with class 'inzeratynadpis'

        Returns:
            Listing object or None
        """
        link_elem = div.find("a", href=re.compile(r"/inzerat/\d+/"))
        if not link_elem:
            return None

        relative_url = link_elem.get("href")
        if not relative_url:
            return None

        url = urljoin(self.base_url, relative_url)
        listing_id = self._extract_id_from_url(url)

        if not listing_id:
            return None

        title = "Unknown"
        title_elem = div.find("h2", class_="nadpis")
        if title_elem:
            title_link = title_elem.find("a")
            if title_link:
                title = title_link.get_text(strip=True)

        date_posted = None
        date_span = div.find("span", class_="velikost10")
        if date_span:
            date_text = date_span.get_text()
            date_match = re.search(r"\[(\d{1,2}\.\d{1,2}\.\s*\d{4})\]", date_text)
            if date_match:
                date_posted = date_match.group(1).strip()

        image_url = None
        img_elem = div.find("img", class_="obrazek")
        if img_elem and img_elem.get("src"):
            img_src = img_elem.get("src")
            if img_src and "no-image" not in img_src.lower():
                image_url = urljoin(self.base_url, img_src)

        description = None
        desc_elem = div.find("div", class_="popis")
        if desc_elem:
            raw_desc = desc_elem.get_text(" ", strip=True)
            description = raw_desc
            if len(description) > 200:
                description = description[:200].rstrip() + "..."

        price = "N/A"
        location = None
        view_count = None
        category = None

        current = div
        for _ in range(10):
            current = current.next_sibling
            if current is None:
                break

            if not hasattr(current, "get"):
                continue

            classes = current.get("class", [])

            if "inzeratycena" in classes:
                price_text = current.get_text(strip=True)
                if price_text and price_text != "N/A":
                    price = price_text

            elif "inzeratylok" in classes:
                loc_text = current.get_text(strip=True)
                location = loc_text.split("\n")[0].strip() if loc_text else None
            if location:
                match = re.match(r"^(.*?)(\d{3,5}\s?\d{2})$", location)
                if match:
                    name = match.group(1).strip().rstrip(",")
                    postal = match.group(2).strip()
                    location = f"{name}, {postal}"

            elif "inzeratyview" in classes:
                view_text = current.get_text(strip=True)
                view_match = re.search(r"(\d+)\s*x", view_text)
                if view_match:
                    view_match = re.search(r"(\d+)\s*x", view_text)
                    if view_match:
                        view_count = int(view_match.group(1))
                    if match:
                        name = match.group(1).strip()
                        postal = match.group(2).strip()
                        location = f"{name}, {postal}"
                    pass

        category_match = re.search(r"https?://([^.]+)\.bazos\.(sk|cz)", url)
        if category_match:
            category = category_match.group(1)

        return Listing(
            listing_id=listing_id,
            source=self.source_name,
            title=title,
            url=url,
            price=price,
            location=location,
            image_url=image_url,
            description=description,
            category=category,
            date_posted=date_posted,
            view_count=view_count,
        )

    def _extract_id_from_url(self, url: str) -> Optional[str]:
        """Extract listing ID from Bazos URL.

        Example: https://auto.bazos.sk/inzerat/184195972/fiat-500-14-16v-sport.php
        Returns: "184195972"

        Args:
            url: Full listing URL

        Returns:
            Listing ID as string or None
        """
        match = re.search(r"/inzerat/(\d+)/", url)
        if match:
            return match.group(1)
        return None
