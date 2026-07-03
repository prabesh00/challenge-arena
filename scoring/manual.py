"""
Challenge Arena - Manual Scorer
For code challenges and other manually-graded submissions.
"""

from .base import BaseScorer


class ManualScorer(BaseScorer):
    """Scorer for manually-graded challenges (e.g., code challenges)."""

    @property
    def required_submission_columns(self):
        return []  # No strict column requirements - submissions are code files/links

    @property
    def required_ground_truth_columns(self):
        return []  # No ground truth needed - manual grading

    @property
    def default_primary_metric(self):
        return "manual_score"

    def available_metrics(self):
        return [
            "manual_score",
        ]

    def score(self, submission_df, ground_truth_df):
        """
        For manual scoring, this is a placeholder.
        Actual scoring happens via admin UI.
        
        Returns a placeholder result.
        """
        return {
            "manual_score": None,
            "primary_score": None,
            "status": "pending_review",
            "n_samples": len(submission_df) if submission_df is not None else 0,
        }

    def validate_submission(self, submission_df):
        """
        For code challenges, submissions are typically zip files or GitHub links.
        CSV validation is minimal.
        """
        return True, None

    def validate_ground_truth(self, ground_truth_df):
        """No ground truth needed for manual challenges."""
        return True, None

    def check_id_mismatch(self, submission_df, ground_truth_df):
        """No ID mismatch check needed for manual challenges."""
        return True, None, set(), set()