import json
import sys

from src.scrapers import BazosScraper


def listing_to_dict(listing):
    return listing.__dict__


def main():
    search_config = {
        "source": "bazos_sk",
        "url": "https://auto.bazos.sk/?hledat=Panda&rubriky=auto&hlokalita=&humkreis=25&cenaod=2000&cenado=15000&Submit=H%C4%BEada%C5%A5&order=&crp=&kitx=ano",
        "max_pages": 1,
    }

    source = search_config["source"]
    scraper = BazosScraper(source)

    print(f"Scraping {source} for '{search_config.get('search_term')}'...", file=sys.stderr)
    listings = scraper.scrape(search_config)

    results = [listing_to_dict(l) for l in listings]

    print(json.dumps(results, indent=2, ensure_ascii=False))
    print(f"\nTotal listings found: {len(results)}", file=sys.stderr)


if __name__ == "__main__":
    main()