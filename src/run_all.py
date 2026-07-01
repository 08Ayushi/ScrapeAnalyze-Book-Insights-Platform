"""
Convenience runner for the full project.

Default run:
    python src/run_all.py

Full run with Selenium also:
    python src/run_all.py --include-selenium
"""

import argparse
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def run_command(command: list[str]) -> None:
    print("\nRunning:", " ".join(command))
    subprocess.run(command, cwd=PROJECT_ROOT, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run scraping, analysis, and optional Selenium scraping")
    parser.add_argument("--pages", type=int, default=5, help="Number of book listing pages to scrape")
    parser.add_argument("--delay", type=float, default=0.2, help="Delay between requests")
    parser.add_argument("--include-selenium", action="store_true", help="Also run the Selenium JS scraper")
    args = parser.parse_args()

    python_executable = sys.executable

    run_command([
        python_executable,
        "src/scrape_books_bs4.py",
        "--pages",
        str(args.pages),
        "--delay",
        str(args.delay),
    ])

    run_command([python_executable, "src/analyze_and_ml.py"])

    if args.include_selenium:
        run_command([python_executable, "src/scrape_quotes_selenium.py", "--pages", "3"])

    print("\nProject pipeline completed.")
    print("Check the data/ and outputs/ folders.")


if __name__ == "__main__":
    main()
