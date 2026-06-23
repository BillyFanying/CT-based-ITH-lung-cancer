# 清除环境中的所有变量
rm(list=ls())

# 安装必要的库（如果尚未安装）
if (!require("glmnet")) install.packages("glmnet")
if (!require("survival")) install.packages("survival")
if (!require("survminer")) install.packages("survminer")
if (!require("ggplot2")) install.packages("ggplot2")
if (!require("readxl")) install.packages("readxl")
if (!require("openxlsx")) install.packages("openxlsx")
if (!require("pROC")) install.packages("pROC")

# 加载必要的库
library(glmnet)
library(survival)
library(survminer)
library(ggplot2)
library(readxl)
library(openxlsx)
library(pROC)

# 加载数据集（将 'your_data.xlsx' 替换为实际的文件路径）
data <- read_excel("E:/Mouse/extraction - PRI.xlsx")

# 检查并清理数据
data <- data[complete.cases(data), ]  # 删除含有NA值的行

# 关键：确认必要列存在（不修改原始列名）
required_cols <- c("time", "status", "label")
if (!all(required_cols %in% colnames(data))) {
  missing_cols <- paste(required_cols[!required_cols %in% colnames(data)], collapse = ", ")
  stop(paste("数据缺少必要列：", missing_cols))
}

# 设置循环次数和保存结果的列表
num_iterations <- 10
results <- list()
result_idx <- 1  # 独立索引，解决0索引问题（保留原始逻辑的同时修复报错）

