# Download GCTA tool from https://yanglab.westlake.edu.cn/software/gcta/#Download

# Calculating the genetic relationship matrix (GRM) from all the autosomal SNPs
gcta64 --bfile ../ABCD_genotype2021/ABCD_QCed_2021_PCair_8620_SNPrsid_final_updated_EUR_5130 --autosome --make-grm --out ../Out.Demo/GRM_EUR_5130 --thread-num 10 

# Estimating the variance explained by the SNPs
gcta64 --grm ../Out.Demo/GRM_EUR_5130 --pheno ../D.Demo/sMRI_Sample.10_EUR_v.ID.txt --mpheno 1 --reml --covar ../D.Demo/cov.cate.1_EUR_v.ID.txt  --qcovar ../D.Demo/cov.conti.4_EUR_v.ID.txt  --out ../Out.Demo/GRM_5130_estimates --thread-num 10