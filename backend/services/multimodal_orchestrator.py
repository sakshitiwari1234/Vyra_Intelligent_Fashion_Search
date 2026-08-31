from pathlib import Path

import pandas as pd

from backend.services.query_parser import parse_query
from backend.services.filters import apply_hard_filters
from backend.services.uploaded_image_intent import (
    UploadedImageIntentEngine,
)
from backend.services.multimodal_search import (
    MultimodalSearchEngine,
)


class MultimodalOrchestrator:
    """
    End-to-end multimodal VYRA orchestration.

    Priority:
    1. Explicit text constraints
    2. Confidence-gated image inference
    3. Semantic + visual ranking

    The CLIP model already loaded by VisualSearchEngine
    is reused for uploaded-image understanding.
    """

    def __init__(
        self,
        products: pd.DataFrame,
        semantic_engine,
        visual_engine,
        project_root: Path,
    ):
        self.products = products.copy()
        self.project_root = Path(project_root)

        self.semantic_engine = semantic_engine
        self.visual_engine = visual_engine

        # Reuse the CLIP model that VisualSearchEngine already loaded.
        self.uploaded_image_intent = UploadedImageIntentEngine(
            device=self.visual_engine.device,
            model=self.visual_engine.model,
            processor=self.visual_engine.processor,
        )

        self.multimodal_engine = MultimodalSearchEngine(
            products=self.products,
            semantic_engine=self.semantic_engine,
            visual_engine=self.visual_engine,
        )

    def search(
        self,
        query: str,
        image_path,
        top_k: int = 5,
    ):
        """
        Run the complete multimodal VYRA pipeline.
        """

        # 1. Parse explicit user text.
        intent = parse_query(query)

        text_intent_before_image = {
            "category": intent.category,
            "colours": list(intent.colours),
            "gender": intent.gender,
            "min_price": intent.min_price,
            "max_price": intent.max_price,
        }

        # 2. Fill missing attributes using image understanding.
        intent, inferred, predictions = (
            self.uploaded_image_intent.enrich_intent(
                intent=intent,
                image_path=image_path,
            )
        )

        # 3. Perform constraint-safe multimodal retrieval.
        results = self.multimodal_engine.search(
            query=query,
            query_image_path=image_path,
            intent=intent,
            hard_filter_function=apply_hard_filters,
            top_k=top_k,
        )

        # 4. Return an explainable response.
        return {
            "query": query,
            "image_path": str(image_path),
            "text_intent": text_intent_before_image,
            "image_inferred": inferred,
            "raw_image_predictions": predictions,
            "final_intent": intent,
            "results": results,
        }