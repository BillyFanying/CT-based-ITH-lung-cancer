glm_step <- function(data.trn){
  # Logistic regression feature selection based on AIC values (smaller is better)
  model.null = glm(label ~ 1, 
                   data=data.trn,
                   family = binomial(link="logit") )
  
  model.full = glm(label ~ .,
                   data=data.trn,
                   family = binomial(link="logit") )
  
  logit_model <- step(model.null,         
                      scope = list(upper=model.full),
                      direction="both",
                      trace = FALSE, # if false, do not print step execution details
                      data=data.trn)
  
  return(logit_model)
}