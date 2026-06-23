library(enrichplot)
library(ggrepel)
library(ggplot2)
library(gridExtra)
# 查看 GSEA 结果中的所有通路名称
head(gsea$Description)

# 查找包含 "pyroptosis" 的通路
pyroptosis_pathway <- grep("pyroptosis", gsea$Description, value = TRUE, ignore.case = TRUE)
print(pyroptosis_pathway)

# 假设您找到了 Pyroptosis 通路对应的索引为 i
pyroptosis_index <- which(gsea$Description == pyroptosis_pathway)

# 使用 gseaplot2 绘制该通路的 GSEA 富集图
gseaplot2(gsea, geneSetID = pyroptosis_index, pvalue_table = TRUE, title = pyroptosis_pathway)

# 绘制 GSEA 富集图并显示更多细节
gseaplot(gsea,
         geneSetID = pyroptosis_index,  # Pyroptosis 通路的索引
         title = pyroptosis_pathway,    # 设置图表标题
         by = "all",                    # 显示所有细节，包括排名折线、ES值、基因位置等
         pvalue_table = TRUE,           # 显示 p-value 表格
         color = "purple"                  # 选择线条颜色（可以自定义颜色）
)


symbol <- strsplit(as.character(gsea@result$core_enrichment[4]), "/")[[1]]

# 随机选择5个基因
g <- sample(symbol, 5)
print(g)  # 输出选定的基因

# 提取 NES 和 P 值等信息
pd <- gsea@result[pyroptosis_index, c("NES", "pvalue", "p.adjust")]
# 将提取的信息转化为数据框格式
pd <- data.frame(
  NES = format(pd["NES"], digits = 4),
  P_value = format(pd["pvalue"], digits = 4),
  Adjusted_P_value = format(pd["p.adjust"], digits = 4),
  row.names = NULL
)

# 创建表格
tt <- ttheme_minimal(base_size = 10,
                     core = list(fg_params = list(col = c("#F8766D", "#00BA38", "#619CFF")))
)

tp <- tableGrob(pd, rows = NULL, theme = tt)
tp$heights <- unit(rep(0.4, nrow(tp)), "cm") 

# 使用 gseaplot2 绘制 GSEA 富集图，并标注所选基因
p <- gseaplot2(gsea, geneSetID = pyroptosis_index, title = pyroptosis_pathway)  # pyroptosis_index 是 Pyroptosis 通路的 ID

# 修改图表以添加标注基因并调整图形格式
p[[1]] <- p[[1]] + 
  geom_gsea_gene(symbol, geom = geom_text_repel)+  # 在图上标注选定的基因
   annotation_custom(tp,
                    xmin = 10000,
                    xmax = 14000,
                    ymin = 0.4,
                    ymax = 0.8
  )+ 
  theme(
          legend.position = "top",          # 将图例放在顶部
          legend.direction = "vertical"     # 设置图例为垂直排列
  )

# 显示图形
print(p)

