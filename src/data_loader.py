import pandas as pd
import numpy as np
from pathlib import Path
from src import config

def load_data(file_path=None) -> pd.DataFrame:
    """
    Loads the stroke prediction dataset.
    """
    path = Path(file_path) if file_path else config.DATA_PATH
    if not path.exists():
        raise FileNotFoundError(f"Dataset file not found at: {path}. Please provide or upload the CSV.")
    
    df = pd.read_csv(path)
    return df

def get_dataset_summary(df: pd.DataFrame = None) -> dict:
    """
    Generates comprehensive dataset statistics for health informatics reporting.
    """
    if df is None:
        df = load_data()

    total_rows = int(len(df))
    total_cols = int(len(df.columns))
    duplicates = int(df.duplicated().sum())
    
    # Missing value analysis
    missing_counts = df.isnull().sum().to_dict()
    missing_pct = ((df.isnull().sum() / total_rows) * 100).round(2).to_dict()
    missing_info = [
        {"column": col, "missing_count": int(missing_counts[col]), "missing_pct": float(missing_pct[col])}
        for col in df.columns if missing_counts[col] > 0
    ]

    # Target variable distribution
    if config.TARGET_COL in df.columns:
        stroke_counts = df[config.TARGET_COL].value_counts().to_dict()
        no_stroke_cnt = int(stroke_counts.get(0, 0))
        stroke_cnt = int(stroke_counts.get(1, 0))
        stroke_rate = round((stroke_cnt / total_rows) * 100, 2) if total_rows > 0 else 0
        target_summary = {
            "no_stroke_count": no_stroke_cnt,
            "stroke_count": stroke_cnt,
            "stroke_percentage": stroke_rate,
            "no_stroke_percentage": round(100 - stroke_rate, 2),
            "imbalance_ratio": f"1:{round(no_stroke_cnt / stroke_cnt, 1)}" if stroke_cnt > 0 else "N/A"
        }
    else:
        target_summary = None

    # Numerical statistics
    num_stats = {}
    for col in config.NUMERICAL_COLS:
        if col in df.columns:
            s = df[col].dropna()
            num_stats[col] = {
                "mean": round(float(s.mean()), 2),
                "std": round(float(s.std()), 2),
                "min": round(float(s.min()), 2),
                "q25": round(float(s.quantile(0.25)), 2),
                "median": round(float(s.median()), 2),
                "q75": round(float(s.quantile(0.75)), 2),
                "max": round(float(s.max()), 2)
            }

    # Categorical distributions
    cat_stats = {}
    for col in config.CATEGORICAL_COLS:
        if col in df.columns:
            cat_stats[col] = {str(k): int(v) for k, v in df[col].value_counts().items()}

    return {
        "total_records": total_rows,
        "total_features": total_cols,
        "columns": df.columns.tolist(),
        "duplicate_rows": duplicates,
        "missing_features": missing_info,
        "target_distribution": target_summary,
        "numerical_statistics": num_stats,
        "categorical_distributions": cat_stats
    }

def get_sample_data(df: pd.DataFrame = None, n: int = 10) -> list:
    """
    Returns the first n rows as dictionaries for table rendering.
    """
    if df is None:
        df = load_data()
    sample_df = df.head(n).copy()
    # Replace NaN with None so JSON serialization handles null gracefully
    sample_df = sample_df.replace({np.nan: None})
    return sample_df.to_dict(orient="records")

def validate_uploaded_csv(filepath: str or Path) -> tuple[bool, str, pd.DataFrame or None]:
    """
    Validates that an uploaded file is a valid CSV and includes all mandatory columns.
    """
    try:
        df = pd.read_csv(filepath)
    except Exception as e:
        return False, f"Failed to parse CSV file: {str(e)}", None

    required_cols = [
        "gender", "age", "hypertension", "heart_disease",
        "avg_glucose_level", "bmi", "smoking_status",
        "work_type", "Residence_type", config.TARGET_COL
    ]
    missing_required = [col for col in required_cols if col not in df.columns]
    if missing_required:
        return False, f"Missing required columns in CSV: {', '.join(missing_required)}", None

    if len(df) < 50:
        return False, "Dataset must contain at least 50 records for meaningful evaluation.", None

    if df[config.TARGET_COL].nunique() < 2:
        return False, "Target column 'stroke' must contain both positive (1) and negative (0) classes.", None

    return True, f"Successfully validated dataset with {len(df)} rows.", df
