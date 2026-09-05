# Genome selected for this assignment
ACCESSION = GCF_000346735.1
ASSEMBLY = GCF_000346735.1_P.mume_V1.0

# NCBI download location
URL = https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/346/735/$(ASSEMBLY)

# Output files
FASTA = data/fasta/$(ACCESSION).fna
GFF = data/gff/$(ACCESSION).gff

# reserve words
.PHONY: $(ACCESSION) count clean
.DELETE_ON_ERROR:

# Download the FASTA and GFF for the selected accession.
# Usage: make GCF_000346735.1
$(ACCESSION): $(FASTA) $(GFF)
	@:

# Download and unzip the genome FASTA file.
$(FASTA):
	mkdir -p data/fasta
	curl -fL $(URL)/$(ASSEMBLY)_genomic.fna.gz | gzip -dc > $@

# Download and unzip the genome annotation file.
$(GFF):
	mkdir -p data/gff
	curl -fL $(URL)/$(ASSEMBLY)_genomic.gff.gz | gzip -dc > $@

# Count total annotations and also report by feature type
# Usage: make count
count: $(GFF)
	@awk -F '\t' '$$0 !~ /^#/ && NF >= 9 {total++} END {print "Total annotations:", total}' $(GFF)
	@echo "Breakdown by feature type:"
	@awk -F '\t' '$$0 !~ /^#/ && NF >= 9 {count[$$3]++} END {for (type in count) print type, count[type]}' $(GFF) | sort

# Remove downloaded files and empty data directories.
clean:
	rm -f $(FASTA) $(GFF)
	rmdir data/fasta data/gff data 2>/dev/null || true
