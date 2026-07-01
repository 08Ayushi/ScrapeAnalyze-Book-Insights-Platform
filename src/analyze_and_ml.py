"""
Data cleaning, exploratory data analysis, and basic ML for scraped book data.

Input:  data/raw_books.csv
Output: data/clean_books.csv, chart PNG files, model_metrics.txt
"""

import re

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split

from config import CLEAN_BOOKS_CSV, OUTPUT_DIR, RAW_BOOKS_CSV


def extract_stock_count(value: str) -> int:
    """Extract stock count from text like 'In stock (22 available)'."""
    if not isinstance(value, str):
        return 0
    match = re.search(r"\((\d+) available\)", value)
    return int(match.group(1)) if match else 0


def clean_currency_column(series: pd.Series) -> pd.Series:
    """Convert values like '£51.77' into numeric values."""
    extracted = series.astype(str).str.extract(r"(\d+(?:\.\d+)?)", expand=False)
    return pd.to_numeric(extracted, errors="coerce")


def load_and_clean_data() -> pd.DataFrame:
    """Load raw CSV and return a cleaned dataframe."""
    if not RAW_BOOKS_CSV.exists():
        raise FileNotFoundError(
            f"{RAW_BOOKS_CSV} not found. Run: python src/scrape_books_bs4.py --pages 5"
        )

    df = pd.read_csv(RAW_BOOKS_CSV)

    # Basic cleanup
    df = df.drop_duplicates(subset=["title", "detail_url"]).copy()
    df["title"] = df["title"].astype(str).str.strip()
    df["category"] = df["category"].fillna("Unknown").astype(str).str.strip()
    df["availability"] = df["availability"].fillna("Unknown").astype(str).str.strip()

    # Numeric cleanup
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce").fillna(0).astype(int)
    df["number_of_reviews"] = pd.to_numeric(df["number_of_reviews"], errors="coerce").fillna(0).astype(int)

    for col in ["price_excl_tax", "price_incl_tax", "tax"]:
        if col in df.columns:
            df[col] = clean_currency_column(df[col])

    df["stock_count"] = df["availability_detail"].apply(extract_stock_count)
    df["availability_in_stock"] = df["availability"].str.contains("In stock", case=False, na=False).astype(int)
    df["price_category"] = np.where(df["price"] >= df["price"].median(), "High", "Low")

    # Keep only rows with valid important values
    df = df.dropna(subset=["price", "rating", "category"])

    CLEAN_BOOKS_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(CLEAN_BOOKS_CSV, index=False, encoding="utf-8")
    return df


def create_charts(df: pd.DataFrame) -> None:
    """Create exploratory analysis charts."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Chart 1: Price distribution
    plt.figure(figsize=(8, 5))
    plt.hist(df["price"], bins=20)
    plt.title("Book Price Distribution")
    plt.xlabel("Price (£)")
    plt.ylabel("Number of Books")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "price_distribution.png", dpi=150)
    plt.close()

    # Chart 2: Books by rating
    rating_counts = df["rating"].value_counts().sort_index()
    plt.figure(figsize=(8, 5))
    plt.bar(rating_counts.index.astype(str), rating_counts.values)
    plt.title("Number of Books by Rating")
    plt.xlabel("Rating")
    plt.ylabel("Number of Books")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "books_by_rating.png", dpi=150)
    plt.close()

    # Chart 3: Average price by top categories
    top_categories = df["category"].value_counts().head(10).index
    avg_price_by_category = (
        df[df["category"].isin(top_categories)]
        .groupby("category")["price"]
        .mean()
        .sort_values(ascending=False)
    )
    plt.figure(figsize=(10, 6))
    plt.bar(avg_price_by_category.index, avg_price_by_category.values)
    plt.title("Average Book Price by Top Categories")
    plt.xlabel("Category")
    plt.ylabel("Average Price (£)")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "avg_price_by_category_top10.png", dpi=150)
    plt.close()

    # Chart 4: Rating vs price scatter
    plt.figure(figsize=(8, 5))
    plt.scatter(df["rating"], df["price"], alpha=0.6)
    plt.title("Rating vs Price")
    plt.xlabel("Rating")
    plt.ylabel("Price (£)")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "rating_vs_price_scatter.png", dpi=150)
    plt.close()


def prepare_ml_features(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series, pd.Series]:
    """Prepare features for regression and classification."""
    features = df[["rating", "category", "availability_in_stock", "stock_count", "number_of_reviews"]].copy()
    X = pd.get_dummies(features, columns=["category"], drop_first=True)
    y_regression = df["price"]
    y_classification = df["price_category"]
    return X, y_regression, y_classification


def run_machine_learning(df: pd.DataFrame) -> str:
    """Run a regression model and a classification model."""
    X, y_regression, y_classification = prepare_ml_features(df)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_regression, test_size=0.2, random_state=42
    )

    regression_model = LinearRegression()
    regression_model.fit(X_train, y_train)
    y_pred = regression_model.predict(X_test)

    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    # Classification: predict whether a book is High or Low price.
    X_train_c, X_test_c, y_train_c, y_test_c = train_test_split(
        X, y_classification, test_size=0.2, random_state=42, stratify=y_classification
    )

    classifier = LogisticRegression(max_iter=1000)
    classifier.fit(X_train_c, y_train_c)
    y_pred_c = classifier.predict(X_test_c)

    accuracy = accuracy_score(y_test_c, y_pred_c)
    report = classification_report(y_test_c, y_pred_c, zero_division=0)

    metrics_text = f"""
Python Web Scraping & Data Analysis Project - ML Results
========================================================

Dataset rows after cleaning: {len(df)}
Features used: rating, category, availability_in_stock, stock_count, number_of_reviews

Regression Model
----------------
Algorithm: Linear Regression
Target: book price
Mean Absolute Error: {mae:.2f}
R2 Score: {r2:.2f}

Classification Model
--------------------
Algorithm: Logistic Regression
Target: price_category (High/Low)
Accuracy: {accuracy:.2f}

Classification Report:
{report}
""".strip()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    metrics_path = OUTPUT_DIR / "model_metrics.txt"
    metrics_path.write_text(metrics_text, encoding="utf-8")

    return metrics_text


def main() -> None:
    df = load_and_clean_data()
    create_charts(df)
    metrics = run_machine_learning(df)

    print("Data cleaning, EDA, and ML completed successfully.\n")
    print(f"Clean data saved at: {CLEAN_BOOKS_CSV}")
    print(f"Charts and metrics saved inside: {OUTPUT_DIR}")
    print("\n" + metrics)


if __name__ == "__main__":
    main()
