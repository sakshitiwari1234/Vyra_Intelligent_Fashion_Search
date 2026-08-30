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