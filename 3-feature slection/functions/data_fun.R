z.score <- function(feat.trn, feat.test){
  # Standardize features, requires feat.trn to contain features only (no labels, etc.)
  train.mean <- apply(feat.trn, 2, mean) # Standardize feature values
  train.sd <- apply(feat.trn, 2, sd)
  feat.trn <- scale(feat.trn, center = TRUE, scale = TRUE)
  feat.test <- scale(feat.test, center = train.mean, scale = train.sd)
  
  return(list(feat.trn, feat.test))
}
