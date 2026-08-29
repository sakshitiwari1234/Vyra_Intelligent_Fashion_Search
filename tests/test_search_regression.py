from pathlib import Path

import pandas as pd

from backend.services.query_parser import parse_query
from backend.services.filters import apply_hard_filters


PROJECT_ROOT = Path(__file__).resolve().parent.parent

PRODUCTS_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "products_v2_enriched.csv"
)

products = pd.read_csv(PRODUCTS_PATH)


def run_query(query):
    intent = parse_query(query)
    return apply_hard_filters(products, intent)


def test_black_shirt():
    results = run_query("black shirt")

    assert len(results) == 1
    assert results.iloc[0]["product_id"] == 31660


def test_men_black_shirt():
    results = run_query("men black shirt")

    assert len(results) == 1
    assert results.iloc[0]["gender"] == "men"
    assert results.iloc[0]["category"] == "shirt"
    assert results.iloc[0]["colour_normalized"] == "black"


def test_women_red_top_under_1000():
    results = run_query(
        "women red top under 1000"
    )

    assert len(results) == 1

    product = results.iloc[0]

    assert product["gender"] == "women"
    assert product["category"] == "top"
    assert product["colour_normalized"] == "red"
    assert product["price"] <= 1000


def test_men_printed_shirt():
    results = run_query(
        "men printed shirt"
    )

    assert len(results) == 1

    product = results.iloc[0]

    assert product["gender"] == "men"
    assert product["category"] == "shirt"
    assert product["pattern"] == "printed"


def test_women_checked_top():
    results = run_query(
        "women checked top"
    )

    assert len(results) == 1

    product = results.iloc[0]

    assert product["gender"] == "women"
    assert product["category"] == "top"
    assert product["pattern"] == "checked"


def test_men_striped_tshirt():
    results = run_query(
        "men striped tshirt"
    )

    assert len(results) == 1

    product = results.iloc[0]

    assert product["gender"] == "men"
    assert product["category"] == "tshirt"
    assert product["pattern"] == "striped"