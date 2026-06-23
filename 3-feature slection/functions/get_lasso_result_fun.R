get_lasso_result<- function(cvmodel,label.trn, feat.trn,label.test,feat.test, lamda = 'lambda.min'){
  if(lamda == 'lambda.min'){
    coefficients<-coef(cvmodel,s=cvmodel$lambda.min) # Extract coefficients of a specific model by specifying lambda
  }else if(lamda == 'lambda.1se'){
    coefficients<-coef(cvmodel,s=cvmodel$lambda.1se) # Extract coefficients of a specific model by specifying lambda
  }
  
  Active.Index<-which(coefficients!=0) # Indexes of features with non-zero coefficients; first is intercept
  Active.coefficients<-coefficients[Active.Index] # Values of non-zero coefficients
 
  # Save remaining features; ensure first column is label and subsequent columns are features
  data.trn = data.frame(label = label.trn, feat.trn)
  data.test = data.frame(label = label.test,feat.test)
  lasso.trn = data.trn[(Active.Index)] # Extract first column as label, and subsequent columns as features
  lasso.test = data.test[(Active.Index)]
  
  return(list(lasso.trn,lasso.test))
}