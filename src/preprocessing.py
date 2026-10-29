import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from src import config

def clean_data(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """
    Cleans raw dataset, drops duplicates, removes ID, and separates features and target.
    Filters out any invalid gender row ('Other' - only 1 occurrence in Kaggle cohort).
    """
    cleaned_df = df.copy()

    # 1. Remove duplicate records
    cleaned_df = cleaned_df.drop_duplicates()

    # 2. Filter out rare/invalid 'Other' gender row if present
    if "gender" in cleaned_df.columns:
        cleaned_df = cleaned_df[cleaned_df["gender"].isin(["Male", "Female"])]

    # 3. Drop patient ID (non-predictive identifier)
    if config.ID_COL in cleaned_df.columns:
        cleaned_df = cleaned_df.drop(columns=[config.ID_COL])

    if config.TARGET_COL not in cleaned_df.columns:
        raise ValueError(f"Target column '{config.TARGET_COL}' not found in dataset.")

    # 4. Separate X and y
    X = cleaned_df.drop(columns=[config.TARGET_COL])
    y = cleaned_df[config.TARGET_COL].astype(int)

    return X, y

def build_preprocessor() -> ColumnTransformer:
    """
    Constructs a Scikit-Learn ColumnTransformer pipeline.
    Ensures zero data leakage: Imputers and Scalers are fitted ONLY on training data.
    - Numerical features (age, glucose, bmi): Median imputation + StandardScaler
    - Categorical features: Most frequent imputation + OneHotEncoder (handle_unknown='ignore')
    """
    numerical_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])

    categorical_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numerical_transformer, config.NUMERICAL_COLS),
            ("cat", categorical_transformer, config.CATEGORICAL_COLS)
        ],
        remainder="drop"
    )

    return preprocessor

def prepare_train_test_split(X: pd.DataFrame, y: pd.Series, test_size: float = 0.2, random_state: int = 42):
    """
    Performs stratified 80/20 train-test split to preserve target class proportions.
    """
    return train_test_split(
        X, y,
        test_size=test_size,
        random_state=random_state,
        stratify=y
    )

def get_preprocessing_metadata(df: pd.DataFrame = None) -> list:
    """
    Returns step-by-step documentation of the preprocessing pipeline for the UI walkthrough.
    """
    return [
        {
            "step": 1,
            "name": "Missing Value Detection & Handling",
            "technique": "Median Imputation inside Pipeline",
            "description": "In the raw dataset, BMI had ~201 missing values (~3.9%). Rather than deleting incomplete patient rows, the median BMI from the training set is imputed. Placing SimpleImputer inside the Scikit-learn Pipeline guarantees that test set values are never observed during training, eliminating data leakage.",
            "leakage_protection": "Learned strictly from training folds (fit_transform on X_train, transform on X_test)."
        },
        {
            "step": 2,
            "name": "Duplicate & Anomaly Removal",
            "technique": "Deduplication & Category Filtering",
            "description": "Checked for exact duplicate patient records. Handled the single 'Other' gender entry by restricting the model to validated demographic categories ('Male' and 'Female'). The non-predictive clinical identifier ('id') was dropped.",
            "leakage_protection": "Record-level filtering applied prior to partition."
        },
        {
            "step": 3,
            "name": "Categorical Feature Encoding",
            "technique": "One-Hot Encoding with handle_unknown='ignore'",
            "description": "Categorical variables ('gender', 'work_type', 'Residence_type', 'smoking_status', 'ever_married') are converted into one-hot binary indicator vectors. Unknown categories at inference time default to zero vectors rather than throwing unhandled exceptions.",
            "leakage_protection": "Categories discovered and mapped strictly from training data."
        },
        {
            "step": 4,
            "name": "Continuous Feature Standardization",
            "technique": "StandardScaler (Z-Score Normalization)",
            "description": "Continuous physiological predictors (Age, Average Blood Glucose Level, BMI) have distinct units and variance. Standardization (mean = 0, std = 1) prevents high-magnitude features like Glucose from dominating regularized Logistic Regression coefficients.",
            "leakage_protection": "Means (μ) and standard deviations (σ) calculated solely on training splits."
        },
        {
            "step": 5,
            "name": "Stratified Train-Test Splitting",
            "technique": "Stratified Shuffle Split (80% Train, 20% Test)",
            "description": "Because stroke accounts for only ~4.9% of total cases, unstratified random sampling risks severe class variance or zero positive instances in small validation batches. Stratified splitting enforces exact 4.9% positive representation in both training (80%) and held-out test (20%) sets.",
            "leakage_protection": "Held-out test set (n=1,022) remains completely untouched until final evaluation."
        },
        {
            "step": 6,
            "name": "Class Imbalance Mitigation",
            "technique": "Cost-Sensitive Loss Weighting (class_weight='balanced')",
            "description": "Standard cross-entropy and Gini impurity penalize errors equally, encouraging models to optimize for the majority class (95.1% negative). Cost-sensitive weighting computes inverse class frequencies, scaling minority class misclassification penalties inversely proportional to class prevalence. This provides recall amplification without generating synthetic boundary artifacts.",
            "leakage_protection": "Weights derived directly from training class distributions."
        }
    ]
