from pathlib import Path

import pandas as pd

from backend.services.visual_search import (
    VisualSearchEngine,
)


PROJECT_ROOT = Path(__file__).resolve().parent

PRODUCTS_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "products_v2_enriched.csv"
)


products = pd.read_csv(
    PRODUCTS_PATH
)


print(
    "Products loaded:",
    len(products)
)


engine = VisualSearchEngine(
    products=products,
    project_root=PROJECT_ROOT,
)


# Use one existing catalogue image
# as the first visual-search test.
query_product = products.iloc[0]

query_image_path = (
    PROJECT_ROOT
    / query_product["image_path"]
)


print(
    "\nQuery product:"
)

print(
    query_product["product_name"]
)

print(
    "\nQuery image:"
)

print(
    query_image_path
)


results = engine.search_by_image(
    query_image_path=query_image_path,
    top_k=5,
)


print(
    "\n"
    + "=" * 80
)

print(
    "VISUAL SEARCH RESULTS"
)

print(
    "=" * 80
)


print(
    results[
        [
            "product_id",
            "product_name",
            "category",
            "colour_normalized",
            "gender",
            "visual_score",
        ]
    ].to_string(
        index=False
    )
)