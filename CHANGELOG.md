# VYRA Improvement Changelog

This document records meaningful engineering iterations made to VYRA.

Some baseline components existed before formal hackathon tracking began.
Later iterations are recorded with the evidence that motivated each change.

---

## Existing Baseline — Pre-Hackathon Work

### Existing capabilities

- Structured fashion catalogue
- Query intent parser
- Category and colour normalization
- Hard constraint filtering
- Semantic search using MiniLM
- Hybrid semantic + constraint-aware retrieval
- Regression tests
- 30-query evaluation benchmark

### Existing measured result

Semantic-only retrieval could return relevant-looking products that violated
explicit user requirements.

On the constraint-grounded evaluation benchmark:

- Semantic Search constraint violation rate: approximately 48.7%
- Hybrid VYRA constraint violation rate: 0%

### Engineering insight

Semantic relevance alone is insufficient for commerce search.
Mandatory user constraints must remain deterministic.

---

## Iteration 1 — Visual Search V1

Status: Completed

### Goal

Add image-based fashion retrieval so users can search using a reference image.

### Change

Implemented CLIP-based image embeddings using:

- `openai/clip-vit-base-patch32`
- PyTorch
- Hugging Face Transformers
- Pillow

Catalogue images and query images are encoded into normalized embeddings and ranked using cosine similarity.

### Issues Found

1. The catalogue referenced image paths, but the actual image assets were initially missing.
2. The first CLIP implementation failed because the installed Transformers version returned a structured model output instead of the expected tensor.
3. A method-indentation issue temporarily caused `_encode_images` to be unavailable inside `VisualSearchEngine`.

### Resolution

- Restored the required catalogue images.
- Switched to explicit CLIP vision encoder → pooled output → visual projection → normalization.
- Rebuilt the visual search service with the correct class structure.

### Verification

- 50 catalogue image embeddings created successfully.
- `test_visual_manual.py` executed successfully.
- Image-to-image similarity retrieval is operational.

### Engineering Insight

Visual retrieval should be treated as an additional retrieval signal rather than replacing structured constraints or text semantics.