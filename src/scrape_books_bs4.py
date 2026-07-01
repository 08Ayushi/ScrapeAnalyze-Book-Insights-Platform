"""
BeautifulSoup scraper for Books to Scrape.

This script extracts structured book data and saves it into data/raw_books.csv.
Website used: https://books.toscrape.com/  (a practice website for scraping)
"""

import argparse
import re
import time
from typing import Dict, List
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup

from config import CATALOGUE_PAGE_URL, RAW_BOOKS_CSV, RATING_MAP

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
    )
}


def get_soup(url: str) -> BeautifulSoup:
    """Download a page and return a BeautifulSoup object."""
    response = requests.get(url, headers=HEADERS, timeout=20)
    response.raise_for_status()
    return BeautifulSoup(response.content, "lxml")


def clean_price(value: str) -> float:
    """Convert a price like '£51.77' into 51.77."""
    match = re.search(r"\d+(?:\.\d+)?", value)
    if not match:
        raise ValueError(f"Could not parse price from {value!r}")
    return float(match.group())


def parse_product_table(soup: BeautifulSoup) -> Dict[str, str]:
    """Extract the product information table from the details page."""
    table_data: Dict[str, str] = {}
    for row in soup.select("table.table.table-striped tr"):
        header = row.find("th")
        value = row.find("td")
        if header and value:
            key = header.get_text(strip=True).lower().replace(" ", "_")
            table_data[key] = value.get_text(strip=True)
    return table_data


def scrape_book_detail(detail_url: str) -> Dict[str, object]:
    """Scrape extra details from an individual book page."""
    soup = get_soup(detail_url)
    product_table = parse_product_table(soup)

    breadcrumb_items = soup.select("ul.breadcrumb li a")
    category = breadcrumb_items[2].get_text(strip=True) if len(breadcrumb_items) >= 3 else "Unknown"

    description_tag = soup.select_one("#product_description + p")
    description = description_tag.get_text(strip=True) if description_tag else ""

    return {
        "category": category,
        "description": description,
        "upc": product_table.get("upc", ""),
        "product_type": product_table.get("product_type", ""),
        "price_excl_tax": product_table.get("price_(excl._tax)", ""),
        "price_incl_tax": product_table.get("price_(incl._tax)", ""),
        "tax": product_table.get("tax", ""),
        "availability_detail": product_table.get("availability", ""),
        "number_of_reviews": product_table.get("number_of_reviews", "0"),
    }


def scrape_listing_page(page_number: int, delay: float) -> List[Dict[str, object]]:
    """Scrape all books from one listing page."""
    page_url = CATALOGUE_PAGE_URL.format(page_number)
    soup = get_soup(page_url)
    books = []

    articles = soup.select("article.product_pod")

    for article in articles:
        title_tag = article.select_one("h3 a")
        price_tag = article.select_one("p.price_color")
        rating_tag = article.select_one("p.star-rating")
        availability_tag = article.select_one("p.instock.availability")

        if not title_tag or not price_tag or not rating_tag:
            continue

        title = title_tag.get("title", "").strip()
        detail_url = urljoin(page_url, title_tag.get("href", ""))
        price = clean_price(price_tag.get_text(strip=True))
        rating_word = rating_tag.get("class", ["", "Zero"])[1]
        rating = RATING_MAP.get(rating_word, 0)
        availability = availability_tag.get_text(" ", strip=True) if availability_tag else "Unknown"

        detail_data = scrape_book_detail(detail_url)

        books.append(
            {
                "title": title,
                "price": price,
                "rating": rating,
                "availability": availability,
                "detail_url": detail_url,
                **detail_data,
            }
        )

        time.sleep(delay)

    return books


def scrape_books(total_pages: int, delay: float) -> pd.DataFrame:
    """Scrape multiple pages and return a dataframe."""
    all_books: List[Dict[str, object]] = []

    for page_number in range(1, total_pages + 1):
        print(f"Scraping page {page_number}/{total_pages}...")
        try:
            all_books.extend(scrape_listing_page(page_number, delay))
        except requests.HTTPError as error:
            print(f"Skipping page {page_number}: {error}")
        time.sleep(delay)

    return pd.DataFrame(all_books)


def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape book data using BeautifulSoup")
    parser.add_argument("--pages", type=int, default=5, help="Number of listing pages to scrape. Use 50 for full site.")
    parser.add_argument("--delay", type=float, default=0.2, help="Delay between requests in seconds.")
    args = parser.parse_args()

    RAW_BOOKS_CSV.parent.mkdir(parents=True, exist_ok=True)

    df = scrape_books(total_pages=args.pages, delay=args.delay)
    df.to_csv(RAW_BOOKS_CSV, index=False, encoding="utf-8")

    print("\nScraping completed successfully.")
    print(f"Rows scraped: {len(df)}")
    print(f"Saved file: {RAW_BOOKS_CSV}")


if __name__ == "__main__":
    main()
