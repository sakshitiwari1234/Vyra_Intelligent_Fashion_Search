from pathlib import Path

import pandas as pd


# ---------------------------------------------------------
# PROJECT PATHS
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "products_v2.csv"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "products_v2_enriched.csv"
)


# ---------------------------------------------------------
# CATEGORY KEYWORDS
# ---------------------------------------------------------

CATEGORY_KEYWORDS = {
    "tshirt": [
        "tshirt",
        "tshirts",
        "t-shirt",
        "t-shirts",
        "tee",
        "tees",
    ],

    "shirt": [
        "shirt",
        "shirts",
    ],

    "kurta": [
        "kurta",
        "kurtas",
    ],

    "sweater": [
        "sweater",
        "sweaters",
    ],

    "dress": [
        "dress",
        "dresses",
    ],

    "jacket": [
        "jacket",
        "jackets",
    ],

    "top": [
        "top",
        "tops",
    ],
}


# ---------------------------------------------------------
# INFER CATEGORY
# ---------------------------------------------------------

def infer_category_from_name(name: str) -> str:

    text = str(name).lower()

    # Specific categories first
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


# ---------------------------------------------------------
# INFER GENDER
# ---------------------------------------------------------

def infer_gender(name: str) -> str:

    text = str(name).lower()

    if (
        "women" in text
        or "woman" in text
        or "girls" in text
        or "girl" in text
    ):
        return "women"

    if (
        "men" in text
        or "man" in text
        or "boys" in text
        or "boy" in text
    ):
        return "men"

    return ""


# ---------------------------------------------------------
# INFER PATTERN
# ---------------------------------------------------------

def infer_pattern(name: str) -> str:

    text = str(name).lower()

    patterns = {
        "printed": [
            "printed",
            "print",
        ],

        "checked": [
            "checked",
            "check",
            "checks",
        ],

        "striped": [
            "striped",
            "stripe",
            "stripes",
        ],

        "solid": [
            "solid",
            "plain",
        ],

        "floral": [
            "floral",
            "flower",
            "flowers",
        ],
    }

    for canonical, keywords in patterns.items():

        for keyword in keywords:

            if keyword in text:
                return canonical

    return ""


# ---------------------------------------------------------
# INFER SLEEVE
# ---------------------------------------------------------

def infer_sleeve(name: str) -> str:

    text = str(name).lower()

    if (
        "full sleeve" in text
        or "long sleeve" in text
        or "full sleeves" in text
        or "long sleeves" in text
    ):
        return "full sleeve"

    if (
        "half sleeve" in text
        or "short sleeve" in text
        or "half sleeves" in text
        or "short sleeves" in text
    ):
        return "short sleeve"

    if "sleeveless" in text:
        return "sleeveless"

    return ""


# ---------------------------------------------------------
# BUILD DESCRIPTION
# ---------------------------------------------------------

def build_description(row) -> str:

    parts = []

    product_name = str(
        row.get("product_name", "")
    ).strip()

    if product_name:
        parts.append(product_name)

    gender = str(
        row.get("gender", "")
    ).strip()

    if gender:
        parts.append(
            f"for {gender}"
        )

    category = str(
        row.get("category", "")
    ).strip()

    if category:
        parts.append(
            f"category {category}"
        )

    colour = str(
        row.get("colour_normalized", "")
    ).strip()

    if colour:
        parts.append(
            f"colour {colour}"
        )

    pattern = str(
        row.get("pattern", "")
    ).strip()

    if pattern:
        parts.append(
            f"{pattern} pattern"
        )

    sleeve = str(
        row.get("sleeve", "")
    ).strip()

    if sleeve:
        parts.append(
            sleeve
        )

    return ". ".join(parts)


# ---------------------------------------------------------
# ENRICH CATALOGUE
# ---------------------------------------------------------

def enrich_catalogue():

    # Check source file
    if not INPUT_PATH.exists():

        raise FileNotFoundError(
            f"Input catalogue not found:\n{INPUT_PATH}"
        )

    # Load catalogue
    df = pd.read_csv(INPUT_PATH)

    print("Catalogue loaded.")
    print("Rows:", len(df))

    # -----------------------------------------------------
    # CLEAN PRODUCT NAME
    # -----------------------------------------------------

    df["product_name"] = (
        df["product_name"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    # -----------------------------------------------------
    # CATEGORY CORRECTION
    # -----------------------------------------------------

    inferred_categories = (
        df["product_name"]
        .apply(infer_category_from_name)
    )

    category_correction_mask = (
        (inferred_categories != "")
        &
        (inferred_categories != df["category"])
    )

    corrected_count = int(
        category_correction_mask.sum()
    )

    # Replace incorrect categories
    df.loc[
        category_correction_mask,
        "category",
    ] = inferred_categories[
        category_correction_mask
    ]

    # -----------------------------------------------------
    # INFER GENDER
    # -----------------------------------------------------

    df["gender"] = (
        df["product_name"]
        .apply(infer_gender)
    )

    # -----------------------------------------------------
    # INFER PATTERN
    # -----------------------------------------------------

    df["pattern"] = (
        df["product_name"]
        .apply(infer_pattern)
    )

    # -----------------------------------------------------
    # INFER SLEEVE
    # -----------------------------------------------------

    df["sleeve"] = (
        df["product_name"]
        .apply(infer_sleeve)
    )

    # -----------------------------------------------------
    # KEEP UNSUPPORTED ATTRIBUTES CLEAN
    # -----------------------------------------------------

    columns_to_clean = [
        "material",
        "fit",
        "occasion",
        "season",
        "subcategory",
        "size",
    ]

    for column in columns_to_clean:

        if column in df.columns:

            df[column] = (
                df[column]
                .fillna("")
                .astype(str)
                .str.strip()
            )

    # -----------------------------------------------------
    # BUILD DESCRIPTION
    # -----------------------------------------------------

    df["description"] = (
        df.apply(
            build_description,
            axis=1,
        )
    )

    # -----------------------------------------------------
    # SAVE ENRICHED CATALOGUE
    # -----------------------------------------------------

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(
        OUTPUT_PATH,
        index=False,
        encoding="utf-8",
    )

    # -----------------------------------------------------
    # OUTPUT SUMMARY
    # -----------------------------------------------------

    print("\nCatalogue enrichment complete.")

    print(
        "\nOutput:",
        OUTPUT_PATH,
    )

    print(
        "\nCategory corrections:",
        corrected_count,
    )

    print(
        "\nFinal category counts:"
    )

    print(
        df["category"]
        .value_counts(
            dropna=False
        )
    )

    print(
        "\nGender counts:"
    )

    print(
        df["gender"]
        .value_counts(
            dropna=False
        )
    )

    print(
        "\nPattern counts:"
    )

    print(
        df["pattern"]
        .value_counts(
            dropna=False
        )
    )

    print(
        "\nSleeve counts:"
    )

    print(
        df["sleeve"]
        .value_counts(
            dropna=False
        )
    )


# ---------------------------------------------------------
# RUN
# ---------------------------------------------------------

if __name__ == "__main__":
    enrich_catalogue()