from pathlib import Path

import pandas as pd

from backend.services.semantic_search import (
    SemanticSearchEngine,
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

print(
    "\nLoading semantic model..."
)

engine = SemanticSearchEngine(
    products
)

print(
    "Semantic search engine ready."
)


queries = [
    "black shirt",
    "something red for women",
    "striped clothing for men",
    "printed men's shirt",
    "pink women's clothing",
    "warm sweater",
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
        query,
        top_k=5,
    )

    print(
        results[
            [
                "product_id",
                "product_name",
                "category",
                "colour_normalized",
                "gender",
                "pattern",
                "semantic_score",
            ]
        ].to_string(
            index=False
        )
    )