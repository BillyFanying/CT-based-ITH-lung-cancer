# Reviewer Code Guide

This documentation serves as a guide for reviewers to understand the core algorithms, detailed implementation logic, and code structures of this project. The codebase consists of two parts (Python and R) covering medical image preprocessing, intratumoral subregion (habitat) segmentation, high-dimensional radiomics feature extraction, robust feature selection, Cox proportional hazards regression modelling, and TCGA-based genomic analyses (MATH, TMB, and GSEA).

---

## 💻 Environment & Dependencies

Please ensure the code is executed under the recommended versions and packages listed below:

### 1. Python Environment
- Python Version: 3.11
- Image I/O & Formatting: SimpleITK, pydicom, nibabel, nrrd (pynrrd)
- Data Processing & Scientific Computing: numpy, pandas, scipy, scikit-image (skimage), trimesh
- Feature Extraction & Machine Learning: pyradiomics (radiomics), scikit-learn (sklearn)
- Image Augmentation: opencv-python (cv2)
- Visualization & Excel Generation: matplotlib, xlsxwriter, xlrd

### 2. R Environment
- R Version: 4.1.1
- Feature Selection & Survival Modeling: glmnet, survival, survminer, pROC
- Genomics & Mutation Heterogeneity: TCGAbiolinks, maftools, mclust
- Enrichment Analysis & Visualization: enrichplot, ggrepel, ggplot2, gridExtra
- Data Import/Export: readxl, openxlsx

---

## 📂 Project Structure & Detailed Implementation

The codebase is organized into four main directories corresponding to sequential stages of our study:

- 1-feature extraction: High-dimensional radiomics feature extraction
- 2-Intratumor Subregion Segmentation: Habitat segmentation based on voxel intensity and entropy
- 3-feature slection: Robust feature selection & Cox predictive modeling
- Gsea: Mutation heterogeneity calculation & GSEA plotting

---

### 📁 1-feature extraction (Radiomics Extraction)

This folder contains the script for extracting high-dimensional radiomics features from standardized patient files.

#### 3.Feature extraction.py
- Function: Batch extracts high-dimensional radiomics features.
- Implementation: Uses the pyradiomics library to execute feature extraction. It initializes RadiomicsFeatureExtractor with customized parameters: binWidth=25 (for gray-level discretization), normalize=True, normalizeScale=100, and correctMask=True. It extracts features from the original image, and applies a Laplacian of Gaussian (LoG) filter at three different scales (sigma = 1.0, 3.0, 5.0 mm) to capture fine, medium, and coarse texture details. The output is written to an Excel worksheet, and paths with extraction failures are logged to an error JSON file (e.g., Eex0lis.json).

---

### 📁 2-Intratumor Subregion Segmentation (Habitat Segmentation)

This directory implements the pipeline for dividing the tumor region of interest (ROI) into micro- and macro-subregions (habitats) based on local voxel intensity and texture entropy.

#### step1.py
- Implementation: Reads the 3D DICOM image and NIfTI mask files. It extracts the Volume of Interest (VOI) by identifying voxels where the binary mask is equal to 1. Voxel values outside the mask are zeroed out. The VOI voxel values are normalized to [0, 255] using min-max scaling and saved as voi_sitk1.nrrd.

#### step2.py
- Implementation: Dilation of the tumor mask in physical dimensions. It reads the voxel spacing of the mask using SimpleITK (GetSpacing()), translates a user-specified boundary thickness (e.g., 5.0 mm) into voxel radius (math.ceil(5.0 / spacing_x)), and extracts 2D boundary contours on each slice using skimage.measure.find_contours at a threshold of 0.5. It dilates the boundary by drawing overlapping ellipses/circles at each contour point using skimage.draw.ellipse and outputs the expanded 3D mask as nii5.nrrd.

#### step3.py
- Implementation: Masks the original DICOM sequence with the dilated mask (nii5.nrrd) to extract the voxel values of both the tumor core and its surrounding margin. Values are normalized to [0, 255] and outputted as dcm5.nrrd.

#### step4.py
- Implementation: Calculates local Shannon entropy maps to represent spatial heterogeneity. For each voxel inside the ROI, it defines a local sliding neighborhood of size 9 x 9. It computes the gray-level histogram (256 bins) of the window, normalizes it to obtain probability distribution p_i, and calculates the Shannon entropy: H = -sum( p_i * log2(p_i) ). The resulting spatial entropy map is saved as entropy.nrrd.

#### step5.py
- Implementation: First-Level Voxel Clustering (Micro-subregions). For each patient, it extracts the intensity from dcm5.nrrd and the localized entropy from entropy.nrrd for every voxel within the tumor ROI. These 2D vectors are scaled to [0, 1] via MinMaxScaler and clustered into 20 micro-subregions using voxel-level K-Means (sklearn.cluster.KMeans(n_clusters=20)). The output labels (1 to 20) are saved as kmeans20.nrrd.

