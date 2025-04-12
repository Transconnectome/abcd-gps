import os
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.stats.multitest import fdrcorrection

# ---------------------------------------------------------
# Function: summary from permutation files
# ---------------------------------------------------------
def two_block_CCA_summary(data_folder, exp_ver_list):
    for exp_idx, exp_ver in enumerate(exp_ver_list):
        data_dir = os.path.join(data_folder)

        ori_crit = pd.read_csv(os.path.join(data_dir, 'original_crit.csv'), header=None)
        ori_corr = pd.read_csv(os.path.join(data_dir, 'original_corr.csv'), header=None)

        null_crit = pd.DataFrame()
        null_corr = pd.DataFrame()

        for i in range(1, 101):
            try:
                null_crit_temp = pd.read_csv(os.path.join(data_dir, f'{i}-th_permutation_crit.csv'), header=None).T
                null_corr_temp = pd.read_csv(os.path.join(data_dir, f'{i}-th_permutation_corr.csv'), header=None).T
                null_crit_temp.index = [f'{i}-th_null']
                null_corr_temp.index = [f'{i}-th_null']
                null_crit = pd.concat([null_crit, null_crit_temp])
                null_corr = pd.concat([null_corr, null_corr_temp])
            except FileNotFoundError:
                print(f"File missing for permutation {i}")

        null_crit.columns = [f'{j}_comp' for j in range(1, null_crit.shape[1] + 1)]
        null_corr.columns = [f'{j}_comp' for j in range(1, null_corr.shape[1] + 1)]

        null_crit.to_csv(os.path.join(data_dir, 'null_crit_total.csv'))
        null_corr.to_csv(os.path.join(data_dir, 'null_corr_total.csv'))
        print(f'{exp_idx + 1} / {len(exp_ver_list)} completed.')

