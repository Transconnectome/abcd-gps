import os
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.stats.multitest import fdrcorrection

# Define functions for CCA summary and significance testing
def two_block_CCA_summary(data_folder, exp_ver_list):
    for exp_idx, exp_ver in enumerate(exp_ver_list):
        data_dir = os.path.join(data_folder)
        ori_crit = pd.read_csv(os.path.join(data_dir, 'original_crit.csv'), index_col=0)
        ori_corr = pd.read_csv(os.path.join(data_dir, 'original_corr.csv'), index_col=0)
        null_crit = pd.DataFrame()
        null_corr = pd.DataFrame()

        for i in range(1, 101):
            try:
                null_crit_temp = pd.read_csv(os.path.join(data_dir, f'{i}-th_permutation_crit.csv'), index_col=0).T
                null_corr_temp = pd.read_csv(os.path.join(data_dir, f'{i}-th_permutation_corr.csv'), index_col=0).T
                null_crit_temp.index = [f'{i}-th_null']
                null_corr_temp.index = [f'{i}-th_null']
                null_crit = pd.concat([null_crit, null_crit_temp])
                null_corr = pd.concat([null_corr, null_corr_temp])
            except FileNotFoundError:
                print(f"File missing for {exp_ver}, iteration {i}")

        null_crit.columns = [f'{j}_comp' for j in range(1, 6)]
        null_corr.columns = [f'{j}_comp' for j in range(1, 6)]
        null_crit.to_csv(os.path.join(data_dir, 'null_crit_total.csv'))
        null_corr.to_csv(os.path.join(data_dir, 'null_corr_total.csv'))
        print(f'{exp_idx + 1} / {len(exp_ver_list)} completed.')

