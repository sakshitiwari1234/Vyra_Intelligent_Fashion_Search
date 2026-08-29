from pathlib import Path
import math

import pandas as pd

from backend.services.query_parser import parse_query
from backend.services.filters import apply_hard_filters
from backend.services.semantic_search import SemanticSearchEngine
from backend.services.hybrid_search import HybridSearchEngine


PROJECT_ROOT = Path(__file__).resolve().parent

PRODUCTS_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "products_v2_enriched.csv"
)

EVALUATION_PATH = (
    PROJECT_ROOT
    / "data"
    / "evaluation"
    / "search_queries.csv"
)


TOP_K = 5


products = pd.read_csv(PRODUCTS_PATH)
evaluation = pd.read_csv(EVALUATION_PATH)


def parse_relevant_ids(value):
    """
    Supports:
    31660
    or
    31660;11033;20668
    """

    return {
        int(product_id.strip())
        for product_id in str(value).split(";")
        if product_id.strip()
    }


def attribute_search(query, top_k=TOP_K):
    intent = parse_query(query)

    results = apply_hard_filters(
        products,
        intent,
    )

    return results.head(top_k)


print("Loading semantic engine...")

semantic_engine = SemanticSearchEngine(
    products
)

print("Loading hybrid engine...")

hybrid_engine = HybridSearchEngine(
    products,
    semantic_engine=semantic_engine,
)    

print("Evaluation engines ready.")


def precision_at_k(result_ids, relevant_ids, k):
    top_results = result_ids[:k]

    if k == 0:
        return 0.0

    relevant_found = sum(
        product_id in relevant_ids
        for product_id in top_results
    )

    return relevant_found / k


def recall_at_k(result_ids, relevant_ids, k):
    if not relevant_ids:
        return 0.0

    top_results = result_ids[:k]

    relevant_found = sum(
        product_id in relevant_ids
        for product_id in top_results
    )

    return relevant_found / len(relevant_ids)


def reciprocal_rank(result_ids, relevant_ids):
    for rank, product_id in enumerate(
        result_ids,
        start=1,
    ):
        if product_id in relevant_ids:
            return 1.0 / rank

    return 0.0


def ndcg_at_k(result_ids, relevant_ids, k):

    dcg = 0.0

    for index, product_id in enumerate(
        result_ids[:k],
        start=1,
    ):
        relevance = (
            1
            if product_id in relevant_ids
            else 0
        )

        if relevance:
            dcg += (
                relevance
                / math.log2(index + 1)
            )

    ideal_relevant_count = min(
        len(relevant_ids),
        k,
    )

    idcg = sum(
        1 / math.log2(index + 1)
        for index in range(
            1,
            ideal_relevant_count + 1,
        )
    )

    if idcg == 0:
        return 0.0

    return dcg / idcg


def constraint_violation_rate(
    results,
    query,
):

    if results.empty:
        return 0.0

    intent = parse_query(query)

    valid_results = apply_hard_filters(
        results,
        intent,
    )

    violations = (
        len(results)
        - len(valid_results)
    )

    return violations / len(results)


def evaluate_engine(
    engine_name,
    search_function,
):

    metrics = []

    zero_results = 0

    print(
        "\n"
        + "=" * 80
    )

    print(
        "ENGINE:",
        engine_name,
    )

    for _, row in evaluation.iterrows():

        query = row["query"]

        relevant_ids = parse_relevant_ids(
            row["relevant_product_ids"]
        )

        results = search_function(
            query
        )

        result_ids = (
            results["product_id"]
            .astype(int)
            .tolist()
        )

        if len(result_ids) == 0:
            zero_results += 1

        precision = precision_at_k(
            result_ids,
            relevant_ids,
            TOP_K,
        )

        recall = recall_at_k(
            result_ids,
            relevant_ids,
            TOP_K,
        )

        rr = reciprocal_rank(
            result_ids,
            relevant_ids,
        )

        ndcg = ndcg_at_k(
            result_ids,
            relevant_ids,
            TOP_K,
        )

        violation_rate = (
            constraint_violation_rate(
                results,
                query,
            )
        )

        metrics.append(
            {
                "query": query,
                "precision": precision,
                "recall": recall,
                "rr": rr,
                "ndcg": ndcg,
                "constraint_violation": violation_rate,
            }
        )

        print(
            f"\nQuery: {query}"
        )

        print(
            "Result IDs:",
            result_ids,
        )

        print(
            "Relevant:",
            sorted(relevant_ids),
        )

    metric_df = pd.DataFrame(
        metrics
    )

    summary = {
        "engine": engine_name,

        f"Precision@{TOP_K}":
            metric_df["precision"].mean(),

        f"Recall@{TOP_K}":
            metric_df["recall"].mean(),

        "MRR":
            metric_df["rr"].mean(),

        f"NDCG@{TOP_K}":
            metric_df["ndcg"].mean(),

        "Constraint Violation Rate":
            metric_df[
                "constraint_violation"
            ].mean(),

        "Zero Result Rate":
            zero_results
            / len(evaluation),
    }

    return summary


attribute_summary = evaluate_engine(
    "Attribute Search",
    lambda query:
    attribute_search(
        query,
        TOP_K,
    ),
)


semantic_summary = evaluate_engine(
    "Semantic Search",
    lambda query:
    semantic_engine.search(
        query,
        top_k=TOP_K,
    ),
)


hybrid_summary = evaluate_engine(
    "Hybrid VYRA",
    lambda query:
    hybrid_engine.search(
        query,
        top_k=TOP_K,
    ),
)


summary_df = pd.DataFrame(
    [
        attribute_summary,
        semantic_summary,
        hybrid_summary,
    ]
)


print(
    "\n\n"
    + "=" * 100
)

print(
    "FINAL EVALUATION SUMMARY"
)

print(
    "=" * 100
)

print(
    summary_df.to_string(
        index=False
    )
)


OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "evaluation"
    / "evaluation_results.csv"
)


summary_df.to_csv(
    OUTPUT_PATH,
    index=False,
)


print(
    "\nResults saved to:"
)

print(
    OUTPUT_PATH
)