# ---------------------------------------------------------
# Function: permutation-based p-values, z-scores, and plots
# ---------------------------------------------------------
def two_block_CCA_pval(data_folder, exp_ver_list):
    crit_p_val_pd, corr_p_val_pd = pd.DataFrame(), pd.DataFrame()
    crit_null_mean_pd, corr_null_mean_pd = pd.DataFrame(), pd.DataFrame()
    crit_null_std_pd, corr_null_std_pd = pd.DataFrame(), pd.DataFrame()
    crit_z_stat_pd, corr_z_stat_pd = pd.DataFrame(), pd.DataFrame()

    for exp_ver in exp_ver_list:
        data_dir = os.path.join(data_folder)

        ori_crit = pd.read_csv(os.path.join(data_dir, 'original_crit.csv'), header=None)
        ori_corr = pd.read_csv(os.path.join(data_dir, 'original_corr.csv'), header=None)

        null_crit_total = pd.read_csv(os.path.join(data_dir, 'null_crit_total.csv'), index_col=0)
        null_corr_total = pd.read_csv(os.path.join(data_dir, 'null_corr_total.csv'), index_col=0)

        # Compute p-values
        crit_p_val = [(ori_crit.iloc[0, j] < null_crit_total.iloc[:, j]).mean() for j in range(null_crit_total.shape[1])]
        corr_p_val = [(ori_corr.iloc[0, j] < null_corr_total.iloc[:, j]).mean() for j in range(null_corr_total.shape[1])]

        # Compute null stats
        crit_null_mean = null_crit_total.mean().values
        corr_null_mean = null_corr_total.mean().values

        crit_null_std = null_crit_total.std().values
        corr_null_std = null_corr_total.std().values

        # Compute z-stats
        crit_z_stat = ((ori_crit.values - crit_null_mean) / crit_null_std)[0]
        corr_z_stat = ((ori_corr.values - corr_null_mean) / corr_null_std)[0]

        # Append results
        crit_p_val_pd = pd.concat([crit_p_val_pd, pd.DataFrame([crit_p_val], index=[exp_ver])])
        corr_p_val_pd = pd.concat([corr_p_val_pd, pd.DataFrame([corr_p_val], index=[exp_ver])])

        crit_null_mean_pd = pd.concat([crit_null_mean_pd, pd.DataFrame([crit_null_mean], index=[exp_ver])])
        corr_null_mean_pd = pd.concat([corr_null_mean_pd, pd.DataFrame([corr_null_mean], index=[exp_ver])])

        crit_null_std_pd = pd.concat([crit_null_std_pd, pd.DataFrame([crit_null_std], index=[exp_ver])])
        corr_null_std_pd = pd.concat([corr_null_std_pd, pd.DataFrame([corr_null_std], index=[exp_ver])])

        crit_z_stat_pd = pd.concat([crit_z_stat_pd, pd.DataFrame([crit_z_stat], index=[exp_ver])])
        corr_z_stat_pd = pd.concat([corr_z_stat_pd, pd.DataFrame([corr_z_stat], index=[exp_ver])])

        # Plot histograms
        perm_summary_dir = os.path.join(data_folder, "perm_summary", exp_ver)
        os.makedirs(perm_summary_dir, exist_ok=True)

        for comp in range(null_crit_total.shape[1]):
            plt.figure(figsize=(8, 6))
            plt.hist(null_crit_total.iloc[:, comp], bins=30, label=f'p_uncor = {crit_p_val[comp]:.4f}')
            plt.axvline(ori_crit.iloc[0, comp], color='r')
            plt.xlabel('SGCCA convergence criteria')
            plt.ylabel('Counts')
            plt.title(f'Permutation test: Component {comp + 1} (crit)')
            plt.legend()
            plt.savefig(os.path.join(perm_summary_dir, f'{comp + 1}_crit_hist.png'))
            plt.close()

            plt.figure(figsize=(8, 6))
            plt.hist(null_corr_total.iloc[:, comp], bins=30, label=f'p_uncor = {corr_p_val[comp]:.4f}')
            plt.axvline(ori_corr.iloc[0, comp], color='r')
            plt.xlabel('SGCCA correlation')
            plt.ylabel('Counts')
            plt.title(f'Permutation test: Component {comp + 1} (corr)')
            plt.legend()
            plt.savefig(os.path.join(perm_summary_dir, f'{comp + 1}_corr_hist.png'))
            plt.close()

    # Name columns
    comp_names = [f'{i}_comp' for i in range(1, crit_p_val_pd.shape[1] + 1)]
    crit_p_val_pd.columns = comp_names
    corr_p_val_pd.columns = comp_names

    crit_null_mean_pd.columns = [f'{c}_null_mean' for c in comp_names]
    corr_null_mean_pd.columns = [f'{c}_null_mean' for c in comp_names]

    crit_null_std_pd.columns = [f'{c}_null_std' for c in comp_names]
    corr_null_std_pd.columns = [f'{c}_null_std' for c in comp_names]

    crit_z_stat_pd.columns = [f'{c}_zstat' for c in comp_names]
    corr_z_stat_pd.columns = [f'{c}_zstat' for c in comp_names]

    output_dir = os.path.join(data_folder, "perm_summary")
    os.makedirs(output_dir, exist_ok=True)

    # Save all
    crit_p_val_pd.to_csv(os.path.join(output_dir, '2block_SGCCA_perm_res_crit.csv'))
    corr_p_val_pd.to_csv(os.path.join(output_dir, '2block_SGCCA_perm_res_corr.csv'))

    crit_null_mean_pd.to_csv(os.path.join(output_dir, '2block_SGCCA_perm_res_crit_null_mean.csv'))
    corr_null_mean_pd.to_csv(os.path.join(output_dir, '2block_SGCCA_perm_res_corr_null_mean.csv'))

    crit_null_std_pd.to_csv(os.path.join(output_dir, '2block_SGCCA_perm_res_crit_null_std.csv'))
    corr_null_std_pd.to_csv(os.path.join(output_dir, '2block_SGCCA_perm_res_corr_null_std.csv'))

    crit_z_stat_pd.to_csv(os.path.join(output_dir, '2block_SGCCA_perm_res_crit_zstat.csv'))
    corr_z_stat_pd.to_csv(os.path.join(output_dir, '2block_SGCCA_perm_res_corr_zstat.csv'))

# ---------------------------------------------------------
# Function: FDR correction
# ---------------------------------------------------------
def CCA_fdrcorrection(data_dir, file_name):
    data_path = os.path.join(data_dir, "perm_summary", f"{file_name}.csv")
    data = pd.read_csv(data_path, index_col=0)
    fdr_corrected = pd.DataFrame(
        fdrcorrection(data.values.flatten())[1].reshape(data.shape),
        index=data.index, columns=data.columns
    )
    fdr_corrected.to_csv(os.path.join(data_dir, "perm_summary", f"{file_name}_fdr_corrected.csv"))

# ---------------------------------------------------------
# Main
# ---------------------------------------------------------
if __name__ == "__main__":
    # Replace this with the path to your result directory
    # It should contain:
    #   - original_crit.csv
    #   - original_corr.csv
    #   - [1-100]-th_permutation_crit.csv
    #   - [1-100]-th_permutation_corr.csv
    data_folder = "/path/to/your/2block_SGCCA/results"
    exp_ver_list = [""]  # 현재 폴더 기준, 경로만 사용

    two_block_CCA_summary(data_folder, exp_ver_list)
    two_block_CCA_pval(data_folder, exp_ver_list)

    for file_name in ['2block_SGCCA_perm_res_crit', '2block_SGCCA_perm_res_corr']:
        CCA_fdrcorrection(data_folder, file_name)
