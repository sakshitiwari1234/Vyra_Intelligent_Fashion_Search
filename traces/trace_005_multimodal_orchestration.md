# Trace 005 — End-to-End Multimodal Orchestration

## Goal

Connect the independent text, image-understanding and multimodal retrieval
components into a single executable workflow.

## Coding Agent

ChatGPT

## Human Instruction

Integrate uploaded-image intent inference into the multimodal search pipeline
without allowing image predictions to override explicit textual constraints.

## Starting State

VYRA already had:

- text intent parsing
- semantic retrieval
- CLIP visual retrieval
- image-aware metadata inference
- zero-shot uploaded-image understanding
- multimodal ranking

These components were not yet exposed through one orchestration layer.

## Implementation

Created:

`backend/services/multimodal_orchestrator.py`

The orchestrator performs:

1. text parsing
2. image inference
3. precedence resolution
4. hard filtering
5. multimodal reranking

## Test

Text:

`something similar but black`

Image:

`1617.jpg`

## Text Intent

- colour = black

## Image Inference

- category = tshirt
- gender = men

The image predicted red as well, but it was not accepted because the text already
provided an explicit colour constraint.

## Final Intent

- category = tshirt
- colour = black
- gender = men

## Final Result

`4359 — Free Authority Men's Melting Records Black T-shirt`

## Human Verification

Confirmed:

- explicit black colour was preserved
- image-derived category and gender filled missing attributes
- no red product survived
- final result satisfied all mandatory constraints

## Status

Completed.