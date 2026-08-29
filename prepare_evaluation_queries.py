from pathlib import Path
import pandas as pd

from backend.services.semantic_search import SemanticSearchEngine
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
    / "evaluation_candidates.csv"
)


products = pd.read_csv(PRODUCTS_PATH)

queries = [
    # Simple
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

    # Semantic / broad
    "something red for women",
    "pink women's clothing",
    "striped clothing for men",
    "warm sweater",
    "something black for men",
    "red clothing for women",
]


print("Loading semantic model...")

semantic_engine = SemanticSearchEngine(products)

rows = []


for query in queries:

    intent = parse_query(query)

    attribute_results = apply_hard_filters(
        products,
        intent,
    ).head(10)

    semantic_results = semantic_engine.search(
        query,
        top_k=10,
    )

    attribute_ids = ";".join(
        str(x)
        for x in attribute_results["product_id"].tolist()
    )

    semantic_ids = ";".join(
        str(x)
        for x in semantic_results["product_id"].tolist()
    )

    rows.append(
        {
            "query": query,
            "attribute_candidate_ids": attribute_ids,
            "semantic_candidate_ids": semantic_ids,
            "relevant_product_ids": "",
        }
    )


output = pd.DataFrame(rows)

OUTPUT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True,
)

output.to_csv(
    OUTPUT_PATH,
    index=False,
)

print("\nEvaluation candidate file created:")
print(OUTPUT_PATH)

print("\nQueries:", len(output))