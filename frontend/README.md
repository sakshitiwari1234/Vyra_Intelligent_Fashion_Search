# VYRA — Intelligent Fashion Search

VYRA is a multimodal, constraint-safe fashion discovery system that combines natural-language search, image understanding, semantic relevance, visual similarity, and hard shopping constraints.

## Problem

Traditional semantic search can return results that look relevant while violating explicit user requirements such as colour, category, gender, or price.

VYRA separates:

- Hard constraints → determine whether a product is allowed.
- Soft relevance → determines how valid products are ranked.

## Core Idea

**Hard constraints decide whether a product is allowed; soft relevance decides where an allowed product ranks.**

## Example

Reference image:

Red men's T-shirt

Query:

`something similar but black`

VYRA understands:

- Text constraint: black
- Image-derived category: tshirt
- Image-derived gender: men

Final constraints:

- black
- tshirt
- men

Result:

`Free Authority Men's Melting Records Black T-shirt`

## Architecture

User Image + Query
↓
Text Intent Parser
↓
CLIP Image Understanding
↓
Constraint Fusion
↓
Hard Filtering
↓
Semantic + Visual Ranking
↓
Explainable Results

## Models

- Sentence Transformers: `all-MiniLM-L6-v2`
- CLIP: `openai/clip-vit-base-patch32`

## Tech Stack

Backend:
- Python
- FastAPI
- Pandas
- PyTorch
- Transformers
- Sentence Transformers

Frontend:
- React
- Vite
- Lucide React

## Baseline

The initial system used attribute-based search over a fashion catalogue.

## Advanced Solution

The advanced VYRA system adds:

- semantic search
- CLIP visual search
- multimodal ranking
- image-derived intent inference
- text-over-image conflict resolution
- hard constraint enforcement
- explainable search results
- FastAPI backend
- polished React frontend

## Evaluation

30-query constraint-grounded benchmark:

| Engine | Precision@5 | Recall@5 | MRR | NDCG@5 | Constraint Violation Rate |
|---|---:|---:|---:|---:|---:|
| Attribute Search | 0.613 | 0.889 | 1.000 | 1.000 | 0.0% |
| Semantic Search | 0.513 | 0.798 | 0.925 | 0.861 | 48.67% |
| Hybrid VYRA | 0.613 | 0.889 | 1.000 | 1.000 | 0.0% |

The main finding is that semantic relevance alone is not sufficient for commerce search.

## Hot Take

A recommendation can be semantically convincing and still be wrong.

For shopping systems, relevance should happen **after constraint validation**, not instead of it.

## Run Locally

See `REPRODUCTION.md`.

## Agentic Development

The project was developed with ChatGPT as the coding agent.

Representative development trajectories are available in:

`traces/`

They document implementation decisions, failures, debugging, retries, verification, and human checkpoints.

## Competition Development

Pre-existing work:
- initial catalogue
- attribute search
- parser foundations

Added during the challenge:
- semantic search
- hybrid constraint-safe ranking
- evaluation framework
- CLIP visual search
- multimodal search
- image-derived intent
- uploaded-image zero-shot understanding
- multimodal orchestration
- CLIP model reuse
- FastAPI backend
- React frontend
- development traces and evidence

# VYRA — Intelligent Fashion Search

VYRA is a multimodal, constraint-safe fashion discovery system that combines natural-language search, image understanding, semantic relevance, visual similarity, and hard shopping constraints.

## Problem

Traditional semantic search can return results that look relevant while violating explicit user requirements such as colour, category, gender, or price.

VYRA separates:

- Hard constraints → determine whether a product is allowed.
- Soft relevance → determines how valid products are ranked.

## Core Idea

**Hard constraints decide whether a product is allowed; soft relevance decides where an allowed product ranks.**

## Example

Reference image:

Red men's T-shirt

Query:

`something similar but black`

VYRA understands:

- Text constraint: black
- Image-derived category: tshirt
- Image-derived gender: men

Final constraints:

- black
- tshirt
- men

Result:

`Free Authority Men's Melting Records Black T-shirt`

## Architecture

User Image + Query
↓
Text Intent Parser
↓
CLIP Image Understanding
↓
Constraint Fusion
↓
Hard Filtering
↓
Semantic + Visual Ranking
↓
Explainable Results

## Models

- Sentence Transformers: `all-MiniLM-L6-v2`
- CLIP: `openai/clip-vit-base-patch32`

## Tech Stack

Backend:
- Python
- FastAPI
- Pandas
- PyTorch
- Transformers
- Sentence Transformers

Frontend:
- React
- Vite
- Lucide React

## Baseline

The initial system used attribute-based search over a fashion catalogue.

## Advanced Solution

The advanced VYRA system adds:

- semantic search
- CLIP visual search
- multimodal ranking
- image-derived intent inference
- text-over-image conflict resolution
- hard constraint enforcement
- explainable search results
- FastAPI backend
- polished React frontend

## Evaluation

30-query constraint-grounded benchmark:

| Engine | Precision@5 | Recall@5 | MRR | NDCG@5 | Constraint Violation Rate |
|---|---:|---:|---:|---:|---:|
| Attribute Search | 0.613 | 0.889 | 1.000 | 1.000 | 0.0% |
| Semantic Search | 0.513 | 0.798 | 0.925 | 0.861 | 48.67% |
| Hybrid VYRA | 0.613 | 0.889 | 1.000 | 1.000 | 0.0% |

The main finding is that semantic relevance alone is not sufficient for commerce search.

## Hot Take

A recommendation can be semantically convincing and still be wrong.

For shopping systems, relevance should happen **after constraint validation**, not instead of it.

## Run Locally

See `REPRODUCTION.md`.

## Agentic Development

The project was developed with ChatGPT as the coding agent.

Representative development trajectories are available in:

`traces/`

They document implementation decisions, failures, debugging, retries, verification, and human checkpoints.

## Competition Development

Pre-existing work:
- initial catalogue
- attribute search
- parser foundations

Added during the challenge:
- semantic search
- hybrid constraint-safe ranking
- evaluation framework
- CLIP visual search
- multimodal search
- image-derived intent
- uploaded-image zero-shot understanding
- multimodal orchestration
- CLIP model reuse
- FastAPI backend
- React frontend
- development traces and evidence

Notes

The first backend startup can take longer because CLIP and Sentence Transformer models are loaded and the product-image embeddings are generated.


---

### 3. Make sure `requirements.txt` contains at least

```txt
fastapi
uvicorn
python-multipart
pandas
numpy
torch
torchvision
transformers
sentence-transformers
Pillow
scikit-learn
pytest
4. Commit everything NOW

From VYRAV2:

git add README.md REPRODUCTION.md requirements.txt CHANGELOG.md traces
git commit -m "docs: finalize hackathon submission package"
git push

Then:

git status

Need:

nothing to commit, working tree clean