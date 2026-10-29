import json
from pathlib import Path
from src import config

def get_evaluation_results() -> dict:
    """
    Loads saved evaluation metrics and validation results.
    If not found, returns a prompt indicating training has not yet completed.
    """
    if not config.EVALUATION_RESULTS_PATH.exists():
        return {
            "status": "not_trained",
            "message": "Model training has not been executed yet. Run training to generate evaluation metrics."
        }

    try:
        with open(config.EVALUATION_RESULTS_PATH, "r") as f:
            data = json.load(f)
        return data
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to load evaluation results: {str(e)}"
        }