#### step6.py & step7.py
- Implementation: Computes the features of the micro-subregions. For each of the 20 micro-subregions in a patient, it identifies voxel coordinates using numpy.argwhere and calculates the average voxel intensity and average local entropy using numpy.mean. These average values represent the texture and intensity profile of the micro-habitats.

#### step8.py
- Implementation: Optimal cluster number determination. It compiles the micro-subregion average intensity and entropy values across the patient cohort, standardizes them, and runs K-Means clustering for values of K in [2, 10]. It calculates and plots the Calinski-Harabasz Index (metrics.calinski_harabasz_score) and Silhouette Coefficient (metrics.silhouette_score) using matplotlib to select the optimal number of macro-subregions.

#### step9.py
- Implementation: Second-Level Cohort Clustering (Macro-subregions). Trains a K-Means model with K=XX (or the optimal K) on the cohort's micro-subregion features. It predicts the macro-subregion label (1 or 2) for each patient's 20 micro-subregions. Finally, it maps voxel labels in kmeans20.nrrd to their corresponding macro-subregion labels, and outputs the final segmented subregion masks.

#### step10.py
- Implementation: Computes the volume (voxel count) of each macro-subregion (e.g., subregion 1 and subregion 2) using numpy.argwhere, and exports the structured data to Excel to support statistical comparisons between clinical groups.

---

### 📁 3-feature slection (Feature Selection & Cox Survival Modeling)

This folder contains a modularized R package for filtering high-dimensional radiomics features and training predictive survival models.

#### main.R
- Function: Main orchestrator script.
- Implementation: Loads and cleans patient feature tables, sets random seeds (e.g., seednum = 6), performs stratified data splits, applies feature filtering (Wilcoxon rank-sum test, normalization, and LASSO Cox regression), fits multivariate Cox proportional hazards models, predicts survival risk scores, and writes outputs to Excel files.

#### Subfolder: functions/
This subfolder acts as a utility library containing modular functions used by the modeling pipeline:
- data_fun.R: Implements z-score standardization (z.score) to scale feature matrices.
- get_lasso_result_fun.R: Extracts features with non-zero coefficients (get_lasso_result) from the LASSO model at a chosen penalty parameter (e.g., lambda.min).
- glm_step_fun.R: Implements stepwise logistic regression feature selection (glm_step) based on Akaike Information Criterion (AIC) minimization.
- mrmr_fun.R: Implements the minimum Redundancy Maximum Relevance (mRMR) ensemble feature selection algorithm (mrmr.fun) to identify maximum-relevance covariates.
- roc_and_plot_fun.R: Plots Receiver Operating Characteristic (ROC) curves (roc_and_plot) with AUC values and optimal thresholds.
- sample_fun.R: Executes stratified sampling (stratified_sampling) to construct balanced train and test subsets.
- u_test_fun.R: Runs univariate Wilcoxon rank-sum tests (u_test) to filter features showing significant statistical association (p < 0.05).
- youden_index_fun.R: Calculates the Youden Index (get_youden_index) from ROC curves to locate the optimal diagnostic threshold.

---

### 📁 Gsea (Genomic Mutation & Pathway Enrichment Analysis)

This folder contains R analyses detailing tumor mutational status and pathway-level transcriptomic enrichment.

#### 4-MATH.R
- Function: Computes Mutant-Allele Tumor Heterogeneity (MATH) and Tumor Mutational Burden (TMB) scores.
- Implementation:
  1. Queries and downloads somatic mutation MAF files from TCGA (LUAD/LUSC) using TCGAbiolinks::GDCquery and GDCdownload.
  2. Reads MAF files using maftools::read.maf.
  3. Calculates the MATH score for each sample barcode via maftools::inferHeterogeneity. The MATH score is calculated as:
     MATH = 100 * Median Absolute Deviation (MAD) / Median Variant Allele Frequency (VAF)
     where the R implementation divides the output by 1.4286 to align with standard normal distributions.
  4. Computes TMB (mutations per megabase) using maftools::tmb.
  5. Filters results for specific patient sub-cohorts and exports the results to Excel.

#### gsea_plot.R
- Function: Generates Gene Set Enrichment Analysis (GSEA) plots.
- Implementation: Loads GSEA results. It searches for target pathway names (such as "Pyroptosis") using grep. It calls enrichplot::gseaplot2 to plot the enrichment score curve, ranking metric, and gene positions. It utilizes ggrepel::geom_text_repel to annotate selected core enrichment genes, and overlays a summary table of GSEA results (NES, P-value, and FDR) on the plot using gridExtra::tableGrob.
