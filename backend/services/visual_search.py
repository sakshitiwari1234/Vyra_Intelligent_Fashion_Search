from pathlib import Path

import numpy as np
import pandas as pd
import torch
from PIL import Image
from transformers import CLIPModel, CLIPProcessor


MODEL_NAME = "openai/clip-vit-base-patch32"


class VisualSearchEngine:

    def __init__(
        self,
        products: pd.DataFrame,
        project_root: Path,
    ):
        self.products = products.copy()
        self.project_root = project_root

        self.device = (
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )

        print(
            "Visual search device:",
            self.device
        )

        self.model = (
            CLIPModel
            .from_pretrained(MODEL_NAME)
            .to(self.device)
        )

        self.processor = (
            CLIPProcessor
            .from_pretrained(MODEL_NAME)
        )

        self.image_embeddings = (
            self._build_catalogue_embeddings()
        )


    def _resolve_image_path(
        self,
        image_path: str,
    ) -> Path:

        path = Path(
            str(image_path)
        )

        if path.is_absolute():
            return path

        return (
            self.project_root
            / path
        )


    def _load_image(
        self,
        image_path: Path,
    ) -> Image.Image:

        return (
            Image
            .open(image_path)
            .convert("RGB")
        )


    def _encode_images(
        self,
        images,
    ):

        inputs = self.processor(
            images=images,
            return_tensors="pt",
            padding=True,
        )

        inputs = {
            key: value.to(self.device)
            for key, value
            in inputs.items()
        }

        with torch.no_grad():

            embeddings = (
                self.model
                .get_image_features(
                    **inputs
                )
            )

        embeddings = torch.nn.functional.normalize(
            embeddings,
            p=2,
            dim=1,
        )

        return (
            embeddings
            .cpu()
            .numpy()
        )


    def _build_catalogue_embeddings(
        self,
    ):

        embeddings = []
        valid_indices = []

        print(
            "Building catalogue image embeddings..."
        )

        for index, row in self.products.iterrows():

            image_path = self._resolve_image_path(
                row["image_path"]
            )

            if not image_path.exists():

                print(
                    "Missing image:",
                    image_path
                )

                continue

            try:

                image = self._load_image(
                    image_path
                )

                embedding = (
                    self._encode_images(
                        [image]
                    )[0]
                )

                embeddings.append(
                    embedding
                )

                valid_indices.append(
                    index
                )

            except Exception as error:

                print(
                    "Image error:",
                    image_path,
                    error
                )

        self.products = (
            self.products
            .loc[valid_indices]
            .reset_index(drop=True)
        )

        if not embeddings:

            raise ValueError(
                "No valid catalogue images "
                "could be embedded."
            )

        print(
            "Catalogue embeddings created:",
            len(embeddings)
        )

        return np.vstack(
            embeddings
        )


    def search_by_image(
        self,
        query_image_path,
        top_k=5,
    ):

        query_image_path = Path(
            query_image_path
        )

        if not query_image_path.exists():

            raise FileNotFoundError(
                f"Query image not found:\n"
                f"{query_image_path}"
            )

        query_image = self._load_image(
            query_image_path
        )

        query_embedding = (
            self._encode_images(
                [query_image]
            )[0]
        )

        similarities = (
            self.image_embeddings
            @ query_embedding
        )

        results = self.products.copy()

        results[
            "visual_score"
        ] = similarities

        results = (
            results
            .sort_values(
                by="visual_score",
                ascending=False,
            )
            .head(top_k)
            .reset_index(drop=True)
        )

        return results