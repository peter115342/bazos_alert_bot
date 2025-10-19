import logging
import sys
from pathlib import Path

from .bot import AutoAlertBot


def setup_logging():
    """Configure logging for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("./data/bot.log", encoding="utf-8"),
        ],
    )

    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)


def main():
    """Main entry point for the bot."""
    import os

    Path("./data").mkdir(parents=True, exist_ok=True)

    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("=" * 50)
    logger.info("Auto Alert Bot Starting")
    logger.info("=" * 50)

    run_mode = os.environ.get("RUN_MODE", "continuous").lower()

    try:
        bot = AutoAlertBot(config_path="./config.json")

        if run_mode == "once":
            logger.info("Running in ONCE mode (scheduled task)")
            bot.run_once()
        else:
            logger.info("Running in CONTINUOUS mode")
            bot.run_forever()

    except FileNotFoundError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
