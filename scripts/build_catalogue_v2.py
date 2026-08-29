from pathlib import Path

import pandas as pd


# ---------------------------------------------------------
# PROJECT PATHS
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "demo_products.csv"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "products_v2.csv"
)


# ---------------------------------------------------------
# CATEGORY NORMALIZATION
# ---------------------------------------------------------

CATEGORY_NORMALIZATION = {
    "tops": "top",
    "top": "top",

    "shirts": "shirt",
    "shirt": "shirt",

    "tshirts": "tshirt",
    "tshirt": "tshirt",
    "t-shirts": "tshirt",
    "t-shirt": "tshirt",

    "kurtas": "kurta",
    "kurta": "kurta",

    "sweaters": "sweater",
    "sweater": "sweater",

    "dresses": "dress",
    "dress": "dress",

    "jackets": "jacket",
    "jacket": "jacket",
}


# ---------------------------------------------------------
# BUILD CATALOGUE
# ---------------------------------------------------------

def build_catalogue():

    # Check input file
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Input catalogue not found:\n{INPUT_PATH}"
        )

    # Load original catalogue
    df = pd.read_csv(INPUT_PATH)

    print("Original catalogue loaded.")
    print("Rows:", len(df))
    print("Original columns:", df.columns.tolist())

    # -----------------------------------------------------
    # Rename old columns
    # -----------------------------------------------------

    df = df.rename(
        columns={
            "listed_colour": "colour_raw"
        }
    )

    # -----------------------------------------------------
    # Validate required original columns
    # -----------------------------------------------------

    original_required_columns = [
        "product_id",
        "product_name",
        "category",
        "colour_raw",
        "price",
        "image_path",
    ]

    missing_columns = [
        column
        for column in original_required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing required columns: "
            + ", ".join(missing_columns)
        )

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
    # NORMALIZE CATEGORY
    # -----------------------------------------------------

    raw_category = (
        df["category"]
        .fillna("")
        .astype(str)
        .str.lower()
        .str.strip()
    )

    df["category"] = (
        raw_category
        .map(CATEGORY_NORMALIZATION)
        .fillna(raw_category)
    )

    # -----------------------------------------------------
    # NORMALIZE COLOUR
    # -----------------------------------------------------

    df["colour_raw"] = (
        df["colour_raw"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    df["colour_normalized"] = (
        df["colour_raw"]
        .str.lower()
        .str.strip()
        .replace(
            {
                "gray": "grey"
            }
        )
    )

    # -----------------------------------------------------
    # CLEAN PRICE
    # -----------------------------------------------------

    df["price"] = pd.to_numeric(
        df["price"],
        errors="coerce"
    )

    # Remove rows with invalid price
    df = df.dropna(
        subset=["price"]
    )

    # -----------------------------------------------------
    # ADD V2 STRUCTURED ATTRIBUTES
    # -----------------------------------------------------

    df["description"] = ""

    # Temporary internal brand value.
    # We can replace this when we enrich the real catalogue.
    df["brand"] = "VYRA"

    df["gender"] = ""
    df["subcategory"] = ""
    df["material"] = ""
    df["fit"] = ""
    df["pattern"] = ""
    df["sleeve"] = ""
    df["occasion"] = ""
    df["season"] = ""
    df["size"] = ""

    # Use nullable numeric type
    df["rating"] = pd.NA

    # -----------------------------------------------------
    # CLEAN IMAGE PATH
    # -----------------------------------------------------

    df["image_path"] = (
        df["image_path"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    # -----------------------------------------------------
    # REMOVE DUPLICATE PRODUCT IDS
    # -----------------------------------------------------

    df = df.drop_duplicates(
        subset=["product_id"],
        keep="first"
    )

    # -----------------------------------------------------
    # FINAL V2 COLUMN ORDER
    # -----------------------------------------------------

    required_columns = [
        "product_id",
        "product_name",
        "description",
        "brand",
        "gender",
        "category",
        "subcategory",
        "colour_raw",
        "colour_normalized",
        "price",
        "material",
        "fit",
        "pattern",
        "sleeve",
        "occasion",
        "season",
        "size",
        "rating",
        "image_path",
    ]

    df = df[required_columns]

    # -----------------------------------------------------
    # CREATE OUTPUT DIRECTORY
    # -----------------------------------------------------

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # -----------------------------------------------------
    # SAVE V2 CATALOGUE
    # -----------------------------------------------------

    df.to_csv(
        OUTPUT_PATH,
        index=False,
        encoding="utf-8"
    )

    # -----------------------------------------------------
    # SUMMARY
    # -----------------------------------------------------

    print("\nCatalogue V2 created successfully.")
    print("Output:", OUTPUT_PATH)
    print("Rows:", len(df))
    print("Columns:", len(df.columns))

    print("\nFinal columns:")
    for column in df.columns:
        print("-", column)

    print("\nNormalized categories:")
    print(
        sorted(
            df["category"]
            .dropna()
            .unique()
            .tolist()
        )
    )

    print("\nNormalized colours:")
    print(
        sorted(
            df["colour_normalized"]
            .dropna()
            .unique()
            .tolist()
        )
    )


# ---------------------------------------------------------
# RUN
# ---------------------------------------------------------

if __name__ == "__main__":
    build_catalogue()