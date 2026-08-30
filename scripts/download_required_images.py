from pathlib import Path
import pandas as pd
from datasets import load_dataset


PROJECT_ROOT = Path(__file__).resolve().parent.parent

CSV_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "products_v2_enriched.csv"
)

OUTPUT_DIR = PROJECT_ROOT / "images"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

products = pd.read_csv(CSV_PATH)

required_ids = set(
    products["product_id"].astype(int).tolist()
)

print("Required images:", len(required_ids))

dataset = load_dataset(
    "ashraq/fashion-product-images-small",
    split="train",
    streaming=True,
)

found = set()

for item in dataset:

    product_id = int(item["id"])

    if product_id not in required_ids:
        continue

    image = item["image"]

    output_path = (
        OUTPUT_DIR
        / f"{product_id}.jpg"
    )

    image.convert("RGB").save(
        output_path,
        format="JPEG",
    )

    found.add(product_id)

    print(
        f"Downloaded {product_id} "
        f"({len(found)}/{len(required_ids)})"
    )

    if found == required_ids:
        break


missing = required_ids - found

print("\nFinished")
print("Downloaded:", len(found))
print("Missing:", len(missing))

if missing:
    print("Missing IDs:", sorted(missing))
    
    
