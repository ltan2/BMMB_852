.DEFAULT_GOAL := all
.PHONY: all download-genome download-read align stats clean

# Run downloads, alignment, BAM indexing, and statistics.
all: download-genome download-read align stats variant-stats

SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c

SRR_ID ?= DRR729363
# About 10.26x input coverage for a 234 Mb genome with paired 150 bp reads.
N ?= 8000000
THREADS ?= 4
ACCESSION ?= GCF_000346735.1
ASSEMBLY ?= GCF_000346735.1_P.mume_V1.0
URL ?= https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/346/735/$(ASSEMBLY)
GENOME = data/fasta/$(ACCESSION).fna
READ_DIR = data/fastq
BAM = data/bam/$(SRR_ID).sorted.bam
REPORT = data/reports/$(SRR_ID)
# The output VCF file.
VCF=data/vcf/variants.vcf.gz
# Annotation parameters for the mpileup command
ANN=-d 100 --annotate 'INFO/AD,FORMAT/DP,FORMAT/AD,FORMAT/ADF,FORMAT/ADR,FORMAT/SP'
# Call parameters for the call command
CALL=--ploidy 2 --annotate 'FORMAT/GQ' 

# Download the reference genome.
download-genome: $(GENOME)

$(GENOME):
	mkdir -p data/fasta
	curl -fL $(URL)/$(ASSEMBLY)_genomic.fna.gz | gzip -dc > $(GENOME)

# Download the first N read pairs, keeping their SRA accession filenames.
download-read:
	mkdir -p $(READ_DIR)
	fastq-dump -X $(N) --split-files --outdir $(READ_DIR) $(SRR_ID)

# Align reads, save a sorted BAM, and create indexes for IGV.
align: $(BAM)

# Build the BAM only when missing or when an input changes.
$(BAM): $(GENOME) $(READ_DIR)/$(SRR_ID)_1.fastq $(READ_DIR)/$(SRR_ID)_2.fastq
	mkdir -p data/bam
	bwa index $(GENOME)
	bwa mem -t $(THREADS) $(GENOME) \
		"$(READ_DIR)/$(SRR_ID)_1.fastq" \
		"$(READ_DIR)/$(SRR_ID)_2.fastq" | \
		samtools sort -o $(BAM) -
	samtools index $(BAM)
	samtools faidx $(GENOME)

# Report mapping percentage and coverage.
stats: align
	mkdir -p data/reports
	samtools flagstat $(BAM) > $(REPORT).flagstat.txt
	samtools coverage $(BAM) > $(REPORT).coverage.tsv

clean:
	rm -rf data

variant:
	mkdir -p data/vcf
	bcftools mpileup ${ANN} -O u -f ${GENOME} ${BAM} | \
	bcftools call ${CALL} -mv -O u | \
	bcftools norm -f ${GENOME} -d all -O u | \
	bcftools sort --write-index -O z -o ${VCF}

variant-stats: variant
	mkdir -p data/reports
	# Run a statistics report on the VCF file
	bcftools stats ${VCF} > $(REPORT).vcf.stats.txt