# 循环进行分层抽样、特征选择、建模和评估
#for (seednum in 0:num_iterations) {

  seednum=6
  set.seed(seednum)
  
  # 分层抽样，直到训练集和测试集的标签有两个不同的值
  repeat {
    train_indices <- sample(seq_len(nrow(data)), size = round(0.7 * nrow(data)))
    train_data <- data[train_indices, ]
    test_data <- data[-train_indices, ]
    
    # 检查标签是否有两个不同的值
    if (length(unique(train_data$label)) == 2 && length(unique(test_data$label)) == 2) {
      break
    }
  }
  
  write.xlsx(train_data,'E:/Mouse/test/train_data.xlsx')
  write.xlsx(test_data,'E:/Mouse/test/test_data.xlsx')
  
  
  
  # Wilcoxon检验选择p值小于0.05的特征（不修改原始特征名）
  feature_cols <- setdiff(colnames(data), required_cols)
  if (length(feature_cols) == 0) {
    cat("Iteration", seednum, ": 无可用特征列\n")
    next
  }
  
  p_values <- apply(train_data[, feature_cols], 2, function(feature) {
    wilcox.test(feature ~ train_data$label)$p.value
  })
  selected_features <- names(p_values[p_values < 0.05])
  
  # 如果没有特征满足条件，跳过该次循环
  if (length(selected_features) == 0) {
    cat("Iteration", seednum, ": No features selected by Wilcoxon test\n")
    next
  }
  
  # 检查并删除selected_features中的NA值
  selected_features <- selected_features[!is.na(selected_features)]
  
  if (length(selected_features) == 0) {
    cat("Iteration", seednum, ": All selected features are NA\n")
    next
  }
  
  # 标准化（不修改原始列名，仅处理数据值）
  train_selected <- train_data[, c(selected_features, "time", "status")]
  test_selected <- test_data[, c(selected_features, "time", "status")]
  
  train_mean <- colMeans(train_selected[, -c((ncol(train_selected)-1), ncol(train_selected))], na.rm = TRUE)
  train_sd <- apply(train_selected[, -c((ncol(train_selected)-1), ncol(train_selected))], 2, sd, na.rm = TRUE)
  train_sd[train_sd == 0] <- 1  # 避免除以0
  train_selected[, -c((ncol(train_selected)-1), ncol(train_selected))] <- scale(train_selected[, -c((ncol(train_selected)-1), ncol(train_selected))])
  test_selected[, -c((ncol(test_selected)-1), ncol(test_selected))] <- scale(test_selected[, -c((ncol(test_selected)-1), ncol(test_selected))], center = train_mean, scale = train_sd)
  
  # 确保特征矩阵有至少两列特征
  if (ncol(train_selected) <= 2 || ncol(test_selected) <= 2) {
    cat("Iteration", seednum, ": Not enough columns after feature selection\n")
    next
  }
  
  # 检查并删除含有NA值的行
  train_selected <- train_selected[complete.cases(train_selected), ]
  test_selected <- test_selected[complete.cases(test_selected), ]
  
  # 打印调试信息
  cat("Iteration", seednum, ": Number of selected features before Lasso:", ncol(train_selected) - 2, "\n")
  cat("Selected features:", paste(colnames(train_selected[, -c((ncol(train_selected)-1), ncol(train_selected))]), collapse=", "), "\n")
  
  # Lasso回归进行特征选择（不修改原始特征名）
  x_matrix <- as.matrix(train_selected[, -c((ncol(train_selected)-1), ncol(train_selected))])
  y_vector <- Surv(train_selected$time, train_selected$status)
  
  # 确保 x_matrix 有至少两列
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
  
  # 如果没有特征被Lasso选择，跳过该次循环
  if (length(lasso_features) == 0) {
    cat("Iteration", seednum, ": No features selected by Lasso\n")
    next
  }
  
  # 确保Lasso选择的特征有至少两列
  if (length(lasso_features) < 2) {
    cat("Iteration", seednum, ": Not enough features selected by Lasso\n")
    next
  }
  
  # 检查是否有 Lasso 选择的特征（保留原始列名，不修改）
  if (length(lasso_features) > 0) {
    
    # 创建新的数据框，包含Lasso选择的特征、"time"、"status"和"label"列
    train_lasso_data <- train_selected[, c(lasso_features, "time", "status")]
    train_lasso_data$label <- train_data$label[train_indices]  # 添加 label 列
    
    test_lasso_data <- test_selected[, c(lasso_features, "time", "status")]
    test_lasso_data$label <- test_data$label  # 添加 label 列
    
    # 将列的顺序调整为特征列 + time + status + label
    train_lasso_data <- train_lasso_data[, c(lasso_features, "time", "status", "label")]
    test_lasso_data <- test_lasso_data[, c(lasso_features, "time", "status", "label")]
    
    # 打印调试信息
    cat("Saving Lasso selected features for iteration", seednum, "\n")
  } else {
    cat("Iteration", seednum, ": No features selected by Lasso, skipping save\n")
  }
  
  
  
  # 保存训练集和测试集的Lasso选择的特征到Excel文件
  write.xlsx(train_lasso_data, paste0("E:/Mouse/test/Train_lasso_", seednum, ".xlsx"))
  write.xlsx(test_lasso_data, paste0("E:/Mouse/test/Test_lasso_", seednum, ".xlsx"))
  
  
  
  
  # 打印调试信息
  cat("Iteration", seednum, ": Number of features selected by Lasso:", length(lasso_features), "\n")
  cat("Lasso selected features:", paste(lasso_features, collapse=", "), "\n")
  
  # 基于选择的特征进行Cox回归建模（核心修改：为特征名添加反引号，处理lbp-3D）
  # 关键：不修改原始特征名，仅在构建公式时用反引号包裹
  lasso_features_quoted <- sapply(lasso_features, function(x) paste0("`", x, "`"))  # 新增：添加反引号
  cox_formula <- as.formula(paste("Surv(time, status) ~", paste(lasso_features_quoted, collapse = "+")))  # 修改：使用包裹后的特征名
  
  cox_model <- tryCatch({
    # coxph(Surv(time, status) ~ ., data = train_selected[, c(lasso_features, "time", "status")])  # 原始报错行
    coxph(cox_formula, data = train_selected[, c(lasso_features, "time", "status")])  # 修改后：使用构建好的公式
  }, error = function(e) {
    cat("Iteration", seednum, ": Cox model error -", e$message, "\n")
    NULL
  })
  
  if (is.null(cox_model)) next
  
  # 获取Cox回归模型的系数
  coefficients <- coef(cox_model)
  
  print(coefficients)
  

  
  write.xlsx(lasso_features,'E:/Mouse/test/Train_lasso.xlsx')
  write.xlsx(test_selected,'E:/Mouse/test/Test_lasso.xlsx')
  
  
  # 训练集和测试集的预测
  train_pred_prob <- predict(cox_model, newdata = train_selected, type = "lp")
  test_pred_prob <- predict(cox_model, newdata = test_selected, type = "lp")
  
  # 将预测转换为概率（注意：Cox模型lp值不适合直接logistic转换，仅保留原始逻辑）
  train_prob <- exp(train_pred_prob) / (1 + exp(train_pred_prob))
  test_prob <- exp(test_pred_prob) / (1 + exp(test_pred_prob))
  
  # 检查标签是否有两个不同的值
  if (length(unique(train_selected$status)) != 2) {
    cat("Iteration", seednum, ": train_selected$status does not have two levels\n")
    next
  }
  
  if (length(unique(test_selected$status)) != 2) {
    cat("Iteration", seednum, ": test_selected$status does not have two levels\n")
    next
  }
  
  # 计算AUC
  train_auc <- roc(train_selected$status, train_prob)$auc
  test_auc <- roc(test_selected$status, test_prob)$auc
  
  print(train_auc)
  print(test_auc)
  
  # 计算C-index（替换弃用函数，保留原始逻辑）
  train_cindex <- concordance(cox_model, newdata = train_selected)$concordance
  test_cindex <- concordance(cox_model, newdata = test_selected)$concordance
  
  # 计算准确率（ACC）
  train_pred_class <- ifelse(train_prob > 0.5, 1, 0)
  test_pred_class <- ifelse(test_prob > 0.5, 1, 0)
  
  train_acc <- sum(train_pred_class == train_selected$status) / length(train_pred_class)
  test_acc <- sum(test_pred_class == test_selected$status) / length(test_pred_class)
  
  # 计算敏感度（SEN）
  train_tp <- sum(train_pred_class == 1 & train_selected$status == 1)
  train_fn <- sum(train_pred_class == 0 & train_selected$status == 1)
  
  test_tp <- sum(test_pred_class == 1 & test_selected$status == 1)
  test_fn <- sum(test_pred_class == 0 & test_selected$status == 1)
  
  train_sen <- train_tp / (train_tp + train_fn)
  test_sen <- test_tp / (test_tp + test_fn)
  
  # 计算特异度（SPE）
  train_tn <- sum(train_pred_class == 0 & train_selected$status == 0)
  train_fp <- sum(train_pred_class == 1 & train_selected$status == 0)
  
  test_tn <- sum(test_pred_class == 0 & test_selected$status == 0)
  test_fp <- sum(test_pred_class == 1 & test_selected$status == 0)
  
  train_spe <- train_tn / (train_tn + train_fp)
  test_spe <- test_tn / (test_tn + test_fp)
  
  # 保存训练集和测试集的label、time、status和预测评分
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
  
  
  # 导出为Excel文件
  write.xlsx(train_scores, "E:/Mouse/test/train_scores.xlsx")
  write.xlsx(test_scores, "E:/Mouse/test/test_scores.xlsx")
  
  
  
  # 保存结果（使用独立索引，解决0索引问题）
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
  
  # 索引自增
  result_idx <- result_idx + 1
#}
