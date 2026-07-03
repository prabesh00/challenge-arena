"""
Challenge Arena - Base Scorer
Abstract base class for all challenge type scorers.
"""

from abc import ABC, abstractmethod


class BaseScorer(ABC):
    """Abstract base class for challenge scorers."""

    @property
    @abstractmethod
    def required_submission_columns(self):
        """List of required column names in the submission CSV."""
        pass

    @property
    @abstractmethod
    def required_ground_truth_columns(self):
        """List of required column names in the ground truth CSV."""
        pass

    @property
    @abstractmethod
    def default_primary_metric(self):
        """The default primary metric name for ranking."""
        pass

    @abstractmethod
    def score(self, submission_df, ground_truth_df):
        """
        Score a submission against ground truth.
        
        Args:
            submission_df: pandas DataFrame of the student's submission
            ground_truth_df: pandas DataFrame of the ground truth
            
        Returns:
            dict: Dictionary of metric_name -> value
                  Must include 'primary_score' key for ranking.
        """
        pass

    def validate_submission(self, submission_df):
        """
        Validate submission columns. Returns (is_valid, error_message).
        """
        missing = [col for col in self.required_submission_columns if col not in submission_df.columns]
        if missing:
            return False, f"Missing required columns: {', '.join(missing)}"
        
        # Check for duplicate IDs in the ID column (first column by convention)
        id_col = submission_df.columns[0]
        if submission_df[id_col].duplicated().any():
            return False, f"Duplicate values found in column '{id_col}'"
        
        return True, None

    def validate_ground_truth(self, ground_truth_df):
        """
        Validate ground truth columns. Returns (is_valid, error_message).
        """
        missing = [col for col in self.required_ground_truth_columns if col not in ground_truth_df.columns]
        if missing:
            return False, f"Missing required columns in ground truth: {', '.join(missing)}"
        
        id_col = ground_truth_df.columns[0]
        if ground_truth_df[id_col].duplicated().any():
            return False, f"Duplicate values found in ground truth column '{id_col}'"
        
        return True, None

    def check_id_mismatch(self, submission_df, ground_truth_df):
        """
        Check for ID mismatches between submission and ground truth.
        Returns (is_valid, error_message, missing_ids, extra_ids).
        """
        sub_id_col = submission_df.columns[0]
        gt_id_col = ground_truth_df.columns[0]
        
        sub_ids = set(submission_df[sub_id_col].astype(str))
        gt_ids = set(ground_truth_df[gt_id_col].astype(str))
        
        missing_in_gt = sub_ids - gt_ids  # IDs in submission but not in ground truth
        missing_in_sub = gt_ids - sub_ids  # IDs in ground truth but not in submission
        
        errors = []
        if missing_in_gt:
            errors.append(f"{len(missing_in_gt)} ID(s) in your submission were not found in the test set")
        if missing_in_sub:
            errors.append(f"{len(missing_in_sub)} ID(s) from the test set are missing in your submission")
        
        return (len(errors) == 0, "; ".join(errors), missing_in_gt, missing_in_sub)