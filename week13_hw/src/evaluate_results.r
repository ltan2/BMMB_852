#!/usr/bin/env Rscript

validate_columns <- function(data, required, path) {
  missing_columns <- setdiff(required, names(data))
  if (length(missing_columns) > 0) {
    stop("Missing columns in ", path, ": ", paste(missing_columns, collapse = ", "))
  }
}

confusion_matrix <- function(changed, significant) {
  data.frame(
    TP = sum(changed & significant),
    FP = sum(!changed & significant),
    TN = sum(!changed & !significant),
    FN = sum(changed & !significant)
  )
}

evaluate <- function(path, results, truth) {
  matched <- match(results$id, truth$id)
  if (anyNA(matched)) stop("Results contain gene IDs absent from the counts: ", path)

  changed <- truth$status[matched] == "changed"
  significant <- results$FDR < 0.05
  counts <- confusion_matrix(changed, significant)
  f1_denominator <- 2 * counts$TP + counts$FP + counts$FN

  summary <- data.frame(
    File = basename(path),
    Reported = nrow(results),
    Omitted = nrow(truth) - nrow(results),
    counts,
    F1 = if (f1_denominator > 0) 2 * counts$TP / f1_denominator else NA_real_
  )

  errors <- which(changed != significant)
  errors <- errors[order(changed[errors], results$FDR[errors], results$id[errors])]
  raw_columns <- setdiff(names(truth), "filter")
  result_columns <- intersect(c("log2FC", "PValue", "FDR"), names(results))
  misclassified <- data.frame(
    Call = ifelse(changed[errors], "FN", "FP"),
    truth[matched[errors], raw_columns, drop = FALSE],
    results[errors, result_columns, drop = FALSE]
  )

  list(summary = summary, misclassified = misclassified)
}

print_report <- function(reports) {
  previous_options <- options(width = 120)
  on.exit(options(previous_options))

  for (result in reports) {
    cat("\nFalse positives and false negatives for ", result$summary$File, "\n", sep = "")
    if (nrow(result$misclassified)) {
      print(result$misclassified, row.names = FALSE,
            max = nrow(result$misclassified) * ncol(result$misclassified))
    } else {
      cat("None\n")
    }
  }
}

# Pass the counts file followed by one or more results files.
main <- function(args = commandArgs(trailingOnly = TRUE)) {
  if (length(args) < 2) stop("Provide the simulated counts and at least one results file")

  truth <- read.csv(args[1])
  validate_columns(truth, c("id", "status"), args[1])

  lapply(args[-1], function(path) {
    results <- read.csv(path)
    validate_columns(results, c("id", "FDR"), path)
    evaluate(path, results, truth)
  })
}

args <- commandArgs(trailingOnly = TRUE)
if (identical(args[1], "--fp-fn-report")) {
  print_report(main(args[-1]))
} else {
  reports <- main(args)
  summary_table <- do.call(rbind, lapply(reports, function(result) result$summary))
  print(summary_table, row.names = FALSE, digits = 4)
}
