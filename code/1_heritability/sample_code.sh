# =============================================================
# GCTA SNP-based Heritability Analysis
#
# Overview:
# Step 1. Generate the Genetic Relationship Matrix (GRM) from autosomal SNPs
# Step 2. Estimate SNP heritability using REML for each phenotype of interest
#
# Note:
# - You only need to create the GRM once per sample set (Step 1).
# - You can then reuse the GRM to estimate heritability for multiple phenotypes (Step 2).
# =============================================================

# ----------------------------------------------
# Step 1: Create Genetic Relationship Matrix (GRM)
# ----------------------------------------------
gcta64 \
  --bfile ABCD_QCed_2021_PCair_8620_SNPrsid_final_updated_EUR_5130 \  # Input PLINK binary genotype files (bed/bim/fam)
  --autosome \                                                        # Use autosomal SNPs only (chromosomes 1–22)
  --make-grm \                                                        # Generate the Genetic Relationship Matrix (GRM)
  --out ../Out.Demo/GRM_EUR_5130 \                                    # Output prefix for GRM files
  --thread-num 10                                                     # Use 10 threads for faster computation

# ----------------------------------------------
# Step 2: Estimate SNP-based Heritability via REML
# ----------------------------------------------
gcta64 \
  --grm ../Out.Demo/GRM_EUR_5130 \                                    # Input GRM file prefix from Step 1
  --pheno heritability_smri_feature.txt \                             # Phenotype file (FID, IID, phenotype1, phenotype2, ...)
  --mpheno 1 \                                                        # Use the 1st phenotype column (can loop over multiple)
  --reml \                                                            # Perform Restricted Maximum Likelihood (REML) analysis
  --covar heritability_demo_cate_data.txt \                           # Categorical covariates (e.g., sex, site)
  --qcovar heritability_demo_conti_data.txt \                         # Quantitative covariates (e.g., age, PCs)
  --out ../Out.Demo/GRM_5130_estimates \                              # Output prefix for heritability results
  --thread-num 10                                                     # Use 10 threads for faster computation
