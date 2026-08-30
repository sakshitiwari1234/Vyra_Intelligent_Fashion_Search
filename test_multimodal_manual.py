from pathlib import Path

import pandas as pd

from backend.services.query_parser import parse_query
from backend.services.filters import apply_hard_filters
from backend.services.semantic_search import SemanticSearchEngine
from backend.services.visual_search import VisualSearchEngine
from backend.services.multimodal_search import MultimodalSearchEngine


PROJECT_ROOT = Path(__file__).resolve().parent

PRODUCTS_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "products_v2_enriched.csv"
)


# --------------------------------------------------
# LOAD PRODUCTS
# --------------------------------------------------

products = pd.read_csv(PRODUCTS_PATH)

print(
    "Products loaded:",
    len(products),
)


# --------------------------------------------------
# INITIALIZE ENGINES
# --------------------------------------------------

print("\nLoading semantic engine...")

semantic_engine = SemanticSearchEngine(
    products
)


print("\nLoading visual engine...")

visual_engine = VisualSearchEngine(
    products=products,
    project_root=PROJECT_ROOT,
)


print("\nLoading multimodal engine...")

multimodal_engine = MultimodalSearchEngine(
    products=products,
    semantic_engine=semantic_engine,
    visual_engine=visual_engine,
)


# --------------------------------------------------
# TEST QUERY
# --------------------------------------------------

query = "red tshirt for men under 1000"


# Use a catalogue image as the reference image.
# Product 1617 is:
# Reebok Men Shoot T-Shirt Red

query_image_path = (
    PROJECT_ROOT
    / "images"
    / "1617.jpg"
)


intent = parse_query(
    query
)


print("\n" + "=" * 80)
print("MULTIMODAL QUERY")
print("=" * 80)

print(
    "Text query:",
    query,
)

print(
    "Reference image:",
    query_image_path,
)

print(
    "\nParsed intent:"
)

print(intent)


# --------------------------------------------------
# SEARCH
# --------------------------------------------------

results = multimodal_engine.search(
    query=query,
    query_image_path=query_image_path,
    intent=intent,
    hard_filter_function=apply_hard_filters,
    top_k=5,
)


# --------------------------------------------------
# RESULTS
# --------------------------------------------------

print("\n" + "=" * 80)
print("MULTIMODAL SEARCH RESULTS")
print("=" * 80)


if results.empty:

    print(
        "No products satisfied "
        "the hard constraints."
    )

else:

    columns = [
        "product_id",
        "product_name",
        "gender",
        "category",
        "colour_normalized",
        "price",
        "semantic_score",
        "visual_score",
        "soft_score",
        "multimodal_score",
    ]

    available_columns = [
        column
        for column in columns
        if column in results.columns
    ]

    print(
        results[
            available_columns
        ].to_string(
            index=False
        )
    )