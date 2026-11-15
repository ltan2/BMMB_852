# Sum transcript counts by common gene name within each sample.
# Run from week12_hw: Rscript src/combine_gene_from_transcript.r

script <- sub("^--file=", "", grep("^--file=", commandArgs(), value = TRUE))
data_dir <- dirname(dirname(normalizePath(script)))
counts <- read.delim(file.path(data_dir, "transcript_counts.tsv"),
                     row.names = 1, check.names = FALSE)

# The annotation supplied in this project is chr22.gtf.
gtf <- read.delim(file.path(data_dir, "gtf", "chr22.gtf"),
                  header = FALSE, comment.char = "#", quote = "",
                  stringsAsFactors = FALSE)
attributes <- gtf[gtf$V3 == "transcript", "V9"]
get_attribute <- function(key) {
  pattern <- paste0('(?:^|;)[[:space:]]*', key, ' "([^"]+)"')
  if (any(!grepl(pattern, attributes, perl = TRUE))) {
    stop("Missing ", key, " in a transcript record.")
  }
  sub(paste0(".*", pattern, ".*"), "\\1", attributes, perl = TRUE)
}
transcript_ids <- get_attribute("transcript_id")
gene_names <- get_attribute("gene_name")
if (anyDuplicated(transcript_ids)) stop("Duplicate transcript IDs in annotation.")

index <- match(rownames(counts), transcript_ids)
if (anyNA(index)) stop("Some transcripts have no annotation mapping.")

# rowsum adds each sample column separately, preserving fractional counts.
gene_counts <- rowsum(as.matrix(counts), gene_names[index], reorder = FALSE)
output <- data.frame(gene_name = rownames(gene_counts), gene_counts,
                     check.names = FALSE)
write.table(output, file.path(data_dir, "gene_counts.tsv"),
            sep = "\t", quote = FALSE, row.names = FALSE)
message("Wrote ", nrow(gene_counts), " genes across ", ncol(gene_counts), " samples.")
