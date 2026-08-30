# Trace 002 — Multimodal Hybrid Search V1

## Goal

Combine semantic text retrieval and CLIP visual retrieval into a single
constraint-safe fashion search pipeline.

## Coding Agent

ChatGPT

## Human Instruction

Build multimodal search using an image and natural-language query while
preserving VYRA's deterministic hard constraints.

## Starting State

VYRA already supported:

- query intent parsing
- hard constraint filtering
- semantic search
- hybrid text search
- CLIP visual search

The semantic and visual systems operated separately.

## Agent Recommendation

Combine both retrieval signals and rerank candidates after hard filtering.

Initial scoring:

- semantic: 0.50
- visual: 0.40
- soft preference: 0.10

## First Test

Text query:

`red tshirt for men under 1000`

Reference image:

`images/1617.jpg`

## Parsed Intent

- category = tshirt
- colour = red
- gender = men
- max price = 1000

## Execution Result

All 50 catalogue images were embedded successfully.

The final results contained only products satisfying the mandatory constraints.

Product 1617 ranked first.

## Human Checkpoint

Verified that every returned result was:

- men's
- red
- tshirt
- priced at or below 1000

## Status

Completed.

## Verification Case 2 — Text Override

### Input

Reference image:

`1617.jpg` — red men's T-shirt

Text query:

`something similar but black`

### Parsed Intent

- colour = black
- no explicit category
- no explicit gender

### Result

All returned products were black.

The system preserved visual similarity while enforcing the textual colour override.

### Observation

Because the text did not explicitly specify a category, results were allowed across
shirt, tshirt and top categories.

### Insight

A future multimodal reasoning layer should infer likely product category from the
reference image when the user uses phrases such as "similar to this" without
restating the category.


