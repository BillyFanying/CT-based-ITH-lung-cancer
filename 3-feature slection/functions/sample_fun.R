stratified_sampling <- function(data, seednum = 0, proportion = 0.67){
  # Requires data first column to be 'label' and remaining columns as features
  # proportion is the ratio for the training set
  data$ID = c(1:dim(data)[1])
  set.seed(seednum)
  data.trn = sampleBy(formula = ~ label, frac= proportion, data = data)
  train_sub = data.trn$ID
  data = subset(data, select = -ID)
  
  data.trn = data[train_sub,]
  data.test = data[-train_sub,]
  
  return(list(data.trn,data.test))
}

# size is the sample count for each stratum; the first is the count for label=0
# the second is the count for label=1
# data: dataset for sampling
# stratanames: variable name used for stratification
# size: sample size to extract for each stratum
# method: choice of 4 sampling methods: srswor, srswr, poisson, or systematic
# description: whether to output stratum summary info
# description = TRUE returns total strata count and counts per stratum
