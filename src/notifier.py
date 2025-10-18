import os
import json
import logging
from typing import Optional

import requests


logger = logging.getLogger(__name__)


class DiscordNotifier:
    def __init__(self, webhook_url: Optional[str] = None):
        self.webhook_url = webhook_url or os.environ.get("DISCORD_WEBHOOK_URL")
        if not self.webhook_url:
            logger.warning("Discord webhook URL not set.")

    def send_vehicle_notification(
        self,
        title: str,
        url: str,
        price: str,
        year: Optional[str] = None,
        mileage: Optional[str] = None,
        location: Optional[str] = None,
        image_url: Optional[str] = None,
        description: Optional[str] = None,
        color: int = 0x3498DB,
    ) -> bool:
        """
        Send a vehicle listing notification to Discord.

        Args:
            title: Vehicle title/name
            url: Link to the listing
            price: Vehicle price
            year: Year of manufacture
            mileage: Vehicle mileage
            location: Seller location
            image_url: URL to vehicle image
            description: Additional description
            color: Embed color (hex as int)

        Returns:
            True if notification sent successfully, False otherwise
        """
        if not self.webhook_url:
            logger.error("Cannot send notification: webhook URL not configured")
            return False

        fields = []

        if price:
            fields.append({"name": "💰 Price", "value": price, "inline": True})

        if year:
            fields.append({"name": "📅 Year", "value": year, "inline": True})

        if mileage:
            fields.append({"name": "🛣️ Mileage", "value": mileage, "inline": True})

        if location:
            fields.append({"name": "📍 Location", "value": location, "inline": True})

        embed = {
            "title": title,
            "url": url,
            "color": color,
            "fields": fields,
        }

        if description:
            embed["description"] = description

        if image_url:
            embed["thumbnail"] = {"url": image_url}

            embed["footer"] = {"text": "New Listing Alert"}
        embed["timestamp"] = self._get_timestamp()

        discord_data = {"embeds": [embed]}

        return self._send_webhook(discord_data)

    def send_notification(
        self, title: str, message: str, color: int = 0x3498DB
    ) -> bool:
        """
        Send a simple text notification to Discord.

        Args:
            title: Notification title
            message: Notification message
            color: Embed color (hex as int)

        Returns:
            True if notification sent successfully, False otherwise
        """
        if not self.webhook_url:
            logger.error("Cannot send notification: webhook URL not configured")
            return False

        discord_data = {
            "embeds": [
                {
                    "title": title,
                    "description": message,
                    "color": color,
                }
            ]
        }

        return self._send_webhook(discord_data)

    def _send_webhook(self, data: dict) -> bool:
        """
        Send data to Discord webhook.

        Args:
            data: Discord webhook payload

        Returns:
            True if successful, False otherwise
        """
        try:
            headers = {"Content-Type": "application/json"}
            response = requests.post(
                self.webhook_url, data=json.dumps(data), headers=headers, timeout=10
            )

            if response.status_code == 204:
                logger.info("Discord notification sent successfully")
                return True
            else:
                logger.error(
                    f"Failed to send Discord notification: {response.status_code}, {response.text}"
                )
                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending Discord notification: {e}")
            return False

    @staticmethod
    def _get_timestamp() -> str:
        from datetime import datetime

        return datetime.utcnow().isoformat()
