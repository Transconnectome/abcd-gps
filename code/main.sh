#!/bin/bash



#### Correlation #####
conda create -n r_env r-base r-essentials
codna activate r_env
Rscript /root/capsule/code/2_correlation/code_corr_brianIDPs_w33gps.R
conda deactivate


##### CCA #####
# 1. 2 block cca
Rscript /root/capsule/code/3_cca/block2.R
python /root/capsule/code/3_cca/sigtest_block2.py



##### Prediction #####
conda env create -f /root/capsule/code/4_prediction/environment_prediction.yml
source /opt/conda/etc/profile.d/conda.sh
conda env list
conda init bash
conda activate abcd_gps_ml

# 1. classification
cd /root/capsule/code/4_prediction
python preprocessing_suicidal_behav_y_base.py
python /root/capsule/code/4_prediction/suicidal_behav_y_base/xgboost_classification_baseline_for_slurm.py 1
python /root/capsule/code/4_prediction/suicidal_behav_y_base/xgboost_classification_main_for_slurm.py 1

# 2. regression 
python preprocessing_nihtbx_cryst_uncorrected_base.py
python /root/capsule/code/4_prediction/nihtbx_cryst_uncorrected_base/xgboost_regression_baseline_for_slurm.py 1
python /root/capsule/code/4_prediction/nihtbx_cryst_uncorrected_base/xgboost_regression_mainmodel_for_slurm.py 1
