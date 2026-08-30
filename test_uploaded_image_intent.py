from pathlib import Path

from backend.services.query_parser import parse_query
from backend.services.uploaded_image_intent import (
    UploadedImageIntentEngine,
)


PROJECT_ROOT = Path(__file__).resolve().parent

IMAGE_PATH = (
    PROJECT_ROOT
    / "images"
    / "1617.jpg"
)

query = "something similar"

intent = parse_query(query)

print("\nOriginal intent:")
print(intent)

engine = UploadedImageIntentEngine()

intent, inferred, predictions = (
    engine.enrich_intent(
        intent=intent,
        image_path=IMAGE_PATH,
    )
)

print("\nRaw image predictions:")

for attribute, result in predictions.items():
    print(
        attribute,
        "=>",
        result["label"],
        "| confidence:",
        round(result["confidence"], 4),
    )

print("\nAccepted image-derived attributes:")
print(inferred)

print("\nFinal enriched intent:")
print(intent)