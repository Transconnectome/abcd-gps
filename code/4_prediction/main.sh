##### Prediction #####
conda env create -f /root/capsule/code/4_prediction/environment_prediction.yml
conda activate abcd_gps_ml

# 1. classification
cd ./4_prediction
python preprocessing_suicidal_behav_y_base.py
python /suicidal_behav_y_base/xgboost_classification_baseline_for_slurm.py 1
python /suicidal_behav_y_base/xgboost_classification_main_for_slurm.py 1

# 2. regression 
python preprocessing_nihtbx_cryst_uncorrected_base.py
python /nihtbx_cryst_uncorrected_base/xgboost_regression_baseline_for_slurm.py 1
python /nihtbx_cryst_uncorrected_base/xgboost_regression_mainmodel_for_slurm.py 1
