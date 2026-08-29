from pathlib import Path

import pandas as pd
from sentence_transformers import SentenceTransformer


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


class SemanticSearchEngine:

    def __init__(self, products: pd.DataFrame):
        self.products = products.copy()

        self.model = SentenceTransformer(
            MODEL_NAME
        )

        self.products["product_text"] = (
            self.products.apply(
                self._build_product_text,
                axis=1
            )
        )

        self.product_embeddings = (
            self.model.encode(
                self.products[
                    "product_text"
                ].tolist(),
                normalize_embeddings=True,
                show_progress_bar=False,
            )
        )

    def _clean_value(self, value):
        if pd.isna(value):
            return ""

        return str(value).strip()

    def _build_product_text(self, row):

        parts = []

        fields = [
            "product_name",
            "description",
            "gender",
            "category",
            "subcategory",
            "colour_normalized",
            "material",
            "fit",
            "pattern",
            "sleeve",
            "occasion",
            "season",
        ]

        for field in fields:

            if field not in row:
                continue

            value = self._clean_value(
                row[field]
            )

            if value:
                parts.append(value)

        return " ".join(parts)

    def search(
        self,
        query: str,
        top_k: int = 10,
    ) -> pd.DataFrame:

        if not query.strip():
            return self.products.iloc[0:0].copy()

        query_embedding = (
            self.model.encode(
                query,
                normalize_embeddings=True,
            )
        )

        similarities = (
            self.product_embeddings
            @ query_embedding
        )

        results = self.products.copy()

        results["semantic_score"] = (
            similarities
        )

        results = (
            results
            .sort_values(
                by="semantic_score",
                ascending=False,
            )
            .head(top_k)
            .reset_index(drop=True)
        )

        return results