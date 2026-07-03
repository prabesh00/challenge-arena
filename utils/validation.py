"""
Challenge Arena - CSV Validation Utilities
Validates submission and ground truth CSVs.
"""

import pandas as pd
from pathlib import Path


ALLOWED_EXTENSIONS = {".csv"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def validate_file_type(filename):
    """Check if the file has an allowed extension."""
    ext = Path(filename).suffix.lower()
    return ext in ALLOWED_EXTENSIONS


def validate_file_size(file_bytes):
    """Check if the file size is within limits."""
    return len(file_bytes) <= MAX_FILE_SIZE


def read_csv_safe(file_path_or_bytes):
    """Safely read a CSV file, handling encoding issues."""
    try:
        if isinstance(file_path_or_bytes, (str, Path)):
            df = pd.read_csv(file_path_or_bytes)
        else:
            df = pd.read_csv(file_path_or_bytes)
        return df, None
    except Exception as e:
        return None, f"Could not read CSV file: {str(e)}"


def validate_submission_csv(df, scorer):
    """Validate a submission CSV against a scorer's requirements."""
    from scoring.base import BaseScorer
    
    # Check basic structure
    if df.empty:
        return False, "Submission CSV is empty"
    
    if len(df.columns) < 2:
        return False, "Submission CSV must have at least 2 columns (ID column + prediction column)"
    
    # Check required columns via scorer
    if hasattr(scorer, 'validate_submission'):
        return scorer.validate_submission(df)
    
    return True, None


def validate_ground_truth_csv(df, scorer):
    """Validate a ground truth CSV against a scorer's requirements."""
    if df.empty:
        return False, "Ground truth CSV is empty"
    
    if len(df.columns) < 2:
        return False, "Ground truth CSV must have at least 2 columns (ID column + label column)"
    
    # Check required columns via scorer
    if hasattr(scorer, 'validate_ground_truth'):
        return scorer.validate_ground_truth(df)
    
    return True, None