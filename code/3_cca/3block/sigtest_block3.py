# sigtest_block3.py
# Python script to compute empirical p-values from 3-block SGCCA permutation

import os
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.stats.multitest import fdrcorrection

# === user-defined ===
result_dir = "./3block/output"
perm_summary_dir = os.path.join(result_dir, "perm_summary")
os.makedirs(perm_summary_dir, exist_ok=True)

# === load data ===
ori_crit = pd.read_csv(os.path.join(result_dir, "original_crit.csv"), header=None)
null_crit = pd.DataFrame()

for i in range(1, 101):  # 100 permutations (단일 예시)
    path = os.path.join(result_dir, f"{i}-th_permutation_crit.csv")
    if os.path.exists(path):
        row = pd.read_csv(path, header=None).T
        row.index = [f"{i}-th"]
        null_crit = pd.concat([null_crit, row])
    else:
        print(f"Missing: {i}-th")

null_crit.columns = [f"{j+1}_comp" for j in range(null_crit.shape[1])]
null_crit.to_csv(os.path.join(result_dir, "null_crit_total.csv"))

# === compute p-values, z-scores ===
ori = ori_crit.values[0]
null_mean = null_crit.mean().values
null_std = null_crit.std().values
z_scores = (ori - null_mean) / null_std
p_vals = [(ori[j] < null_crit.iloc[:, j]).mean() for j in range(len(ori))]
p_fdr = fdrcorrection(p_vals)[1]

# === save results ===
summary_df = pd.DataFrame({
    "original": ori,
    "null_mean": null_mean,
    "null_std": null_std,
    "z_stat": z_scores,
    "p_uncorrected": p_vals,
    "p_fdr": p_fdr
}, index=[f"{j+1}_comp" for j in range(len(ori))])
summary_df.to_csv(os.path.join(perm_summary_dir, "3block_perm_result_summary.csv"))

# === plot histograms ===
for j in range(len(ori)):
    plt.figure(figsize=(7, 5))
    plt.hist(null_crit.iloc[:, j], bins=30, alpha=0.7, label=f'p = {p_vals[j]:.4f}')
    plt.axvline(ori[j], color='red', label='Original')
    plt.title(f'Permutation Test - Component {j+1}')
    plt.xlabel("SGCCA Criterion")
    plt.ylabel("Count")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(perm_summary_dir, f"{j+1}_comp_hist.png"))
    plt.close()

print("Permutation analysis complete.")
