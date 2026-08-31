from pathlib import Path

import pandas as pd

from backend.services.semantic_search import (
    SemanticSearchEngine,
)
from backend.services.visual_search import (
    VisualSearchEngine,
)
from backend.services.multimodal_orchestrator import (
    MultimodalOrchestrator,
)


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

print(
    "Products loaded:",
    len(products),
)


print(
    "\nLoading semantic engine..."
)

semantic_engine = (
    SemanticSearchEngine(
        products
    )
)


print(
    "\nLoading visual engine..."
)

visual_engine = (
    VisualSearchEngine(
        products=products,
        project_root=PROJECT_ROOT,
    )
)


print(
    "\nLoading multimodal orchestrator..."
)

orchestrator = (
    MultimodalOrchestrator(
        products=products,
        semantic_engine=semantic_engine,
        visual_engine=visual_engine,
        project_root=PROJECT_ROOT,
    )
)


# --------------------------------------------------
# TEST
# --------------------------------------------------

query = "something similar but black"

image_path = (
    PROJECT_ROOT
    / "images"
    / "1617.jpg"
)


response = orchestrator.search(
    query=query,
    image_path=image_path,
    top_k=5,
)


print(
    "\n" + "=" * 80
)

print(
    "END-TO-END MULTIMODAL VYRA"
)

print(
    "=" * 80
)


print(
    "\nText query:"
)

print(
    response["query"]
)


print(
    "\nText intent before image:"
)

print(
    response["text_intent"]
)


print(
    "\nImage-derived attributes:"
)

print(
    response["image_inferred"]
)


print(
    "\nFinal intent:"
)

print(
    response["final_intent"]
)


print(
    "\nFinal results:"
)


results = response[
    "results"
]


if results.empty:

    print(
        "No products matched."
    )

else:

    columns = [
        "product_id",
        "product_name",
        "gender",
        "category",
        "colour_normalized",
        "price",
        "semantic_score",
        "visual_score",
        "multimodal_score",
    ]

    print(
        results[
            [
                column
                for column in columns
                if column in results.columns
            ]
        ].to_string(
            index=False
        )
    )