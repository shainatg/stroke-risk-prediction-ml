/**
 * Stroke Risk Prediction Using Machine Learning
 * Frontend Client Controller
 */

document.addEventListener("DOMContentLoaded", () => {
    initNavigation();
    loadSystemStatus();
    loadDatasetSummary();
    loadDatasetPreview();
    loadPreprocessingDocs();
    loadEdaVisualizations();
    loadEvaluationResults();
    loadSampleProfiles();
    setupPredictionForm();
    setupCsvUpload();
    setupRetrainButton();
});

// -------------------------------------------------------------
// 1. Tab Navigation
// -------------------------------------------------------------
function initNavigation() {
    const tabs = document.querySelectorAll(".nav-tab");
    const sections = document.querySelectorAll(".page-section");

    tabs.forEach(tab => {
        tab.addEventListener("click", () => {
            const targetId = tab.getAttribute("data-target");
            if (!targetId) return;

            tabs.forEach(t => t.classList.remove("active"));
            sections.forEach(s => s.classList.remove("active"));

            tab.classList.add("active");
            const targetSection = document.getElementById(targetId);
            if (targetSection) {
                targetSection.classList.add("active");
                window.scrollTo({ top: 0, behavior: "smooth" });
            }
        });
    });
}

// -------------------------------------------------------------
// 2. System Status
// -------------------------------------------------------------
async function loadSystemStatus() {
    try {
        const res = await fetch("/api/status");
        const data = await res.json();
        const statusEl = document.getElementById("systemStatusText");
        if (data.model_loaded) {
            statusEl.textContent = `Model Ready (${data.champion_classifier})`;
        } else {
            statusEl.textContent = "Model Not Ready";
        }
    } catch (err) {
        console.error("Failed to load status:", err);
    }
}

// -------------------------------------------------------------
// 3. Dataset Summary & Preview
// -------------------------------------------------------------
async function loadDatasetSummary() {
    try {
        const res = await fetch("/api/dataset/summary");
        const json = await res.json();
        if (json.status !== "success") return;

        const d = json.data;
        document.getElementById("kpiTotalPatients").textContent = d.total_records.toLocaleString();
        document.getElementById("dsTotalRows").textContent = d.total_records.toLocaleString();
        document.getElementById("dsDuplicates").textContent = d.duplicate_rows.toString();

        if (d.target_distribution) {
            const rate = d.target_distribution.stroke_percentage;
            document.getElementById("kpiStrokeRate").textContent = `${rate}%`;
        }
    } catch (err) {
        console.error("Failed to load dataset summary:", err);
    }
}

async function loadDatasetPreview(limit = 15) {
    try {
        const res = await fetch(`/api/dataset/preview?limit=${limit}`);
        const data = await res.json();
        if (data.status !== "success") return;

        const tbody = document.getElementById("datasetPreviewBody");
        tbody.innerHTML = "";

        data.records.forEach(row => {
            const tr = document.createElement("tr");
            const strokeVal = row.stroke;
            const strokeClass = strokeVal === 1 ? 'class="text-danger font-bold"' : '';

            tr.innerHTML = `
                <td><code>${row.id || "N/A"}</code></td>
                <td>${row.gender || "—"}</td>
                <td>${row.age !== null ? row.age : "—"}</td>
                <td>${row.hypertension === 1 ? '<span class="badge-blue">Yes (1)</span>' : 'No (0)'}</td>
                <td>${row.heart_disease === 1 ? '<span class="badge-blue">Yes (1)</span>' : 'No (0)'}</td>
                <td>${row.ever_married || "—"}</td>
                <td>${row.work_type || "—"}</td>
                <td>${row.Residence_type || "—"}</td>
                <td>${row.avg_glucose_level !== null ? row.avg_glucose_level.toFixed(1) : "—"}</td>
                <td>${row.bmi !== null ? row.bmi.toFixed(1) : '<span class="text-muted">Imputed</span>'}</td>
                <td>${row.smoking_status || "—"}</td>
                <td ${strokeClass}>${strokeVal === 1 ? '<strong>Stroke (1)</strong>' : 'No (0)'}</td>
            `;
            tbody.appendChild(tr);
        });

        const counter = document.getElementById("previewRowCounter");
        if (counter) {
            counter.textContent = `Showing first ${data.records.length} of ${data.total_rows.toLocaleString()} patients`;
        }
    } catch (err) {
        console.error("Failed to load dataset preview:", err);
    }
}

