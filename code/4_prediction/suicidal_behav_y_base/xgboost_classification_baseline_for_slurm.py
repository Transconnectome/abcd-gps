import os
import pandas as pd
import numpy as np
import sys
from sklearn.model_selection import GridSearchCV, cross_val_predict
from sklearn.metrics import accuracy_score, balanced_accuracy_score, roc_auc_score, confusion_matrix, precision_recall_curve, average_precision_score
from sklearn.metrics import roc_curve
from xgboost import XGBClassifier

# 실험 번호를 인자로 받기
experiment_number = int(sys.argv[1])  # Slurm에서 전달된 번호

# Define paths
base_dir = "4_prediction/"
outcome_var = "suicidal_behav_y_base"

save_dir = os.path.join(base_dir, outcome_var)
X_train_path = os.path.join(save_dir, "X_train_scaled.csv")
X_test_path = os.path.join(save_dir, "X_test_scaled.csv")
y_train_path = os.path.join(save_dir, "y_train_scaled.csv")
y_test_path = os.path.join(save_dir, "y_test_scaled.csv")

# Load datasets
X_train = pd.read_csv(X_train_path)
X_test = pd.read_csv(X_test_path)
y_train = pd.read_csv(y_train_path).squeeze()
y_test = pd.read_csv(y_test_path).squeeze()

# Transform outcome variable back to 0 and 1
y_train = (y_train > 0).astype(int)
y_test = (y_test > 0).astype(int)

# Selected columns
selected_columns = [
    'age', 'high.educ', 'income', 'race.ethnicity_2', 'race.ethnicity_3', 'race.ethnicity_4',
    'race.ethnicity_5', 'married_2', 'married_3', 'married_4', 'married_5', 'married_6',
    'abcd_site_2', 'abcd_site_3', 'abcd_site_4', 'abcd_site_5', 'abcd_site_6', 'abcd_site_7',
    'abcd_site_8', 'abcd_site_9', 'abcd_site_10', 'abcd_site_11', 'abcd_site_12', 'abcd_site_13',
    'abcd_site_14', 'abcd_site_15', 'abcd_site_16', 'abcd_site_17', 'abcd_site_18', 'abcd_site_19',
    'abcd_site_20', 'abcd_site_21', 'abcd_site_22'
]
X_train_filtered = X_train[selected_columns]
X_test_filtered = X_test[selected_columns]

# Parameters
param_grid = {
    "learning_rate": [0.01, 0.05],
    "max_depth": [3, 4],
    "min_child_weight": [1, 5],
    "subsample": [0.8],
    "colsample_bytree": [0.8]
}

# Define model
xgb_model = XGBClassifier(
    tree_method="hist",
    objective="binary:logistic",
    n_estimators=50,
    random_state=experiment_number
)

# GridSearchCV
grid_search = GridSearchCV(
    estimator=xgb_model,
    param_grid=param_grid,
    scoring="roc_auc",
    cv=5,
    verbose=0,
    n_jobs=1
)
grid_search.fit(X_train_filtered.values, y_train.values)

# Cross-Validation 성능 계산
cv_best_model = grid_search.best_estimator_
y_cv_pred = cross_val_predict(cv_best_model, X_train_filtered.values, y_train.values, cv=5, method="predict_proba")[:, 1]

# Youden's J statistic for Valid
fpr, tpr, thresholds = roc_curve(y_train.values, y_cv_pred)
youden_index = np.argmax(tpr - fpr)
optimal_threshold_valid = thresholds[youden_index]

# Threshold 적용
y_cv_pred_class = (y_cv_pred >= optimal_threshold_valid).astype(int)

conf_matrix = confusion_matrix(y_train.values, y_cv_pred_class)
sensitivity = conf_matrix[1, 1] / (conf_matrix[1, 0] + conf_matrix[1, 1])
specificity = conf_matrix[0, 0] / (conf_matrix[0, 0] + conf_matrix[0, 1])

cv_metrics = {
    "Valid_Accuracy": accuracy_score(y_train.values, y_cv_pred_class),
    "Valid_Balanced_Accuracy": balanced_accuracy_score(y_train.values, y_cv_pred_class),
    "Valid_AUROC": roc_auc_score(y_train.values, y_cv_pred),
    "Valid_Specificity": specificity,
    "Valid_Sensitivity": sensitivity,
    "Valid_Average_Precision": average_precision_score(y_train.values, y_cv_pred),
    "Valid_Optimal_Threshold": optimal_threshold_valid
}

# Train final model
best_params = grid_search.best_params_
final_model = XGBClassifier(
    **best_params,
    tree_method="hist",
    objective="binary:logistic",
    n_estimators=500,
    random_state=experiment_number
)
final_model.fit(X_train_filtered.values, y_train.values)

# Save model
model_dir = os.path.join(save_dir, "baseline_models")
os.makedirs(model_dir, exist_ok=True)
model_path = os.path.join(model_dir, f"final_model_{experiment_number}.json")
final_model.save_model(model_path)

# Predict on test data
y_test_pred_proba = final_model.predict_proba(X_test_filtered)[:, 1]

# Youden's J statistic for Test
fpr_test, tpr_test, thresholds_test = roc_curve(y_test.values, y_test_pred_proba)
youden_index_test = np.argmax(tpr_test - fpr_test)
optimal_threshold_test = thresholds_test[youden_index_test]

# Threshold 적용
y_test_pred_class = (y_test_pred_proba >= optimal_threshold_test).astype(int)

conf_matrix_test = confusion_matrix(y_test.values, y_test_pred_class)
test_sensitivity = conf_matrix_test[1, 1] / (conf_matrix_test[1, 0] + conf_matrix_test[1, 1])
test_specificity = conf_matrix_test[0, 0] / (conf_matrix_test[0, 0] + conf_matrix_test[0, 1])

test_metrics = {
    "Test_Accuracy": accuracy_score(y_test, y_test_pred_class),
    "Test_Balanced_Accuracy": balanced_accuracy_score(y_test, y_test_pred_class),
    "Test_AUROC": roc_auc_score(y_test, y_test_pred_proba),
    "Test_Specificity": test_specificity,
    "Test_Sensitivity": test_sensitivity,
    "Test_Average_Precision": average_precision_score(y_test, y_test_pred_proba),
    "Test_Optimal_Threshold": optimal_threshold_test
}

# Save metrics
metrics_dir = os.path.join(save_dir, "baseline_metrics")
os.makedirs(metrics_dir, exist_ok=True)
metrics_path = os.path.join(metrics_dir, f"metrics_{experiment_number}.csv")

# Combine CV and Test metrics
all_metrics = {**cv_metrics, **test_metrics}
pd.DataFrame([all_metrics]).to_csv(metrics_path, index=False)

# Save feature importance
importance_dir = os.path.join(save_dir, "baseline_feature_importance")
os.makedirs(importance_dir, exist_ok=True)
feature_importance = pd.DataFrame({
    "Feature": selected_columns,
    "Importance": final_model.feature_importances_
}).sort_values(by="Importance", ascending=False)
feature_importance_path = os.path.join(importance_dir, f"feature_importance_{experiment_number}.csv")
feature_importance.to_csv(feature_importance_path, index=False)

print(f"Experiment {experiment_number} completed successfully.")
