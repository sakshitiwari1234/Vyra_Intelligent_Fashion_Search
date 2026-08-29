import re

from backend.schemas.query_intent import QueryIntent


COLOUR_ALIASES = {
    "red": ["red", "crimson", "scarlet"],
    "black": ["black"],
    "blue": ["blue", "navy"],
    "white": ["white"],
    "green": ["green"],
    "yellow": ["yellow"],
    "orange": ["orange"],
    "purple": ["purple", "violet"],
    "pink": ["pink", "magenta"],
    "brown": ["brown"],
    "beige": ["beige"],
    "grey": ["grey", "gray"],
    "maroon": ["maroon"],
}


CATEGORY_ALIASES = {
    "top": ["top", "tops"],
    "shirt": ["shirt", "shirts"],
    "tshirt": ["tshirt", "tshirts", "t-shirt", "t-shirts", "tee", "tees"],
    "dress": ["dress", "dresses"],
    "jacket": ["jacket", "jackets"],
    "kurta": ["kurta", "kurtas"],
    "sweater": ["sweater", "sweaters"],
}


GENDER_ALIASES = {
    "men": ["men", "mens", "men's", "male"],
    "women": ["women", "womens", "women's", "female"],
    "unisex": ["unisex"],
}


MATERIAL_ALIASES = {
    "cotton": ["cotton"],
    "linen": ["linen"],
    "denim": ["denim"],
    "silk": ["silk"],
    "wool": ["wool", "woollen"],
    "polyester": ["polyester"],
    "satin": ["satin"],
}


FIT_ALIASES = {
    "slim": ["slim", "slim fit"],
    "regular": ["regular", "regular fit"],
    "oversized": ["oversized", "oversize"],
    "relaxed": ["relaxed", "relaxed fit"],
}


PATTERN_ALIASES = {
    "printed": ["printed", "print"],
    "checked": ["checked", "check", "checks"],
    "striped": ["striped", "stripe", "stripes"],
    "solid": ["solid", "plain"],
    "floral": ["floral", "flower", "flowers"],
}


OCCASION_ALIASES = {
    "casual": ["casual", "daily wear", "everyday"],
    "formal": ["formal", "office", "workwear"],
    "party": ["party", "partywear"],
    "wedding": ["wedding"],
    "dinner": ["dinner", "dinner date"],
    "college": ["college", "campus"],
}


SEASON_ALIASES = {
    "summer": ["summer"],
    "winter": ["winter"],
    "spring": ["spring"],
    "monsoon": ["monsoon", "rainy"],
}


STYLE_ALIASES = {
    "elegant": ["elegant", "classy", "sophisticated"],
    "minimal": ["minimal", "minimalist"],
    "streetwear": ["streetwear", "street style"],
    "sporty": ["sporty", "athletic"],
    "vintage": ["vintage", "retro"],
}


def normalize_query(query: str) -> str:
    query = query.lower().strip()
    query = re.sub(r"\s+", " ", query)
    return query


def find_alias(query: str, alias_map: dict):
    for canonical_value, aliases in alias_map.items():
        for alias in sorted(aliases, key=len, reverse=True):
            pattern = rf"\b{re.escape(alias)}\b"

            if re.search(pattern, query):
                return canonical_value

    return None


def find_colours(query: str) -> list[str]:
    colours = []

    for canonical_colour, aliases in COLOUR_ALIASES.items():
        for alias in aliases:
            pattern = rf"\b{re.escape(alias)}\b"

            if re.search(pattern, query):
                colours.append(canonical_colour)
                break

    return colours


def extract_price_range(query: str):
    min_price = None
    max_price = None

    range_patterns = [
        r"between\s*(?:₹|rs\.?\s*)?(\d+)\s*(?:and|to)\s*(?:₹|rs\.?\s*)?(\d+)",
        r"from\s*(?:₹|rs\.?\s*)?(\d+)\s*(?:to|-)\s*(?:₹|rs\.?\s*)?(\d+)",
    ]

    for pattern in range_patterns:
        match = re.search(pattern, query)

        if match:
            first = float(match.group(1))
            second = float(match.group(2))

            min_price = min(first, second)
            max_price = max(first, second)

            return min_price, max_price

    max_patterns = [
        r"(?:under|below|less than|up to|upto|within)\s*(?:₹|rs\.?\s*)?(\d+)",
        r"(?:₹|rs\.?\s*)?(\d+)\s*(?:or less|max|maximum)",
    ]

    for pattern in max_patterns:
        match = re.search(pattern, query)

        if match:
            max_price = float(match.group(1))
            break

    min_patterns = [
        r"(?:above|over|more than|at least|minimum|min)\s*(?:₹|rs\.?\s*)?(\d+)",
        r"(?:₹|rs\.?\s*)?(\d+)\s*(?:or more)",
    ]

    for pattern in min_patterns:
        match = re.search(pattern, query)

        if match:
            min_price = float(match.group(1))
            break

    return min_price, max_price


def parse_query(query: str) -> QueryIntent:
    normalized_query = normalize_query(query)

    intent = QueryIntent()

    intent.category = find_alias(
        normalized_query,
        CATEGORY_ALIASES,
    )

    intent.colours = find_colours(
        normalized_query
    )

    intent.gender = find_alias(
        normalized_query,
        GENDER_ALIASES,
    )

    intent.material = find_alias(
        normalized_query,
        MATERIAL_ALIASES,
    )

    intent.fit = find_alias(
        normalized_query,
        FIT_ALIASES,
    )

    intent.pattern = find_alias(
        normalized_query,
        PATTERN_ALIASES,
    )

    intent.occasion = find_alias(
        normalized_query,
        OCCASION_ALIASES,
    )

    intent.season = find_alias(
        normalized_query,
        SEASON_ALIASES,
    )

    style = find_alias(
        normalized_query,
        STYLE_ALIASES,
    )

    if style:
        intent.styles.append(style)

    intent.min_price, intent.max_price = extract_price_range(
        normalized_query
    )

    # -------------------------------------------------
    # HARD CONSTRAINTS
    # -------------------------------------------------

    if intent.category:
        intent.hard_constraints.append("category")

    if intent.colours:
        intent.hard_constraints.append("colours")

    if intent.min_price is not None:
        intent.hard_constraints.append("min_price")

    if intent.max_price is not None:
        intent.hard_constraints.append("max_price")

    if intent.gender:
        intent.hard_constraints.append("gender")

    if intent.material:
        intent.hard_constraints.append("material")

    if intent.fit:
        intent.hard_constraints.append("fit")

    if intent.pattern:
        intent.hard_constraints.append("pattern")

    # -------------------------------------------------
    # SOFT PREFERENCES
    # -------------------------------------------------

    if intent.occasion:
        intent.soft_preferences.append("occasion")

    if intent.season:
        intent.soft_preferences.append("season")

    if intent.styles:
        intent.soft_preferences.append("styles")

    return intent