// -------------------------------------------------------------
// 4. Preprocessing Documentation
// -------------------------------------------------------------
async function loadPreprocessingDocs() {
    try {
        const res = await fetch("/api/preprocessing");
        const data = await res.json();
        if (data.status !== "success") return;

        const container = document.getElementById("preprocessingStepsContainer");
        container.innerHTML = "";

        data.steps.forEach(step => {
            const div = document.createElement("div");
            div.className = "timeline-item";
            div.innerHTML = `
                <div class="timeline-header">
                    <span class="timeline-title">Stage 0${step.step}: ${step.name}</span>
                    <span class="timeline-tech">${step.technique}</span>
                </div>
                <p class="timeline-desc">${step.description}</p>
                <div class="timeline-leakage">
                    <strong>🛡️ Data Leakage Guard:</strong> ${step.leakage_protection}
                </div>
            `;
            container.appendChild(div);
        });
    } catch (err) {
        console.error("Failed to load preprocessing documentation:", err);
    }
}

// -------------------------------------------------------------
// 5. EDA Visualizations & Explanations
// -------------------------------------------------------------
async function loadEdaVisualizations() {
    try {
        const res = await fetch("/api/eda");
        const data = await res.json();
        if (data.status !== "success") return;

        const container = document.getElementById("edaGalleryContainer");
        container.innerHTML = "";

        data.visualizations.forEach((vis, idx) => {
            const card = document.createElement("div");
            card.className = "eda-card";
            card.innerHTML = `
                <div class="eda-header">
                    <h3 class="eda-title">${idx + 1}. ${vis.title}</h3>
                    <span class="eda-category-tag">${vis.category}</span>
                </div>
                <div class="eda-media">
                    <img src="${vis.image_url}?t=${Date.now()}" alt="${vis.title}" class="eda-img" loading="lazy">
                </div>
                <div class="eda-explanation-box">
                    <h4>Clinical & Health Informatics Interpretation</h4>
                    <p>${vis.explanation}</p>
                </div>
            `;
            container.appendChild(card);
        });
    } catch (err) {
        console.error("Failed to load EDA visualizations:", err);
    }
}

// -------------------------------------------------------------
// 6. Model Evaluation
// -------------------------------------------------------------
async function loadEvaluationResults() {
    try {
        const res = await fetch("/api/models/evaluation");
        const data = await res.json();
        if (data.status !== "success") return;

        // KPI hero updates
        document.getElementById("kpiChampionModel").textContent = data.champion_model;
        document.getElementById("championModelName").textContent = data.champion_model;
        document.getElementById("championRationaleText").textContent = data.champion_rationale;

        // Model Metrics Table
        const lr = data.models.logistic_regression;
        const rf = data.models.random_forest;

        if (lr && lr.test_metrics) {
            document.getElementById("lrAcc").textContent = (lr.test_metrics.accuracy * 100).toFixed(2) + "%";
            document.getElementById("lrRecall").textContent = (lr.test_metrics.recall * 100).toFixed(2) + "%";
            document.getElementById("lrPrec").textContent = (lr.test_metrics.precision * 100).toFixed(2) + "%";
            document.getElementById("lrSpec").textContent = (lr.test_metrics.specificity * 100).toFixed(2) + "%";
            document.getElementById("lrF1").textContent = lr.test_metrics.f1_score.toFixed(4);
            document.getElementById("lrRocAuc").textContent = lr.test_metrics.roc_auc.toFixed(4);
            document.getElementById("lrPrAuc").textContent = lr.test_metrics.pr_auc.toFixed(4);
            document.getElementById("lrCvScore").textContent = lr.validation_roc_auc.toFixed(4);
            document.getElementById("lrBestParams").textContent = JSON.stringify(lr.best_hyperparameters);
            document.getElementById("kpiChampionRecall").textContent = (lr.test_metrics.recall * 100).toFixed(1) + "%";
        }

        if (rf && rf.test_metrics) {
            document.getElementById("rfAcc").textContent = (rf.test_metrics.accuracy * 100).toFixed(2) + "%";
            document.getElementById("rfRecall").textContent = (rf.test_metrics.recall * 100).toFixed(2) + "%";
            document.getElementById("rfPrec").textContent = (rf.test_metrics.precision * 100).toFixed(2) + "%";
            document.getElementById("rfSpec").textContent = (rf.test_metrics.specificity * 100).toFixed(2) + "%";
            document.getElementById("rfF1").textContent = rf.test_metrics.f1_score.toFixed(4);
            document.getElementById("rfRocAuc").textContent = rf.test_metrics.roc_auc.toFixed(4);
            document.getElementById("rfPrAuc").textContent = rf.test_metrics.pr_auc.toFixed(4);
            document.getElementById("rfCvScore").textContent = rf.validation_roc_auc.toFixed(4);
            document.getElementById("rfBestParams").textContent = JSON.stringify(rf.best_hyperparameters);
        }
    } catch (err) {
        console.error("Failed to load evaluation metrics:", err);
    }
}

