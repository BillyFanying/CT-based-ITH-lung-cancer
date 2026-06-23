mrmr.fun <- function(data.trn,data.test,feature_count=6){
  # Requires the first column of data.trn to be 'label'
  mrmr_feature<-data.trn
  label.trn <- data.trn$label
  label.test <- data.test$label
  
  target_indices = which(names(mrmr_feature)=='label') # Find the index of the 'label' column
  # Convert to mRMR.data object for execution
  Data <- mRMR.data(data = data.frame(mrmr_feature))
  # data represents covariates, target_indices is index of label, representing column comparison
  # feature_count is the target number of features to select
  mrmr=mRMR.ensemble(data = Data, target_indices = target_indices, 
                     feature_count = feature_count, solution_count = 1)
  # Selected feature indices are stored in mrmr@filters list
  index=mrmr@filters[[as.character(mrmr@target_indices)]]
  # Get training features
  data.trn <- mrmr_feature[,index]
  # Get test features
  data.test <- data.test[,index]
  
  data.trn = data.frame(label = label.trn, data.trn)
  data.test = data.frame(label = label.test,data.test)
  
  return(list(data.trn,data.test))
}
