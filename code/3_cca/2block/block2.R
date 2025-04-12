# Load required libraries
library(tidyverse)  # Data manipulation and visualization
library(magrittr)   # Pipe operator (%>%)
library(RGCCA)      # Generalized Canonical Correlation Analysis
library(caret)      # Data preprocessing

# Clear environment
rm(list = ls())

# Set working directory and load data

# Load synthetic data
smri <- read_csv('smri_synthetic_EUR_100.csv')  # sMRI data (9,958 x 390)
gps <- read_csv('gps_eur_synthetic_100.csv') %>% 
  filter(set == 'test', ethnic_g == 'EUR')  # Filter test set and EUR ethnicity (4,254 x 37)
pheno <- read_csv('pheno_synthetic_EUR_100.csv')         # Phenotype data

# Load subject list
list_subj <- read_csv('subjectlist_EUR_100.csv')

# Merge all datasets by "subjectkey"
all <- list_subj %>% 
  left_join(gps, by = 'subjectkey') %>% 
  left_join(smri, by = 'subjectkey') %>% 
  left_join(pheno, by = 'subjectkey')

# Prepare data blocks for SGCCA
brain <- all %>% select(lh_bankssts_area._.1:wm.rh.insula._.18)  # sMRI block
gene <- all %>% select(GMeur:GHappieur2)                         # GPS block
behav <- all %>% select(asr_scr_adhd_r:famhx_ss_parent_vs_p)     # Phenotype block

# Convert selected blocks to matrices
brain_block <- as.matrix(brain)
gene_block <- as.matrix(gene)
behav_block <- as.matrix(behav)

# Define data blocks and their connections
A <- list(gene_block, brain_block)  # List of data blocks (GPS and sMRI)
C <- matrix(c(0, 1, 1, 0), 2, 2)    # Connection matrix (1 indicates connection)

# Name the blocks for reference
names(A) <- c("GPS", "sMRI")

# Perform permutation test to determine optimal sparsity parameters
cat("Starting permutation test...\n")
perm.out <- rgcca_permutation(A, n_cores = 8, par_type = "sparsity", n_perms = 50)
cat("Permutation test completed.\n")

# Run SGCCA with the optimal sparsity parameters
cat("Starting SGCCA...\n")
result.rgcca <- rgcca(
  A, C, ncomp = c(5, 5), sparsity = perm.out$best_params,
  verbose = TRUE, scale = TRUE, scale_block = "lambda1", method = "sgcca"
)
cat("SGCCA completed.\n")

# Save original crit and corr results for sigtest_2block.py
ori_corr <- abs(diag(cor(result.rgcca$Y$GPS, result.rgcca$Y$sMRI)))
ori_crit <- sapply(1:5, function(j) max(result.rgcca$crit[[j]]))

saving_dir <- "/output"
if (!dir.exists(saving_dir)) dir.create(saving_dir, recursive = TRUE)
setwd(saving_dir)

write.csv(ori_corr, file = paste0(saving_dir, "/original_corr.csv"), row.names = FALSE)
write.csv(ori_crit, file = paste0(saving_dir, "/original_crit.csv"), row.names = FALSE)

# Perform bootstrap to assess stability of the results
cat("Starting bootstrap...\n")
result.rgcca.boot <- rgcca_bootstrap(result.rgcca, n_boot = 10, n_cores = 1)
cat("Bootstrap completed.\n")

# Save SGCCA and bootstrap results
save(
  result.rgcca.boot, result.rgcca, perm.out, brain_block, gene_block,
  file = paste0("SGCCA_2blocks_results_EA_sMRI_BS1000.RData")
)

# Export loadings for GPS and sMRI blocks to CSV files
data <- result.rgcca.boot$stats %>% filter(type == "loadings")
write.csv(
  data %>% filter(block == "GPS"),
  file = paste0("SGCCA_2blocks_EA_GPS_sMRI_BS1000_loadings.csv"),
  row.names = TRUE
)
write.csv(
  data %>% filter(block == "sMRI"),
  file = paste0("SGCCA_2blocks_EA_brain_sMRI_BS1000_loadings.csv"),
  row.names = TRUE
)

cat("All steps completed successfully.\n")

# Run Permutation for SGCCA Results
cat("Starting Permutation Test on Results...\n")
n_perm <- 100
n_start <- 1
n_step <- 1
subjectkey <- row.names(brain)

for (i in seq(n_start, n_perm, by = n_step)) {
  cat("Starting permutation", i, "\n")
  if (file.exists(paste0(saving_dir, '/', i, '-th_permutation_crit.csv'))) {
    cat("File already exists for permutation", i, "- Skipping.\n")
    next # Skip if file already exists
  } else {
    try({
      rand1 <- sample(nrow(brain_block))
      brain_perm <- brain_block[rand1, ]
      rownames(brain_perm) <- subjectkey

      A_perm <- list(gene_block, brain_perm)
      sgcca_perm <- rgcca(
        A_perm, connection = C, ncomp = c(5, 5), sparsity = perm.out$best_params,
        verbose = TRUE, scale = TRUE, scale_block = "lambda1", method = "sgcca"
      )

      perm_corr <- abs(diag(cor(sgcca_perm$Y$block1, sgcca_perm$Y$block2)))
      perm_crit <- sapply(1:5, function(j) max(sgcca_perm$crit[[j]]))

      write.csv(perm_corr, file = paste0(saving_dir, '/', i, '-th_permutation_corr.csv'))
      write.csv(perm_crit, file = paste0(saving_dir, '/', i, '-th_permutation_crit.csv'))

      cat("Permutation", i, "completed successfully.\n")
    }, silent = FALSE)
  }
}
cat("Permutation testing completed successfully.\n")
