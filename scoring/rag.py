"""
Challenge Arena - RAG Scorer
Computes retrieval metrics (Precision@k, Recall@k, MRR) and semantic similarity.
"""

import numpy as np
from .base import BaseScorer


class RAGScorer(BaseScorer):
    """Scorer for RAG (Retrieval Augmented Generation) challenges."""

    @property
    def required_submission_columns(self):
        return ["generated_answer"]

    @property
    def required_ground_truth_columns(self):
        return ["expected_answer"]

    @property
    def default_primary_metric(self):
        return "semantic_similarity"

    def available_metrics(self):
        return [
            "exact_match_rate",
            "normalized_match_rate",
            "semantic_similarity",
            "retrieval_precision_at_k",
            "retrieval_recall_at_k",
            "mrr",
        ]

    def score(self, submission_df, ground_truth_df):
        """
        Score RAG submission.
        
        Expected format:
        Submission: question_id, generated_answer [, retrieved_doc_ids]
        Ground truth: question_id, expected_answer [, relevant_doc_ids]
        """
        id_col_sub = submission_df.columns[0]
        id_col_gt = ground_truth_df.columns[0]

        # Merge on ID column
        merged = submission_df.merge(
            ground_truth_df,
            left_on=id_col_sub,
            right_on=id_col_gt,
            how="inner",
            suffixes=("_sub", "_gt"),
        )

        metrics = {}

        # --- Answer Quality Metrics ---
        generated = merged["generated_answer"].astype(str)
        expected = merged["expected_answer"].astype(str)

        # Exact match rate
        metrics["exact_match_rate"] = round(float((generated == expected).mean()), 4)

        # Normalized match rate (case-insensitive, strip whitespace)
        norm_gen = generated.str.strip().str.lower()
        norm_exp = expected.str.strip().str.lower()
        metrics["normalized_match_rate"] = round(float((norm_gen == norm_exp).mean()), 4)

        # Semantic similarity using sentence-transformers
        try:
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer("all-MiniLM-L6-v2")
            embeddings_gen = model.encode(generated.tolist(), convert_to_numpy=True)
            embeddings_exp = model.encode(expected.tolist(), convert_to_numpy=True)

            # Cosine similarity
            norms_gen = np.linalg.norm(embeddings_gen, axis=1, keepdims=True)
            norms_exp = np.linalg.norm(embeddings_exp, axis=1, keepdims=True)
            cosine_sim = np.sum(embeddings_gen * embeddings_exp, axis=1) / (norms_gen.flatten() * norms_exp.flatten() + 1e-10)
            metrics["semantic_similarity"] = round(float(np.mean(cosine_sim)), 4)
        except Exception as e:
            metrics["semantic_similarity"] = 0.0
            metrics["_semantic_error"] = str(e)

        # --- Retrieval Metrics (if retrieved_doc_ids and relevant_doc_ids are present) ---
        has_retrieval = "retrieved_doc_ids" in submission_df.columns and "relevant_doc_ids" in ground_truth_df.columns

        if has_retrieval:
            precision_at_k_list = []
            recall_at_k_list = []
            mrr_list = []

            for _, row in merged.iterrows():
                retrieved = str(row["retrieved_doc_ids"]).split("|")
                retrieved = [r.strip() for r in retrieved if r.strip()]
                relevant = str(row["relevant_doc_ids"]).split("|")
                relevant = [r.strip() for r in relevant if r.strip()]

                if not relevant:
                    continue

                k = len(retrieved)
                if k == 0:
                    precision_at_k_list.append(0.0)
                    recall_at_k_list.append(0.0)
                    mrr_list.append(0.0)
                    continue

                # Precision@k
                retrieved_set = set(retrieved)
                relevant_set = set(relevant)
                hits = len(retrieved_set & relevant_set)
                precision_at_k_list.append(hits / k)

                # Recall@k
                recall_at_k_list.append(hits / len(relevant_set))

                # MRR (Mean Reciprocal Rank)
                for rank, doc_id in enumerate(retrieved, 1):
                    if doc_id in relevant_set:
                        mrr_list.append(1.0 / rank)
                        break
                else:
                    mrr_list.append(0.0)

            if precision_at_k_list:
                metrics["retrieval_precision_at_k"] = round(float(np.mean(precision_at_k_list)), 4)
                metrics["retrieval_recall_at_k"] = round(float(np.mean(recall_at_k_list)), 4)
                metrics["mrr"] = round(float(np.mean(mrr_list)), 4)
            else:
                metrics["retrieval_precision_at_k"] = 0.0
                metrics["retrieval_recall_at_k"] = 0.0
                metrics["mrr"] = 0.0

        # Primary score (semantic similarity by default)
        metrics["primary_score"] = metrics.get("semantic_similarity", 0.0)

        # Additional info
        metrics["n_samples"] = len(merged)
        metrics["has_retrieval_metrics"] = has_retrieval

        return metrics