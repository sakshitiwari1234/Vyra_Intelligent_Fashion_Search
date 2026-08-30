# Trace 001 — Visual Search V1

## Goal

Add image-to-image fashion retrieval to VYRA.

## Coding Agent

ChatGPT

## Human Instruction

Implement Visual Search V1 using CLIP so a user can provide a fashion image
and retrieve visually similar catalogue products.

## Starting State

VYRA already supported:

- intent parsing
- deterministic hard filtering
- MiniLM semantic search
- hybrid retrieval
- evaluation

It did not support image-based retrieval.

## Agent Recommendation

Use:

- openai/clip-vit-base-patch32
- PyTorch
- Hugging Face Transformers
- Pillow

Architecture:

Catalogue image
→ CLIP image encoder
→ normalized image embedding

Query image
→ CLIP image encoder
→ normalized query embedding

Then:

cosine similarity
→ rank catalogue images

## Files Planned

- backend/services/visual_search.py
- test_visual_manual.py

## Human Checkpoint

Dependencies are being installed before implementation is tested.

## Commands

```powershell
python.exe -m pip install --upgrade pip
pip install transformers pillow torch torchvision

## Final Result

Visual Search V1 completed successfully.

The system:

- loaded 50 catalogue products
- loaded the CLIP vision model
- created embeddings for all 50 catalogue images
- encoded a query image
- calculated cosine similarity
- returned ranked visually similar products

## Human Verification

The implementation was accepted after successful end-to-end execution.

## Status

Completed.