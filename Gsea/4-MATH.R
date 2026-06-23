BiocManager::install("TCGAbiolinks")
BiocManager::install("maftools")
install.packages("mclust")

library(TCGAbiolinks)
library(maftools)
library(mclust)
library(openxlsx)

setwd("/Users/wangziying/Desktop/数据集/MAF_LUAD")

query_SNV <- GDCquery(project = "TCGA-LUAD",
                      data.category = "Simple Nucleotide Variation",
                      data.type = "Masked Somatic Mutation",
                      workflow.type = "Aliquot Ensemble Somatic Variant Merging and Masking")
GDCdownload(query_SNV)

FilePath = dir("/Users/wangziying/Desktop/数据集/MAF_LUSC/GDCdata", ".maf.gz$", recursive = TRUE, full.names = TRUE)
head(FilePath)

# Initialize results storage
MATH <- data.frame()

# Loop to read each MAF file and calculate MATH
for (file in FilePath) {
  # Use tryCatch to capture errors
  tryCatch({
    maf <- read.maf(maf = file, vc_nonSyn = NULL)  # Allow all mutation types
    
    # Check if mutation data exists
    if (nrow(maf@data) == 0) {
      message(paste("Skip file with no mutations:", file))
      next  # If no mutation, skip current file
    }
    
    # Get barcodes of all samples
    barcode <- unique(maf@data$Tumor_Sample_Barcode)
    
    # Calculate MATH value for each sample
    for (i in barcode) {
      out.math = inferHeterogeneity(maf = maf, tsb = i)
      Tumor_Sample_Barcode = unique(out.math$clusterData$Tumor_Sample_Barcode)
      m = unique(out.math$clusterData$MATH)/1.4286
      out = data.frame(Tumor_Sample_Barcode, m)
      MATH = rbind(MATH, out)  # Accumulate results
    }
    
  }, error = function(e) {
    # Capture error and record file path
    message(paste("Error processing file:", file))
    message("Error message:", e$message)
    
  })
}
head(MATH)

 # Specify required Tumor_Sample_Barcode - LUAD
selected_barcodes <- c("TCGA-38-4628", 
                        "TCGA-38-6178", 
                        "TCGA-50-5066", 
                        "TCGA-50-5072", 
                        "TCGA-50-5941", 
                        "TCGA-50-6590", 
                        "TCGA-50-5051",
                        "TCGA-50-5936",
                        "TCGA-50-6595")

 # Specify required Tumor_Sample_Barcode - LUSC
selected_barcodes <- c("TCGA-34-5240", 
                        "TCGA-34-8454", 
                        "TCGA-60-2710", 
                        "TCGA-60-2716", 
                        "TCGA-60-2724", 
                        "TCGA-J1-A4AH", 
                        "TCGA-92-7340",
                        "TCGA-92-8063",
                        "TCGA-92-8064")

# Filter MATH dataframe
# Filter sample barcodes starting with specified prefix
filtered_MATH <- MATH[grepl(paste0(paste0(selected_barcodes, "-"), collapse = "|"), MATH$Tumor_Sample_Barcode), ]

# Save filtered MATH dataframe to Excel file
write.xlsx(filtered_MATH, "/Users/wangziying/Desktop/数据集/MAF_LUSC/MATH_selected_results.xlsx", rowNames = FALSE)

# Save MATH dataframe to Excel file
write.xlsx(MATH, "/Users/wangziying/Desktop/数据集/MAF_LUSC/MATH_results.xlsx", rowNames = FALSE)


####################################################


# Calculate TMB
FilePath = dir("/Users/wangziying/Desktop/数据集/MAF_LUAD/GDCdata", ".maf.gz$", recursive = TRUE, full.names = TRUE)

# Initialize results storage
TMB_Results <- data.frame()

for (file in FilePath) {
  tryCatch({
   maf <- read.maf(maf = file)
   # Calculate TMB
   tmb_res <- tmb(maf = maf,
             
             logScale = T)
   # Get sample barcodes
   sample_barcodes <- unique(maf@data$Tumor_Sample_Barcode)
   # Create dataframe containing barcodes and TMB results
   tmb_out <- data.frame(Tumor_Sample_Barcode = sample_barcodes, TMB = tmb_res)
   # Accumulate results
   TMB_Results <- rbind(TMB_Results, tmb_out)
   
  }, error = function(e) {
    # Capture error and record file path
    message(paste("Error processing file:", file))
    message("Error message:", e$message)
  })
}
# View aggregated results
head(TMB_Results)

# Specify required Tumor_Sample_Barcode - LUAD
selected_barcodes <- c("TCGA-38-4628", 
                       "TCGA-38-6178", 
                       "TCGA-50-5066", 
                       "TCGA-50-5072", 
                       "TCGA-50-5941", 
                       "TCGA-50-6590", 
                       "TCGA-50-5051",
                       "TCGA-50-5936",
                       "TCGA-50-6595")

# Specify required Tumor_Sample_Barcode - LUSC
selected_barcodes <- c("TCGA-34-5240", 
                       "TCGA-34-8454", 
                       "TCGA-60-2710", 
                       "TCGA-60-2716", 
                       "TCGA-60-2724", 
                       "TCGA-J1-A4AH", 
                       "TCGA-92-7340",
                       "TCGA-92-8063",
                       "TCGA-92-8064")

# Filter MATH dataframe
# Filter sample barcodes starting with specified prefix
filtered_TMB_Results <- TMB_Results[grepl(paste0(paste0(selected_barcodes, "-"), collapse = "|"), TMB_Results$Tumor_Sample_Barcode), ]


# Save TMB dataframe to Excel file
write.xlsx(filtered_TMB_Results, "/Users/wangziying/Desktop/数据集/MAF_LUAD/TMB_results.xlsx", rowNames = FALSE)

#########################################################




FilePath = dir("/Users/wangziying/Desktop/数据集/MAF_LUAD/GDCdata",".maf.gz$",recursive=T,full.names = T)
head(FilePath)
maf <- read.maf(maf = "/Users/wangziying/Desktop/数据集/MAF_LUAD/GDCdata/TCGA-LUAD/Simple_Nucleotide_Variation/Masked_Somatic_Mutation/009254a2-ea81-4c76-8044-7267a9f81364/dcc71d2d-9707-4234-a3e7-49b9cf977250.wxs.aliquot_ensemble_masked.maf.gz", 
                isTCGA = TRUE,verbose = TRUE)
getFields(maf)

# Calculate mutant-allele tumor heterogeneity
barcode <- unique(maf@data$Tumor_Sample_Barcode)
head(barcode)
MATH <- data.frame()
head(maf@data)


for (i in barcode){
  out.math = inferHeterogeneity(maf = maf, tsb = i)
  Tumor_Sample_Barcode=unique(out.math$clusterData$Tumor_Sample_Barcode)
  m = unique(out.math$clusterData$MATH)/1.4286
  out = data.frame(Tumor_Sample_Barcode, m)
  MATH = rbind(MATH, out)
}
head(MATH)
