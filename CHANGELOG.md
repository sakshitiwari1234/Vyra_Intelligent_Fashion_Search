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

## Iteration 2 — Multimodal Hybrid Search V1

Status: Completed

### Goal

Combine text understanding and visual similarity while preserving mandatory user constraints.

### Change

Integrated:

- MiniLM semantic similarity
- CLIP visual similarity
- deterministic hard constraint filtering
- soft preference scoring
- multimodal reranking

The first multimodal scoring formula uses:

- 50% semantic relevance
- 40% visual similarity
- 10% soft preference score

### Verification

Test query:

`red tshirt for men under 1000`

Reference image:

`1617.jpg`

Parsed hard constraints:

- category = tshirt
- colour = red
- gender = men
- max price = 1000

All returned products satisfied every hard constraint.

Product 1617, whose image was used as the reference, ranked first.

### Engineering Insight

Visual similarity and semantic relevance are useful ranking signals, but neither is allowed to override mandatory user constraints.
A second test using a red T-shirt reference image with the query
"something similar but black" returned only black products, confirming that
textual hard constraints can override visual appearance.
