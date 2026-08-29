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

OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "evaluation"
    / "search_queries.csv"
)


products = pd.read_csv(PRODUCTS_PATH)


queries = [
    # Simple attribute queries
    "black shirt",
    "red kurta",
    "pink top",
    "white tshirt",
    "red sweater",
    "maroon tshirt",

    # Gender + category
    "men shirt",
    "women top",
    "men tshirt",
    "women tshirt",
    "men sweater",
    "women kurta",

    # Pattern
    "men striped shirt",
    "printed men's shirt",
    "women checked top",
    "solid men's sweater",
    "striped tshirt for men",
    "printed tshirt",

    # Multi-constraint
    "women red top under 1000",
    "men black shirt under 1000",
    "red kurta under 1000",
    "pink women top under 2000",
    "men striped tshirt under 1000",
    "women red tshirt under 1500",

    # Broad / semantic wording
    "something red for women",
    "pink women's clothing",
    "striped clothing for men",
    "warm sweater",
    "something black for men",
    "red clothing for women",
]


rows = []


for query in queries:

    intent = parse_query(query)

    # Apply VYRA's explicit hard-intent rules to the
    # ENTIRE catalogue, not only retrieved candidates.
    relevant_products = apply_hard_filters(
        products,
        intent,
    )

    relevant_ids = (
        relevant_products["product_id"]
        .astype(int)
        .tolist()
    )

    relevant_ids_string = ";".join(
        str(product_id)
        for product_id in relevant_ids
    )

    rows.append(
        {
            "query": query,
            "relevant_product_ids": relevant_ids_string,
        }
    )

    print("\nQUERY:", query)
    print("RELEVANT COUNT:", len(relevant_ids))
    print("IDS:", relevant_ids)


evaluation_df = pd.DataFrame(rows)


OUTPUT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True,
)


evaluation_df.to_csv(
    OUTPUT_PATH,
    index=False,
    encoding="utf-8",
)


print("\n" + "=" * 70)
print("GROUND-TRUTH EVALUATION SET CREATED")
print("=" * 70)

print("\nQueries:", len(evaluation_df))
print("Output:", OUTPUT_PATH)