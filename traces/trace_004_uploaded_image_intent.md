# Trace 004 — Uploaded Image Intent Understanding

## Goal

Enable VYRA to understand fashion attributes from images that do not depend on catalogue metadata lookup.

## Coding Agent

ChatGPT

## Human Instruction

Add arbitrary uploaded-image understanding using CLIP and infer a small, controlled set of attributes.

## Starting State

The previous image-aware intent layer could infer category and gender only when the reference image corresponded to a known catalogue product.

That was useful for internal catalogue images but not sufficient for real user uploads.

## Agent Recommendation

Use CLIP zero-shot classification over a fixed fashion label set.

Attributes:

- category
- colour
- gender

Apply confidence thresholds before accepting any image-derived attribute.

Explicit text-derived constraints must always take priority.

## Implementation

Created:

`backend/services/uploaded_image_intent.py`

The engine:

1. loads the uploaded image
2. compares it against controlled text labels with CLIP
3. computes probability scores
4. accepts predictions only when they exceed confidence thresholds
5. enriches only missing intent attributes

## Test

Query:

`something similar`

Image:

`1617.jpg`

## Raw Predictions

- tshirt: approximately 0.72
- red: approximately 0.89
- men: approximately 0.95

## Accepted Attributes

- category = tshirt
- colour = red
- gender = men

## Final Intent

- category = tshirt
- colours = [red]
- gender = men

## Human Verification

All accepted attributes matched the visible product represented by the test image.

## Status

Completed.