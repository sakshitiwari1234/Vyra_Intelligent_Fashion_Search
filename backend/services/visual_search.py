from pathlib import Path

import numpy as np
import pandas as pd
import torch
from PIL import Image
from transformers import CLIPModel, CLIPProcessor


MODEL_NAME = "openai/clip-vit-base-patch32"


class VisualSearchEngine:
    """
    CLIP-based visual retrieval engine for VYRA.

    Catalogue images are converted into normalized CLIP embeddings.
    A query image is encoded using the same model and ranked using
    cosine similarity.
    """

    def __init__(
        self,
        products: pd.DataFrame,
        project_root: Path,
    ):
        self.products = products.copy()
        self.project_root = Path(project_root)

        self.device = (
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )

        print(
            "Visual search device:",
            self.device,
        )

        print(
            "Loading CLIP model..."
        )

        self.model = (
            CLIPModel
            .from_pretrained(MODEL_NAME)
            .to(self.device)
        )

        self.model.eval()

        self.processor = (
            CLIPProcessor
            .from_pretrained(MODEL_NAME)
        )

        self.image_embeddings = (
            self._build_catalogue_embeddings()
        )

    # --------------------------------------------------
    # IMAGE PATH
    # --------------------------------------------------

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

    # --------------------------------------------------
    # IMAGE LOADING
    # --------------------------------------------------

    def _load_image(
        self,
        image_path: Path,
    ) -> Image.Image:

        return (
            Image
            .open(image_path)
            .convert("RGB")
        )

    # --------------------------------------------------
    # CLIP IMAGE ENCODING
    # --------------------------------------------------

    def _encode_images(
        self,
        images,
    ) -> np.ndarray:
        """
        Convert PIL images into normalized CLIP image embeddings.
        """

        inputs = self.processor(
            images=images,
            return_tensors="pt",
        )

        pixel_values = (
            inputs["pixel_values"]
            .to(self.device)
        )

        with torch.no_grad():

            vision_outputs = (
                self.model.vision_model(
                    pixel_values=pixel_values
                )
            )

            pooled_output = (
                vision_outputs.pooler_output
            )

            embeddings = (
                self.model.visual_projection(
                    pooled_output
                )
            )

            embeddings = (
                torch.nn.functional.normalize(
                    embeddings,
                    p=2,
                    dim=-1,
                )
            )

        return (
            embeddings
            .cpu()
            .numpy()
        )

    # --------------------------------------------------
    # BUILD CATALOGUE INDEX
    # --------------------------------------------------

    def _build_catalogue_embeddings(
        self,
    ) -> np.ndarray:

        embeddings = []
        valid_indices = []

        print(
            "Building catalogue image embeddings..."
        )

        total_products = len(
            self.products
        )

        for count, (index, row) in enumerate(
            self.products.iterrows(),
            start=1,
        ):

            image_path = (
                self._resolve_image_path(
                    row["image_path"]
                )
            )

            if not image_path.exists():

                print(
                    f"Missing image: {image_path}"
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

                print(
                    f"Embedded "
                    f"{count}/{total_products}: "
                    f"{row['product_id']}"
                )

            except Exception as error:

                print(
                    "Image error:",
                    image_path,
                    error,
                )

        if not embeddings:

            raise ValueError(
                "No valid catalogue images "
                "could be embedded."
            )

        self.products = (
            self.products
            .loc[valid_indices]
            .reset_index(drop=True)
        )

        matrix = np.vstack(
            embeddings
        )

        print(
            "\nCatalogue embeddings created:",
            len(matrix),
        )

        return matrix

    # --------------------------------------------------
    # VISUAL SEARCH
    # --------------------------------------------------

    def search_by_image(
        self,
        query_image_path,
        top_k: int = 5,
    ) -> pd.DataFrame:

        query_image_path = Path(
            query_image_path
        )

        if not query_image_path.exists():

            raise FileNotFoundError(
                f"Query image not found: "
                f"{query_image_path}"
            )

        query_image = (
            self._load_image(
                query_image_path
            )
        )

        query_embedding = (
            self._encode_images(
                [query_image]
            )[0]
        )

        # Both vectors are normalized,
        # therefore dot product = cosine similarity.
        similarities = (
            self.image_embeddings
            @ query_embedding
        )

        results = (
            self.products
            .copy()
        )

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
    
    
    

