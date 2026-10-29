import os
os.environ["MPLCONFIGDIR"] = os.path.abspath("models")
import json
import time
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import joblib

from sklearn.model_selection import StratifiedKFold, GridSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, confusion_matrix,
    roc_curve, precision_recall_curve
)

from src import config
from src.data_loader import load_data
from src.preprocessing import clean_data, build_preprocessor, prepare_train_test_split

os.environ["MPLCONFIGDIR"] = str(config.MODELS_DIR)

def compute_metrics(y_true, y_pred, y_prob):
    """
    Computes standard healthcare diagnostic performance metrics.
    """
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0

    return {
        "accuracy": round(float(accuracy_score(y_true, y_pred)), 4),
        "precision": round(float(precision_score(y_true, y_pred, zero_division=0)), 4),
        "recall": round(float(recall_score(y_true, y_pred, zero_division=0)), 4),
        "specificity": round(float(specificity), 4),
        "f1_score": round(float(f1_score(y_true, y_pred, zero_division=0)), 4),
        "roc_auc": round(float(roc_auc_score(y_true, y_prob)), 4),
        "pr_auc": round(float(average_precision_score(y_true, y_prob)), 4),
        "confusion_matrix": {
            "tn": int(tn),
            "fp": int(fp),
            "fn": int(fn),
            "tp": int(tp)
        }
    }