// -------------------------------------------------------------
// 7. Preset Profiles
// -------------------------------------------------------------
let presetDataCache = {};

async function loadSampleProfiles() {
    try {
        const res = await fetch("/api/samples");
        const json = await res.json();
        if (json.status === "success") {
            presetDataCache = json.samples;
        }

        const btnHigh = document.getElementById("btnPresetHigh");
        const btnLow = document.getElementById("btnPresetLow");
        const btnMod = document.getElementById("btnPresetMod");

        if (btnHigh) btnHigh.addEventListener("click", () => populateAndPredict("high_risk"));
        if (btnLow) btnLow.addEventListener("click", () => populateAndPredict("low_risk"));
        if (btnMod) btnMod.addEventListener("click", () => populateAndPredict("moderate_risk"));
    } catch (err) {
        console.error("Failed to load sample profiles:", err);
    }
}

function populateAndPredict(profileKey) {
    const profile = presetDataCache[profileKey];
    if (!profile) return;

    const d = profile.data;
    document.getElementById("inputAge").value = d.age;
    document.getElementById("inputGender").value = d.gender;
    document.getElementById("inputHypertension").value = d.hypertension;
    document.getElementById("inputHeartDisease").value = d.heart_disease;
    document.getElementById("inputGlucose").value = d.avg_glucose_level;
    document.getElementById("inputBmi").value = d.bmi;
    document.getElementById("inputSmoking").value = d.smoking_status;
    document.getElementById("inputWorkType").value = d.work_type;
    document.getElementById("inputResidence").value = d.Residence_type;

    // Trigger instant prediction
    submitPrediction();
}

// -------------------------------------------------------------
// 8. Patient Prediction
// -------------------------------------------------------------
function setupPredictionForm() {
    const form = document.getElementById("predictionForm");
    const btnReset = document.getElementById("btnResetForm");

    form.addEventListener("submit", (e) => {
        e.preventDefault();
        submitPrediction();
    });

    if (btnReset) {
        btnReset.addEventListener("click", () => {
            form.reset();
            document.getElementById("resultActive").classList.add("hidden");
            document.getElementById("resultPlaceholder").classList.remove("hidden");
        });
    }
}

