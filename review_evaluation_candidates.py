from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent

PRODUCTS_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "products_v2_enriched.csv"
)

CANDIDATES_PATH = (
    PROJECT_ROOT
    / "data"
    / "evaluation"
    / "evaluation_candidates.csv"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "evaluation"
    / "evaluation_review.csv"
)


products = pd.read_csv(PRODUCTS_PATH)
candidates = pd.read_csv(CANDIDATES_PATH)


product_lookup = products.set_index(
    "product_id"
).to_dict("index")


def parse_ids(value):
    if pd.isna(value):
        return []

    return [
        int(x.strip())
        for x in str(value).split(";")
        if x.strip()
    ]


def describe_product(product_id):

    product = product_lookup.get(product_id)

    if product is None:
        return f"{product_id}: UNKNOWN PRODUCT"

    return (
        f"{product_id}: "
        f"{product.get('product_name', '')} | "
        f"category={product.get('category', '')} | "
        f"colour={product.get('colour_normalized', '')} | "
        f"gender={product.get('gender', '')} | "
        f"pattern={product.get('pattern', '')} | "
        f"price={product.get('price', '')}"
    )


review_rows = []


for _, row in candidates.iterrows():

    query = row["query"]

    attribute_ids = parse_ids(
        row["attribute_candidate_ids"]
    )

    semantic_ids = parse_ids(
        row["semantic_candidate_ids"]
    )

    # Combine and remove duplicates
    all_ids = list(
        dict.fromkeys(
            attribute_ids + semantic_ids
        )
    )

    candidate_descriptions = "\n".join(
        describe_product(product_id)
        for product_id in all_ids
    )

    review_rows.append(
        {
            "query": query,
            "candidate_products": candidate_descriptions,
            "relevant_product_ids": "",
        }
    )


review_df = pd.DataFrame(
    review_rows
)

review_df.to_csv(
    OUTPUT_PATH,
    index=False,
    encoding="utf-8",
)

print("Evaluation review file created:")
print(OUTPUT_PATH)

print("\nQueries:", len(review_df))