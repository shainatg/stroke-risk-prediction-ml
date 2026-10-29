import joblib
import pandas as pd
import numpy as np
from src import config

_cached_model = None

def get_loaded_model():
    """
    Returns the cached champion model or loads it from disk.
    """
    global _cached_model
    if _cached_model is None:
        if not config.BEST_MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Trained model not found at {config.BEST_MODEL_PATH}. Please run training first."
            )
        _cached_model = joblib.load(config.BEST_MODEL_PATH)
    return _cached_model

def reload_model():
    """
    Forces reloading the model from disk after retraining.
    """
    global _cached_model
    _cached_model = None
    return get_loaded_model()

def validate_patient_input(data: dict) -> tuple[bool, str, dict]:
    """
    Validates and standardizes patient input fields for prediction.
    """
    clean_input = {}

    # 1. Age
    try:
        age = float(data.get("age", -1))
        if not (config.FEATURE_RANGES["age"]["min"] <= age <= config.FEATURE_RANGES["age"]["max"]):
            return False, f"Age must be between {config.FEATURE_RANGES['age']['min']} and {config.FEATURE_RANGES['age']['max']} years.", {}
        clean_input["age"] = age
    except (ValueError, TypeError):
        return False, "Age must be a valid numerical value.", {}

    # 2. Gender
    gender = str(data.get("gender", "")).capitalize()
    if gender not in config.VALID_GENDERS:
        return False, f"Gender must be one of: {', '.join(config.VALID_GENDERS)}.", {}
    clean_input["gender"] = gender

    # 3. Hypertension
    try:
        ht = int(data.get("hypertension", -1))
        if ht not in config.VALID_HYPERTENSION:
            return False, "Hypertension must be 0 (No) or 1 (Yes).", {}
        clean_input["hypertension"] = ht
    except (ValueError, TypeError):
        return False, "Hypertension must be an integer (0 or 1).", {}

    # 4. Heart Disease
    try:
        hd = int(data.get("heart_disease", -1))
        if hd not in config.VALID_HEART_DISEASE:
            return False, "Heart disease must be 0 (No) or 1 (Yes).", {}
        clean_input["heart_disease"] = hd
    except (ValueError, TypeError):
        return False, "Heart disease must be an integer (0 or 1).", {}

    # 5. Average Glucose Level
    try:
        glucose = float(data.get("avg_glucose_level", -1))
        if not (config.FEATURE_RANGES["avg_glucose_level"]["min"] <= glucose <= config.FEATURE_RANGES["avg_glucose_level"]["max"]):
            return False, f"Average glucose level must be between {config.FEATURE_RANGES['avg_glucose_level']['min']} and {config.FEATURE_RANGES['avg_glucose_level']['max']} mg/dL.", {}
        clean_input["avg_glucose_level"] = glucose
    except (ValueError, TypeError):
        return False, "Average glucose level must be a valid numerical value.", {}

    # 6. BMI
    try:
        bmi = float(data.get("bmi", -1))
        if not (config.FEATURE_RANGES["bmi"]["min"] <= bmi <= config.FEATURE_RANGES["bmi"]["max"]):
            return False, f"BMI must be between {config.FEATURE_RANGES['bmi']['min']} and {config.FEATURE_RANGES['bmi']['max']} kg/m².", {}
        clean_input["bmi"] = bmi
    except (ValueError, TypeError):
        return False, "BMI must be a valid numerical value.", {}

    # 7. Smoking Status
    smoking = str(data.get("smoking_status", "")).strip().lower()
    valid_smoking = [s.lower() for s in config.VALID_SMOKING_STATUSES]
    if smoking not in valid_smoking:
        return False, f"Smoking status must be one of: {', '.join(config.VALID_SMOKING_STATUSES)}.", {}
    clean_input["smoking_status"] = smoking

    # 8. Work Type
    work = str(data.get("work_type", "Private")).strip()
    if work not in config.VALID_WORK_TYPES:
        work = "Private"
    clean_input["work_type"] = work

    # 9. Residence Type
    residence = str(data.get("Residence_type", "Urban")).strip().capitalize()
    if residence not in config.VALID_RESIDENCE_TYPES:
        residence = "Urban"
    clean_input["Residence_type"] = residence

    # 10. Ever Married (Inferred if not provided)
    married = data.get("ever_married")
    if married in config.VALID_EVER_MARRIED:
        clean_input["ever_married"] = married
    else:
        clean_input["ever_married"] = "Yes" if clean_input["age"] >= 30 else "No"

    return True, "Validation successful", clean_input

