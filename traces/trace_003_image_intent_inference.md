# Trace 003 — Image-Aware Intent Inference

## Goal

Improve multimodal requests where the user refers to the image without
restating the product category or gender.

## Coding Agent

ChatGPT

## Human Instruction

When the user says something like "something similar but black", infer missing
attributes from the reference image while keeping explicit text constraints
authoritative.

## Starting Observation

Reference image:

`1617.jpg` — red men's T-shirt

Text query:

`something similar but black`

The text parser correctly extracted:

- colour = black

However, category and gender were absent.

The multimodal engine therefore returned black products across multiple
categories.

## Agent Recommendation

Add an image-aware intent enrichment layer.

Rules:

1. Explicit text constraints must never be overwritten.
2. Missing attributes may be inherited from the reference image metadata.
3. Image-derived attributes should become hard constraints only when they are
   intentionally inferred.

## Implementation

Created:

`backend/services/image_intent_inference.py`

The first version infers:

- category
- gender

from the known catalogue reference product.

## Test

Reference image:

`images/1617.jpg`

Text query:

`something similar but black`

## Result

Image-derived intent:

- category = tshirt
- gender = men

Text-derived intent:

- colour = black

Final result:

`4359 — Free Authority Men's Melting Records Black T-shirt`

## Human Verification

Confirmed that:

- the textual colour override remained black
- category was inferred as tshirt
- gender was inferred as men
- no unrelated black shirts or women's tops remained

## Status

Completed.

## Verification Case 2 — Text/Image Conflict Resolution

### Input

Reference image:

`1617.jpg` — red men's T-shirt

Text query:

`something similar for women in pink`

### Text-Derived Intent

- colour = pink
- gender = women

### Image-Derived Intent

- category = tshirt

The image did not overwrite the explicitly supplied gender.

### Final Intent

- category = tshirt
- colour = pink
- gender = women

### Result

Returned products:

- Roxy Women Pink T-shirt
- Doodle Sporty Girl dark Pink Tshirts

All returned products satisfied the final multimodal intent.

### Verified Precedence Rule

1. Explicit textual constraints have highest priority.
2. Image-derived metadata fills only missing attributes.
3. Semantic and visual similarity determine ranking only after constraints are satisfied.

### Human Verification

Confirmed that the men's gender from the reference image did not override the
explicit request for women's products.

## Status

Passed.