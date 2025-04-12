# Behavior Prediction using XGBoost (ABCD-GPS Project)

This folder contains code for predicting behavioral outcomes using **XGBoost** models.  
The models are designed to handle both **classification** (e.g., suicidal behavior) and **regression** (e.g., cognitive scores) tasks, using **demographic variables alone (baseline)** or **demographic + GPS features (main model)**.

We include working examples for both task types:
- **Classification**: predicting suicidal behavior
- **Regression**: predicting uncorrected crystallized IQ score

---

## 📁 Folder Structure

```
4_prediction/
├── environment_prediction.yml                 # Conda environment specification
├── main.sh                                    # Bash script to run the full pipeline
├── preprocessing_suicidal_behav_y_base.py     # Preprocessing for classification task
├── suicidal_behav_y_base/                     # Folder with classification model code
│   ├── xgboost_classification_baseline_for_slurm.py
│   └── xgboost_classification_main_for_slurm.py
├── preprocessing_nihtbx_cryst_uncorrected_base.py  # Preprocessing for regression task
├── nihtbx_cryst_uncorrected_base/            # Folder with regression model code
    ├── xgboost_regression_baseline_for_slurm.py
    └── xgboost_regression_mainmodel_for_slurm.py
```

---

## ▶️ Setup

Before running the prediction pipeline, create and activate the appropriate conda environment:

```bash
# Create environment
conda env create -f /root/capsule/code/4_prediction/environment_prediction.yml

# Activate environment
conda activate abcd_gps_ml
```

---

## ▶️ Example: Classification Task

This task predicts **suicidal behavior**.

### 1. Run preprocessing script  
Generates the input features and labels.

```bash
cd ./4_prediction
python preprocessing_suicidal_behav_y_base.py
```

### 2. Run baseline model  
Predicts using only demographic variables.

```bash
python suicidal_behav_y_base/xgboost_classification_baseline_for_slurm.py 1
```

### 3. Run main model  
Predicts using demographic + GPS features.

```bash
python suicidal_behav_y_base/xgboost_classification_main_for_slurm.py 1
```

---

## ▶️ Example: Regression Task

This task predicts **uncorrected crystallized IQ** scores (NIH Toolbox).

### 1. Run preprocessing script

```bash
python preprocessing_nihtbx_cryst_uncorrected_base.py
```

### 2. Run baseline model  
Predicts using only demographic variables.

```bash
python nihtbx_cryst_uncorrected_base/xgboost_regression_baseline_for_slurm.py 1
```

### 3. Run main model  
Predicts using demographic + GPS features.

```bash
python nihtbx_cryst_uncorrected_base/xgboost_regression_mainmodel_for_slurm.py 1
```

---

## 📌 Notes

- The `1` argument passed to the `*_for_slurm.py` scripts typically denotes **seed index** or **fold index** (depending on implementation).
- You can modify the input index to run different CV folds or random splits.
- All scripts are designed to be **SLURM-friendly**, but can also be run locally.

---s