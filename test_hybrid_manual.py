from pathlib import Path

import pandas as pd

from backend.services.hybrid_search import (
    HybridSearchEngine,
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


print("Products loaded:", len(products))

print("\nLoading Hybrid VYRA engine...")


engine = HybridSearchEngine(
    products
)


print("Hybrid VYRA engine ready.")


queries = [
    "black shirt",
    "something red for women",
    "striped clothing for men",
    "printed men's shirt",
    "pink women's clothing",
    "red top under 1000",
]


for query in queries:

    print(
        "\n"
        + "=" * 70
    )

    print(
        "QUERY:",
        query
    )

    results = engine.search(
        query=query,
        top_k=5,
    )

    if results.empty:

        print(
            "No products matched "
            "all mandatory constraints."
        )

        continue

    print(
        results[
            [
                "product_id",
                "product_name",
                "category",
                "colour_normalized",
                "gender",
                "pattern",
                "price",
                "semantic_score",
            ]
        ].to_string(
            index=False
        )
    )