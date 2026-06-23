u_test <- function(data.trn, data.test, p.val = 0.05){
  # Requires the first column of data.trn/data.test to be 'label' and remaining columns as features
  wilcox = c()
  for (num in 1:length(data.trn)){
    test <- wilcox.test(data.trn[which(data.trn$label == 0),num], 
                        data.trn[which(data.trn$label == 1),num])
    wilcox[num] <- test$p.value
  }
  
  # Keep variables with Wilcoxon U-test p-value < 0.05, including the first column (label)
  data.trn <- data.trn[,which(wilcox< p.val)] 
  data.test <-data.test[,which(wilcox< p.val)]
  
  return(list(data.trn, data.test))
}
