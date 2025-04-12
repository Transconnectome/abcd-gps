rm(list = ls())

# --------------------------------------------------------------
# Correlation Analysis between GPS and Brain Features
# Description: Performs correlation and FDR-correction between
#              multiple GPS scores and imaging phenotypes
# Input: synthetic datasets (100 subjects, EUR) in /data folder
# Output: .csv files with significant correlations in /output folder
# --------------------------------------------------------------

############################# load library #############################
library(dplyr)
library(tidyr)
library(stats)  # for correlation and p-value calculation
library(qvalue) # for FDR correction

############################# load data #############################
# Please place the following CSV files into the /data directory.
# Example:
#   data/gps_eur_synthetic_100.csv
#   data/smri_synthetic_EUR_100.csv
#   ...

gps <- read.csv("data/gps_eur_synthetic_100.csv")

smri   <- read.csv("data/smri_synthetic_EUR_100.csv")
count  <- read.csv("data/count_synthetic_EUR_100.csv")
fa     <- read.csv("data/fa_synthetic_EUR_100.csv")
rs     <- read.csv("data/rsfmri_synthetic_EUR_100.csv")
mid    <- read.csv("data/midfmri_synthetic_EUR_100.csv")
nback  <- read.csv("data/nbackfmri_synthetic_EUR_100.csv")
sst    <- read.csv("data/sstfmri_synthetic_EUR_100.csv")

############################# prep data #############################
gps_smri   <- merge(gps, smri,  by = "subjectkey")
gps_count  <- merge(gps, count, by = "subjectkey")
gps_fa     <- merge(gps, fa,    by = "subjectkey")
gps_rs     <- merge(gps, rs,    by = "subjectkey")
gps_mid    <- merge(gps, mid,   by = "subjectkey")
gps_nback  <- merge(gps, nback, by = "subjectkey")
gps_sst    <- merge(gps, sst,   by = "subjectkey")

############################# correlation function #############################
correlation_analysis <- function(merged_data, gps_vars) {
    results <- data.frame()
    
    # Convert columns to numeric
    merged_data[gps_vars] <- lapply(merged_data[gps_vars], as.numeric)
    brain_vars <- setdiff(names(merged_data), gps_vars)
    merged_data[brain_vars] <- lapply(merged_data[brain_vars], as.numeric)
    
    for (gps_var in gps_vars) {
        for (brain_var in brain_vars) {
            data_subset <- merged_data %>% select(gps_var, brain_var) %>% na.omit()
            if (nrow(data_subset) > 2) {
                correlation_test <- cor.test(data_subset[[gps_var]], data_subset[[brain_var]], method = "pearson")
                results <- rbind(results, data.frame(
                    gps_variable = gps_var,
                    brain_variable = brain_var,
                    brain_p = correlation_test$p.value,
                    brain_r = correlation_test$estimate
                ))
            }
        }
    }
    
    # FDR correction
    results$brain_pfdr <- p.adjust(results$brain_p, method = "fdr")
    results$brain_sig <- ifelse(results$brain_pfdr < 0.0001, "****",
                                ifelse(results$brain_pfdr < 0.001, "***",
                                       ifelse(results$brain_pfdr < 0.01, "**",
                                              ifelse(results$brain_pfdr < 0.05, "*", ""))))
    
    significant_results <- results %>% filter(brain_sig != "")
    return(significant_results)
}

############################# define GPS variables #############################
gps_variables <- c(
    "GMeur", "WMeur", "TBVeur", "HEIGHTeur", "CPeur2", "EAeur1", "MDDeur6", "INSOMNIAeur6",
    "SNORINGeur1", "IQeur2", "PTSDeur4", "ADHDeur6", "DEPeur4", "BMIeur4", "ALCDEP_EURauto",
    "ASDauto", "ASPauto", "BIPauto", "CANNABISauto", "CROSSauto", "DRINKauto", "EDauto",
    "NEUROTICISMauto", "OCDauto", "RISK4PCauto", "RISKTOLauto", "SCZ_EURauto", "SMOKERauto",
    "WORRYauto", "SWBeur4", "GHappiHealth6", "GHappiMeaneur1", "GHappieur2"
)

############################# run correlation analysis #############################
gps_smri_results   <- correlation_analysis(gps_smri, gps_variables)
gps_count_results  <- correlation_analysis(gps_count, gps_variables)
gps_fa_results     <- correlation_analysis(gps_fa, gps_variables)
gps_rs_results     <- correlation_analysis(gps_rs, gps_variables)
gps_mid_results    <- correlation_analysis(gps_mid, gps_variables)
gps_nback_results  <- correlation_analysis(gps_nback, gps_variables)
gps_sst_results    <- correlation_analysis(gps_sst, gps_variables)

############################# write output #############################
# Please ensure an /output directory exists in the working directory

write.csv(gps_smri_results,  "output/gps_smri_results_w33gps.csv",  row.names = FALSE)
write.csv(gps_count_results, "output/gps_count_results_w33gps.csv", row.names = FALSE)
write.csv(gps_fa_results,    "output/gps_fa_results_w33gps.csv",    row.names = FALSE)
write.csv(gps_rs_results,    "output/gps_rs_results_w33gps.csv",    row.names = FALSE)
write.csv(gps_mid_results,   "output/gps_mid_results_w33gps.csv",   row.names = FALSE)
write.csv(gps_nback_results, "output/gps_nback_results_w33gps.csv", row.names = FALSE)
write.csv(gps_sst_results,   "output/gps_sst_results_w33gps.csv",   row.names = FALSE)

############################# summary check #############################
cat(paste0("smri: ",         nrow(gps_smri_results), "\n"))
cat(paste0("dmri(count): ",  nrow(gps_count_results), "\n"))
cat(paste0("dmri(fa): ",     nrow(gps_fa_results), "\n"))
cat(paste0("rs: ",           nrow(gps_rs_results), "\n"))
cat(paste0("fMRI(mid): ",    nrow(gps_mid_results), "\n"))
cat(paste0("fMRI(nback): ",  nrow(gps_nback_results), "\n"))
cat(paste0("fMRI(sst): ",    nrow(gps_sst_results), "\n"))
