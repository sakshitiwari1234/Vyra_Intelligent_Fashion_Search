import pandas as pd

from backend.services.query_parser import parse_query
from backend.services.filters import apply_hard_filters
from backend.services.semantic_search import SemanticSearchEngine


class HybridSearchEngine:

    def __init__(
        self,
        products: pd.DataFrame,
        semantic_engine=None,
    ):
        self.products = products.copy()

        if semantic_engine is not None:
            self.semantic_engine = semantic_engine
        else:
            self.semantic_engine = SemanticSearchEngine(
                self.products
            )

    def _soft_preference_score(
        self,
        row,
        intent,
    ) -> float:

        score = 0.0

        if intent.occasion:
            value = str(
                row.get("occasion", "")
            ).lower().strip()

            if value == intent.occasion.lower():
                score += 1.0

        if intent.season:
            value = str(
                row.get("season", "")
            ).lower().strip()

            if value == intent.season.lower():
                score += 1.0

        if intent.styles:

            text = " ".join(
                [
                    str(row.get("product_name", "")),
                    str(row.get("description", "")),
                    str(row.get("occasion", "")),
                    str(row.get("season", "")),
                    str(row.get("fit", "")),
                    str(row.get("material", "")),
                ]
            ).lower()

            for style in intent.styles:

                if style.lower() in text:
                    score += 1.0

        return score

    def _attribute_completeness_score(
        self,
        row,
    ) -> float:

        fields = [
            "gender",
            "category",
            "colour_normalized",
            "material",
            "fit",
            "pattern",
            "sleeve",
            "occasion",
            "season",
        ]

        available = 0

        for field in fields:

            value = row.get(
                field,
                "",
            )

            if (
                pd.notna(value)
                and str(value).strip()
            ):
                available += 1

        return available / len(fields)

    def search(
        self,
        query: str,
        top_k: int = 10,
        candidate_k: int = 30,
    ) -> pd.DataFrame:

        intent = parse_query(query)

        semantic_results = (
            self.semantic_engine.search(
                query=query,
                top_k=candidate_k,
            )
        )

        filtered_results = (
            apply_hard_filters(
                semantic_results,
                intent,
            )
        )

        if filtered_results.empty:
            return filtered_results

        filtered_results[
            "soft_preference_score"
        ] = filtered_results.apply(
            lambda row:
            self._soft_preference_score(
                row,
                intent,
            ),
            axis=1,
        )

        filtered_results[
            "attribute_completeness"
        ] = filtered_results.apply(
            self._attribute_completeness_score,
            axis=1,
        )

        max_soft = filtered_results[
            "soft_preference_score"
        ].max()

        if max_soft > 0:
            filtered_results[
                "soft_preference_normalized"
            ] = (
                filtered_results[
                    "soft_preference_score"
                ]
                / max_soft
            )
        else:
            filtered_results[
                "soft_preference_normalized"
            ] = 0.0

        filtered_results[
            "hybrid_score"
        ] = (
            0.80
            * filtered_results[
                "semantic_score"
            ]
            +
            0.15
            * filtered_results[
                "soft_preference_normalized"
            ]
            +
            0.05
            * filtered_results[
                "attribute_completeness"
            ]
        )

        return (
            filtered_results
            .sort_values(
                "hybrid_score",
                ascending=False,
            )
            .head(top_k)
            .reset_index(drop=True)
        )