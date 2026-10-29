import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# Paths configuration
DATA_PATH = Path(os.getenv("DATA_PATH", BASE_DIR / "data" / "healthcare-dataset-stroke-data.csv"))
MODELS_DIR = Path(os.getenv("MODELS_DIR", BASE_DIR / "models"))
IMAGES_DIR = Path(os.getenv("IMAGES_DIR", BASE_DIR / "static" / "images"))
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", BASE_DIR / "data" / "uploads"))

# Ensure required directories exist
MODELS_DIR.mkdir(parents=True, exist_ok=True)
IMAGES_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Server configuration
PORT = int(os.getenv("PORT", 5000))
DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1")
SECRET_KEY = os.getenv("SECRET_KEY", "stroke-prediction-health-informatics-secret-key-2026")

# Target and Feature Schema
TARGET_COL = "stroke"
ID_COL = "id"

NUMERICAL_COLS = ["age", "avg_glucose_level", "bmi"]

CATEGORICAL_COLS = [
    "gender",
    "hypertension",
    "heart_disease",
    "ever_married",
    "work_type",
    "Residence_type",
    "smoking_status",
]

# Patient Input Validations & Choices
VALID_GENDERS = ["Male", "Female"]
VALID_HYPERTENSION = [0, 1]
VALID_HEART_DISEASE = [0, 1]
VALID_EVER_MARRIED = ["Yes", "No"]
VALID_WORK_TYPES = ["Private", "Self-employed", "Govt_job", "children", "Never_worked"]
VALID_RESIDENCE_TYPES = ["Urban", "Rural"]
VALID_SMOKING_STATUSES = ["formerly smoked", "never smoked", "smokes", "Unknown"]

# Permissible physiological ranges for input validation
FEATURE_RANGES = {
    "age": {"min": 1.0, "max": 110.0, "default": 50.0, "unit": "years"},
    "avg_glucose_level": {"min": 40.0, "max": 350.0, "default": 100.0, "unit": "mg/dL"},
    "bmi": {"min": 10.0, "max": 80.0, "default": 27.0, "unit": "kg/m²"}
}

# Clinical risk indicator thresholds (for educational explanation only)
CLINICAL_RISK_FACTORS = {
    "age": {"threshold": 65.0, "label": "Advanced Age (≥ 65)", "desc": "Cardiovascular and cerebrovascular risk doubles every decade past age 55."},
    "avg_glucose_level": {"threshold": 140.0, "label": "Elevated Blood Glucose (≥ 140 mg/dL)", "desc": "Hyperglycemia indicates impaired glucose tolerance or diabetes, accelerating atherogenesis."},
    "bmi": {"threshold": 30.0, "label": "Obesity (BMI ≥ 30.0 kg/m²)", "desc": "Excess adiposity contributes to systemic inflammation, dyslipidemia, and arterial stiffness."},
    "hypertension": {"value": 1, "label": "Documented Hypertension", "desc": "Chronic high blood pressure is the single most critical modifiable risk factor for ischemic and hemorrhagic stroke."},
    "heart_disease": {"value": 1, "label": "Pre-existing Heart Disease", "desc": "Coronary artery disease and cardiac arrhythmias (such as atrial fibrillation) increase thromboembolic stroke potential."},
    "smoking_status": {"values": ["smokes", "formerly smoked"], "label": "Tobacco Exposure History", "desc": "Nicotine and carbon monoxide cause endothelial dysfunction, platelet aggregation, and vascular plaque rupture."}
}

# Model Filenames
BEST_MODEL_PATH = MODELS_DIR / "best_stroke_model.joblib"
LOGISTIC_MODEL_PATH = MODELS_DIR / "logistic_regression.joblib"
RANDOM_FOREST_PATH = MODELS_DIR / "random_forest.joblib"
EVALUATION_RESULTS_PATH = MODELS_DIR / "evaluation_results.json"
