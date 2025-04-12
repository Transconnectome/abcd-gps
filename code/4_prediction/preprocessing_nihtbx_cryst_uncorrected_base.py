import os
import pandas as pd
import numpy as np
import xgboost as xgb
from xgboost.callback import EarlyStopping
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, roc_auc_score, mean_squared_error
import json
import matplotlib.pyplot as plt

# Directory creation function
def create_dir_if_not_exists(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

# Load data (replace paths with actual file paths)
df_targets = pd.read_csv("xgb_synthetic_EUR_100.csv")
demo = pd.read_csv("demo_synthetic_EUR_100.csv")
gps_eur = pd.read_csv("gps_eur_synthetic_100.csv")
subj_list = pd.read_csv('subjectlist_EUR_100.csv')
subj_list.rename(columns={'x': 'subjectkey'}, inplace=True)

# Define covariates and merge data
cov_list = ["age", "high.educ", "income", "race.ethnicity", "married", "abcd_site"]
demo_2 = demo[["subjectkey"] + cov_list]

gps_eur = gps_eur[gps_eur["ethnic_g"] == "EUR"]
gps_eur = gps_eur[gps_eur["set"] == "test"]  # 6555
gps_eur_list = gps_eur.columns[4:36].tolist()
print(gps_eur_list)

exclude_vars = [
    'nihtbx_cardsort_uncorrected_2yr', 
    'nihtbx_list_uncorrected_2yr', 
    'nihtbx_fluidcomp_uncorrected_2yr', 
    'nihtbx_totalcomp_uncorrected_2yr'
]
cbcl_vars = [col for col in df_targets.columns if col.startswith('cbcl')]
nihtbx_vars = [col for col in df_targets.columns if col.startswith('nihtbx') and col not in exclude_vars]
print('The number of cbcl_vars:', len(cbcl_vars))
print('The number of nihtbx_vars:', len(nihtbx_vars))
print('cbcl_vars:', cbcl_vars)
print('nihtbx_vars:', nihtbx_vars)

outcome_var = 'nihtbx_cryst_uncorrected_base'
print('Outcome variable:', outcome_var)

data_eur = (
    subj_list
    .merge(df_targets, on="subjectkey", how="left")
    .merge(demo, on="subjectkey", how="left")
    .merge(gps_eur, on="subjectkey", how="left")
)

print('Shape of data_eur', data_eur.shape)
data_eur = data_eur[['subjectkey'] + [outcome_var] + gps_eur_list + cov_list]
print('Shape of data_eur', data_eur.shape)

# Check missing values
def check_missing_values(dataframe):
    missing_data = dataframe.isnull().sum()
    missing_percentage = (missing_data / len(dataframe)) * 100
    missing_summary = pd.DataFrame({
        "Column": missing_data.index,
        "Missing Count": missing_data.values,
        "Missing Percentage": missing_percentage.values
    })
    return missing_summary.sort_values(by="Missing Percentage", ascending=False)

missing_summary = check_missing_values(data_eur)
print("Missing values summary:")
print(missing_summary)

# Drop rows with missing outcome values
data_eur_cleaned = data_eur.dropna(subset=[outcome_var])
print(f"Shape after dropping rows with missing values in {outcome_var}: {data_eur_cleaned.shape}")

# One-hot encoding for categorical variables
categorical_vars = cov_list[3:6]
data_eur_encoded = pd.get_dummies(data_eur_cleaned, columns=categorical_vars, drop_first=True)
print(f"Shape after one-hot encoding: {data_eur_encoded.shape}")

# Split data with matched outcome distribution
def split_data_with_matched_distribution(data, outcome_var, test_size=0.2, bins=10):
    data['outcome_bin'] = pd.qcut(data[outcome_var], q=bins, duplicates='drop')
    X = data.drop(columns=[outcome_var, 'outcome_bin'])
    y = data[outcome_var]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42, stratify=data['outcome_bin']
    )
    train_subjectkeys = X_train["subjectkey"].tolist()
    test_subjectkeys = X_test["subjectkey"].tolist()
    X_train = X_train.drop(columns=["subjectkey"])
    X_test = X_test.drop(columns=["subjectkey"])
    data = data.drop(columns=['outcome_bin'])
    return X_train, X_test, y_train, y_test, train_subjectkeys, test_subjectkeys

