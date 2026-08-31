from contextlib import asynccontextmanager
from dataclasses import asdict
from pathlib import Path
import shutil
import uuid

import numpy as np
import pandas as pd

from fastapi import (
    FastAPI,
    File,
    Form,
    HTTPException,
    UploadFile,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.services.semantic_search import (
    SemanticSearchEngine,
)
from backend.services.visual_search import (
    VisualSearchEngine,
)
from backend.services.multimodal_orchestrator import (
    MultimodalOrchestrator,
)


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[2]
)

PRODUCTS_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "products_v2_enriched.csv"
)

IMAGES_DIR = (
    PROJECT_ROOT
    / "images"
)

UPLOADS_DIR = (
    PROJECT_ROOT
    / "temp"
    / "uploads"
)

UPLOADS_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# GLOBAL APP STATE
# ============================================================

products = None
semantic_engine = None
visual_engine = None
orchestrator = None


# ============================================================
# HELPERS
# ============================================================

def clean_value(value):
    """
    Convert pandas / NumPy values into JSON-safe Python values.
    """

    if value is None:
        return None

    if isinstance(
        value,
        (np.integer,),
    ):
        return int(value)

    if isinstance(
        value,
        (np.floating,),
    ):
        if np.isnan(value):
            return None

        return float(value)

    if isinstance(
        value,
        np.ndarray,
    ):
        return value.tolist()

    try:
        if pd.isna(value):
            return None
    except Exception:
        pass

    return value


def dataframe_to_records(
    dataframe: pd.DataFrame,
):
    records = []

    for _, row in dataframe.iterrows():

        record = {}

        for column in dataframe.columns:
            record[column] = clean_value(
                row[column]
            )

        image_path = record.get(
            "image_path"
        )

        if image_path:
            filename = Path(
                str(image_path)
            ).name

            record[
                "image_url"
            ] = (
                f"/images/{filename}"
            )

        records.append(
            record
        )

    return records


# ============================================================
# STARTUP
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    global products
    global semantic_engine
    global visual_engine
    global orchestrator

    print(
        "\n========================================"
    )
    print(
        "Starting VYRA AI backend..."
    )
    print(
        "========================================"
    )

    if not PRODUCTS_PATH.exists():
        raise RuntimeError(
            f"Catalogue not found: "
            f"{PRODUCTS_PATH}"
        )

    products = pd.read_csv(
        PRODUCTS_PATH
    )

    print(
        f"Products loaded: "
        f"{len(products)}"
    )

    print(
        "\nLoading semantic engine..."
    )

    semantic_engine = (
        SemanticSearchEngine(
            products
        )
    )

    print(
        "\nLoading visual engine..."
    )

    visual_engine = (
        VisualSearchEngine(
            products=products,
            project_root=PROJECT_ROOT,
        )
    )

    print(
        "\nLoading multimodal orchestrator..."
    )

    orchestrator = (
        MultimodalOrchestrator(
            products=products,
            semantic_engine=semantic_engine,
            visual_engine=visual_engine,
            project_root=PROJECT_ROOT,
        )
    )

    print(
        "\n========================================"
    )
    print(
        "VYRA backend READY"
    )
    print(
        "========================================\n"
    )

    yield

    print(
        "Shutting down VYRA backend."
    )


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="VYRA API",
    description=(
        "Constraint-safe multimodal "
        "fashion retrieval API"
    ),
    version="1.0.0",
    lifespan=lifespan,
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# STATIC PRODUCT IMAGES
# ============================================================

if IMAGES_DIR.exists():

    app.mount(
        "/images",
        StaticFiles(
            directory=str(
                IMAGES_DIR
            )
        ),
        name="images",
    )


# ============================================================
# ROUTES
# ============================================================

@app.get("/")
def root():

    return {
        "name": "VYRA",
        "status": "running",
        "description": (
            "Constraint-safe multimodal "
            "fashion discovery"
        ),
    }


@app.get("/health")
def health():

    return {
        "status": (
            "ready"
            if orchestrator
            is not None
            else "loading"
        ),
        "products": (
            len(products)
            if products is not None
            else 0
        ),
        "semantic_engine": (
            semantic_engine
            is not None
        ),
        "visual_engine": (
            visual_engine
            is not None
        ),
        "multimodal_engine": (
            orchestrator
            is not None
        ),
    }


@app.post(
    "/search/multimodal"
)
async def multimodal_search(
    query: str = Form(
        default="something similar"
    ),
    image: UploadFile = File(...),
    top_k: int = Form(
        default=5
    ),
):

    if orchestrator is None:

        raise HTTPException(
            status_code=503,
            detail=(
                "VYRA models are "
                "still loading."
            ),
        )

    if top_k < 1:
        top_k = 1

    if top_k > 20:
        top_k = 20

    allowed_types = {
        "image/jpeg",
        "image/png",
        "image/webp",
    }

    if (
        image.content_type
        not in allowed_types
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "Upload a JPG, PNG "
                "or WEBP image."
            ),
        )

    suffix = (
        Path(
            image.filename or "upload.jpg"
        )
        .suffix
        .lower()
    )

    if suffix not in {
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
    }:
        suffix = ".jpg"

    temp_filename = (
        f"{uuid.uuid4().hex}"
        f"{suffix}"
    )

    temp_path = (
        UPLOADS_DIR
        / temp_filename
    )

    try:

        with temp_path.open(
            "wb"
        ) as buffer:

            shutil.copyfileobj(
                image.file,
                buffer,
            )

        response = (
            orchestrator.search(
                query=query,
                image_path=temp_path,
                top_k=top_k,
            )
        )

        final_intent = (
            asdict(
                response[
                    "final_intent"
                ]
            )
        )

        results = (
            dataframe_to_records(
                response[
                    "results"
                ]
            )
        )

        return {
            "success": True,
            "query": query,
            "text_intent": response[
                "text_intent"
            ],
            "image_inferred": response[
                "image_inferred"
            ],
            "final_intent": (
                final_intent
            ),
            "result_count": (
                len(results)
            ),
            "results": results,
        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )

    finally:

        try:
            image.file.close()
        except Exception:
            pass

        if temp_path.exists():

            try:
                temp_path.unlink()
            except Exception:
                pass