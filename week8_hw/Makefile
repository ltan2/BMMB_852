.DEFAULT_GOAL := all
.DELETE_ON_ERROR:
.PHONY: all download-genome download-read align stats variant variant-stats clean

SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c

SRR_ID ?= DRR729363
# DRR730103 DRR730104 DRR730105
# About 10.26x input coverage for a 234 Mb genome with paired 150 bp reads.
N ?= 8000000
THREADS ?= 4
ACCESSION ?= GCF_000346735.1
ASSEMBLY ?= GCF_000346735.1_P.mume_V1.0
URL ?= https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/346/735/$(ASSEMBLY)
GENOME = data/fasta/$(ACCESSION).fna
READ_DIR = data/fastq
READ1 = $(READ_DIR)/$(SRR_ID)_1.fastq
READ2 = $(READ_DIR)/$(SRR_ID)_2.fastq
BWA_INDEX = $(addprefix $(GENOME).,amb ann bwt pac sa)
BAM = data/bam/$(SRR_ID).sorted.bam
REPORT = data/reports/$(SRR_ID)
STATS = $(REPORT).flagstat.txt $(REPORT).coverage.tsv
VCF = data/vcf/$(SRR_ID)_variants.vcf.gz
GFF = data/gff/$(ACCESSION)
# Annotation parameters for the mpileup command.
ANN = -d 100 --annotate 'INFO/AD,FORMAT/DP,FORMAT/AD,FORMAT/ADF,FORMAT/ADR,FORMAT/SP'
# Call parameters for the call command.
CALL = --ploidy 2 --annotate 'FORMAT/GQ'

# Each shortcut depends on actual output files, so completed steps are reused.
all: download-genome download-read align stats variant-stats

download-genome: $(GENOME)
download-read: $(READ1) $(READ2)
align: $(BAM) $(BAM).bai $(GENOME).fai
stats: $(STATS)
gff: ${GFF}
variant: $(VCF) $(VCF).tbi
variant-stats: $(REPORT).vcf.stats.txt $(VCF).tbi

$(GENOME):
	mkdir -p $(@D)
	curl -fL $(URL)/$(ASSEMBLY)_genomic.fna.gz | gzip -dc > $@

# A multi-output pattern rule downloads both mates once, even with make -j.
# If either mate is missing, download the pair again.
$(READ_DIR)/%_1.fastq $(READ_DIR)/%_2.fastq:
	mkdir -p $(READ_DIR)
	fastq-dump -X $(N) --split-files --outdir $(READ_DIR) $*

# BWA creates these five files together; rebuild if any one is missing.
data/fasta/%.fna.amb data/fasta/%.fna.ann data/fasta/%.fna.bwt data/fasta/%.fna.pac data/fasta/%.fna.sa: data/fasta/%.fna
	bwa index $<

$(GENOME).fai: $(GENOME)
	samtools faidx $<

$(BAM): $(GENOME) $(READ1) $(READ2) $(BWA_INDEX)
	mkdir -p $(@D)
	bwa mem -t $(THREADS) $(GENOME) "$(READ1)" "$(READ2)" | \
		samtools sort -o $@ -

$(BAM).bai: $(BAM)
	samtools index $< $@

$(REPORT).flagstat.txt: $(BAM)
	mkdir -p $(@D)
	samtools flagstat $< > $@

$(REPORT).coverage.tsv: $(BAM)
	mkdir -p $(@D)
	samtools coverage $< > $@

$(VCF): $(BAM) $(BAM).bai $(GENOME) $(GENOME).fai
	mkdir -p $(@D)
	bcftools mpileup $(ANN) -O u -f $(GENOME) $(BAM) | \
		bcftools call $(CALL) -mv -O u | \
		bcftools norm -f $(GENOME) -d all -O u | \
		bcftools sort -O z -o $@

# IGV needs a Tabix (.tbi) index to avoid loading the entire VCF into memory.
data/vcf/%.vcf.gz.tbi: data/vcf/%.vcf.gz
	bcftools index --force --tbi $<

$(REPORT).vcf.stats.txt: $(VCF)
	mkdir -p $(@D)
	bcftools stats $< > $@

$(GFF):
	mkdir -p $(@D)
	curl -fL $(URL)/$(ASSEMBLY)_genomic.gff.gz | gzip -dc > $@

clean:
	rm -rf data
