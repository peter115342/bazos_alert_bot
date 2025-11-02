# Bazos Alert Bot

Automated web scraper for Bazos.sk/cz that monitors listings and sends Discord notifications for new matches.

## Features

- Scrapes Bazos.sk and Bazos.cz for listings
- Filters by search terms, price range, and location
- Sends Discord notifications for new listings
- Saves listing data in a SQLite database (further analysis possible)
- Prevents duplicate notifications using database tracking
- Supports scheduled runs via GitHub Actions or Docker

## Quick Start

### 1. Configuration

Create a `config.json` file in the project root based off the `config.example.json` provided. Example:

```json
{
  "database_path": "./data/listings.db",
  "searches": [
    {
      "name": "Fiat Panda",
      "source": "bazos_sk",
      "search_term": "Panda",
      "price_min": 2000,
      "price_max": 15000,
      "max_pages": 3,
    }
  ]
}
```

or like this (preferred, because it only goes through the category in the URL):

```json
{
  "database_path": "./data/listings.db",
  "searches": [
    {
      "name": "Macbook Air",
      "source": "bazos_sk",
      "url": "https://pc.bazos.sk/notebook/?hledat=MacBook+Air&rubriky=pc&hlokalita=81101&humkreis=45&cenaod=&cenado=&Submit=H%C4%BEada%C5%A5&order=&crp=&kitx=ano",
      "max_pages": 3
    }
  ]
}
```

#### Configuration Options

- `database_path`: Path to SQLite database file (default: `./data/listings.db`)
- `searches`: Array of search configurations

**Important:** The Discord webhook URL is not stored in `config.json`. It must be provided via the `DISCORD_WEBHOOK_URL` environment variable (see `.env.example`).

#### Search Configuration

- `name`: Descriptive name for this search
- `source`: `bazos_sk` or `bazos_cz`
- `url`: (optional - no need to use other search parameters with this) Full URL to a specific search
- `search_term`: What to search for (e.g., "Panda", "A4")
- `price_min`: Minimum price filter (optional)
- `price_max`: Maximum price filter (optional)
- `max_pages`: Maximum number of pages to scrape (default: 3)
- `location`: Location to filter results (optional)
- `radius`: Radius in kilometers to filter results (optional)

### 2. Discord Webhook Setup

1. Go to your Discord server settings
2. Create a channel
3. Navigate to channel Edit Channel > Integrations > Webhooks
4. Click "New Webhook"
5. Copy the webhook URL

## Deployment Options

### Option 1: GitHub Actions (Recommended)

**Setup:**

1. Fork this repository

2. Add your Discord webhook as a repository secret:

   - Go to Settings > Secrets and variables > Actions
   - Click "New repository secret"
   - Name: `DISCORD_WEBHOOK_URL`
   - Value: Your Discord webhook URL

3. Edit `config.json` with your search preferences (commit and push)

4. The workflow will run automatically at 8:00, 14:00, and 20:00 CET

5. You can also trigger it manually:
   - Go to Actions > Scheduled Bazos Scraper
   - Click "Run workflow"

**Notes:**

- **Database** is stored as a GitHub Actions artifact (only 90-day retention!)
- First run will notify all matching listings
- Subsequent runs only notify new listings

### Option 2: Docker

**Setup:**

1. Clone the repository:

```bash
git clone https://github.com/peter115342/auto_alert_bot.git
cd auto_alert_bot
```

2. Create a `.env` file:

````bash
echo "DISCORD_WEBHOOK_URL=your_webhook_url_here" > .env

```bash
DISCORD_WEBHOOK_URL=your_webhook_url_here
````

```bash
DISCORD_WEBHOOK_URL=your_webhook_url_here
```

3. Edit `config.json` with your search preferences

4. Build and run:

```bash
docker compose -f docker-compose.scheduled.yaml up -d
```

**Docker Configuration:**

The `docker-compose.scheduled.yaml` file runs the scraper at 8:00, 14:00, and 20:00 daily using cron.

To modify the schedule, edit line 20:

```yaml
echo "0 8,14,20 * * * cd /app && /root/.local/bin/uv run python -m src.main >> /app/data/cron.log 2>&1" > /etc/cron.d/bazos-scraper
```

Cron format: `minute hour day month weekday`

- `0 8,14,20 * * *` = 8:00, 14:00, 20:00 daily
- `0 */6 * * *` = Every 6 hours
- `*/30 * * * *` = Every 30 minutes

**Docker Commands:**

```bash
# Start the bot
docker compose -f docker-compose.scheduled.yaml up -d

# View logs
docker compose -f docker-compose.scheduled.yaml logs -f

# Stop the bot
docker compose -f docker-compose.scheduled.yaml down

# Rebuild after code changes
docker compose -f docker-compose.scheduled.yaml build --no-cache
docker compose -f docker-compose.scheduled.yaml up -d
```

**Database Location:**

The database is stored in `./data/listings.db` on your host machine and persists between container restarts.

## Database Schema

The SQLite database tracks listings with the following fields:

- `id`: Listing ID
- `source`: bazos_sk or bazos_cz
- `title`: Listing title
- `url`: Full URL to listing
- `price`: Price string
- `location`: Location with postal code
- `description`: First 200 characters
- `date_posted`: Date posted
- `view_count`: Number of views
- `first_seen`: When first discovered
- `last_checked`: Last time seen in scrape
- `notified`: Whether Discord notification was sent
