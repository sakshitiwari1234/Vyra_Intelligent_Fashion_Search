from pathlib import Path

import pandas as pd

from backend.services.query_parser import parse_query
from backend.services.filters import apply_hard_filters
from backend.services.semantic_search import SemanticSearchEngine
from backend.services.hybrid_search import HybridSearchEngine


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


print("\nLoading semantic engine...")

semantic_engine = SemanticSearchEngine(
    products
)


print("Loading hybrid engine...")

hybrid_engine = HybridSearchEngine(
    products
)


print("Engines ready.")


queries = [
    "black shirt",
    "something red for women",
    "striped clothing for men",
    "printed men's shirt",
    "pink women's clothing",
    "red top under 1000",
]


def attribute_search(query):

    intent = parse_query(
        query
    )

    results = apply_hard_filters(
        products,
        intent,
    )

    return results.head(5)


for query in queries:

    print(
        "\n"
        + "=" * 90
    )

    print(
        "QUERY:",
        query
    )

    # -------------------------------------------------
    # ATTRIBUTE SEARCH
    # -------------------------------------------------

    attribute_results = (
        attribute_search(
            query
        )
    )

    print(
        "\n--- ATTRIBUTE SEARCH ---"
    )

    if attribute_results.empty:

        print("No results.")

    else:

        print(
            attribute_results[
                [
                    "product_id",
                    "product_name",
                    "category",
                    "colour_normalized",
                    "gender",
                ]
            ].to_string(
                index=False
            )
        )

    # -------------------------------------------------
    # SEMANTIC SEARCH
    # -------------------------------------------------

    semantic_results = (
        semantic_engine.search(
            query=query,
            top_k=5,
        )
    )

    print(
        "\n--- SEMANTIC SEARCH ---"
    )

    print(
        semantic_results[
            [
                "product_id",
                "product_name",
                "category",
                "colour_normalized",
                "gender",
                "semantic_score",
            ]
        ].to_string(
            index=False
        )
    )

    # -------------------------------------------------
    # HYBRID SEARCH
    # -------------------------------------------------

    hybrid_results = (
        hybrid_engine.search(
            query=query,
            top_k=5,
        )
    )

    print(
        "\n--- HYBRID VYRA ---"
    )

    if hybrid_results.empty:

        print(
            "No products satisfy "
            "all hard constraints."
        )

    else:

        print(
            hybrid_results[
                [
                    "product_id",
                    "product_name",
                    "category",
                    "colour_normalized",
                    "gender",
                    "semantic_score",
                    "soft_preference_score",
                    "attribute_completeness",
                    "hybrid_score",
                ]
            ].to_string(
                index=False
            )
        )