import os
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename

from src import config
from src.data_loader import load_data, get_dataset_summary, get_sample_data, validate_uploaded_csv
from src.preprocessing import get_preprocessing_metadata
from src.eda import generate_eda_visualizations
from src.evaluate import get_evaluation_results
from src.train import train_and_evaluate
from src.predict import predict_patient, SAMPLE_PATIENTS, reload_model, get_loaded_model

app = Flask(__name__, static_folder="static", template_folder="templates")
app.config["SECRET_KEY"] = config.SECRET_KEY
app.config["MAX_CONTENT_LENGTH"] = 32 * 1024 * 1024  # 32 MB max upload
app.config["UPLOAD_FOLDER"] = config.UPLOAD_DIR

# In-memory cached EDA catalog
_eda_catalog_cache = None

def get_cached_eda():
    global _eda_catalog_cache
    if _eda_catalog_cache is None:
        _eda_catalog_cache = generate_eda_visualizations()
    return _eda_catalog_cache

# -------------------------------------------------------------
# Frontend Routes
# -------------------------------------------------------------
@app.route("/")
def index():
    """
    Serves the primary Single-Page Healthcare Dashboard UI.
    """
    return render_template("index.html")

# -------------------------------------------------------------
# API Endpoints
# -------------------------------------------------------------
@app.route("/api/status", methods=["GET"])
def api_status():
    """
    Returns system readiness, loaded model info, and configuration.
    """
    try:
        model = get_loaded_model()
        classifier_type = type(model.named_steps["classifier"]).__name__
        model_ready = True
    except Exception as e:
        classifier_type = f"Error: {str(e)}"
        model_ready = False

    return jsonify({
        "status": "healthy",
        "system": "Stroke Risk Prediction Healthcare System",
        "model_loaded": model_ready,
        "champion_classifier": classifier_type,
        "dataset_path": str(config.DATA_PATH.name),
        "debug": config.DEBUG
    })

@app.route("/api/dataset/summary", methods=["GET"])
def api_dataset_summary():
    """
    Provides comprehensive statistical summaries of the active dataset.
    """
    try:
        df = load_data()
        summary = get_dataset_summary(df)
        return jsonify({"status": "success", "data": summary})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/dataset/preview", methods=["GET"])
def api_dataset_preview():
    """
    Returns the first N records for the dataset explorer table.
    """
    try:
        n = int(request.args.get("limit", 15))
        df = load_data()
        records = get_sample_data(df, n=n)
        columns = df.columns.tolist()
        return jsonify({"status": "success", "columns": columns, "records": records, "total_rows": len(df)})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/dataset/upload", methods=["POST"])
def api_dataset_upload():
    """
    Handles CSV file upload, validates schema, and updates active dataset.
    """
    if "file" not in request.files:
        return jsonify({"status": "error", "message": "No file part in upload request."}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"status": "error", "message": "No file selected."}), 400

    if not file.filename.lower().endswith(".csv"):
        return jsonify({"status": "error", "message": "Uploaded file must be in .CSV format."}), 400

    filename = secure_filename(file.filename)
    save_path = config.UPLOAD_DIR / filename
    file.save(save_path)

    # Validate uploaded CSV schema
    is_valid, validation_msg, validated_df = validate_uploaded_csv(save_path)
    if not is_valid:
        if save_path.exists():
            save_path.unlink()
        return jsonify({"status": "error", "message": validation_msg}), 422

    # Option: automatically train on the new dataset or update default
    retrain_now = request.form.get("retrain", "false").lower() in ("true", "1")
    if retrain_now:
        try:
            eval_results = train_and_evaluate(str(save_path))
            reload_model()
            global _eda_catalog_cache
            _eda_catalog_cache = generate_eda_visualizations(validated_df)
            return jsonify({
                "status": "success",
                "message": f"Dataset uploaded and models retrained successfully! ({len(validated_df)} rows)",
                "filename": filename,
                "retrained": True,
                "evaluation": eval_results
            })
        except Exception as e:
            return jsonify({"status": "error", "message": f"Upload saved but retraining failed: {str(e)}"}), 500

    return jsonify({
        "status": "success",
        "message": f"Dataset uploaded and validated successfully ({len(validated_df)} rows).",
        "filename": filename,
        "retrained": False
    })

@app.route("/api/preprocessing", methods=["GET"])
def api_preprocessing():
    """
    Provides documented stages of the preprocessing and leakage-prevention pipeline.
    """
    metadata = get_preprocessing_metadata()
    return jsonify({"status": "success", "steps": metadata})

@app.route("/api/eda", methods=["GET"])
def api_eda():
    """
    Returns the metadata and clinical explanations for all 5 EDA figures.
    """
    try:
        catalog = get_cached_eda()
        return jsonify({"status": "success", "visualizations": catalog})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/models/evaluation", methods=["GET"])
def api_models_evaluation():
    """
    Retrieves cross-validation results, hyperparameter choices, and test set diagnostic metrics.
    """
    data = get_evaluation_results()
    return jsonify(data)

@app.route("/api/samples", methods=["GET"])
def api_samples():
    """
    Supplies preset clinical patient profiles for quick demonstration during practicals.
    """
    return jsonify({"status": "success", "samples": SAMPLE_PATIENTS})

@app.route("/api/predict", methods=["POST"])
def api_predict():
    """
    Performs real-time stroke risk prediction for an individual patient.
    """
    if not request.is_json:
        return jsonify({"status": "error", "message": "Request payload must be application/json."}), 400

    patient_payload = request.get_json()
    result = predict_patient(patient_payload)
    if result.get("status") == "error":
        return jsonify(result), 400

    return jsonify(result)

@app.route("/api/retrain", methods=["POST"])
def api_retrain():
    """
    Initiates model retraining on the current dataset.
    """
    try:
        eval_results = train_and_evaluate()
        reload_model()
        global _eda_catalog_cache
        _eda_catalog_cache = generate_eda_visualizations()
        return jsonify({
            "status": "success",
            "message": "Model retraining and evaluation completed successfully.",
            "results": eval_results
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    print(f"Starting Stroke Risk Prediction Healthcare Server on http://127.0.0.1:{config.PORT}")
    app.run(host="127.0.0.1", port=config.PORT, debug=config.DEBUG)
