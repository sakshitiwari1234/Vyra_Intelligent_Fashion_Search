from pathlib import Path

import pandas as pd


class ImageIntentInference:
    """
    Enriches text intent using metadata associated with a reference image.

    Text constraints always take priority.
    Image-derived attributes are only used when the user did not explicitly
    specify them.
    """

    def __init__(
        self,
        products: pd.DataFrame,
        project_root: Path,
    ):
        self.products = products.copy()
        self.project_root = Path(project_root)

    def _normalize_path(
        self,
        value,
    ) -> Path:

        path = Path(str(value))

        if path.is_absolute():
            return path.resolve()

        return (
            self.project_root
            / path
        ).resolve()

    def find_reference_product(
        self,
        query_image_path,
    ):

        query_path = Path(
            query_image_path
        ).resolve()

        for _, row in self.products.iterrows():

            product_image_path = (
                self._normalize_path(
                    row["image_path"]
                )
            )

            if product_image_path == query_path:
                return row

        return None

    def enrich_intent(
        self,
        intent,
        query_image_path,
    ):

        reference_product = (
            self.find_reference_product(
                query_image_path
            )
        )

        inferred = {}

        if reference_product is None:
            return intent, inferred

        # Only infer category if text did not provide one.
        if not getattr(
            intent,
            "category",
            None,
        ):

            category = reference_product.get(
                "category"
            )

            if pd.notna(category):

                intent.category = str(
                    category
                ).lower()

                if (
                    "category"
                    not in intent.hard_constraints
                ):
                    intent.hard_constraints.append(
                        "category"
                    )

                inferred[
                    "category"
                ] = intent.category

        # Gender can also be inferred when absent.
        if not getattr(
            intent,
            "gender",
            None,
        ):

            gender = reference_product.get(
                "gender"
            )

            if pd.notna(gender):

                intent.gender = str(
                    gender
                ).lower()

                if (
                    "gender"
                    not in intent.hard_constraints
                ):
                    intent.hard_constraints.append(
                        "gender"
                    )

                inferred[
                    "gender"
                ] = intent.gender

        return intent, inferred