from pathlib import Path

import pandas as pd

from backend.services.query_parser import parse_query
from backend.services.filters import apply_hard_filters


PROJECT_ROOT = Path(__file__).resolve().parent


PRODUCTS_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "products_v2_enriched.csv"
)


print("Looking for catalogue at:")
print(PRODUCTS_PATH)

print("\nFile exists:", PRODUCTS_PATH.exists())


products = pd.read_csv(PRODUCTS_PATH)


queries = [
    "black shirt",
    "men black shirt",
    "women red top under 1000",
    "men printed shirt",
    "women checked top",
    "men striped tshirt",
]


for query in queries:

    intent = parse_query(query)

    results = apply_hard_filters(
        products,
        intent,
    )

    print("\n" + "=" * 70)

    print("QUERY:", query)

    print("\nINTENT:")
    print(intent)

    print("\nRESULT COUNT:", len(results))

    if not results.empty:

        columns_to_show = [
            "product_id",
            "product_name",
            "gender",
            "category",
            "colour_normalized",
            "pattern",
            "price",
        ]

        print(
            results[
                columns_to_show
            ].head(10)
        )

    else:
        print("No products matched.")