def two_block_CCA_pval(data_folder, exp_ver_list):
    # Initialize DataFrames to store results
    crit_p_val_pd = pd.DataFrame()
    corr_p_val_pd = pd.DataFrame()

    crit_null_mean_pd = pd.DataFrame()
    corr_null_mean_pd = pd.DataFrame()

    crit_null_std_pd = pd.DataFrame()
    corr_null_std_pd = pd.DataFrame()

    crit_z_stat_pd = pd.DataFrame()
    corr_z_stat_pd = pd.DataFrame()

    for exp_ver in exp_ver_list:
        data_dir = os.path.join(data_folder)

        # Load original crit and corr
        ori_crit_path = os.path.join(data_dir, 'original_crit.csv')
        ori_corr_path = os.path.join(data_dir, 'original_corr.csv')
        null_crit_total_path = os.path.join(data_dir, 'null_crit_total.csv')
        null_corr_total_path = os.path.join(data_dir, 'null_corr_total.csv')

        # Validate file existence
        for file_path in [ori_crit_path, ori_corr_path, null_crit_total_path, null_corr_total_path]:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")

        # Load data
        ori_crit = pd.read_csv(ori_crit_path, header=0, index_col=None, names=["value"]).T
        ori_corr = pd.read_csv(ori_corr_path, header=0, index_col=None, names=["value"]).T
    
        null_crit_total = pd.read_csv(null_crit_total_path, index_col=0, header=0)
        null_corr_total = pd.read_csv(null_corr_total_path, index_col=0, header=0)
        print('ori_crit: ', ori_crit)
        print('ori_corr: ', ori_corr)

        # Validate data content
        if ori_crit.empty or ori_corr.empty or null_crit_total.empty or null_corr_total.empty:
            raise ValueError("One or more required datasets are empty.")

        # Calculate p-values
        crit_p_val = [(ori_crit.iloc[0, j] < null_crit_total.iloc[:, j]).mean() for j in range(null_crit_total.shape[1])]
        corr_p_val = [(ori_corr.iloc[0, j] < null_corr_total.iloc[:, j]).mean() for j in range(null_corr_total.shape[1])]

        # Calculate null means and stds
        crit_null_mean = null_crit_total.mean().values
        corr_null_mean = null_corr_total.mean().values

        crit_null_std = null_crit_total.std().values
        corr_null_std = null_corr_total.std().values

        # Calculate z-scores
        crit_z_stat = ((ori_crit.values - crit_null_mean) / crit_null_std)[0]
        corr_z_stat = ((ori_corr.values - corr_null_mean) / corr_null_std)[0]

        # Append results to DataFrames
        crit_p_val_pd = pd.concat([crit_p_val_pd, pd.DataFrame([crit_p_val], index=[exp_ver])])
        corr_p_val_pd = pd.concat([corr_p_val_pd, pd.DataFrame([corr_p_val], index=[exp_ver])])

        crit_null_mean_pd = pd.concat([crit_null_mean_pd, pd.DataFrame([crit_null_mean], index=[exp_ver])])
        corr_null_mean_pd = pd.concat([corr_null_mean_pd, pd.DataFrame([corr_null_mean], index=[exp_ver])])

        crit_null_std_pd = pd.concat([crit_null_std_pd, pd.DataFrame([crit_null_std], index=[exp_ver])])
        corr_null_std_pd = pd.concat([corr_null_std_pd, pd.DataFrame([corr_null_std], index=[exp_ver])])

        crit_z_stat_pd = pd.concat([crit_z_stat_pd, pd.DataFrame([crit_z_stat], index=[exp_ver])])
        corr_z_stat_pd = pd.concat([corr_z_stat_pd, pd.DataFrame([corr_z_stat], index=[exp_ver])])

        # Save histograms
        perm_summary_dir = os.path.join(data_folder, "perm_summary", exp_ver)
        os.makedirs(perm_summary_dir, exist_ok=True)

        for comp in range(5):
            plt.figure(figsize=(8, 6))
            plt.hist(null_crit_total.iloc[:, comp], bins=30, label=f'p_uncor = {crit_p_val[comp]:.4f}')
            plt.axvline(ori_crit.iloc[0, comp], color='r')
            plt.xlabel('SGCCA convergence criteria', fontsize=15)
            plt.ylabel('Counts', fontsize=15)
            plt.title(f'Permutation test result: {comp + 1}_comp \n {exp_ver}')
            plt.legend()
            plt.savefig(os.path.join(perm_summary_dir, f'{comp + 1}_crit_hist.png'))
            plt.close()

            plt.figure(figsize=(8, 6))
            plt.hist(null_corr_total.iloc[:, comp], bins=30, label=f'p_uncor = {corr_p_val[comp]:.4f}')
            plt.axvline(ori_corr.iloc[0, comp], color='r')
            plt.xlabel('SGCCA correlation coefficient', fontsize=15)
            plt.ylabel('Counts', fontsize=15)
            plt.title(f'Permutation test result: {comp + 1}_comp \n {exp_ver}')
            plt.legend()
            plt.savefig(os.path.join(perm_summary_dir, f'{comp + 1}_corr_hist.png'))
            plt.close()

    # Save results to CSV
    crit_p_val_pd.columns = [f'{i}_comp' for i in range(1, 6)]
    corr_p_val_pd.columns = [f'{i}_comp' for i in range(1, 6)]

    crit_null_mean_pd.columns = [f'{i}_comp_null_mean' for i in range(1, 6)]
    corr_null_mean_pd.columns = [f'{i}_comp_null_mean' for i in range(1, 6)]

    crit_null_std_pd.columns = [f'{i}_comp_null_std' for i in range(1, 6)]
    corr_null_std_pd.columns = [f'{i}_comp_null_std' for i in range(1, 6)]

    crit_z_stat_pd.columns = [f'{i}_comp_zstat' for i in range(1, 6)]
    corr_z_stat_pd.columns = [f'{i}_comp_zstat' for i in range(1, 6)]

    output_dir = os.path.join(data_folder, "perm_summary")
    os.makedirs(output_dir, exist_ok=True)

    crit_p_val_pd.to_csv(os.path.join(output_dir, '2block_SGCCA_perm_res_crit.csv'))
    corr_p_val_pd.to_csv(os.path.join(output_dir, '2block_SGCCA_perm_res_corr.csv'))

    crit_null_mean_pd.to_csv(os.path.join(output_dir, '2block_SGCCA_perm_res_crit_null_mean.csv'))
    corr_null_mean_pd.to_csv(os.path.join(output_dir, '2block_SGCCA_perm_res_corr_null_mean.csv'))

    crit_null_std_pd.to_csv(os.path.join(output_dir, '2block_SGCCA_perm_res_crit_null_std.csv'))
    corr_null_std_pd.to_csv(os.path.join(output_dir, '2block_SGCCA_perm_res_corr_null_std.csv'))

    crit_z_stat_pd.to_csv(os.path.join(output_dir, '2block_SGCCA_perm_res_crit_zstat.csv'))
    corr_z_stat_pd.to_csv(os.path.join(output_dir, '2block_SGCCA_perm_res_corr_zstat.csv'))
    

def CCA_fdrcorrection(data_dir, file_name):
    data_path = os.path.join(data_dir, "perm_summary", f"{file_name}.csv")
    print('data_path: ', data_path)
    data = pd.read_csv(data_path, index_col=0)
    print('data: ', data)
    # FDR correction for total p-values
    total_fdr_corrected = pd.DataFrame(fdrcorrection(data.values.flatten())[1].reshape(data.shape),
                                        index=data.index, columns=data.columns)
    total_fdr_corrected_path = os.path.join(data_dir, "perm_summary", f"{file_name}_fdr_corrected.csv")
    total_fdr_corrected.to_csv(total_fdr_corrected_path)

###### main ######
data_folder = '/root/capsule/results/3_cca_2block'
exp_ver_list = ["SGCCA_2blocks_results_EA_sMRI_BS1000.RData"]

print(data_folder)

two_block_CCA_summary(data_folder, exp_ver_list)
two_block_CCA_pval(data_folder, exp_ver_list)
for file_name in ['2block_SGCCA_perm_res_crit', '2block_SGCCA_perm_res_corr']:
    CCA_fdrcorrection(data_folder, file_name)