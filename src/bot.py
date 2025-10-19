import logging
import time
from typing import List

from .config import Config
from .database import ListingDatabase
from .notifier import DiscordNotifier
from .scrapers import BazosScraper, Listing


logger = logging.getLogger(__name__)


class AutoAlertBot:
    def __init__(self, config_path: str = "./config.json"):
        self.config = Config(config_path)
        self.database = ListingDatabase(self.config.database_path)
        self.notifier = DiscordNotifier(self.config.discord_webhook_url)
        self.scrapers = {
            "bazos_sk": BazosScraper("bazos_sk"),
            "bazos_cz": BazosScraper("bazos_cz"),
        }
        logger.info("AutoAlertBot initialized")

    def process_listings(self, listings: List[Listing]):
        """Process scraped listings and send notifications for new ones.

        Args:
            listings: List of Listing objects to process
        """
        new_count = 0

        for listing in listings:
            if not self.database.is_listing_seen(listing.listing_id, listing.source):
                self.database.add_listing(
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
            else:
                self.database.update_last_checked(listing.listing_id, listing.source)

            if not self.database.is_listing_notified(
                listing.listing_id, listing.source
            ):
                self.notifier.send_vehicle_notification(
                    title=listing.title,
                    url=listing.url,
                    price=listing.price,
                    year=listing.year,
                    mileage=listing.mileage,
                    location=listing.location,
                    image_url=listing.image_url,
                    description=listing.description,
                    color=0xF16400,
                )
                self.database.mark_as_notified(listing.listing_id, listing.source)
                new_count += 1
                logger.info(f"New listing notified: {listing.title}")

        if new_count > 0:
            logger.info(f"Processed {len(listings)} listings, {new_count} were new")
        else:
            logger.debug(f"Processed {len(listings)} listings, no new ones found")

    def run_search_cycle(self):
        """Run one complete search cycle for all configured searches."""
        logger.info("Starting search cycle")

        for search_config in self.config.searches:
            source = search_config.get("source")
            if not source:
                logger.warning(f"Search config missing source: {search_config}")
                continue

            scraper = self.scrapers.get(source)
            if not scraper:
                logger.warning(f"No scraper available for source: {source}")
                continue

            try:
                logger.info(
                    f"Scraping {source} with query: {search_config.get('name', 'unnamed')}"
                )
                listings = scraper.scrape(search_config)
                self.process_listings(listings)

            except Exception as e:
                logger.error(f"Error scraping {source}: {e}", exc_info=True)
                self.notifier.send_notification(
                    title="⚠️ Scraping Error",
                    message=f"Error scraping {source}: {str(e)}",
                    color=0xFF0000,
                )

        logger.info("Search cycle completed")

    def run_once(self):
        """Run one search cycle and exit (for cron/scheduled tasks)."""
        logger.info("Bot starting in run-once mode")

        try:
            self.run_search_cycle()
            logger.info("Search cycle completed successfully")
        except Exception as e:
            logger.error(f"Error in search cycle: {e}", exc_info=True)
            self.notifier.send_notification(
                title="⚠️ Scraping Error",
                message=f"Error during scheduled run: {str(e)}",
                color=0xFF0000,
            )
            raise

    def run_forever(self):
        """Run the bot continuously with configured interval."""
        logger.info(
            f"Bot starting in continuous mode (interval: {self.config.check_interval_minutes} minutes)"
        )

        self.notifier.send_notification(
            title="🚀 Bot Started",
            message=f"Auto Alert Bot is now running. Checking every {self.config.check_interval_minutes} minutes.",
            color=0x00FF00,
        )

        while True:
            try:
                self.run_search_cycle()

                sleep_seconds = self.config.check_interval_minutes * 60
                logger.info(
                    f"Sleeping for {self.config.check_interval_minutes} minutes"
                )
                time.sleep(sleep_seconds)

            except KeyboardInterrupt:
                logger.info("Bot stopped by user")
                self.notifier.send_notification(
                    title="🛑 Bot Stopped",
                    message="Auto Alert Bot has been stopped.",
                    color=0xFF0000,
                )
                break

            except Exception as e:
                logger.error(f"Unexpected error in main loop: {e}", exc_info=True)
                self.notifier.send_notification(
                    title="⚠️ Bot Error",
                    message=f"Unexpected error: {str(e)}",
                    color=0xFF0000,
                )
                time.sleep(60)
