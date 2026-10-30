# Stroke Risk Prediction Using Machine Learning
**Postgraduate Health Informatics Practical Demonstration Project**

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-v1.4%2B-orange.svg)](https://scikit-learn.org/)
[![Flask](https://img.shields.io/badge/Flask-v3.0%2B-green.svg)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

---

## 📋 Project Overview

According to the World Health Organization (WHO), stroke is the second leading cause of death globally and a primary driver of long-term disability. This project delivers an end-to-end clinical machine learning application that analyzes multi-parametric patient demographic, physiological, and vascular factors to estimate acute cerebrovascular stroke risk.

The application is tailored for postgraduate **Health Informatics** and **Biomedical Data Science** practical demonstrations, highlighting key tenets of medical artificial intelligence:
- **Zero Data Leakage:** Imputation, scaling, and encoding fitted strictly on training partitions via Scikit-Learn `Pipeline` and `ColumnTransformer`.
- **Severe Class Imbalance Mitigation:** Addressing the ~4.9% positive stroke prevalence using cost-sensitive class balancing (`class_weight='balanced'`) and stratified 5-fold cross-validation.
- **Screening-Oriented Clinical Metrics:** Prioritizing **Recall (Sensitivity = 80.0%)** and **PR-AUC (0.2478)** over misleading raw accuracy to prevent missed life-threatening cases.
- **Explainable Predictions:** Translating raw probabilities into evidence-based risk drivers (e.g., advanced chronological age, hyperglycemia, documented hypertension, cardiac history).

---

## 🛠️ Technology Stack

| Component | Technology | Role / Purpose |
| :--- | :--- | :--- |
| **Language** | Python 3.10+ | Core development language |
| **Data Manipulation** | Pandas, NumPy | Dataset ingestion, cleaning, matrix operations |
| **Preprocessing & ML** | Scikit-Learn | Pipelines, ColumnTransformer, Imputation, Scaling, GridSearch, Logistic Regression, Random Forest |
| **Model Persistence** | Joblib | Serialization and loading of fitted pipelines |
| **Visualization** | Matplotlib, Seaborn | 300 DPI publication-quality clinical EDA and diagnostic evaluation plots |
| **Backend API** | Flask | RESTful endpoints for inference, dataset querying, retraining, and upload |
| **Frontend UI** | HTML5, CSS3, Vanilla JS | Modern, responsive blue-and-white healthcare dashboard (7 dedicated pages) |
| **Configuration** | Python-Dotenv | Environment variable management (`.env`) |

---

## 🗂️ Project Directory Structure

```text
mini project/
├── data/
│   ├── healthcare-dataset-stroke-data.csv     # Kaggle healthcare stroke cohort (5,110 rows)
│   └── uploads/                               # Destination for uploaded custom CSV datasets
├── models/
│   ├── best_stroke_model.joblib               # Fitted champion pipeline (preprocessing + classifier)
│   ├── logistic_regression.joblib             # Fitted Logistic Regression pipeline
│   ├── random_forest.joblib                   # Fitted Random Forest pipeline
│   └── evaluation_results.json                # Complete cross-validation and test set metrics
├── src/
│   ├── __init__.py                            # Package initializer
│   ├── config.py                              # Central paths, clinical ranges, and settings
│   ├── data_loader.py                         # Ingestion, validation, and dataset summarization
│   ├── preprocessing.py                       # Leakage-free ColumnTransformer & stratified splitting
│   ├── eda.py                                 # Exploratory Data Analysis chart generation
│   ├── train.py                               # 5-fold CV, GridSearch hyperparameter tuning, evaluation
│   ├── evaluate.py                            # Evaluation loader & metric extractors
│   └── predict.py                             # Real-time inference & risk factor derivation
├── static/
│   ├── css/
│   │   └── style.css                          # Modern healthcare blue-and-white theme
│   ├── js/
│   │   └── main.js                            # UI state management, API calls, dynamic charts
│   └── images/
│       ├── eda_stroke_distribution.png        # Class imbalance distribution
│       ├── eda_age_vs_stroke.png              # Age KDE and boxplot by outcome
│       ├── eda_glucose_vs_stroke.png          # Fasting/random glucose distribution
│       ├── eda_hypertension_heart_disease.png # Comorbidity prevalence bars
│       ├── eda_correlation_heatmap.png        # Pearson correlation matrix
│       ├── eval_confusion_matrices.png        # Test set confusion matrices (LR vs RF)
│       └── eval_roc_pr_curves.png             # Test set ROC and PR curves
├── templates/
│   └── index.html                             # Single-page multi-tab healthcare dashboard
├── app.py                                     # Flask application and REST API endpoints
├── run.py                                     # Convenience server entrypoint
├── requirements.txt                           # Python package dependencies
├── .env                                       # Environment configuration
├── .env.example                               # Environment configuration template
├── .gitignore                                 # Git ignore patterns
└── README.md                                  # Complete project documentation
```

---

## 📊 Dataset Description

The system utilizes the authentic Kaggle **Healthcare Stroke Dataset** (`healthcare-dataset-stroke-data.csv`), containing **5,110 patient records** and 11 clinical predictors:

| Feature Name | Clinical Meaning | Data Type | Range / Categories |
| :--- | :--- | :--- | :--- |
| `id` | Unique patient identifier (dropped) | Integer | 67 – 72,940 |
| `gender` | Biological sex | Categorical | `Male`, `Female` |
| `age` | Patient age in years | Continuous | 0.08 – 82.0 years |
| `hypertension` | Chronic high blood pressure history | Binary | `0` (No), `1` (Yes) |
| `heart_disease` | Pre-existing cardiovascular disease | Binary | `0` (No), `1` (Yes) |
| `ever_married` | Marital status indicator | Categorical | `No`, `Yes` |
| `work_type` | Occupational exposure category | Categorical | `Private`, `Self-employed`, `Govt_job`, `children`, `Never_worked` |
| `Residence_type` | Living environment | Categorical | `Urban`, `Rural` |
| `avg_glucose_level` | Blood glucose level | Continuous | 55.12 – 271.74 mg/dL |
| `bmi` | Body Mass Index | Continuous | 10.3 – 97.6 kg/m² (~3.9% missing) |
| `smoking_status` | Tobacco consumption history | Categorical | `never smoked`, `formerly smoked`, `smokes`, `Unknown` |
| **`stroke`** | **Primary Clinical Target** | **Binary Target** | **`0` = No Stroke (95.1%), `1` = Stroke (4.9%)** |

---

## ⚙️ Data Preprocessing & Zero Leakage Pipeline

Data preprocessing follows strict epidemiological and machine learning safety standards:

1. **Deduplication & Record Hygiene:** Duplicate records checked and purged. The single rare "Other" gender entry is removed to maintain validated binary classification.
2. **Missing Value Imputation:** BMI contains 201 missing values (~3.9%). Missing values are imputed using **Median Imputation** (`SimpleImputer(strategy='median')`). Crucially, the imputer is fitted *exclusively* on the training fold (`X_train`) to prevent knowledge of test set distribution leaking into model weights.
3. **Continuous Feature Standardization:** Age, average blood glucose level, and BMI are normalized using `StandardScaler` (z-score normalization: $\mu=0, \sigma=1$).
4. **Categorical Feature Encoding:** One-Hot Encoding (`OneHotEncoder(handle_unknown='ignore')`) maps categorical categories into orthogonal binary columns. Unknown categories at inference automatically default to zero vectors.
5. **Stratified 80/20 Train-Test Split:** A `StratifiedShuffleSplit` partitions 4,087 patients into training and 1,022 into a held-out test set, preserving the exact 4.89% stroke prevalence in both sets.
6. **Class Imbalance Handling:** Rather than synthetic oversampling (e.g. SMOTE) which can generate unrealistic physiological combinations, **Cost-Sensitive Class Weighting** (`class_weight='balanced'`) scales loss penalties inversely proportional to class frequencies:
   $$w_j = \frac{N}{2 \times N_j}$$

---

## 📈 Exploratory Data Analysis (EDA)

The application automatically generates 5 publication-ready charts stored in `static/images/`:

1. **Class Imbalance Distribution (`eda_stroke_distribution.png`):**
   Demonstrates the severe ~1:19.5 class imbalance (249 stroke cases vs. 4,861 non-stroke controls).
2. **Age vs. Stroke Occurrence (`eda_age_vs_stroke.png`):**
   Dual boxplot and kernel density estimation (KDE) demonstrating that stroke cases heavily cluster past age 60 (median age ~71 years vs 43 in controls).
3. **Average Glucose Level vs. Stroke (`eda_glucose_vs_stroke.png`):**
   Bimodal glucose distribution showing a pronounced stroke spike in the hyperglycemic range (> 180–220 mg/dL).
4. **Hypertension and Heart Disease Comorbidities (`eda_hypertension_heart_disease.png`):**
   Shows stroke rate jumps from 4.0% in normotensive to 13.3% in hypertensive patients (3.3x relative risk), and from 4.2% to 17.0% in cardiac patients (> 4x relative risk).
5. **Correlation Heatmap (`eda_correlation_heatmap.png`):**
   Lower triangular correlation matrix illustrating that age ($r \approx 0.25$), glucose ($r \approx 0.13$), hypertension ($r \approx 0.13$), and heart disease ($r \approx 0.13$) are the top positive linear risk correlates.

---

## 🧠 Model Training, Comparison & Evaluation

Two distinct machine learning paradigms were tuned using **Stratified 5-Fold Cross Validation** via `GridSearchCV` scoring on ROC-AUC:

1. **Logistic Regression (Champion Model):**
   - Regularization: L2 Penalty
   - Hyperparameter Grid: $C \in [0.01, 0.1, 1.0, 10.0]$, Solvers: `['lbfgs', 'liblinear']`
   - Optimal Hyperparameters: `C = 0.01`, `solver = 'liblinear'`
   - Validation 5-Fold ROC-AUC: **0.8397**
2. **Random Forest Classifier:**
   - Architecture: Ensemble of Decision Trees with Balanced Class Weights
   - Hyperparameter Grid: `n_estimators` [50, 100, 200], `max_depth` [None, 6, 12], `min_samples_split` [2, 5], `min_samples_leaf` [1, 2]
   - Optimal Hyperparameters: `max_depth = 6`, `n_estimators = 200`, `min_samples_leaf = 2`, `min_samples_split = 5`
   - Validation 5-Fold ROC-AUC: **0.8216**

### Held-Out 20% Test Set Evaluation (N = 1,022 Patients)

| Evaluated Metric | Logistic Regression (Champion) | Random Forest Classifier | Clinical Screening Significance |
| :--- | :---: | :---: | :--- |
| **Accuracy** | 72.21% | 68.88% | Misleading baseline in 95% negative cohort |
| **Recall (Sensitivity) 🌟** | **80.00%** | **80.00%** | **40 / 50 true stroke cases successfully flagged** |
| **Precision** | 12.74% | 11.49% | Positive predictive value under low prevalence |
| **Specificity** | 71.81% | 68.31% | Correct rejection of non-stroke individuals |
| **F1-Score** | 0.2198 | 0.2010 | Harmonic mean of precision and sensitivity |
| **ROC-AUC Score 🌟** | **0.8379** | **0.8197** | Strong discrimination across all cut-offs |
| **PR-AUC (Avg. Prec.) 🌟** | **0.2478** | **0.1978** | **> 5-fold lift over 4.89% random baseline** |
| **True Negatives (TN)** | 698 | 664 | Correctly identified non-stroke patients |
| **False Positives (FP)** | 274 | 308 | Patients flagged for preventive follow-up |
| **False Negatives (FN)** | **10** | **10** | **Critical metric to minimize in clinical screening** |
| **True Positives (TP)** | 40 | 40 | High-risk patients correctly identified |

> **Champion Selection Rationale:**  
> Logistic Regression was selected as champion. Both models achieved identical high Recall (80.0%), but Logistic Regression demonstrated higher cross-validated ROC-AUC (0.8397 vs 0.8216), higher test PR-AUC (0.2478 vs 0.1978), generated 34 fewer False Positives, and offers direct clinical interpretability via linear log-odds coefficients.

---

## 💻 User Interface Features

The user interface is structured into 7 dedicated sections:
1. **Dashboard:** High-level project metrics, health informatics rationale, and end-to-end pipeline architecture.
2. **Dataset Explorer:** Dynamic tabular preview of patient records, summary statistics, and an interactive **CSV File Uploader** with automatic schema validation and retraining options.
3. **Data Preprocessing:** Interactive timeline detailing missing value imputation, encoding, standardization, and leakage prevention mechanisms.
4. **EDA Visualizations:** Interactive gallery rendering the 5 clinical graphs with comprehensive medical explanations.
5. **Model Training:** Cross-validation scores, hyperparameter grids, and selection rationale.
6. **Model Evaluation:** Diagnostic comparison table, side-by-side Confusion Matrices, and high-resolution ROC & Precision-Recall curves.
7. **Clinical Predictor:** Interactive patient input form with real-time prediction output, probability gauge, influential factor breakdown, and **quick-load demo presets**.

---

## 🧪 Preset Patient Profiles for Practical / Viva Testing

For quick demonstrations during examinations and vivas, use the 3 preset buttons on the **Clinical Predictor** page:

### Profile A: High-Risk Elderly Patient (Elevated Stroke Risk)
- **Age:** 72 years
- **Gender:** Male
- **Hypertension:** Yes (1)
- **Heart Disease:** Yes (1)
- **Average Glucose:** 215.0 mg/dL
- **BMI:** 32.5 kg/m²
- **Smoking Status:** Smokes
- **Result:** ~89.9% probability | Class: **Elevated Stroke Risk (Positive Screening)**

### Profile B: Healthy Young Adult (Low Risk)
- **Age:** 24 years
- **Gender:** Female
- **Hypertension:** No (0)
- **Heart Disease:** No (0)
- **Average Glucose:** 88.0 mg/dL
- **BMI:** 21.8 kg/m²
- **Smoking Status:** Never smoked
- **Result:** ~8.9% probability | Class: **Standard / Lower Stroke Risk (Negative Screening)**

### Profile C: Middle-Aged Borderline Patient
- **Age:** 55 years
- **Gender:** Male
- **Hypertension:** Yes (1)
- **Heart Disease:** No (0)
- **Average Glucose:** 148.0 mg/dL
- **BMI:** 29.4 kg/m²
- **Smoking Status:** Formerly smoked
- **Result:** ~64.3% probability | Class: **Elevated Stroke Risk (Positive Screening)**

---

## 🚀 Execution & Setup Instructions

### 1. Prerequisites
- Python 3.10, 3.11, 3.12, or 3.13 installed.
- VS Code or Google Antigravity IDE.

### 2. Installation
Open your terminal in the project directory:

```bash
# Clone or navigate to the project directory
cd "c:\Users\shaina\OneDrive\Desktop\mini project"

# Install required dependencies
pip install -r requirements.txt
```

### 3. Running Model Training (Optional, Already Pre-trained)
The models, curves, and evaluation files are already pre-generated and stored in `models/` and `static/images/`. To trigger a fresh training run:

```bash
python -m src.train
```

### 4. Starting the Web Application
Launch the Flask development server:

```bash
python app.py
# or
python run.py
```

Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 📡 REST API Reference

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `GET /` | `GET` | Renders the primary single-page healthcare dashboard |
| `GET /api/status` | `GET` | Health check, model status, and champion classifier name |
| `GET /api/dataset/summary` | `GET` | Dataset dimensions, missing value counts, and class statistics |
| `GET /api/dataset/preview?limit=15` | `GET` | Returns first N rows of the dataset as JSON |
| `POST /api/dataset/upload` | `POST` | Upload custom CSV, validate schema, optionally retrain |
| `GET /api/preprocessing` | `GET` | Step-by-step preprocessing documentation and leakage guards |
| `GET /api/eda` | `GET` | Returns paths and clinical interpretations for all 5 EDA figures |
| `GET /api/models/evaluation` | `GET` | Cross-validation scores, test metrics, and hyperparameter logs |
| `GET /api/samples` | `GET` | Preset clinical profiles for rapid demonstration |
| `POST /api/predict` | `POST` | Inference endpoint accepting patient JSON payload |
| `POST /api/retrain` | `POST` | Re-runs 5-fold CV, model tuning, and evaluation plots |

---

## ⚖️ Clinical & Ethical Disclaimer

> **DISCLAIMER:**  
> This software is an **academic demonstration project** developed strictly for postgraduate Health Informatics and educational purposes. The predictions generated by the machine learning models are statistical estimates derived from historical survey datasets. **This application is NOT a certified medical diagnostic device, does NOT provide clinically validated risk scores, and MUST NOT be utilized for individual clinical diagnosis, emergency triage, or patient treatment decisions.** Patients and healthcare providers should always consult licensed medical physicians for health evaluations.
