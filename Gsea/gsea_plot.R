library(enrichplot)
library(ggrepel)
library(ggplot2)
library(gridExtra)
# View all pathway names in the GSEA results
head(gsea$Description)

# Find pathways containing "pyroptosis"
pyroptosis_pathway <- grep("pyroptosis", gsea$Description, value = TRUE, ignore.case = TRUE)
print(pyroptosis_pathway)

# Assuming you found the index for the Pyroptosis pathway as i
pyroptosis_index <- which(gsea$Description == pyroptosis_pathway)

# Use gseaplot2 to plot the GSEA enrichment plot of the pathway
gseaplot2(gsea, geneSetID = pyroptosis_index, pvalue_table = TRUE, title = pyroptosis_pathway)

# Plot GSEA enrichment and show more details
gseaplot(gsea,
         geneSetID = pyroptosis_index,  # Index of the Pyroptosis pathway
         title = pyroptosis_pathway,    # Set chart title
         by = "all",                    # Show all details, including rank line, ES values, gene hits, etc.
         pvalue_table = TRUE,           # Show p-value table
         color = "purple"               # Choose line color (can customize)
)


symbol <- strsplit(as.character(gsea@result$core_enrichment[4]), "/")[[1]]

# Randomly select 5 genes
g <- sample(symbol, 5)
print(g)  # Output selected genes

# Extract NES and P-values
pd <- gsea@result[pyroptosis_index, c("NES", "pvalue", "p.adjust")]
# Convert extracted info into a dataframe
pd <- data.frame(
  NES = format(pd["NES"], digits = 4),
  P_value = format(pd["pvalue"], digits = 4),
  Adjusted_P_value = format(pd["p.adjust"], digits = 4),
  row.names = NULL
)

# Create table
tt <- ttheme_minimal(base_size = 10,
                     core = list(fg_params = list(col = c("#F8766D", "#00BA38", "#619CFF")))
)

tp <- tableGrob(pd, rows = NULL, theme = tt)
tp$heights <- unit(rep(0.4, nrow(tp)), "cm") 

# Use gseaplot2 to plot the GSEA enrichment plot and label selected genes
p <- gseaplot2(gsea, geneSetID = pyroptosis_index, title = pyroptosis_pathway)  # pyroptosis_index is the ID of the Pyroptosis pathway

# Modify plot to add annotated genes and adjust graph layout
p[[1]] <- p[[1]] + 
  geom_gsea_gene(symbol, geom = geom_text_repel)+  # Annotate selected genes on the plot
   annotation_custom(tp,
                    xmin = 10000,
                    xmax = 14000,
                    ymin = 0.4,
                    ymax = 0.8
  )+ 
  theme(
          legend.position = "top",          # Place legend on top
          legend.direction = "vertical"     # Set legend to vertical layout
  )

# Display plot
print(p)
