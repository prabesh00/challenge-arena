"""
Challenge Arena - Scorer Registry
Maps challenge types to their scorer implementations.
"""

from .base import BaseScorer
from .classification import ClassificationScorer
from .regression import RegressionScorer
from .rag import RAGScorer
from .llm import LLMScorer
from .manual import ManualScorer

# Registry mapping challenge type strings to scorer classes
SCORER_REGISTRY = {
    "classification": ClassificationScorer,
    "regression": RegressionScorer,
    "rag": RAGScorer,
    "llm": LLMScorer,
    "code_challenge": ManualScorer,
}

# Display names for challenge types
CHALLENGE_TYPE_NAMES = {
    "classification": "Classification",
    "regression": "Regression",
    "rag": "RAG (Retrieval Augmented Generation)",
    "llm": "LLM Evaluation",
    "code_challenge": "Code Challenge (Manual Scoring)",
}

# Default primary metrics per type
DEFAULT_PRIMARY_METRICS = {
    "classification": "accuracy",
    "regression": "r2_score",
    "rag": "semantic_similarity",
    "llm": "combined_score",
    "code_challenge": "manual_score",
}


def get_scorer(challenge_type):
    """Get the scorer instance for a challenge type."""
    scorer_class = SCORER_REGISTRY.get(challenge_type)
    if scorer_class is None:
        raise ValueError(f"Unknown challenge type: {challenge_type}")
    return scorer_class()


def get_available_metrics(challenge_type):
    """Get the list of available metrics for a challenge type."""
    scorer = get_scorer(challenge_type)
    return scorer.available_metrics()


def get_default_primary_metric(challenge_type):
    """Get the default primary metric for a challenge type."""
    return DEFAULT_PRIMARY_METRICS.get(challenge_type, "accuracy")