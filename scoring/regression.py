"""
Challenge Arena - Regression Scorer
Computes MSE, MAE, R², RMSE, and MAPE metrics.
"""

import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from .base import BaseScorer


class RegressionScorer(BaseScorer):
    """Scorer for regression challenges."""

    @property
    def required_submission_columns(self):
        return ["predicted_value"]

    @property
    def required_ground_truth_columns(self):
        return ["true_value"]

    @property
    def default_primary_metric(self):
        return "r2_score"

    def available_metrics(self):
        return [
            "mse",
            "rmse",
            "mae",
            "r2_score",
            "mape",
        ]

    def score(self, submission_df, ground_truth_df):
        """
        Score regression submission.
        
        Expected format:
        Submission: id_column, predicted_value
        Ground truth: id_column, true_value
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

        y_pred = merged["predicted_value"].astype(float)
        y_true = merged["true_value"].astype(float)

        metrics = {}

        # MSE
        mse = mean_squared_error(y_true, y_pred)
        metrics["mse"] = round(mse, 4)

        # RMSE
        metrics["rmse"] = round(np.sqrt(mse), 4)

        # MAE
        metrics["mae"] = round(mean_absolute_error(y_true, y_pred), 4)

        # R² Score
        metrics["r2_score"] = round(r2_score(y_true, y_pred), 4)

        # MAPE (Mean Absolute Percentage Error)
        try:
            mape = np.mean(np.abs((y_true - y_pred) / np.maximum(np.abs(y_true), 1e-10))) * 100
            metrics["mape"] = round(mape, 4)
        except Exception:
            metrics["mape"] = None

        # Primary score (R² by default)
        metrics["primary_score"] = metrics.get("r2_score", 0.0)

        # Additional info
        metrics["n_samples"] = len(merged)

        return metrics