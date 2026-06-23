# Clear all variables in the environment
rm(list=ls())

# Install necessary libraries if not already installed
if (!require("glmnet")) install.packages("glmnet")
if (!require("survival")) install.packages("survival")
if (!require("survminer")) install.packages("survminer")
if (!require("ggplot2")) install.packages("ggplot2")
if (!require("readxl")) install.packages("readxl")
if (!require("openxlsx")) install.packages("openxlsx")
if (!require("pROC")) install.packages("pROC")

# Load necessary libraries
library(glmnet)
library(survival)
library(survminer)
library(ggplot2)
library(readxl)
library(openxlsx)
library(pROC)

# Load dataset
data <- read_excel("E:/Mouse/extraction - PRI.xlsx")

# Check and clean data
data <- data[complete.cases(data), ]  # Remove rows with NA values

# Verify required columns exist
required_cols <- c("time", "status", "label")
if (!all(required_cols %in% colnames(data))) {
  missing_cols <- paste(required_cols[!required_cols %in% colnames(data)], collapse = ", ")
  stop(paste("Data missing required columns: ", missing_cols))
}

# Set iteration count and results storage list
num_iterations <- 10
results <- list()
result_idx <- 1  # Independent index to prevent 0-indexing issues

# Loop for stratified sampling, feature selection, modeling, and evaluation
#for (seednum in 0:num_iterations) {

  seednum=6
  set.seed(seednum)
  
  # Stratified sampling until training and testing labels both have two distinct levels
  repeat {
    train_indices <- sample(seq_len(nrow(data)), size = round(0.7 * nrow(data)))
    train_data <- data[train_indices, ]
    test_data <- data[-train_indices, ]
    
    # Check if labels have two distinct levels
    if (length(unique(train_data$label)) == 2 && length(unique(test_data$label)) == 2) {
      break
    }
  }
  
  write.xlsx(train_data,'E:/Mouse/test/train_data.xlsx')
  write.xlsx(test_data,'E:/Mouse/test/test_data.xlsx')
  
  # Wilcoxon test to select features with p-value < 0.05
  feature_cols <- setdiff(colnames(data), required_cols)
  if (length(feature_cols) == 0) {
    cat("Iteration", seednum, ": No available feature columns\n")
    next
  }
  
  p_values <- apply(train_data[, feature_cols], 2, function(feature) {
    wilcox.test(feature ~ train_data$label)$p.value
  })
  selected_features <- names(p_values[p_values < 0.05])
  
  # Skip iteration if no features satisfy criteria
  if (length(selected_features) == 0) {
    cat("Iteration", seednum, ": No features selected by Wilcoxon test\n")
    next
  }
  
  # Check and remove NA values from selected_features
  selected_features <- selected_features[!is.na(selected_features)]
  
  if (length(selected_features) == 0) {
    cat("Iteration", seednum, ": All selected features are NA\n")
    next
  }
  
  # Standardization
  train_selected <- train_data[, c(selected_features, "time", "status")]
  test_selected <- test_data[, c(selected_features, "time", "status")]
  
  train_mean <- colMeans(train_selected[, -c((ncol(train_selected)-1), ncol(train_selected))], na.rm = TRUE)
  train_sd <- apply(train_selected[, -c((ncol(train_selected)-1), ncol(train_selected))], 2, sd, na.rm = TRUE)
  train_sd[train_sd == 0] <- 1  # Avoid division by zero
  train_selected[, -c((ncol(train_selected)-1), ncol(train_selected))] <- scale(train_selected[, -c((ncol(train_selected)-1), ncol(train_selected))])
  test_selected[, -c((ncol(test_selected)-1), ncol(test_selected))] <- scale(test_selected[, -c((ncol(test_selected)-1), ncol(test_selected))], center = train_mean, scale = train_sd)
  
  # Ensure feature matrix has at least two features
  if (ncol(train_selected) <= 2 || ncol(test_selected) <= 2) {
    cat("Iteration", seednum, ": Not enough columns after feature selection\n")
    next
  }
  
  # Check and remove rows containing NA
  train_selected <- train_selected[complete.cases(train_selected), ]
  test_selected <- test_selected[complete.cases(test_selected), ]
  
  # Print debugging information
  cat("Iteration", seednum, ": Number of selected features before Lasso:", ncol(train_selected) - 2, "\n")
  cat("Selected features:", paste(colnames(train_selected[, -c((ncol(train_selected)-1), ncol(train_selected))]), collapse=", "), "\n")
  
  # Lasso regression for feature selection
  x_matrix <- as.matrix(train_selected[, -c((ncol(train_selected)-1), ncol(train_selected))])
  y_vector <- Surv(train_selected$time, train_selected$status)
  
  # Ensure x_matrix has at least two columns
  if (ncol(x_matrix) < 2) {
    cat("Iteration", seednum, ": x_matrix has less than 2 columns\n")
    next
  }
  
  lasso_model <- tryCatch({
    cv.glmnet(x_matrix, y_vector, family = "cox")
  }, error = function(e) {
    cat("Iteration", seednum, ": Lasso model error -", e$message, "\n")
    NULL
  })
  
  if (is.null(lasso_model)) next
  
  lasso_features <- coef(lasso_model, s = "lambda.min")
  lasso_features <- rownames(lasso_features)[lasso_features[,1] != 0]
  lasso_features <- lasso_features[lasso_features != "(Intercept)"]
  
  # Skip iteration if no features satisfy criteria
  if (length(lasso_features) == 0) {
    cat("Iteration", seednum, ": No features selected by Lasso\n")
    next
  }
  
  # Ensure Lasso selected features have at least two columns
  if (length(lasso_features) < 2) {
    cat("Iteration", seednum, ": Not enough features selected by Lasso\n")
    next
  }
  
  # Check if Lasso selected features
  if (length(lasso_features) > 0) {
    
    # Create new dataframe with selected features, time, status, and label
    train_lasso_data <- train_selected[, c(lasso_features, "time", "status")]
    train_lasso_data$label <- train_data$label[train_indices]  # Add label
    
    test_lasso_data <- test_selected[, c(lasso_features, "time", "status")]
    test_lasso_data$label <- test_data$label  # Add label
    
    # Reorder columns: features + time + status + label
    train_lasso_data <- train_lasso_data[, c(lasso_features, "time", "status", "label")]
    test_lasso_data <- test_lasso_data[, c(lasso_features, "time", "status", "label")]
    
    # Print debugging information
    cat("Saving Lasso selected features for iteration", seednum, "\n")
  } else {
    cat("Iteration", seednum, ": No features selected by Lasso, skipping save\n")
  }
  
  # Save Lasso selected features for training and testing to Excel
  write.xlsx(train_lasso_data, paste0("E:/Mouse/test/Train_lasso_", seednum, ".xlsx"))
  write.xlsx(test_lasso_data, paste0("E:/Mouse/test/Test_lasso_", seednum, ".xlsx"))
  
  # Print debugging information
  cat("Iteration", seednum, ": Number of features selected by Lasso:", length(lasso_features), "\n")
  cat("Lasso selected features:", paste(lasso_features, collapse=", "), "\n")
  
  # Cox proportional hazards regression model fitting with backticks to support special characters
  lasso_features_quoted <- sapply(lasso_features, function(x) paste0("`", x, "`"))
  cox_formula <- as.formula(paste("Surv(time, status) ~", paste(lasso_features_quoted, collapse = "+")))
  
  cox_model <- tryCatch({
    coxph(cox_formula, data = train_selected[, c(lasso_features, "time", "status")])
  }, error = function(e) {
    cat("Iteration", seednum, ": Cox model error -", e$message, "\n")
    NULL
  })
  
  if (is.null(cox_model)) next
  
  # Get Cox regression coefficients
  coefficients <- coef(cox_model)
  
  print(coefficients)
  
  write.xlsx(lasso_features,'E:/Mouse/test/Train_lasso.xlsx')
  write.xlsx(test_selected,'E:/Mouse/test/Test_lasso.xlsx')
  
  # Predictions for training and testing sets
  train_pred_prob <- predict(cox_model, newdata = train_selected, type = "lp")
  test_pred_prob <- predict(cox_model, newdata = test_selected, type = "lp")
  
  # Convert risk scores to probabilities (retains original logic)
  train_prob <- exp(train_pred_prob) / (1 + exp(train_pred_prob))
  test_prob <- exp(test_pred_prob) / (1 + exp(test_pred_prob))
  
  # Verify status variable has two levels
  if (length(unique(train_selected$status)) != 2) {
    cat("Iteration", seednum, ": train_selected$status does not have two levels\n")
    next
  }
  
  if (length(unique(test_selected$status)) != 2) {
    cat("Iteration", seednum, ": test_selected$status does not have two levels\n")
    next
  }
  
  # Calculate AUC
  train_auc <- roc(train_selected$status, train_prob)$auc
  test_auc <- roc(test_selected$status, test_prob)$auc
  
  print(train_auc)
  print(test_auc)
  
  # Calculate C-index (retains original logic)
  train_cindex <- concordance(cox_model, newdata = train_selected)$concordance
  test_cindex <- concordance(cox_model, newdata = test_selected)$concordance
  
  # Calculate Accuracy (ACC)
  train_pred_class <- ifelse(train_prob > 0.5, 1, 0)
  test_pred_class <- ifelse(test_prob > 0.5, 1, 0)
  
  train_acc <- sum(train_pred_class == train_selected$status) / length(train_pred_class)
  test_acc <- sum(test_pred_class == test_selected$status) / length(test_pred_class)
  
  # Calculate Sensitivity (SEN)
  train_tp <- sum(train_pred_class == 1 & train_selected$status == 1)
  train_fn <- sum(train_pred_class == 0 & train_selected$status == 1)
  
  test_tp <- sum(test_pred_class == 1 & test_selected$status == 1)
  test_fn <- sum(test_pred_class == 0 & test_selected$status == 1)
  
  train_sen <- train_tp / (train_tp + train_fn)
  test_sen <- test_tp / (test_tp + test_fn)
  
  # Calculate Specificity (SPE)
  train_tn <- sum(train_pred_class == 0 & train_selected$status == 0)
  train_fp <- sum(train_pred_class == 1 & train_selected$status == 0)
  
  test_tn <- sum(test_pred_class == 0 & test_selected$status == 0)
  test_fp <- sum(test_pred_class == 1 & test_selected$status == 0)
  
  train_spe <- train_tn / (train_tn + train_fp)
  test_spe <- test_tn / (test_tn + test_fp)
  
  # Save labels, survival endpoints, and risk scores
  train_scores <- data.frame(
    label = train_data$label,
    time = train_selected$time,
    status = train_selected$status,
    score = train_pred_prob
  )
  
  test_scores <- data.frame(
    label = test_data$label,
    time = test_selected$time,
    status = test_selected$status,
    score = test_pred_prob
  )
  
  # Export to Excel
  write.xlsx(train_scores, "E:/Mouse/test/train_scores.xlsx")
  write.xlsx(test_scores, "E:/Mouse/test/test_scores.xlsx")
  
  # Save results using independent indexing
  results[[result_idx]] <- data.frame(
    seednum = seednum,
    train_cindex = train_cindex,
    train_auc = train_auc,
    train_acc = train_acc,
    train_sen = train_sen,
    train_spe = train_spe,
    test_cindex = test_cindex,
    test_auc = test_auc,
    test_acc = test_acc,
    test_sen = test_sen,
    test_spe = test_spe
  )
  
  # Increment index
  result_idx <- result_idx + 1
#}
