# 2-Block SGCCA Analysis

This repository contains scripts to perform **2-block Sparse Generalized Canonical Correlation Analysis (SGCCA)** between **genetic polygenic scores (GPS)** and **brain imaging phenotypes (IDPs)**.

---

## 🔍 Overview

This code is designed to compute correlations and shared variance between two data blocks:
- **Block 1**: GPS variables (genetic predictors)
- **Block 2**: Brain imaging variables (e.g., structural MRI, diffusion MRI, fMRI)

The example script included here uses **sMRI** (structural MRI) as the brain modality.  
To analyze other modalities (e.g., FA, rsfMRI, task-fMRI), simply replace the brain dataset.

---

## ▶️ How to Run

1. Prepare your GPS and brain imaging data in CSV format and place them in a data directory of your choice.

2. In `block2.R`, modify the brain data file path to the modality you want to analyze  
   (e.g., replace `smri_synthetic_EUR_100.csv` with `fa_synthetic_EUR_100.csv`).

3. Run the 2-block SGCCA and permutation-based significance test as follows:

   ```bash
   Rscript block2.R
   python sigtest_block2.py
   ```

This will:

- Perform 2-block SGCCA  
- Compute canonical correlations and convergence criteria  
- Run permutation testing (default: 100 iterations)  
- Save null distributions, p-values, and FDR-corrected results  

All outputs will be saved under a designated `/output` folder.

---

## 📊 Supported Modalities

This pipeline is designed to be **modality-independent**. You can reuse the same script to analyze any of the following by swapping out the brain data:

- sMRI (e.g., cortical thickness, surface area)  
- dMRI (e.g., count, FA)  
- rsfMRI (e.g., connectivity matrices)  
- task-fMRI (e.g., MID, N-back, SST fMRI)  

Each modality can be analyzed independently using the same SGCCA framework.

---

## 📎 Notes

- The SGCCA analysis uses 5 components and performs permutation testing with 100 iterations by default.  
- p-values are computed empirically by comparing to permuted null distributions.  
- z-scores and FDR-corrected p-values are also provided for both canonical correlations and convergence criteria.  
- To ensure consistency, original and permuted results are saved in CSV format, which are processed by `sigtest_block2.py`.

---
