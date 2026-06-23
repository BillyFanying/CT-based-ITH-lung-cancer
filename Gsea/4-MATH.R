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

# 初始化结果存储
MATH <- data.frame()

# 循环读取每个 MAF 文件并计算 MATH
# 允许所有突变类型
for (file in FilePath) {
  # 使用 tryCatch 捕获错误
  tryCatch({
    maf <- read.maf(maf = file, vc_nonSyn = NULL)  # 允许所有突变类型
    
    # 检查是否包含突变数据
    if (nrow(maf@data) == 0) {
      message(paste("跳过没有突变的文件:", file))
      next  # 如果没有突变，跳过当前文件
    }
    
    # 获取所有样本的 barcode
    barcode <- unique(maf@data$Tumor_Sample_Barcode)
    
    # 计算每个样本的 MATH 值
    for (i in barcode) {
      out.math = inferHeterogeneity(maf = maf, tsb = i)
      Tumor_Sample_Barcode = unique(out.math$clusterData$Tumor_Sample_Barcode)
      m = unique(out.math$clusterData$MATH)/1.4286
      out = data.frame(Tumor_Sample_Barcode, m)
      MATH = rbind(MATH, out)  # 将结果汇总
    }
    
  }, error = function(e) {
    # 捕获错误并记录出错文件的路径
    message(paste("处理文件时出错:", file))
    message("错误信息:", e$message)
    
  })
}
head(MATH)
# 
 # 指定需要的 Tumor_Sample_Barcode——LUAD
selected_barcodes <- c("TCGA-38-4628", 
                        "TCGA-38-6178", 
                        "TCGA-50-5066", 
                        "TCGA-50-5072", 
                        "TCGA-50-5941", 
                        "TCGA-50-6590", 
                        "TCGA-50-5051",
                        "TCGA-50-5936",
                        "TCGA-50-6595")

 # 指定需要的 Tumor_Sample_Barcode——LUSC
selected_barcodes <- c("TCGA-34-5240", 
                        "TCGA-34-8454", 
                        "TCGA-60-2710", 
                        "TCGA-60-2716", 
                        "TCGA-60-2724", 
                        "TCGA-J1-A4AH", 
                        "TCGA-92-7340",
                        "TCGA-92-8063",
                        "TCGA-92-8064")

# 筛选 MATH 数据框
#filtered_MATH <- MATH[MATH$Tumor_Sample_Barcode %in% selected_barcodes, ]
# 筛选以指定前缀开头的样本条形码
filtered_MATH <- MATH[grepl(paste0(paste0(selected_barcodes, "-"), collapse = "|"), MATH$Tumor_Sample_Barcode), ]

# 将筛选后的 MATH 数据框保存为 Excel 文件
write.xlsx(filtered_MATH, "/Users/wangziying/Desktop/数据集/MAF_LUSC/MATH_selected_results.xlsx", rowNames = FALSE)

# 将 MATH 数据框保存为 Excel 文件
write.xlsx(MATH, "/Users/wangziying/Desktop/数据集/MAF_LUSC/MATH_results.xlsx", rowNames = FALSE)


####################################################



#计算TMB
FilePath = dir("/Users/wangziying/Desktop/数据集/MAF_LUAD/GDCdata", ".maf.gz$", recursive = TRUE, full.names = TRUE)

# 初始化结果存储
TMB_Results <- data.frame()

for (file in FilePath) {
  tryCatch({
   maf <- read.maf(maf = file)
   ##计算TMB
   tmb_res <- tmb(maf = maf,
             
             logScale = T)
   # 获取样本信息
   sample_barcodes <- unique(maf@data$Tumor_Sample_Barcode)
   # 创建包含样本条形码和 TMB 结果的数据框
   tmb_out <- data.frame(Tumor_Sample_Barcode = sample_barcodes, TMB = tmb_res)
   # 汇总结果
   TMB_Results <- rbind(TMB_Results, tmb_out)
   
  }, error = function(e) {
    # 捕获错误并记录出错文件的路径
    message(paste("处理文件时出错:", file))
    message("错误信息:", e$message)
  })
}
# 查看汇总结果
head(TMB_Results)

# 指定需要的 Tumor_Sample_Barcode——LUAD
selected_barcodes <- c("TCGA-38-4628", 
                       "TCGA-38-6178", 
                       "TCGA-50-5066", 
                       "TCGA-50-5072", 
                       "TCGA-50-5941", 
                       "TCGA-50-6590", 
                       "TCGA-50-5051",
                       "TCGA-50-5936",
                       "TCGA-50-6595")

# 指定需要的 Tumor_Sample_Barcode——LUSC
selected_barcodes <- c("TCGA-34-5240", 
                       "TCGA-34-8454", 
                       "TCGA-60-2710", 
                       "TCGA-60-2716", 
                       "TCGA-60-2724", 
                       "TCGA-J1-A4AH", 
                       "TCGA-92-7340",
                       "TCGA-92-8063",
                       "TCGA-92-8064")

# 筛选 MATH 数据框
#filtered_MATH <- MATH[MATH$Tumor_Sample_Barcode %in% selected_barcodes, ]
# 筛选以指定前缀开头的样本条形码
filtered_TMB_Results <- TMB_Results[grepl(paste0(paste0(selected_barcodes, "-"), collapse = "|"), TMB_Results$Tumor_Sample_Barcode), ]


# 将 TMB 数据框保存为 Excel 文件
write.xlsx(filtered_TMB_Results, "/Users/wangziying/Desktop/数据集/MAF_LUAD/TMB_results.xlsx", rowNames = FALSE)

#########################################################




FilePath = dir("/Users/wangziying/Desktop/数据集/MAF_LUAD/GDCdata",".maf.gz$",recursive=T,full.names = T)
head(FilePath)
maf <- read.maf(maf = "/Users/wangziying/Desktop/数据集/MAF_LUAD/GDCdata/TCGA-LUAD/Simple_Nucleotide_Variation/Masked_Somatic_Mutation/009254a2-ea81-4c76-8044-7267a9f81364/dcc71d2d-9707-4234-a3e7-49b9cf977250.wxs.aliquot_ensemble_masked.maf.gz", 
                isTCGA = TRUE,verbose = TRUE)
getFields(maf)

#计算mutant-allele tumor heterogeneity
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