def derive_influential_risk_factors(patient: dict, probability: float) -> list:
    """
    Analyzes patient parameters against evidence-based clinical risk factors
    to provide educational rationale for Health Informatics demonstrations.
    """
    factors = []

    # Age Factor
    if patient["age"] >= 65:
        factors.append({
            "factor": "Advanced Age",
            "patient_value": f"{patient['age']:.0f} years (≥ 65)",
            "impact": "High Risk",
            "severity": "danger",
            "explanation": "Advanced chronological age is the most potent non-modifiable risk factor; arterial stiffness and cumulative atherogenesis escalate sharply above age 60."
        })
    elif patient["age"] >= 50:
        factors.append({
            "factor": "Mature Age",
            "patient_value": f"{patient['age']:.0f} years (50–64)",
            "impact": "Moderate Risk",
            "severity": "warning",
            "explanation": "Cerebrovascular risk begins measurable progression in the fifth decade of life."
        })
    else:
        factors.append({
            "factor": "Younger Age",
            "patient_value": f"{patient['age']:.0f} years (< 50)",
            "impact": "Protective / Favorable",
            "severity": "success",
            "explanation": "Lower baseline vascular wear and preserved arterial elasticity reduce background ischemic vulnerability."
        })

    # Hypertension Factor
    if patient["hypertension"] == 1:
        factors.append({
            "factor": "Hypertension Present",
            "patient_value": "Documented (1)",
            "impact": "High Risk",
            "severity": "danger",
            "explanation": "Chronic elevated arterial pressure causes microaneurysms, endothelial damage, and small-vessel lipohyalinosis."
        })
    else:
        factors.append({
            "factor": "Normotensive",
            "patient_value": "No documented hypertension (0)",
            "impact": "Protective / Favorable",
            "severity": "success",
            "explanation": "Absence of chronic high blood pressure significantly diminishes arterial wall remodeling."
        })

    # Heart Disease Factor
    if patient["heart_disease"] == 1:
        factors.append({
            "factor": "Pre-existing Heart Disease",
            "patient_value": "Documented (1)",
            "impact": "High Risk",
            "severity": "danger",
            "explanation": "Coronary artery disease and cardiac dysrhythmias (e.g. atrial fibrillation) substantially elevate the hazard of cardioembolic stroke."
        })

    # Glucose Factor
    if patient["avg_glucose_level"] >= 200:
        factors.append({
            "factor": "Diabetic Hyperglycemia",
            "patient_value": f"{patient['avg_glucose_level']:.1f} mg/dL (≥ 200)",
            "impact": "High Risk",
            "severity": "danger",
            "explanation": "Marked hyperglycemia accelerates atheroma formation and worsens ischemic stroke penumbra injury."
        })
    elif patient["avg_glucose_level"] >= 140:
        factors.append({
            "factor": "Impaired Glucose Regulation",
            "patient_value": f"{patient['avg_glucose_level']:.1f} mg/dL (140–199)",
            "impact": "Moderate Risk",
            "severity": "warning",
            "explanation": "Prediabetic glycemia promotes systemic low-grade inflammation and vascular endothelial dysfunction."
        })
    else:
        factors.append({
            "factor": "Euglycemic (Normal Glucose)",
            "patient_value": f"{patient['avg_glucose_level']:.1f} mg/dL (< 140)",
            "impact": "Protective / Favorable",
            "severity": "success",
            "explanation": "Normoglycemia supports healthy microvascular autoregulation."
        })

    # BMI Factor
    if patient["bmi"] >= 30.0:
        factors.append({
            "factor": "Obesity (Class I+)",
            "patient_value": f"{patient['bmi']:.1f} kg/m² (≥ 30.0)",
            "impact": "Moderate Risk",
            "severity": "warning",
            "explanation": "Excess body mass index is associated with obstructive sleep apnea, dyslipidemia, and systemic pro-thrombotic states."
        })
    elif patient["bmi"] < 18.5:
        factors.append({
            "factor": "Underweight",
            "patient_value": f"{patient['bmi']:.1f} kg/m² (< 18.5)",
            "impact": "Potential Malnutrition",
            "severity": "warning",
            "explanation": "Low BMI may indicate frailty or underlying chronic illness."
        })

    # Smoking Factor
    if patient["smoking_status"] == "smokes":
        factors.append({
            "factor": "Active Tobacco Smoking",
            "patient_value": "Current smoker",
            "impact": "High Risk",
            "severity": "danger",
            "explanation": "Cigarette smoke induces immediate vasoconstriction, elevates fibrinogen, and doubles the hazard of ischemic stroke."
        })
    elif patient["smoking_status"] == "formerly smoked":
        factors.append({
            "factor": "Former Tobacco Exposure",
            "patient_value": "Formerly smoked",
            "impact": "Residual Risk",
            "severity": "warning",
            "explanation": "Past tobacco exposure leaves residual vascular remodeling, though risk diminishes steadily over smoke-free years."
        })

    return factors

