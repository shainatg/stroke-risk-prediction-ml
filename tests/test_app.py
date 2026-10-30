import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import json
from app import app

def test_index_page(client):
    res = client.get("/")
    assert res.status_code == 200
    html = res.data.decode("utf-8")
    assert "Stroke Risk Prediction" in html
    assert "page-dashboard" in html
    assert "page-dataset" in html
    assert "page-preprocessing" in html
    assert "page-eda" in html
    assert "page-training" in html
    assert "page-evaluation" in html
    assert "page-prediction" in html

def test_api_status(client):
    res = client.get("/api/status")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "healthy"
    assert data["model_loaded"] is True
    assert "LogisticRegression" in data["champion_classifier"]

def test_api_dataset_summary(client):
    res = client.get("/api/dataset/summary")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert data["data"]["total_records"] > 5000
    assert "target_distribution" in data["data"]

def test_api_dataset_preview(client):
    res = client.get("/api/dataset/preview?limit=10")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert len(data["records"]) == 10
    assert "stroke" in data["columns"]

def test_api_preprocessing(client):
    res = client.get("/api/preprocessing")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert len(data["steps"]) >= 5

def test_api_eda(client):
    res = client.get("/api/eda")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert len(data["visualizations"]) == 5

def test_api_models_evaluation(client):
    res = client.get("/api/models/evaluation")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert "logistic_regression" in data["models"]
    assert "random_forest" in data["models"]
    assert data["models"]["logistic_regression"]["test_metrics"]["recall"] >= 0.70

def test_api_samples(client):
    res = client.get("/api/samples")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert "high_risk" in data["samples"]
    assert "low_risk" in data["samples"]

def test_api_predict_high_risk(client):
    payload = {
        "gender": "Male",
        "age": 75.0,
        "hypertension": 1,
        "heart_disease": 1,
        "avg_glucose_level": 220.0,
        "bmi": 34.0,
        "smoking_status": "smokes",
        "work_type": "Private",
        "Residence_type": "Urban"
    }
    res = client.post("/api/predict", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert data["predicted_class"] == 1
    assert data["estimated_probability"] > 0.5
    assert len(data["influential_risk_factors"]) > 0
    assert "EDUCATIONAL DEMONSTRATION NOTICE" in data["disclaimer"]

def test_api_predict_low_risk(client):
    payload = {
        "gender": "Female",
        "age": 22.0,
        "hypertension": 0,
        "heart_disease": 0,
        "avg_glucose_level": 85.0,
        "bmi": 21.0,
        "smoking_status": "never smoked",
        "work_type": "Private",
        "Residence_type": "Rural"
    }
    res = client.post("/api/predict", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert data["predicted_class"] == 0
    assert data["estimated_probability"] < 0.2

def test_api_predict_invalid_input(client):
    payload = {
        "gender": "InvalidSex",
        "age": 200.0,
        "hypertension": 5
    }
    res = client.post("/api/predict", json=payload)
    assert res.status_code == 400
    data = res.get_json()
    assert data["status"] == "error"

if __name__ == "__main__":
    import sys
    # Direct test runner if pytest not installed
    with app.test_client() as c:
        for test_fn in [
            test_index_page, test_api_status, test_api_dataset_summary,
            test_api_dataset_preview, test_api_preprocessing, test_api_eda,
            test_api_models_evaluation, test_api_samples, test_api_predict_high_risk,
            test_api_predict_low_risk, test_api_predict_invalid_input
        ]:
            try:
                test_fn(c)
                print(f"PASSED: {test_fn.__name__}")
            except Exception as e:
                import traceback
                print(f"FAILED: {test_fn.__name__} - {e}")
                traceback.print_exc()
                sys.exit(1)
    print("\nALL 11 AUTOMATED TESTS PASSED SUCCESSFULLY!")