def train_and_evaluate(data_path: str = None) -> dict:
    """
    Executes the full machine learning training, cross-validation, hyperparameter tuning,
    model comparison, evaluation on held-out test split, and artifact persistence.
    """
    start_time = time.time()
    raw_df = load_data(data_path)
    X, y = clean_data(raw_df)

    # 80/20 Stratified Split
    X_train, X_test, y_train, y_test = prepare_train_test_split(X, y, test_size=0.2, random_state=42)

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    # ------------------------------------------------------------------
    # 1. Logistic Regression Pipeline & Grid Search
    # ------------------------------------------------------------------
    lr_pipeline = Pipeline([
        ("preprocessor", build_preprocessor()),
        ("classifier", LogisticRegression(class_weight="balanced", max_iter=1000, random_state=42))
    ])

    lr_param_grid = {
        "classifier__C": [0.01, 0.1, 1.0, 10.0],
        "classifier__solver": ["lbfgs", "liblinear"]
    }

    print("Running Stratified 5-Fold Grid Search for Logistic Regression...")
    lr_grid = GridSearchCV(
        lr_pipeline,
        param_grid=lr_param_grid,
        cv=cv,
        scoring="roc_auc",
        n_jobs=1
    )
    lr_grid.fit(X_train, y_train)
    best_lr = lr_grid.best_estimator_

    # ------------------------------------------------------------------
    # 2. Random Forest Classifier Pipeline & Grid Search
    # ------------------------------------------------------------------
    rf_pipeline = Pipeline([
        ("preprocessor", build_preprocessor()),
        ("classifier", RandomForestClassifier(class_weight="balanced", random_state=42))
    ])

    rf_param_grid = {
        "classifier__n_estimators": [50, 100, 200],
        "classifier__max_depth": [None, 6, 12],
        "classifier__min_samples_split": [2, 5],
        "classifier__min_samples_leaf": [1, 2]
    }

    print("Running Stratified 5-Fold Grid Search for Random Forest...")
    rf_grid = GridSearchCV(
        rf_pipeline,
        param_grid=rf_param_grid,
        cv=cv,
        scoring="roc_auc",
        n_jobs=1
    )
    rf_grid.fit(X_train, y_train)
    best_rf = rf_grid.best_estimator_

    # ------------------------------------------------------------------
    # 3. Held-out Test Set Evaluation
    # ------------------------------------------------------------------
    y_test_pred_lr = best_lr.predict(X_test)
    y_test_prob_lr = best_lr.predict_proba(X_test)[:, 1]
    lr_metrics = compute_metrics(y_test, y_test_pred_lr, y_test_prob_lr)
    lr_metrics["cv_roc_auc_mean"] = round(float(lr_grid.best_score_), 4)
    lr_metrics["best_params"] = {k.replace("classifier__", ""): v for k, v in lr_grid.best_params_.items()}

    y_test_pred_rf = best_rf.predict(X_test)
    y_test_prob_rf = best_rf.predict_proba(X_test)[:, 1]
    rf_metrics = compute_metrics(y_test, y_test_pred_rf, y_test_prob_rf)
    rf_metrics["cv_roc_auc_mean"] = round(float(rf_grid.best_score_), 4)
    rf_metrics["best_params"] = {k.replace("classifier__", ""): v for k, v in rf_grid.best_params_.items()}

    # ------------------------------------------------------------------
    # 4. Model Selection Logic
    # ------------------------------------------------------------------
    # In clinical screening under rare event conditions (4.9% prevalence),
    # ROC-AUC and Recall (Sensitivity) determine clinical safety to minimize false negatives.
    # We compare validation ROC-AUC and held-out test recall.
    if lr_metrics["cv_roc_auc_mean"] >= rf_metrics["cv_roc_auc_mean"] and lr_metrics["recall"] >= 0.70:
        best_model_name = "Logistic Regression"
        best_model_obj = best_lr
        best_metrics = lr_metrics
        selection_rationale = (
            "Logistic Regression was selected as the champion model. It achieved superior cross-validated ROC-AUC "
            f"({lr_metrics['cv_roc_auc_mean']:.4f}) and high sensitivity/recall ({lr_metrics['recall']*100:.1f}%), "
            "which is critical in acute stroke screening to prevent missed life-threatening cases. Its linear log-odds "
            "coefficients also provide clinical interpretability essential in healthcare."
        )
    else:
        best_model_name = "Random Forest Classifier"
        best_model_obj = best_rf
        best_metrics = rf_metrics
        selection_rationale = (
            "Random Forest Classifier was selected as the champion model. It demonstrated stronger non-linear discrimination "
            f"and cross-validated ROC-AUC ({rf_metrics['cv_roc_auc_mean']:.4f}) with balanced precision and recall."
        )

    # ------------------------------------------------------------------
    # 5. Persist Models & Pipelines with Joblib
    # ------------------------------------------------------------------
    joblib.dump(best_lr, config.LOGISTIC_MODEL_PATH)
    joblib.dump(best_rf, config.RANDOM_FOREST_PATH)
    joblib.dump(best_model_obj, config.BEST_MODEL_PATH)

    # ------------------------------------------------------------------
    # 6. Generate Evaluation Visualizations (Confusion Matrices & Curves)
    # ------------------------------------------------------------------
    generate_evaluation_plots(y_test, y_test_prob_lr, y_test_prob_rf, y_test_pred_lr, y_test_pred_rf)

    # ------------------------------------------------------------------
    # 7. Compile Evaluation Results
    # ------------------------------------------------------------------
    total_time = round(time.time() - start_time, 2)
    evaluation_summary = {
        "status": "success",
        "training_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "training_duration_seconds": total_time,
        "train_set_size": int(len(X_train)),
        "test_set_size": int(len(X_test)),
        "target_prevalence_train": round(float(y_train.mean()) * 100, 2),
        "target_prevalence_test": round(float(y_test.mean()) * 100, 2),
        "champion_model": best_model_name,
        "champion_rationale": selection_rationale,
        "models": {
            "logistic_regression": {
                "display_name": "Logistic Regression (Balanced Weights)",
                "validation_roc_auc": lr_metrics["cv_roc_auc_mean"],
                "best_hyperparameters": lr_metrics["best_params"],
                "test_metrics": lr_metrics
            },
            "random_forest": {
                "display_name": "Random Forest Classifier (Balanced Weights)",
                "validation_roc_auc": rf_metrics["cv_roc_auc_mean"],
                "best_hyperparameters": rf_metrics["best_params"],
                "test_metrics": rf_metrics
            }
        },
        "clinical_evaluation_guidance": (
            "Because stroke cases represent only ~4.9% of the dataset, traditional Accuracy is misleadingly inflated. "
            "In healthcare informatics, Recall (Sensitivity) measures the proportion of true stroke patients accurately "
            "flagged (minimizing fatal False Negatives), while PR-AUC (Average Precision) captures predictive precision "
            "across all probability thresholds in highly unbalanced clinical populations."
        )
    }

    with open(config.EVALUATION_RESULTS_PATH, "w") as f:
        json.dump(evaluation_summary, f, indent=2)

    print("Model training and evaluation successfully completed!")
    return evaluation_summary

