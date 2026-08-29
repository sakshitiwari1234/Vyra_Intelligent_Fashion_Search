from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent

PRODUCTS_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "products_v2_enriched.csv"
)


CATEGORY_KEYWORDS = {
    "top": ["top", "tops"],
    "shirt": ["shirt", "shirts"],
    "tshirt": [
        "tshirt",
        "tshirts",
        "t-shirt",
        "t-shirts",
        "tee",
    ],
    "kurta": ["kurta", "kurtas"],
    "sweater": ["sweater", "sweaters"],
    "dress": ["dress", "dresses"],
    "jacket": ["jacket", "jackets"],
}


def infer_category_from_name(product_name: str):
    text = product_name.lower()

    # More specific categories first
    priority = [
        "tshirt",
        "shirt",
        "kurta",
        "sweater",
        "dress",
        "jacket",
        "top",
    ]

    for category in priority:
        for keyword in CATEGORY_KEYWORDS[category]:
            if keyword in text:
                return category

    return ""


def audit_catalogue():
    df = pd.read_csv(PRODUCTS_PATH)

    print("Catalogue rows:", len(df))

    df["category_from_name"] = (
        df["product_name"]
        .fillna("")
        .apply(infer_category_from_name)
    )

    mismatches = df[
        (df["category_from_name"] != "")
        &
        (df["category_from_name"] != df["category"])
    ].copy()

    print("\nCategory mismatches found:", len(mismatches))

    if not mismatches.empty:
        print(
            mismatches[
                [
                    "product_id",
                    "product_name",
                    "category",
                    "category_from_name",
                ]
            ].to_string(index=False)
        )

    output_path = (
        PROJECT_ROOT
        / "data"
        / "evaluation"
        / "category_mismatches.csv"
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    mismatches.to_csv(
        output_path,
        index=False,
    )

    print("\nAudit saved to:")
    print(output_path)


if __name__ == "__main__":
    audit_catalogue()