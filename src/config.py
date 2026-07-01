from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "outputs"

RAW_BOOKS_CSV = DATA_DIR / "raw_books.csv"
CLEAN_BOOKS_CSV = DATA_DIR / "clean_books.csv"
SELENIUM_QUOTES_CSV = DATA_DIR / "selenium_quotes.csv"

BASE_URL = "https://books.toscrape.com/"
CATALOGUE_PAGE_URL = "https://books.toscrape.com/catalogue/page-{}.html"

RATING_MAP = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}