def generate_evaluation_plots(y_test, y_prob_lr, y_prob_rf, y_pred_lr, y_pred_rf):
    """
    Renders and saves Confusion Matrix comparisons and ROC / PR Curve charts.
    """
    output_dir = config.IMAGES_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Confusion Matrices Comparison
    cm_lr = confusion_matrix(y_test, y_pred_lr)
    cm_rf = confusion_matrix(y_test, y_pred_rf)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    labels = ["No Stroke (0)", "Stroke (1)"]

    sns.heatmap(cm_lr, annot=True, fmt="d", cmap="Blues", cbar=False, ax=ax1,
                xticklabels=labels, yticklabels=labels, annot_kws={"size": 13, "weight": "bold"})
    ax1.set_title("Logistic Regression\nConfusion Matrix (Test Set)", pad=12, fontweight="bold", color="#0f2942")
    ax1.set_xlabel("Predicted Diagnosis")
    ax1.set_ylabel("Actual Clinical Outcome")

    sns.heatmap(cm_rf, annot=True, fmt="d", cmap="Blues", cbar=False, ax=ax2,
                xticklabels=labels, yticklabels=labels, annot_kws={"size": 13, "weight": "bold"})
    ax2.set_title("Random Forest Classifier\nConfusion Matrix (Test Set)", pad=12, fontweight="bold", color="#0f2942")
    ax2.set_xlabel("Predicted Diagnosis")
    ax2.set_ylabel("Actual Clinical Outcome")

    plt.tight_layout()
    plt.savefig(output_dir / "eval_confusion_matrices.png", dpi=300)
    plt.close()

    # 2. ROC & Precision-Recall Curves
    fig, (ax_roc, ax_pr) = plt.subplots(1, 2, figsize=(13, 5.5))

    # ROC Curves
    fpr_lr, tpr_lr, _ = roc_curve(y_test, y_prob_lr)
    auc_lr = roc_auc_score(y_test, y_prob_lr)
    fpr_rf, tpr_rf, _ = roc_curve(y_test, y_prob_rf)
    auc_rf = roc_auc_score(y_test, y_prob_rf)

    ax_roc.plot(fpr_lr, tpr_lr, label=f"Logistic Regression (AUC = {auc_lr:.3f})", color="#0284c7", linewidth=2.2)
    ax_roc.plot(fpr_rf, tpr_rf, label=f"Random Forest (AUC = {auc_rf:.3f})", color="#10b981", linewidth=2.2)
    ax_roc.plot([0, 1], [0, 1], "k--", alpha=0.5, label="Random Guess (AUC = 0.500)")
    ax_roc.set_title("Receiver Operating Characteristic (ROC) Curves", pad=12, fontweight="bold", color="#0f2942")
    ax_roc.set_xlabel("False Positive Rate (1 - Specificity)")
    ax_roc.set_ylabel("True Positive Rate (Recall / Sensitivity)")
    ax_roc.legend(loc="lower right")

    # Precision-Recall Curves
    prec_lr, rec_lr, _ = precision_recall_curve(y_test, y_prob_lr)
    pr_auc_lr = average_precision_score(y_test, y_prob_lr)
    prec_rf, rec_rf, _ = precision_recall_curve(y_test, y_prob_rf)
    pr_auc_rf = average_precision_score(y_test, y_prob_rf)
    prevalence = float(y_test.mean())

    ax_pr.plot(rec_lr, prec_lr, label=f"Logistic Regression (PR-AUC = {pr_auc_lr:.3f})", color="#0284c7", linewidth=2.2)
    ax_pr.plot(rec_rf, prec_rf, label=f"Random Forest (PR-AUC = {pr_auc_rf:.3f})", color="#10b981", linewidth=2.2)
    ax_pr.axhline(prevalence, color="red", linestyle="--", alpha=0.6, label=f"Prevalence Baseline ({prevalence:.1%})")
    ax_pr.set_title("Precision-Recall (PR) Curves (Imbalanced Metric)", pad=12, fontweight="bold", color="#0f2942")
    ax_pr.set_xlabel("Recall (Sensitivity)")
    ax_pr.set_ylabel("Precision (Positive Predictive Value)")
    ax_pr.legend(loc="upper right")

    plt.tight_layout()
    plt.savefig(output_dir / "eval_roc_pr_curves.png", dpi=300)
    plt.close()

if __name__ == "__main__":
    train_and_evaluate()
