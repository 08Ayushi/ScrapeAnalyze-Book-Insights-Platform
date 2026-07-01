"""
Selenium scraper for JavaScript-rendered quotes.

This script opens https://quotes.toscrape.com/js/ in a real browser engine,
extracts visible quote data, and saves it into data/selenium_quotes.csv.
"""

import argparse
import time
from typing import Dict, List

import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from config import SELENIUM_QUOTES_CSV


def build_driver(headless: bool = True) -> webdriver.Chrome:
    """Create a Chrome WebDriver instance using Selenium Manager."""
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1200,900")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    return webdriver.Chrome(options=options)


def scrape_quotes(pages: int = 3, headless: bool = True) -> pd.DataFrame:
    """Scrape JavaScript-rendered quotes using Selenium."""
    driver = build_driver(headless=headless)
    all_quotes: List[Dict[str, str]] = []

    try:
        for page in range(1, pages + 1):
            url = f"https://quotes.toscrape.com/js/page/{page}/"
            print(f"Scraping JS page {page}/{pages}...")
            driver.get(url)
            time.sleep(2)

            quotes = driver.find_elements(By.CLASS_NAME, "quote")
            for quote in quotes:
                text = quote.find_element(By.CLASS_NAME, "text").text
                author = quote.find_element(By.CLASS_NAME, "author").text
                tags = [tag.text for tag in quote.find_elements(By.CLASS_NAME, "tag")]

                all_quotes.append(
                    {
                        "quote": text,
                        "author": author,
                        "tags": ", ".join(tags),
                    }
                )
    finally:
        driver.quit()

    return pd.DataFrame(all_quotes)


def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape JavaScript-rendered quotes using Selenium")
    parser.add_argument("--pages", type=int, default=3, help="Number of JS quote pages to scrape.")
    parser.add_argument("--show-browser", action="store_true", help="Open Chrome visibly instead of headless mode.")
    args = parser.parse_args()

    SELENIUM_QUOTES_CSV.parent.mkdir(parents=True, exist_ok=True)

    try:
        df = scrape_quotes(pages=args.pages, headless=not args.show_browser)
    except WebDriverException as error:
        print("\nSelenium could not start Chrome.")
        print("Make sure Google Chrome is installed, then run this script again.")
        print(f"Original error: {error}")
        return

    df.to_csv(SELENIUM_QUOTES_CSV, index=False, encoding="utf-8")

    print("\nSelenium scraping completed successfully.")
    print(f"Rows scraped: {len(df)}")
    print(f"Saved file: {SELENIUM_QUOTES_CSV}")


if __name__ == "__main__":
    main()
