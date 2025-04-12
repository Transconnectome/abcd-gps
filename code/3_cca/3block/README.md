# 3-Block SGCCA Analysis (Permutation Test)

This folder provides a minimal example of how to perform **3-block Sparse Generalized Canonical Correlation Analysis (SGCCA)** with permutation-based significance testing.  
We demonstrate the pipeline using **GPS, sMRI**, and **Phenotype** blocks.

---

## ▶️ How to Run

1. Run the full SGCCA analysis and permutation test in R:

   This script performs:
   - 3-block SGCCA model fitting
   - Sparsity tuning via permutation
   - Original model evaluation
   - 100 permutations to generate null distributions

   ```bash
   Rscript block3.R
   ```

   This will generate:
   - `original_crit.csv`
   - `1-th_permutation_crit.csv` to `100-th_permutation_crit.csv`
   - `SGCCA_3blocks_result.RData`

   All results will be saved in:

   ```
   ./3block/output/
   ```

2. Run the permutation analysis and significance test in Python:

   ```bash
   python sigtest_block3.py
   ```

This will:

- Compute the permutation null distributions  
- Estimate uncorrected and FDR-corrected p-values  
- Save histograms and result summary files under:

```
./3block/output/perm_summary/
```

---

## 💡 Notes

- This example is based on sMRI brain data.
- You can reuse the same code for other imaging modalities by modifying the `brain` block in `block3.R`.
- The `.RData` file includes `result.rgcca` and `perm.out` for reference or reuse.
