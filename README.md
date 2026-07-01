# ScrapeAnalyze-Book-Insights-Platform

The project includes:

- Web scraping using **BeautifulSoup**
- JavaScript-rendered page scraping using **Selenium**
- Data cleaning using **Pandas** and **NumPy**
- CSV-based data storage
- Exploratory Data Analysis using **Matplotlib**
- Basic Machine Learning using **Scikit-Learn**

---

## Project Idea

The project scrapes book data from `books.toscrape.com`, cleans the dataset, creates charts, and applies basic ML models.

It also includes a separate Selenium scraper for `quotes.toscrape.com/js/` to show that you can handle JavaScript-rendered websites.

---

## Tech Stack

- Python
- BeautifulSoup
- Selenium
- Pandas
- NumPy
- CSV
- Matplotlib
- Scikit-Learn

---

## Folder Structure

```text
python_web_scraping_data_analysis_project/
│
├── data/
│   ├── sample_books.csv
│   ├── raw_books.csv              # generated after running scraper
│   ├── clean_books.csv            # generated after analysis
│   └── selenium_quotes.csv        # generated after Selenium script
│
├── outputs/
│   ├── price_distribution.png
│   ├── books_by_rating.png
│   ├── avg_price_by_category_top10.png
│   ├── rating_vs_price_scatter.png
│   └── model_metrics.txt
│
├── screenshots/
│
├── src/
│   ├── config.py
│   ├── scrape_books_bs4.py
│   ├── scrape_quotes_selenium.py
│   ├── analyze_and_ml.py
│   └── run_all.py
│
├── requirements.txt
├── .gitignore
├── PROJECT_EXPLANATION.md
└── README.md
```

---

## How to Run on Windows with Python 3.14.3

### 1. Open the project folder

Open Command Prompt or VS Code terminal inside this folder.

### 2. Check Python version

```bash
python --version
```

Or:

```bash
py --version
```

You should see something like:

```bash
Python 3.14.3
```

### 3. Create a virtual environment

```bash
py -3.14 -m venv .venv
```

If `py -3.14` does not work, use:

```bash
python -m venv .venv
```

### 4. Activate the virtual environment

```bash
.venv\Scripts\activate
```

After activation, your terminal should show `(.venv)`.

### 5. Upgrade pip

```bash
python -m pip install --upgrade pip setuptools wheel
```

### 6. Install required libraries

```bash
pip install -r requirements.txt
```

---

## Run the Project

### Option 1: Run everything except Selenium

This is the easiest command:

```bash
python src/run_all.py
```

This will:

1. Scrape book data using BeautifulSoup
2. Save raw data in `data/raw_books.csv`
3. Clean data and save `data/clean_books.csv`
4. Generate charts in `outputs/`
5. Run basic ML models
6. Save ML results in `outputs/model_metrics.txt`

---

### Option 2: Run with more data

By default, it scrapes 5 pages. To scrape the full site, run:

```bash
python src/run_all.py --pages 50
```

---

### Option 3: Run Selenium also

Make sure Google Chrome is installed first.

```bash
python src/run_all.py --include-selenium
```

Or run Selenium separately:

```bash
python src/scrape_quotes_selenium.py --pages 3
```

This creates:

```text
data/selenium_quotes.csv
```

---

## Run Scripts One by One

### Scrape book data

```bash
python src/scrape_books_bs4.py --pages 5
```

For full scraping:

```bash
python src/scrape_books_bs4.py --pages 50
```

### Clean data, create charts, and run ML

```bash
python src/analyze_and_ml.py
```

### Scrape JavaScript-rendered data with Selenium

```bash
python src/scrape_quotes_selenium.py --pages 3
```

---

## Outputs Generated

After running the project, check these folders:

### `data/`

- `raw_books.csv`
- `clean_books.csv`
- `selenium_quotes.csv`

### `outputs/`

- `price_distribution.png`
- `books_by_rating.png`
- `avg_price_by_category_top10.png`
- `rating_vs_price_scatter.png`
- `model_metrics.txt`

---

## Machine Learning Used

This project uses two beginner-level ML models:

### 1. Linear Regression

Used to predict book price using:

- Rating
- Category
- Availability
- Stock count
- Number of reviews

### 2. Logistic Regression

Used to classify books into:

- High price
- Low price
