import os
import pandas as pd
import numpy as np
import sys
from sklearn.model_selection import GridSearchCV, cross_val_predict
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score, explained_variance_score
from xgboost import XGBRegressor

# 실험 번호를 인자로 받기
experiment_number = int(sys.argv[1])  # Slurm에서 전달된 번호

# Define paths
base_dir = "4_prediction/"
outcome_var = "nihtbx_cryst_uncorrected_base"

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

# Parameters
param_grid = {
    "learning_rate": [0.01, 0.05],
    "max_depth": [3, 4],
    "min_child_weight": [1, 5],
    "subsample": [0.8],
    "colsample_bytree": [0.8]
}

# Define model
xgb_model = XGBRegressor(
    tree_method="hist",
    device="cuda",
    objective="reg:squarederror",
    n_estimators=50,  # During Grid Search
    seed=experiment_number  # Use experiment number as seed
)

# GridSearchCV
grid_search = GridSearchCV(
    estimator=xgb_model,
    param_grid=param_grid,
    scoring="neg_mean_squared_error",
    cv=5,
    verbose=0,
    n_jobs=1
)
grid_search.fit(X_train.values, y_train.values)

# Cross-Validation 성능 계산
cv_best_model = grid_search.best_estimator_
y_cv_pred = cross_val_predict(cv_best_model, X_train.values, y_train.values, cv=5)

cv_metrics = {
    "Valid_RMSE": np.sqrt(mean_squared_error(y_train.values, y_cv_pred)),
    "Valid_MAE": mean_absolute_error(y_train.values, y_cv_pred),
    "Valid_R2": r2_score(y_train.values, y_cv_pred),
    "Valid_Explained_Variance": explained_variance_score(y_train.values, y_cv_pred),
}

# Train final model
best_params = grid_search.best_params_
final_model = XGBRegressor(
    **best_params,
    tree_method="hist",
    device="cuda",
    objective="reg:squarederror",
    n_estimators=500,
    seed=experiment_number
)
final_model.fit(X_train.values, y_train.values)

# Save model
model_dir = os.path.join(save_dir, "main_models")
os.makedirs(model_dir, exist_ok=True)
model_path = os.path.join(model_dir, f"final_model_{experiment_number}.json")
final_model.save_model(model_path)

# Predict on test data
y_test_pred = final_model.predict(X_test)

# Evaluate test set metrics
test_metrics = {
    "Test_RMSE": np.sqrt(mean_squared_error(y_test, y_test_pred)),
    "Test_MAE": mean_absolute_error(y_test, y_test_pred),
    "Test_R2": r2_score(y_test, y_test_pred),
    "Test_Explained_Variance": explained_variance_score(y_test, y_test_pred)
}

# Save metrics
metrics_dir = os.path.join(save_dir, "main_metrics")
os.makedirs(metrics_dir, exist_ok=True)
metrics_path = os.path.join(metrics_dir, f"metrics_{experiment_number}.csv")

# Combine CV and Test metrics
all_metrics = {**cv_metrics, **test_metrics}
pd.DataFrame([all_metrics]).to_csv(metrics_path, index=False)

# Save feature importance
importance_dir = os.path.join(save_dir, "main_feature_importance")
os.makedirs(importance_dir, exist_ok=True)
feature_importance = pd.DataFrame({
    "Feature": X_train.columns,
    "Importance": final_model.feature_importances_
}).sort_values(by="Importance", ascending=False)
feature_importance_path = os.path.join(importance_dir, f"feature_importance_{experiment_number}.csv")
feature_importance.to_csv(feature_importance_path, index=False)

print(f"Experiment {experiment_number} completed successfully.")
