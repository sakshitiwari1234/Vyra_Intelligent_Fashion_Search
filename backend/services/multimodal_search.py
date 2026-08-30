import numpy as np
import pandas as pd


class MultimodalSearchEngine:
    """
    Combines:
    - semantic text similarity
    - visual image similarity
    - hard constraint filtering
    - optional soft preference score

    Final score:
        0.50 semantic
        0.40 visual
        0.10 soft preference
    """

    def __init__(
        self,
        products: pd.DataFrame,
        semantic_engine,
        visual_engine,
    ):
        self.products = products.copy()

        self.semantic_engine = semantic_engine
        self.visual_engine = visual_engine


    def _normalize_score(
        self,
        series: pd.Series,
    ) -> pd.Series:

        minimum = series.min()
        maximum = series.max()

        if maximum == minimum:
            return pd.Series(
                np.ones(len(series)),
                index=series.index,
            )

        return (
            (series - minimum)
            / (maximum - minimum)
        )


    def _get_visual_scores(
        self,
        query_image_path,
    ) -> pd.DataFrame:

        visual_results = (
            self.visual_engine
            .search_by_image(
                query_image_path=query_image_path,
                top_k=len(self.products),
            )
        )

        return visual_results[
            [
                "product_id",
                "visual_score",
            ]
        ].copy()


    def _calculate_soft_score(
        self,
        row,
        intent,
    ) -> float:

        score = 0.0

        # Occasion
        if getattr(
            intent,
            "occasion",
            None,
        ):

            if (
                str(row.get("occasion", "")).lower()
                == str(intent.occasion).lower()
            ):
                score += 1.0

        # Season
        if getattr(
            intent,
            "season",
            None,
        ):

            if (
                str(row.get("season", "")).lower()
                == str(intent.season).lower()
            ):
                score += 1.0

        # Style terms
        styles = getattr(
            intent,
            "styles",
            [],
        )

        if styles:

            searchable_text = " ".join(
                [
                    str(
                        row.get(
                            "product_name",
                            "",
                        )
                    ),
                    str(
                        row.get(
                            "description",
                            "",
                        )
                    ),
                    str(
                        row.get(
                            "occasion",
                            "",
                        )
                    ),
                    str(
                        row.get(
                            "season",
                            "",
                        )
                    ),
                ]
            ).lower()

            for style in styles:

                if (
                    str(style).lower()
                    in searchable_text
                ):
                    score += 1.0

        return score


    def search(
        self,
        query: str,
        query_image_path,
        intent,
        hard_filter_function,
        top_k: int = 5,
    ) -> pd.DataFrame:
        """
        Multimodal search.

        query:
            Natural-language query.

        query_image_path:
            Reference fashion image.

        intent:
            Parsed QueryIntent.

        hard_filter_function:
            Existing apply_hard_filters function.
        """

        # -----------------------------------------
        # 1. Semantic search
        # -----------------------------------------

        semantic_results = (
            self.semantic_engine.search(
                query=query,
                top_k=len(self.products),
            )
        )

        semantic_scores = semantic_results[
            [
                "product_id",
                "semantic_score",
            ]
        ].copy()

        # -----------------------------------------
        # 2. Visual search
        # -----------------------------------------

        visual_scores = (
            self._get_visual_scores(
                query_image_path
            )
        )

        # -----------------------------------------
        # 3. Merge scores
        # -----------------------------------------

        candidates = (
            self.products
            .merge(
                semantic_scores,
                on="product_id",
                how="left",
            )
            .merge(
                visual_scores,
                on="product_id",
                how="left",
            )
        )

        candidates[
            "semantic_score"
        ] = (
            candidates[
                "semantic_score"
            ]
            .fillna(0.0)
        )

        candidates[
            "visual_score"
        ] = (
            candidates[
                "visual_score"
            ]
            .fillna(0.0)
        )

        # -----------------------------------------
        # 4. HARD CONSTRAINTS
        # -----------------------------------------

        candidates = (
            hard_filter_function(
                candidates,
                intent,
            )
        )

        if candidates.empty:

            return candidates

        # -----------------------------------------
        # 5. Soft preference score
        # -----------------------------------------

        candidates[
            "soft_score"
        ] = candidates.apply(
            lambda row:
            self._calculate_soft_score(
                row,
                intent,
            ),
            axis=1,
        )

        # -----------------------------------------
        # 6. Normalize
        # -----------------------------------------

        candidates[
            "semantic_normalized"
        ] = self._normalize_score(
            candidates[
                "semantic_score"
            ]
        )

        candidates[
            "visual_normalized"
        ] = self._normalize_score(
            candidates[
                "visual_score"
            ]
        )

        candidates[
            "soft_normalized"
        ] = self._normalize_score(
            candidates[
                "soft_score"
            ]
        )

        # -----------------------------------------
        # 7. Multimodal score
        # -----------------------------------------

        candidates[
            "multimodal_score"
        ] = (
            0.50
            * candidates[
                "semantic_normalized"
            ]
            +
            0.40
            * candidates[
                "visual_normalized"
            ]
            +
            0.10
            * candidates[
                "soft_normalized"
            ]
        )

        # -----------------------------------------
        # 8. Final ranking
        # -----------------------------------------

        results = (
            candidates
            .sort_values(
                by="multimodal_score",
                ascending=False,
            )
            .head(top_k)
            .reset_index(drop=True)
        )

        return results