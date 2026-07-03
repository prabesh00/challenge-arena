"""
Challenge Arena - Classification Scorer
Computes accuracy, precision, recall, F1, and AUC-ROC metrics.
"""

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
)
from .base import BaseScorer


class ClassificationScorer(BaseScorer):
    """Scorer for classification challenges."""

    @property
    def required_submission_columns(self):
        return ["predicted_label"]

    @property
    def required_ground_truth_columns(self):
        return ["true_label"]

    @property
    def default_primary_metric(self):
        return "accuracy"

    def available_metrics(self):
        return [
            "accuracy",
            "precision_macro",
            "precision_weighted",
            "recall_macro",
            "recall_weighted",
            "f1_macro",
            "f1_weighted",
            "auc_roc_ovr",
            "confusion_matrix",
        ]

    def score(self, submission_df, ground_truth_df):
        """
        Score classification submission.
        
        Expected format:
        Submission: id_column, predicted_label
        Ground truth: id_column, true_label
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

        y_pred = merged["predicted_label"]
        y_true = merged["true_label"]

        # Ensure string type for label comparison
        y_pred = y_pred.astype(str)
        y_true = y_true.astype(str)

        metrics = {}

        # Basic metrics
        metrics["accuracy"] = round(accuracy_score(y_true, y_pred), 4)
        metrics["precision_macro"] = round(precision_score(y_true, y_pred, average="macro", zero_division=0), 4)
        metrics["precision_weighted"] = round(precision_score(y_true, y_pred, average="weighted", zero_division=0), 4)
        metrics["recall_macro"] = round(recall_score(y_true, y_pred, average="macro", zero_division=0), 4)
        metrics["recall_weighted"] = round(recall_score(y_true, y_pred, average="weighted", zero_division=0), 4)
        metrics["f1_macro"] = round(f1_score(y_true, y_pred, average="macro", zero_division=0), 4)
        metrics["f1_weighted"] = round(f1_score(y_true, y_pred, average="weighted", zero_division=0), 4)

        # AUC-ROC (One-vs-Rest for multiclass)
        try:
            unique_classes = np.unique(np.concatenate([y_true, y_pred]))
            if len(unique_classes) == 2:
                # Binary classification
                y_true_bin = (y_true == unique_classes[1]).astype(int)
                y_pred_bin = (y_pred == unique_classes[1]).astype(int)
                metrics["auc_roc_ovr"] = round(roc_auc_score(y_true_bin, y_pred_bin), 4)
            elif len(unique_classes) > 2:
                # Multiclass - use OVR
                from sklearn.preprocessing import LabelBinarizer
                lb = LabelBinarizer()
                y_true_bin = lb.fit_transform(y_true)
                y_pred_bin = lb.transform(y_pred)
                metrics["auc_roc_ovr"] = round(roc_auc_score(y_true_bin, y_pred_bin, multi_class="ovr"), 4)
            else:
                metrics["auc_roc_ovr"] = 1.0
        except Exception:
            metrics["auc_roc_ovr"] = None

        # Confusion matrix (as list of lists for JSON serialization)
        try:
            cm = confusion_matrix(y_true, y_pred)
            metrics["confusion_matrix"] = cm.tolist()
            metrics["confusion_matrix_labels"] = sorted(set(y_true) | set(y_pred))
        except Exception:
            metrics["confusion_matrix"] = None

        # Primary score (accuracy by default)
        metrics["primary_score"] = metrics.get("accuracy", 0.0)

        # Additional info
        metrics["n_samples"] = len(merged)
        metrics["n_classes"] = len(set(y_true) | set(y_pred))

        return metrics