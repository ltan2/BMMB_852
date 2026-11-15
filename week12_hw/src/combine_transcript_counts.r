# Combine Salmon NumReads into a transcript-by-sample count matrix.
# Run with: Rscript week12_hw/src/combine_transcript_counts.r

# Find the data relative to this script, regardless of the working directory.
script <- sub("^--file=", "", grep("^--file=", commandArgs(), value = TRUE))
data_dir <- dirname(dirname(normalizePath(script)))
design <- read.csv(file.path(data_dir, "design.csv"), stringsAsFactors = FALSE)
samples <- design$sample
if (length(samples) == 0 || anyNA(samples) || any(samples == "") || anyDuplicated(samples)) {
  stop("design.csv must contain a nonempty, unique sample column.")
}

counts <- NULL
for (sample in samples) {
  quant <- read.delim(file.path(data_dir, "counts", sample, "quant.sf"),
                      stringsAsFactors = FALSE)
  if (!all(c("Name", "NumReads") %in% names(quant)) || anyDuplicated(quant$Name)) {
    stop("Missing Name/NumReads columns or duplicate transcript names for ", sample)
  }
  if (is.null(counts)) {
    counts <- matrix(NA_real_, nrow = nrow(quant), ncol = length(samples),
                     dimnames = list(quant$Name, samples))
  }
  # Reuse the match for validation and ordering; names were checked for duplicates above.
  transcript_index <- match(rownames(counts), quant$Name)
  if (nrow(quant) != nrow(counts) || anyNA(transcript_index)) {
    stop("Transcript names differ for sample ", sample)
  }
  # Match by transcript name so input row order does not affect the result.
  counts[, sample] <- quant$NumReads[transcript_index]
}

output <- data.frame(Name = rownames(counts), counts, check.names = FALSE)
output_file <- file.path(data_dir, "transcript_counts.tsv")
write.table(output, output_file, sep = "\t", quote = FALSE, row.names = FALSE)
message("Wrote ", nrow(counts), " transcripts across ", ncol(counts),
        " samples to ", output_file)