X_train, X_test, y_train, y_test, train_subjectkeys, test_subjectkeys = split_data_with_matched_distribution(data_eur_encoded, outcome_var)
print(f"Shape of X_train: {X_train.shape}")
print(f"Shape of X_test: {X_test.shape}")

# Function to plot and save histograms
def plot_outcome_histograms(y_train, y_test, outcome_var, plot_dir):
    plt.figure(figsize=(12, 6))
    plt.subplot(1, 2, 1)
    plt.hist(y_train, bins=30, edgecolor="black", alpha=0.7)
    plt.title(f"{outcome_var} Distribution in Train Set")
    plt.xlabel(outcome_var)
    plt.ylabel("Frequency")
    plt.grid(axis="y", alpha=0.75)

    plt.subplot(1, 2, 2)
    plt.hist(y_test, bins=30, edgecolor="black", alpha=0.7, color="orange")
    plt.title(f"{outcome_var} Distribution in Test Set")
    plt.xlabel(outcome_var)
    plt.ylabel("Frequency")
    plt.grid(axis="y", alpha=0.75)

    plt.tight_layout()
    plot_file_path = os.path.join(plot_dir, f"{outcome_var}_distribution_histograms.png")
    plt.savefig(plot_file_path)
    print(f"Histogram saved to {plot_file_path}")
    plt.close()

# Ensure plot directory exists and save plots
base_dir = "4_prediction/nihtbx_cryst_uncorrected_base"
os.makedirs(base_dir, exist_ok=True)
plot_dir = "4_prediction/plot"

plot_outcome_histograms(y_train, y_test, outcome_var, plot_dir)

# Z-normalization
def z_normalize_with_outcome(X_train, X_test, y_train, y_test):
    feature_scaler = StandardScaler()
    X_train_scaled = feature_scaler.fit_transform(X_train)
    X_test_scaled = feature_scaler.transform(X_test)
    outcome_scaler = StandardScaler()
    y_train_scaled = outcome_scaler.fit_transform(y_train.values.reshape(-1, 1)).flatten()
    y_test_scaled = outcome_scaler.transform(y_test.values.reshape(-1, 1)).flatten()
    X_train_scaled = pd.DataFrame(X_train_scaled, columns=X_train.columns, index=X_train.index)
    X_test_scaled = pd.DataFrame(X_test_scaled, columns=X_test.columns, index=X_test.index)
    y_train_scaled = pd.Series(y_train_scaled, index=y_train.index, name=y_train.name)
    y_test_scaled = pd.Series(y_test_scaled, index=y_test.index, name=y_test.name)
    return X_train_scaled, X_test_scaled, y_train_scaled, y_test_scaled

X_train_scaled, X_test_scaled, y_train_scaled, y_test_scaled = z_normalize_with_outcome(X_train, X_test, y_train, y_test)


pd.DataFrame(train_subjectkeys, columns=["subjectkey"]).to_csv(
    os.path.join(base_dir, "train_subjectkeys.csv"), index=False
)
pd.DataFrame(test_subjectkeys, columns=["subjectkey"]).to_csv(
    os.path.join(base_dir, "test_subjectkeys.csv"), index=False
)
X_train_scaled.to_csv(os.path.join(base_dir, "X_train_scaled.csv"), index=False)
X_test_scaled.to_csv(os.path.join(base_dir, "X_test_scaled.csv"), index=False)
y_train_scaled.to_csv(os.path.join(base_dir, "y_train_scaled.csv"), index=False)
y_test_scaled.to_csv(os.path.join(base_dir, "y_test_scaled.csv"), index=False)

print(f"Data saved to directory: {base_dir}")