async function submitPrediction() {
    const age = parseFloat(document.getElementById("inputAge").value);
    const gender = document.getElementById("inputGender").value;
    const hypertension = parseInt(document.getElementById("inputHypertension").value);
    const heart_disease = parseInt(document.getElementById("inputHeartDisease").value);
    const avg_glucose_level = parseFloat(document.getElementById("inputGlucose").value);
    const bmi = parseFloat(document.getElementById("inputBmi").value);
    const smoking_status = document.getElementById("inputSmoking").value;
    const work_type = document.getElementById("inputWorkType").value;
    const Residence_type = document.getElementById("inputResidence").value;

    const payload = {
        age,
        gender,
        hypertension,
        heart_disease,
        avg_glucose_level,
        bmi,
        smoking_status,
        work_type,
        Residence_type
    };

    const btnPredict = document.getElementById("btnPredict");
    btnPredict.disabled = true;
    btnPredict.innerHTML = "<span>Predicting...</span>";

    try {
        const res = await fetch("/api/predict", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        const result = await res.json();
        btnPredict.disabled = false;
        btnPredict.innerHTML = "<span>🩺 Predict Stroke Risk</span>";

        if (result.status === "error") {
            alert(`Validation Error: ${result.message}`);
            return;
        }

        renderPredictionResult(result);
    } catch (err) {
        btnPredict.disabled = false;
        btnPredict.innerHTML = "<span>🩺 Predict Stroke Risk</span>";
        alert(`Prediction failed: ${err.message}`);
    }
}

function renderPredictionResult(result) {
    document.getElementById("resultPlaceholder").classList.add("hidden");
    const activeDiv = document.getElementById("resultActive");
    activeDiv.classList.remove("hidden");

    // Class Badge
    const badge = document.getElementById("resClassBadge");
    badge.textContent = result.predicted_class_label;
    if (result.predicted_class === 1) {
        badge.className = "result-class-badge danger";
    } else {
        badge.className = "result-class-badge success";
    }

    // Probability Gauge
    const pct = result.estimated_probability_percentage;
    document.getElementById("resProbPct").textContent = `${pct.toFixed(1)}%`;
    const bar = document.getElementById("resProbBar");
    bar.style.width = `${Math.min(Math.max(pct, 4), 100)}%`;

    // Influential Risk Factors
    const list = document.getElementById("resFactorsList");
    list.innerHTML = "";

    if (result.influential_risk_factors && result.influential_risk_factors.length > 0) {
        result.influential_risk_factors.forEach(f => {
            const item = document.createElement("div");
            item.className = `factor-item ${f.severity || "warning"}`;
            item.innerHTML = `
                <div class="factor-header">
                    <span class="factor-name">${f.factor}</span>
                    <span class="factor-val">${f.patient_value}</span>
                </div>
                <p class="factor-desc">${f.explanation}</p>
            `;
            list.appendChild(item);
        });
    }

    // Disclaimer
    document.getElementById("resDisclaimer").textContent = result.disclaimer;
}

// -------------------------------------------------------------
// 9. CSV Upload
// -------------------------------------------------------------
function setupCsvUpload() {
    const form = document.getElementById("uploadCsvForm");
    const fileInput = document.getElementById("csvFileInput");
    const dropZone = document.getElementById("dropZone");
    const feedback = document.getElementById("uploadFeedback");

    fileInput.addEventListener("change", () => {
        if (fileInput.files.length > 0) {
            const fileName = fileInput.files[0].name;
            dropZone.querySelector(".dropzone-text").textContent = `Selected: ${fileName}`;
        }
    });

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        if (fileInput.files.length === 0) {
            alert("Please select a CSV file first.");
            return;
        }

        const formData = new FormData(form);
        const btn = document.getElementById("btnUploadSubmit");
        btn.disabled = true;
        btn.innerHTML = "Processing CSV...";

        feedback.className = "feedback-alert hidden";

        try {
            const res = await fetch("/api/dataset/upload", {
                method: "POST",
                body: formData
            });
            const data = await res.json();
            btn.disabled = false;
            btn.innerHTML = "Upload & Process CSV";

            if (data.status === "success") {
                feedback.className = "feedback-alert success";
                feedback.textContent = `✅ ${data.message}`;
                // Reload dataset views
                loadDatasetSummary();
                loadDatasetPreview();
                if (data.retrained) {
                    loadEvaluationResults();
                    loadEdaVisualizations();
                }
            } else {
                feedback.className = "feedback-alert error";
                feedback.textContent = `❌ ${data.message}`;
            }
        } catch (err) {
            btn.disabled = false;
            btn.innerHTML = "Upload & Process CSV";
            feedback.className = "feedback-alert error";
            feedback.textContent = `Upload failed: ${err.message}`;
        }
    });

    const btnRefresh = document.getElementById("btnRefreshDataset");
    if (btnRefresh) {
        btnRefresh.addEventListener("click", () => {
            loadDatasetSummary();
            loadDatasetPreview();
        });
    }

    const btnRefreshEda = document.getElementById("btnRefreshEda");
    if (btnRefreshEda) {
        btnRefreshEda.addEventListener("click", () => {
            loadEdaVisualizations();
        });
    }
}

// -------------------------------------------------------------
// 10. Re-run Training Pipeline
// -------------------------------------------------------------
function setupRetrainButton() {
    const btn = document.getElementById("btnTriggerRetrain");
    if (!btn) return;

    btn.addEventListener("click", async () => {
        const confirmRetrain = confirm("Are you sure you want to re-run the full training pipeline, 5-fold cross validation, and curve generation? This may take ~45 seconds.");
        if (!confirmRetrain) return;

        btn.disabled = true;
        btn.innerHTML = "⚡ Training In Progress...";

        try {
            const res = await fetch("/api/retrain", { method: "POST" });
            const data = await res.json();
            btn.disabled = false;
            btn.innerHTML = "⚡ Re-run Full Training Pipeline";

            if (data.status === "success") {
                alert("Model retraining completed successfully!");
                loadEvaluationResults();
                loadEdaVisualizations();
            } else {
                alert(`Retraining error: ${data.message}`);
            }
        } catch (err) {
            btn.disabled = false;
            btn.innerHTML = "⚡ Re-run Full Training Pipeline";
            alert(`Request failed: ${err.message}`);
        }
    });
}
