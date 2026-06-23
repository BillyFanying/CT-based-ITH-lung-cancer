# Reviewer Code Guide

This documentation serves as a guide for reviewers to understand the core algorithms, detailed implementation logic, and code structures of this project. The codebase consists of two parts (Python and R) covering medical image preprocessing, image data augmentation, intratumoral subregion (habitat) segmentation, high-dimensional radiomics feature extraction, robust feature selection, Cox proportional hazards regression modelling, and TCGA-based genomic analyses (MATH, TMB, and GSEA).

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

- 1-feature extraction: Image augmentation, formatting & radiomics extraction
- 2-Intratumor Subregion Segmentation: Habitat segmentation based on voxel intensity and entropy
- 3-feature slection: Robust feature selection & Cox predictive modeling
- Gsea: Mutation heterogeneity calculation & GSEA plotting

---

### 📁 1-feature extraction (Image Preprocessing & Radiomics Extraction)

This folder contains scripts for scanning image datasets, performing medical data augmentation, converting formats to NRRD, and extracting high-dimensional radiomics features.

#### 1.pathlist.py
- Function: Generates patient image file path databases. 
- Implementation: Uses Python's os.walk to recursively traverse the data directories. It filters and matches sequence folder names containing specific target modalities (e.g., 'T2W'), and exports the matching directories into a JSON structure and an Excel spreadsheet (via pandas and xlsxwriter) to serve as a cohort path index.

#### 1-Zengqiang.py
- Function: Performs medical-grade data augmentation.
- Implementation:
  1. Data Normalization: Loads 2D/3D DICOM files using pydicom, extracts raw voxel arrays, and rescales them to 8-bit intensity ranges [0, 255].
  2. Augmentation Operations: Applies seven mild, clinically reasonable augmentations to the pixel array:
     - Rotation: Done within +/- 5 degrees using scipy.ndimage.rotate.
     - Brightness & Contrast Scaling: Scales voxel intensities and contrast by a random factor within [0.95, 1.05].
     - Gaussian Noise: Adds noise with sigma in [0.5, 2.0].
     - Translation: Shifts images by +/- 2 pixels using affine mapping (cv2.warpAffine).
     - Zooming: Scales images by a factor of [0.98, 1.02] via bilinear interpolation (cv2.resize).
     - Elastic Deformation: Introduces local distortion by applying a Gaussian-filtered displacement field (alpha=5, sigma=3) via scipy.ndimage.map_coordinates.
  3. Metadata Update: Re-writes the augmented arrays back to new DICOM files while appending metadata information (SeriesDescription and ImageType).
  4. Quality Assessment: Uses skimage.metrics.structural_similarity to calculate the Structural Similarity Index (SSIM) between original and augmented images, verifying that the augmentation remains mild and preserves diagnostic structures (average SSIM > 0.85).

#### 2.Dcm-Nii to Nrrd.py
- Function: Standardizes file formats.
- Implementation: Uses SimpleITK.ImageSeriesReader to query Series IDs and filenames of the DICOM sequences. It reads the DICOM slice stack into a 3D image object and writes it as an NRRD file using sitk.WriteImage. For NIfTI segmentation masks (.nii / .nii.gz), it reads the files using sitk.ReadImage and saves them in NRRD format, ensuring spatial resolution, coordinate origin, and spacing match the image sequence.

#### 3.Feature extraction.py
- Function: Batch extracts high-dimensional radiomics features.
- Implementation: Uses the pyradiomics library to execute feature extraction. It initializes RadiomicsFeatureExtractor with customized parameters: binWidth=25 (for gray-level discretization), normalize=True, normalizeScale=100, and correctMask=True. It extracts features from the original image, and applies a Laplacian of Gaussian (LoG) filter at three different scales (sigma = 1.0, 3.0, 5.0 mm) to capture fine, medium, and coarse texture details. The output is written to an Excel worksheet, and paths with extraction failures are logged to "Eex0lis(提特征错误的人S1).json".

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
- Implementation: Second-Level Cohort Clustering (Macro-subregions). Trains a K-Means model with K=2 (or the optimal K) on the cohort's micro-subregion features. It predicts the macro-subregion label (1 or 2) for each patient's 20 micro-subregions. Finally, it maps voxel labels in kmeans20.nrrd to their corresponding macro-subregion labels, and outputs the final segmented subregion masks.

#### step10.py & To_Boxpot.py
- Implementation: Computes the volume (voxel count) of each macro-subregion using numpy.argwhere and extracts their mean intensity/entropy values, exporting the structured data to Excel to generate boxplots for statistical comparisons between clinical groups.

---

### 📁 3-feature slection (Feature Selection & Cox Survival Modeling)

This folder contains R scripts for filtering high-dimensional radiomics features and training multivariate Cox proportional hazards models to predict patient outcomes (e.g., Progression-Free Survival).

#### 1.txt
- Implementation: Builds a robust survival modeling pipeline using R packages:
  1. Stratified Splitting: Repeats random splitting until both the training set (70%) and testing set (30%) contain representative balances of the binary labels (label).
  2. Wilcoxon Rank-Sum Test: Conducts Wilcoxon tests (wilcox.test) on the training set for all radiomics features, retaining features with p < 0.05 that are significantly associated with the labels.
  3. Z-score Standardization: Standardizes the selected features of the training set. The testing set is normalized using the mean and standard deviation derived from the training set.
  4. LASSO Cox Regression: Feeds the standardized features and survival endpoints (Time, Status) into glmnet::cv.glmnet(..., family = "cox"). It runs a 10-fold cross-validation to find the optimal penalty parameter (lambda.min) and extracts features with non-zero coefficients.
  5. Multivariate Cox Regression: Fits a multivariate Cox model using the survival::coxph function with backtick-quoted feature names (to support features with special characters). It generates survival risk scores (linear predictors, lp) using the predict function.
  6. Evaluation: Evaluates performance by computing the C-index (survival::concordance), Area Under the Curve (AUC) via the pROC package, Accuracy (ACC), Sensitivity (SEN), and Specificity (SPE). Metrics are saved across 10 iterations and outputted to Excel.

#### 2.txt
- Implementation: Executes the exact same pipeline on a single selected seed (e.g., seednum = 6) and writes intermediate results (such as train/test splits, selected features, and prediction risk scores) to Excel files, ensuring reproducibility and allowing reviewers to inspect intermediate data.

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
- Implementation: Loads pre-calculated GSEA workspace results from gseago2.RData. It searches for target pathway names (such as "Pyroptosis") using grep. It calls enrichplot::gseaplot2 to plot the enrichment score curve, ranking metric, and gene positions. It utilizes ggrepel::geom_text_repel to annotate selected core enrichment genes, and overlays a summary table of GSEA results (NES, P-value, and FDR) on the plot using gridExtra::tableGrob.

#### gseago2.RData
- Function: Stores pre-calculated GSEA analysis results (gsea object) to be loaded and plotted by gsea_plot.R.
