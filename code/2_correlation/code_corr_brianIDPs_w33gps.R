rm(list=ls())
############################# load library #############################
library(dplyr)
library(tidyr)
library(stats)  # for correlation and p-value calculation
library(tidyverse)
library(magrittr)
############################# load data #############################
# Set working directory and load the data files (modify the path as needed)
setwd("/root/capsule/data")

subj_list <- read.csv('/root/capsule/data/subjectlist_EUR_100.csv')
colnames(subj_list) <- 'subjectkey'

gps <- read.csv('/root/capsule/data/gps_eur_synthetic.csv')
gps <- subj_list %>% left_join(gps, by = 'subjectkey')


# Load brain datasets
smri <- read.csv("/root/capsule/data/smri_synthetic.csv")
count <- read.csv("/root/capsule/data/dmri_count_synthetic.csv")
fa <- read.csv("/root/capsule/data/dmri_fa_synthetic.csv")
rs <- read.csv("/root/capsule/data/rsfmri_synthetic.csv")
mid <- read.csv("/root/capsule/data/midfmri_synthetic.csv")
nback <- read.csv("/root/capsule/data/nbackfmri_synthetic.csv")
sst <- read.csv("/root/capsule/data/sstfmri_synthetic.csv")

############################# prep data #############################
# Merge datasets with gps
gps_smri <- left_join(gps, smri, by = "subjectkey")
gps_count <- left_join(gps, count, by = "subjectkey")
gps_fa <- left_join(gps, fa, by = "subjectkey")
gps_rs <- left_join(gps, rs, by = "subjectkey")
gps_mid <- left_join(gps, mid, by = "subjectkey")
gps_nback <- left_join(gps, nback, by = "subjectkey")
gps_sst <- left_join(gps, sst, by = "subjectkey")

############################# correlation function #############################
# Function to perform correlation and FDR correction using the merged dataset
correlation_analysis <- function(merged_data, gps_vars) {
  results <- data.frame()
  
  # Ensure all columns are numeric
  merged_data[gps_vars] <- lapply(merged_data[gps_vars], as.numeric)
  brain_vars <- setdiff(names(merged_data), gps_vars)
  merged_data[brain_vars] <- lapply(merged_data[brain_vars], as.numeric)
  
  for (gps_var in gps_vars) {  # Loop through specified GPS variables
    for (brain_var in brain_vars) {  # Loop through non-GPS (brain) variables
      # Remove rows with NA values for the current pair of variables
      data_subset <- merged_data %>% select(gps_var, brain_var) %>% na.omit()
      
      # Check if there are enough valid observations for correlation
      if (nrow(data_subset) > 2) {  # At least 3 observations needed for correlation
        correlation_test <- cor.test(data_subset[[gps_var]], data_subset[[brain_var]], method = "pearson")
        p_value <- correlation_test$p.value
        cor_value <- correlation_test$estimate
        
        results <- rbind(results, data.frame(gps_variable = gps_var,
                                             brain_variable = brain_var,
                                             brain_p = p_value,
                                             brain_r = cor_value))
      }
    }
  }
  
  # FDR correction
  results$brain_pfdr <- p.adjust(results$brain_p, method = "fdr")
  results$brain_sig <- ifelse(results$brain_pfdr < 0.0001, "****",
                              ifelse(results$brain_pfdr < 0.001, "***",
                                     ifelse(results$brain_pfdr < 0.01, "**",
                                            ifelse(results$brain_pfdr < 0.05, "*", ""))))
  
  # Filter only significant results
  significant_results <- results %>% filter(brain_sig != "")
  return(significant_results)
}

############################# perform correlation for each dataset #############################
# List of specific GPS variables to be used in the analysis
gps_variables <- c("GMeur", "WMeur", "TBVeur", "HEIGHTeur",  "CPeur2","EAeur1", "MDDeur6", "INSOMNIAeur6", "SNORINGeur1", "IQeur2",        
                   "PTSDeur4","ADHDeur6", "DEPeur4", "BMIeur4","ALCDEP_EURauto", "ASDauto","ASPauto", 
                   "BIPauto", "CANNABISauto", "CROSSauto","DRINKauto", "EDauto", "NEUROTICISMauto","OCDauto",       
                   "RISK4PCauto", "RISKTOLauto","SCZ_EURauto","SMOKERauto","WORRYauto","SWBeur4", "GHappiHealth6", 
                   "GHappiMeaneur1", "GHappieur2"   )

# Perform correlation analysis on each merged dataset using only specified GPS variables
gps_smri_results <- correlation_analysis(gps_smri, gps_variables)
gps_count_results <- correlation_analysis(gps_count, gps_variables)
gps_fa_results <- correlation_analysis(gps_fa, gps_variables)
gps_rs_results <- correlation_analysis(gps_rs, gps_variables)
gps_mid_results <- correlation_analysis(gps_mid, gps_variables)
gps_nback_results <- correlation_analysis(gps_nback, gps_variables)
gps_sst_results <- correlation_analysis(gps_sst, gps_variables)

############################# write csv #############################
# Set output directory
setwd("/root/capsule/results")
if (!dir.exists("2_correlation")) {
  dir.create("2_correlation")
}
setwd("/root/capsule/results/2_correlation")

# Write results to CSV files
write.csv(gps_smri_results, "gps_smri_results_w33gps.csv", row.names = FALSE)
# write.csv(gps_count_results, "gps_count_results_w33gps.csv", row.names = FALSE)
# write.csv(gps_fa_results, "gps_fa_results_w33gps.csv", row.names = FALSE)
# write.csv(gps_rs_results, "gps_rs_results_w33gps.csv", row.names = FALSE)
# write.csv(gps_mid_results, "gps_mid_results_w33gps.csv", row.names = FALSE)
# write.csv(gps_nback_results, "gps_nback_results_w33gps.csv", row.names = FALSE)
# write.csv(gps_sst_results, "gps_sst_results_w33gps.csv", row.names = FALSE)

############################# check data #############################
print(paste0('smri: ', nrow(gps_smri_results))) #2189
# print(paste0('dmri(count): ', nrow(gps_count_results))) #83
# print(paste0('dmri(fa): ', nrow(gps_fa_results))) #394
# print(paste0('rs: ', nrow(gps_rs_results))) #0
# print(paste0('fMRI(mid): ', nrow(gps_mid_results))) #0
# print(paste0('fMRI(nback): ', nrow(gps_nback_results))) #61
# print(paste0('fMRI(sst): ', nrow(gps_sst_results))) #0

