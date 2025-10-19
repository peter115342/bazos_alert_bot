import json
import logging
from pathlib import Path
from typing import Dict, List, Optional


logger = logging.getLogger(__name__)


class Config:
    """Configuration handler for the bot."""

    def __init__(self, config_path: str = "./config.json"):
        self.config_path = Path(config_path)
        self.data = self._load_config()

    def _load_config(self) -> Dict:
        """Load configuration from JSON file."""
        if not self.config_path.exists():
            logger.error(f"Config file not found: {self.config_path}")
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                logger.info(f"Configuration loaded from {self.config_path}")
                return config
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file: {e}")
            raise

    @property
    def discord_webhook_url(self) -> Optional[str]:
        """Get Discord webhook URL from config or environment."""
        import os

        return self.data.get("discord_webhook_url") or os.environ.get(
            "DISCORD_WEBHOOK_URL"
        )

    @property
    def check_interval_minutes(self) -> int:
        """Get check interval in minutes."""
        return self.data.get("check_interval_minutes", 15)

    @property
    def searches(self) -> List[Dict]:
        """Get list of search configurations."""
        return self.data.get("searches", [])

    @property
    def database_path(self) -> str:
        """Get database path."""
        return self.data.get("database_path", "./data/listings.db")

    def get_searches_by_source(self, source: str) -> List[Dict]:
        """Get searches filtered by source.

        Args:
            source: Source name (e.g., 'bazos_sk', 'bazos_cz')

        Returns:
            List of search configurations for the specified source
        """
        return [s for s in self.searches if s.get("source") == source]
