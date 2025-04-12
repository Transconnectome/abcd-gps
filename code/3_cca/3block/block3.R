# block3_single.R
# 3-block SGCCA + permutation (단일 스크립트 재현용)

library(tidyverse)
library(magrittr)
library(RGCCA)
library(caret)

rm(list = ls())

# ------------------------------
# Load synthetic example data
# ------------------------------
smri  <- read_csv('smri_synthetic_EUR_100.csv')
gps   <- read_csv('gps_eur_synthetic_100.csv') %>%
  filter(set == 'test', ethnic_g == 'EUR')
pheno <- read_csv('pheno_synthetic_EUR_100.csv')
list_subj <- read_csv('subjectlist_EUR_100.csv')

# ------------------------------
# Merge datasets
# ------------------------------
all <- list_subj %>%
  left_join(gps, by = 'subjectkey') %>%
  left_join(smri, by = 'subjectkey') %>%
  left_join(pheno, by = 'subjectkey')

# ------------------------------
# Define data blocks
# ------------------------------
brain_block <- all %>% select(lh_bankssts_area._.1:wm.rh.insula._.18) %>% as.matrix()
gene_block  <- all %>% select(GMeur:GHappieur2) %>% as.matrix()
behav_block <- all %>% select(asr_scr_adhd_r:famhx_ss_parent_vs_p) %>% as.matrix()

A <- list(gene_block, brain_block, behav_block)
names(A) <- c("GPS", "sMRI", "Phenotype")

# 3-block connection matrix
C <- matrix(c(0, 1, 1,
              1, 0, 1,
              1, 1, 0), 3, 3)

# ------------------------------
# Sparsity parameter tuning
# ------------------------------
cat("Running permutation to find optimal sparsity...\n")
perm.out <- rgcca_permutation(A, n_cores = 4, par_type = "sparsity", n_perms = 50)
cat("Permutation completed.\n")

# ------------------------------
# Fit SGCCA model
# ------------------------------
cat("Running SGCCA model...\n")
result.rgcca <- rgcca(
  A, C, ncomp = c(5, 5, 5),
  sparsity = perm.out$best_params,
  verbose = TRUE, scale = TRUE,
  scale_block = "lambda1",
  method = "sgcca", superblock = FALSE,
  scheme = "centroid", comp_orth = FALSE,
  NA_method = "na.ignore"
)
cat("SGCCA completed.\n")

# ------------------------------
# Save original crit
# ------------------------------
output_dir <- "./3block/output"
if (!dir.exists(output_dir)) dir.create(output_dir, recursive = TRUE)
setwd(output_dir)

subjectkey <- rownames(A[[1]])
ori_crit <- sapply(1:5, function(j) max(result.rgcca$crit[[j]]))
write.csv(ori_crit, file = "original_crit.csv", row.names = FALSE)

save(result.rgcca, perm.out, gene_block, brain_block, behav_block,
     file = "SGCCA_3blocks_result.RData")

# ------------------------------
# Run permutation (100 iterations)
# ------------------------------
cat("Starting permutation testing...\n")
n_perm <- 100
for (i in 1:n_perm) {
  try({
    rand1 <- sample(nrow(A[[1]]))
    rand3 <- sample(nrow(A[[3]]))

    A_perm <- list(
      block1 = A[[1]][rand1, ],
      block2 = A[[2]],
      block3 = A[[3]][rand3, ]
    )
    names(A_perm) <- names(A)
    rownames(A_perm[[1]]) <- subjectkey
    rownames(A_perm[[3]]) <- subjectkey

    sgcca_perm <- rgcca(
      A_perm, connection = C, ncomp = 5,
      sparsity = perm.out$best_params,
      scale_block = "lambda1", scale = TRUE,
      method = "sgcca", superblock = FALSE,
      scheme = "centroid", verbose = TRUE,
      comp_orth = FALSE, NA_method = "na.ignore"
    )

    perm_crit <- sapply(1:5, function(j) max(sgcca_perm$crit[[j]]))
    write.csv(perm_crit, file = paste0(i, "-th_permutation_crit.csv"),
              row.names = FALSE)

    cat("Permutation", i, "completed\n")
  }, silent = TRUE)
}
cat("Permutation testing completed.\n")
