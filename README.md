# abcd-gps

This repository contains code and **synthetic** data for the manuscript:

> **Joo, Y. Y., Kim, B. G., Kim, G., Lee, E., Seo, J., & Cha, J.** (2025).  
> **Polygenic architecture of brain structure and function, behaviors, and psychopathologies in children.**

---

## Table of Contents
1. [Overview](#overview)  
2. [Repository Structure](#repository-structure)  
3. [Getting Started](#getting-started)  
4. [Data Availability](#data-availability)  
5. [Usage](#usage)  
6. [Authors and Contributors](#authors-and-contributors)  
7. [License](#license)  
8. [Contact](#contact)  
9. [Citation](#citation)  

---

## Overview
This study examines the genetic architecture of brain structure, function, behaviors, and psychopathologies in a large cohort of preadolescent children. Using genome-wide polygenic scores (GPSs) across multiple traits and advanced multivariate analyses, we uncover key connections between genetic risk profiles and a wide range of brain imaging-derived phenotypes, cognitive measures, and psychological traits.

---

## Repository Structure
- **code/**: Jupyter Notebooks and scripts for reproducing key aspects of the analysis.  
  - *Note*: For heritability calculations, only sample code is included due to restrictions on sharing real SNP data.  

*We do not host raw participant data from the ABCD Study due to data use agreements.*

---

## Getting Started

1. **Clone the repository**  
   ```bash
   git clone https://github.com/your-username/abcd-gps.git
   ```

2. **Install required packages**  
   - Refer to the `code/requirements.txt` (or any environment file) for a list of Python/R packages.  
   - We recommend using a virtual environment or Conda environment to avoid dependency conflicts.

3. **Reproduce analyses with synthetic data**  
   - Each main analysis step is in a separate notebook or script in `code/`.  
   - Since only synthetic data are provided, results will not match those in the manuscript exactly, but the workflow and structure remain the same.

---

## Data Availability

- **ABCD Study**: Real data can be accessed from the [Adolescent Brain Cognitive Development (ABCD) Study](https://abcdstudy.org/) upon approval.

- **Synthetic Data**: This repository uses synthetic data generated from the real cohort using CTGAN and other generative methods.  
  - The synthetic dataset consists of **100 randomly sampled participants** and mimics the structure of the ABCD dataset.  
  - Due to GitHub file size limits, data are externally hosted and can be downloaded from the following link:

  👉 **[Download synthetic data (Google Drive)](https://drive.google.com/drive/folders/1M-uzD1k1IiEXAbrHxE_vYVaWtiq4AHx2?ths=true)**

- **GWAS Summary Statistics**: Publicly available GWAS summary statistics are referenced in the manuscript. However, only **sample code** is provided here for heritability-related analyses due to privacy and data-use constraints.

---

## Usage

1. **Preprocessing**  
   - Scripts for basic data cleaning, quality control, and merging across modalities in the synthetic dataset.

2. **Analysis**  
   - Main analyses (e.g., SGCCA, heritability scripts, GPS-based predictions) are demonstrated with sample code in `code/`.

3. **Visualization**  
   - Example scripts for generating figures from the synthetic dataset.

*Please note that the synthetic data do not reflect actual results or distributions of the ABCD Study participants.*

---

## Authors and Contributors

- **Yoonjung (Yoonie) Joo**  
- **Bo-Gyeom Kim**  
- **Gakyung Kim**  
- **Eunji Lee**  
- **Jungwoo Seo**  
- **Jiook Cha** (*Corresponding Author*)  

For questions, please contact [Jiook Cha](mailto:connectome@snu.ac.kr).

---

## License

This project is licensed under the terms of the [MIT License](LICENSE).  
Please see the `LICENSE` file for details.

---

## Contact

For inquiries or suggestions related to this repository, please reach out to:

**Jiook Cha, Ph.D.**  
[connectome@snu.ac.kr](mailto:connectome@snu.ac.kr)

---

## Citation

If you use this code (or any part of it) for your research, please cite our work:
