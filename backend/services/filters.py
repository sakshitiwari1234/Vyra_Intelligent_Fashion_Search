import pandas as pd

from backend.schemas.query_intent import QueryIntent


def apply_hard_filters(
    products: pd.DataFrame,
    intent: QueryIntent,
) -> pd.DataFrame:

    filtered = products.copy()

    # -------------------------------------------------
    # CATEGORY
    # -------------------------------------------------

    if intent.category:
        filtered = filtered[
            filtered["category"]
            .fillna("")
            .astype(str)
            .str.lower()
            .str.strip()
            == intent.category.lower()
        ]

    # -------------------------------------------------
    # COLOUR
    # -------------------------------------------------

    if intent.colours:
        normalized_colours = [
            colour.lower().strip()
            for colour in intent.colours
        ]

        filtered = filtered[
            filtered["colour_normalized"]
            .fillna("")
            .astype(str)
            .str.lower()
            .str.strip()
            .isin(normalized_colours)
        ]

    # -------------------------------------------------
    # MINIMUM PRICE
    # -------------------------------------------------

    if intent.min_price is not None:
        filtered = filtered[
            pd.to_numeric(
                filtered["price"],
                errors="coerce",
            )
            >= intent.min_price
        ]

    # -------------------------------------------------
    # MAXIMUM PRICE
    # -------------------------------------------------

    if intent.max_price is not None:
        filtered = filtered[
            pd.to_numeric(
                filtered["price"],
                errors="coerce",
            )
            <= intent.max_price
        ]

    # -------------------------------------------------
    # GENDER
    # -------------------------------------------------

    if intent.gender:
        filtered = filtered[
            filtered["gender"]
            .fillna("")
            .astype(str)
            .str.lower()
            .str.strip()
            == intent.gender.lower()
        ]

    # -------------------------------------------------
    # MATERIAL
    # -------------------------------------------------

    if intent.material:
        filtered = filtered[
            filtered["material"]
            .fillna("")
            .astype(str)
            .str.lower()
            .str.strip()
            == intent.material.lower()
        ]

    # -------------------------------------------------
    # FIT
    # -------------------------------------------------

    if intent.fit:
        filtered = filtered[
            filtered["fit"]
            .fillna("")
            .astype(str)
            .str.lower()
            .str.strip()
            == intent.fit.lower()
        ]

    # -------------------------------------------------
    # PATTERN
    # -------------------------------------------------

    if intent.pattern:
        filtered = filtered[
            filtered["pattern"]
            .fillna("")
            .astype(str)
            .str.lower()
            .str.strip()
            == intent.pattern.lower()
        ]

    return filtered.reset_index(drop=True)