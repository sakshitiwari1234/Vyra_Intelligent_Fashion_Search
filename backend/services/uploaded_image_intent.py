from pathlib import Path

import numpy as np
import torch
from PIL import Image
from transformers import CLIPModel, CLIPProcessor


MODEL_NAME = "openai/clip-vit-base-patch32"


class UploadedImageIntentEngine:
    """
    Zero-shot attribute inference for arbitrary uploaded fashion images.

    Rules:
    - infer only from a small fixed label set
    - use confidence thresholds
    - never overwrite explicit text constraints
    """

    CATEGORY_LABELS = [
        "tshirt",
        "shirt",
        "top",
        "kurta",
        "sweater",
    ]

    COLOUR_LABELS = [
        "red",
        "pink",
        "black",
        "white",
        "blue",
        "maroon",
        "yellow",
        "magenta",
    ]

    GENDER_LABELS = [
        "men",
        "women",
    ]

    def __init__(self, device=None):
        self.device = device or (
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )

        print(
            "Uploaded-image intent device:",
            self.device,
        )

        print(
            "Loading CLIP model for uploaded-image inference..."
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

    def _load_image(
        self,
        image_path,
    ):
        image_path = Path(
            image_path
        )

        if not image_path.exists():
            raise FileNotFoundError(
                f"Image not found: {image_path}"
            )

        return (
            Image
            .open(image_path)
            .convert("RGB")
        )

    def _predict_label(
        self,
        image,
        labels,
        prompt_template,
    ):
        """
        Perform CLIP zero-shot classification
        over a fixed set of candidate labels.
        """

        prompts = [
            prompt_template.format(
                label=label
            )
            for label in labels
        ]

        inputs = self.processor(
            text=prompts,
            images=image,
            return_tensors="pt",
            padding=True,
        )

        inputs = {
            key: value.to(self.device)
            for key, value
            in inputs.items()
        }

        with torch.no_grad():
            outputs = self.model(
                **inputs
            )

            logits = (
                outputs.logits_per_image
            )

            probabilities = (
                logits
                .softmax(dim=1)
                .cpu()
                .numpy()[0]
            )

        best_index = int(
            np.argmax(
                probabilities
            )
        )

        return {
            "label": labels[
                best_index
            ],
            "confidence": float(
                probabilities[
                    best_index
                ]
            ),
            "scores": {
                label: float(score)
                for label, score
                in zip(
                    labels,
                    probabilities,
                )
            },
        }

    def infer_attributes(
        self,
        image_path,
    ):
        """
        Infer category, colour and gender
        from an arbitrary uploaded image.
        """

        image = self._load_image(
            image_path
        )

        category = (
            self._predict_label(
                image=image,
                labels=self.CATEGORY_LABELS,
                prompt_template=(
                    "a fashion product photo "
                    "of a {label}"
                ),
            )
        )

        colour = (
            self._predict_label(
                image=image,
                labels=self.COLOUR_LABELS,
                prompt_template=(
                    "a {label} coloured "
                    "fashion garment"
                ),
            )
        )

        gender = (
            self._predict_label(
                image=image,
                labels=self.GENDER_LABELS,
                prompt_template=(
                    "a fashion garment "
                    "designed for {label}"
                ),
            )
        )

        return {
            "category": category,
            "colour": colour,
            "gender": gender,
        }

    def enrich_intent(
        self,
        intent,
        image_path,
        category_threshold=0.35,
        colour_threshold=0.35,
        gender_threshold=0.65,
    ):
        """
        Fill missing intent attributes using image predictions.

        Explicit text-derived attributes are never overwritten.
        """

        predictions = (
            self.infer_attributes(
                image_path
            )
        )

        inferred = {}

        # ----------------------------------------
        # CATEGORY
        # ----------------------------------------

        if (
            not getattr(
                intent,
                "category",
                None,
            )
            and predictions[
                "category"
            ]["confidence"]
            >= category_threshold
        ):
            category = (
                predictions[
                    "category"
                ]["label"]
            )

            intent.category = (
                category
            )

            if (
                "category"
                not in intent.hard_constraints
            ):
                intent.hard_constraints.append(
                    "category"
                )

            inferred[
                "category"
            ] = {
                "value": category,
                "confidence": predictions[
                    "category"
                ]["confidence"],
            }

        # ----------------------------------------
        # COLOUR
        # ----------------------------------------

        if (
            not getattr(
                intent,
                "colours",
                [],
            )
            and predictions[
                "colour"
            ]["confidence"]
            >= colour_threshold
        ):
            colour = (
                predictions[
                    "colour"
                ]["label"]
            )

            intent.colours = [
                colour
            ]

            if (
                "colours"
                not in intent.hard_constraints
            ):
                intent.hard_constraints.append(
                    "colours"
                )

            inferred[
                "colour"
            ] = {
                "value": colour,
                "confidence": predictions[
                    "colour"
                ]["confidence"],
            }

        # ----------------------------------------
        # GENDER
        # ----------------------------------------

        if (
            not getattr(
                intent,
                "gender",
                None,
            )
            and predictions[
                "gender"
            ]["confidence"]
            >= gender_threshold
        ):
            gender = (
                predictions[
                    "gender"
                ]["label"]
            )

            intent.gender = (
                gender
            )

            if (
                "gender"
                not in intent.hard_constraints
            ):
                intent.hard_constraints.append(
                    "gender"
                )

            inferred[
                "gender"
            ] = {
                "value": gender,
                "confidence": predictions[
                    "gender"
                ]["confidence"],
            }

        return (
            intent,
            inferred,
            predictions,
        )