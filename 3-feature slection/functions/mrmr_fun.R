
mrmr.fun <- function(data.trn,data.test,feature_count=6){
  # 要求data.trn 第一列是label
  mrmr_feature<-data.trn
  label.trn <- data.trn$label
  label.test <- data.test$label
  
  target_indices = which(names(mrmr_feature)=='label') # 找到label的列数
  #因为读取csv文件的时候，Y（label）值是整数，没有小数，所以就被转换成了integer
  #但是mRMR.data需要所有的数据都是numeric，所以要将里面不是numeric的转换成numeric
  # for (m in which(sapply(mrmr_feature, class)!="numeric")){
  #   mrmr_feature[,m]=as.numeric(mrmr_feature[,m])
  # }
  #转化成mRMR.data的形式才能被使用
  Data <- mRMR.data(data = data.frame(mrmr_feature))
  #data就是数据，target_indices就是label的列数，也就是需要对比相关度的列
  #feature_count是需要筛选出来的特征个数
  mrmr=mRMR.ensemble(data = Data, target_indices = target_indices, 
                     feature_count = feature_count, solution_count = 1)
  #获取筛选出来的特征的列，包含在mrmr@filters中，mrmr@filters[原特征个数]这个list里
  index=mrmr@filters[[as.character(mrmr@target_indices)]]
  #获取训练集特征
  data.trn <- mrmr_feature[,index]
  #获取验证集特征
  data.test <- data.test[,index]
  
  data.trn = data.frame(label = label.trn, data.trn)
  data.test = data.frame(label = label.test,data.test)
  
  return(list(data.trn,data.test))
}