def predict_patient(data: dict) -> dict:
    """
    Performs inference for an individual patient record and formats the educational response.
    """
    is_valid, msg, clean_input = validate_patient_input(data)
    if not is_valid:
        return {
            "status": "error",
            "error_type": "validation_error",
            "message": msg
        }

    model = get_loaded_model()

    # Create single-row DataFrame with expected columns
    df_patient = pd.DataFrame([clean_input])

    # Run inference
    try:
        prob = float(model.predict_proba(df_patient)[0, 1])
        pred_class = int(model.predict(df_patient)[0])
    except Exception as e:
        return {
            "status": "error",
            "error_type": "inference_error",
            "message": f"Inference execution failed: {str(e)}"
        }

    # Clinical factor analysis
    factors = derive_influential_risk_factors(clean_input, prob)

    # Educational class description
    class_label = "Elevated Stroke Risk (Positive Screening)" if pred_class == 1 else "Standard / Lower Stroke Risk (Negative Screening)"
    
    return {
        "status": "success",
        "patient_input": clean_input,
        "predicted_class": pred_class,
        "predicted_class_label": class_label,
        "estimated_probability": round(prob, 4),
        "estimated_probability_percentage": round(prob * 100, 1),
        "influential_risk_factors": factors,
        "disclaimer": (
            "EDUCATIONAL DEMONSTRATION NOTICE: This prediction represents an academic machine learning "
            "statistical estimate trained on historical survey data. It is NOT a clinically validated risk "
            "assessment, certified medical device, or diagnostic triage tool. It should not be used for "
            "clinical treatment decisions or individual patient diagnosis."
        )
    }

# Preset Clinical Profiles for Demonstration
SAMPLE_PATIENTS = {
    "high_risk": {
        "name": "Profile A: Elderly Patient with Cardiovascular Co-morbidities",
        "description": "72-year-old male with active hypertension, pre-existing heart disease, high blood glucose (215 mg/dL), and smoking history.",
        "data": {
            "gender": "Male",
            "age": 72.0,
            "hypertension": 1,
            "heart_disease": 1,
            "ever_married": "Yes",
            "work_type": "Private",
            "Residence_type": "Urban",
            "avg_glucose_level": 215.0,
            "bmi": 32.5,
            "smoking_status": "smokes"
        }
    },
    "low_risk": {
        "name": "Profile B: Healthy Young Adult",
        "description": "24-year-old female with no hypertension, no heart disease, normal glucose (88 mg/dL), healthy BMI (21.8), and non-smoker.",
        "data": {
            "gender": "Female",
            "age": 24.0,
            "hypertension": 0,
            "heart_disease": 0,
            "ever_married": "No",
            "work_type": "Private",
            "Residence_type": "Rural",
            "avg_glucose_level": 88.0,
            "bmi": 21.8,
            "smoking_status": "never smoked"
        }
    },
    "moderate_risk": {
        "name": "Profile C: Middle-Aged Adult with Borderline Risk Factors",
        "description": "55-year-old male with hypertension, borderline glucose (148 mg/dL), overweight (BMI 29.4), and former smoker history.",
        "data": {
            "gender": "Male",
            "age": 55.0,
            "hypertension": 1,
            "heart_disease": 0,
            "ever_married": "Yes",
            "work_type": "Self-employed",
            "Residence_type": "Urban",
            "avg_glucose_level": 148.0,
            "bmi": 29.4,
            "smoking_status": "formerly smoked"
        }
    }
}
