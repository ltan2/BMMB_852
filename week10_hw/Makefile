.DEFAULT_GOAL := help
.DELETE_ON_ERROR:
.PHONY: help all download-genome download-read align peak-calling gff clean

SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c

SRR_ID ?= SRR40530218
# About 10.26x input coverage for a 234 Mb genome with paired 150 bp reads.
N ?= 1200000
THREADS ?= 4
MACS ?= macs3
# Approximate effective genome size for S. cerevisiae; override for other organisms.
GSIZE ?= 1.2e7
QVALUE ?= 0.01
DESIGN ?= design.csv
PROJECT ?= PRJNA1523976
SAMPLES ?= 0
MATCH ?=
STRATEGY ?=
PYTHON ?= python3
JOBS ?= 10
BACKGROUND_MATCH ?= ^sth1_0hr_
CONDITION_MATCH ?= ^sth1_1hr_
BATCH_MATCH ?=
CONTROL_BAM ?=
PEAK_ROOT ?= data/peaks
BACKGROUND_BAM = data/background-bam/pooled.bam
ASSEMBLY ?= GCF_000146045.2
ASSEMBLY_NAME ?= R64
REMOTE_PREFIX = $(ASSEMBLY)_$(ASSEMBLY_NAME)
URL ?= https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/146/045/$(REMOTE_PREFIX)
GENOME = data/fasta/$(ASSEMBLY).fna
READ_DIR = data/fastq
READ1 = $(READ_DIR)/$(SRR_ID)_1.fastq
READ2 = $(READ_DIR)/$(SRR_ID)_2.fastq
BWA_INDEX = $(addprefix $(GENOME).,amb ann bwt pac sa)
BAM = data/bam/$(SRR_ID).sorted.bam
PEAK_BAM = data/bam/$(SRR_ID).peak-input.bam
PEAK_DIR = $(PEAK_ROOT)/$(SRR_ID)
PEAKS = $(PEAK_DIR)/$(SRR_ID)_peaks.narrowPeak
GFF = data/gff/$(ASSEMBLY)

help:
	@printf '%s\n' \
		'make design-csv PROJECT=PRJNA1523976  Fetch all run and GEO metadata.' \
		'make design-csv MATCH="^sth1_" STRATEGY=ATAC-seq  Select Sth1 ATAC-seq samples.' \
		'make batch JOBS=10 THREADS=1  Run all samples in design.csv (up to 10 at once).' \
		'make background              Run background samples in parallel and pool their alignments.' \
		'make peaks                   Call condition peaks relative to the pooled background in parallel.' \
		'make all                     Run the complete single-sample workflow.' \
		'make download-genome         Download the reference genome.' \
		'make download-read           Download paired reads for one sample.' \
		'make align                   Align reads and index the BAM and reference.' \
		'make peak-calling            Call ATAC-seq peaks and print the peak count.' \
		'make gff                     Download the reference gene annotation for IGV.' \
		'make batch-reference         Prepare the shared reference and indexes.' \
		'make clean                   Delete the entire data directory, including results.' \
		'make help                    Show this help (also shown by plain make).' 

all: download-genome download-read gff align peak-calling

download-genome: $(GENOME)
download-read: $(READ1) $(READ2)
align: $(BAM) $(BAM).bai $(GENOME).fai
peak-calling: $(PEAKS)
	@printf '%s peaks: ' '$(SRR_ID)'; wc -l < "$(PEAKS)"
gff: ${GFF}

.PHONY: design-csv batch batch-reference background peaks

design-csv:
	$(PYTHON) build_design.py --project "$(PROJECT)" --match "$(MATCH)" --strategy "$(STRATEGY)" --limit "$(SAMPLES)" --read-pairs "$(N)" --output "$(DESIGN)"

# Extract only validated run IDs and read counts; GEO CSV fields can contain commas.
batch: $(DESIGN)
	$(MAKE) batch-reference
	$(PYTHON) build_design.py --batch-rows "$(DESIGN)" --batch-match "$(BATCH_MATCH)" | \
		parallel --jobs $(JOBS) --halt soon,fail=1 --line-buffer \
			--colsep '\t' \
			'$(MAKE) -j1 all SRR_ID={1} N={2} THREADS=$(THREADS)'

background: $(DESIGN)
	$(MAKE) batch BATCH_MATCH='$(BACKGROUND_MATCH)' CONTROL_BAM= PEAK_ROOT=data/background
	mkdir -p data/background-bam
	$(PYTHON) build_design.py --batch-rows "$(DESIGN)" --batch-match '$(BACKGROUND_MATCH)' | \
		parallel --jobs $(JOBS) --halt soon,fail=1 --keep-order --colsep '\t' \
			'printf "%s\n" data/bam/{1}.peak-input.bam' > data/background-bam/bams.txt
	samtools merge -f -b data/background-bam/bams.txt -o "$(BACKGROUND_BAM).tmp.bam"
	mv "$(BACKGROUND_BAM).tmp.bam" "$(BACKGROUND_BAM)"

peaks: background
	$(MAKE) batch BATCH_MATCH='$(CONDITION_MATCH)' CONTROL_BAM='$(BACKGROUND_BAM)' PEAK_ROOT=data/condition

batch-reference:
	$(MAKE) download-genome $(BWA_INDEX) $(GENOME).fai

$(GENOME):
	mkdir -p $(@D)
	curl -fL $(URL)/$(REMOTE_PREFIX)_genomic.fna.gz | gzip -dc > $@

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

# Use properly paired primary alignments with MAPQ >= 30; exclude unmapped,
# secondary, QC-failed, duplicate-marked, and supplementary records.
$(PEAK_BAM): $(BAM)
	samtools view -b -f 2 -F 3852 -q 30 -o $@ $<

$(PEAKS): $(PEAK_BAM) $(CONTROL_BAM)
	@command -v $(MACS) >/dev/null || { echo "MACS3 is required; run pixi install from the repository root."; exit 1; }
	mkdir -p "$(PEAK_DIR)"
	$(MACS) callpeak -t "$<" -f BAMPE -g $(GSIZE) -q $(QVALUE) \
		$(if $(CONTROL_BAM),-c "$(CONTROL_BAM)") \
		--keep-dup 1 -n "$(SRR_ID)" --outdir "$(PEAK_DIR)"

$(GFF):
	mkdir -p $(@D)
	curl -fL $(URL)/$(REMOTE_PREFIX)_genomic.gff.gz | gzip -dc > $@

clean:
	rm -rf data
