"""
Challenge Arena - LLM Scorer
Computes semantic similarity, exact match rates, and LLM-as-judge via OpenRouter.
"""

import numpy as np
import json
import os
import streamlit as st
from .base import BaseScorer


class LLMScorer(BaseScorer):
    """Scorer for LLM evaluation challenges."""

    @property
    def required_submission_columns(self):
        return ["generated_answer"]

    @property
    def required_ground_truth_columns(self):
        return ["expected_answer"]

    @property
    def default_primary_metric(self):
        return "combined_score"

    def available_metrics(self):
        return [
            "exact_match_rate",
            "normalized_match_rate",
            "semantic_similarity",
            "llm_judge_score",
            "combined_score",
        ]

    def score(self, submission_df, ground_truth_df):
        """
        Score LLM submission.
        
        Expected format:
        Submission: question_id, generated_answer [, question_text]
        Ground truth: question_id, expected_answer [, question_text]
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

        generated = merged["generated_answer"].astype(str)
        expected = merged["expected_answer"].astype(str)

        # Get question text if available
        question_col = None
        if "question_text" in merged.columns:
            question_col = "question_text"
        elif "question_text_sub" in merged.columns:
            question_col = "question_text_sub"
        elif "question_text_gt" in merged.columns:
            question_col = "question_text_gt"

        # --- Basic Metrics ---
        # Exact match rate
        metrics["exact_match_rate"] = round(float((generated == expected).mean()), 4)

        # Normalized match rate
        norm_gen = generated.str.strip().str.lower()
        norm_exp = expected.str.strip().str.lower()
        metrics["normalized_match_rate"] = round(float((norm_gen == norm_exp).mean()), 4)

        # --- Semantic Similarity ---
        try:
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer("all-MiniLM-L6-v2")
            embeddings_gen = model.encode(generated.tolist(), convert_to_numpy=True)
            embeddings_exp = model.encode(expected.tolist(), convert_to_numpy=True)

            norms_gen = np.linalg.norm(embeddings_gen, axis=1, keepdims=True)
            norms_exp = np.linalg.norm(embeddings_exp, axis=1, keepdims=True)
            cosine_sim = np.sum(embeddings_gen * embeddings_exp, axis=1) / (norms_gen.flatten() * norms_exp.flatten() + 1e-10)
            metrics["semantic_similarity"] = round(float(np.mean(cosine_sim)), 4)
        except Exception as e:
            metrics["semantic_similarity"] = 0.0
            metrics["_semantic_error"] = str(e)

        # --- LLM-as-Judge via OpenRouter ---
        try:
            api_key = os.environ.get("OPENROUTER_API_KEY") or st.secrets.get("openrouter_api_key", "")
            model_name = os.environ.get("OPENROUTER_MODEL") or st.secrets.get("openrouter_model", "openai/gpt-4o")

            if api_key:
                from openai import OpenAI
                client = OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=api_key,
                )

                scores = []
                for idx, row in merged.iterrows():
                    question = row.get(question_col, f"Question {idx}") if question_col else f"Question {idx}"
                    expected_ans = row["expected_answer"]
                    generated_ans = row["generated_answer"]

                    prompt = f"""You are an AI answer evaluator. Rate the quality of the student's answer on a scale of 0 to 100.

Question: {question}
Expected Answer: {expected_ans}
Student's Answer: {generated_ans}

Return ONLY a JSON object with two fields: "score" (a number 0-100) and "reasoning" (a brief explanation)."""

                    response = client.chat.completions.create(
                        model=model_name,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.1,
                        max_tokens=200,
                    )

                    content = response.choices[0].message.content.strip()
                    try:
                        # Try to parse JSON response
                        if content.startswith("```"):
                            content = content.split("```")[1]
                            if content.startswith("json"):
                                content = content[4:]
                        result = json.loads(content)
                        score = float(result.get("score", 50))
                    except (json.JSONDecodeError, ValueError):
                        # Fallback: try to extract number
                        import re
                        numbers = re.findall(r'\d+\.?\d*', content)
                        score = float(numbers[0]) if numbers else 50.0

                    scores.append(min(max(score, 0.0), 100.0))  # Clamp to 0-100

                if scores:
                    metrics["llm_judge_score"] = round(float(np.mean(scores)) / 100.0, 4)  # Normalize to 0-1
                    metrics["_llm_judge_details"] = {
                        "model": model_name,
                        "n_judged": len(scores),
                        "raw_scores": [round(s, 1) for s in scores],
                    }
                else:
                    metrics["llm_judge_score"] = 0.0
            else:
                metrics["llm_judge_score"] = 0.0
                metrics["_llm_judge_error"] = "No OpenRouter API key configured"
        except Exception as e:
            metrics["llm_judge_score"] = 0.0
            metrics["_llm_judge_error"] = str(e)

        # --- Combined Score (average of semantic similarity and LLM judge) ---
        sem_sim = metrics.get("semantic_similarity", 0.0)
        llm_score = metrics.get("llm_judge_score", 0.0)
        if llm_score > 0:
            metrics["combined_score"] = round((sem_sim + llm_score) / 2, 4)
        else:
            metrics["combined_score"] = sem_sim

        # Primary score
        metrics["primary_score"] = metrics.get("combined_score", 0.0)

        # Additional info
        metrics["n_samples"] = len(merged)

        return metrics