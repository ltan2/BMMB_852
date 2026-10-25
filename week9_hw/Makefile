.DEFAULT_GOAL := help
.DELETE_ON_ERROR:
.PHONY: help all download-genome download-read align stats variant variant-stats gff clean

SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c

SRR_ID ?= DRR729363
# About 10.26x input coverage for a 234 Mb genome with paired 150 bp reads.
N ?= 8000000
THREADS ?= 4
DESIGN ?= design.csv
JOBS ?= 10
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
MERGED_VCF = data/vcf/merged.vcf.gz
MERGE_LIST = data/vcf/merge_inputs.txt
GFF = data/gff/$(ACCESSION)
ANN = -d 100 --annotate 'INFO/AD,FORMAT/DP,FORMAT/AD,FORMAT/ADF,FORMAT/ADR,FORMAT/SP'
CALL = --ploidy 2 --annotate 'FORMAT/GQ'

help:
	@printf '%s\n' \
		'make batch JOBS=10 THREADS=1  Run all samples in design.csv (up to 10 at once).' \
		'make merge JOBS=10 THREADS=1  Run the batch, then create data/vcf/merged.vcf.gz and its index.' \
		'make check-design             Validate design.csv without running the workflow.' \
		'make all                     Run the complete single-sample workflow.' \
		'make download-genome         Download the reference genome.' \
		'make download-read           Download paired reads for one sample.' \
		'make align                   Align reads and index the BAM and reference.' \
		'make stats                   Generate alignment statistics and coverage reports.' \
		'make variant                 Call variants and index the sample VCF.' \
		'make variant-stats           Generate variant calls, statistics, and VCF index.' \
		'make gff                     Download the reference gene annotation for IGV.' \
		'make batch-reference         Prepare the shared reference and indexes.' \
		'make clean                   Delete the entire data directory, including results.' \
		'make help                    Show this help (also shown by plain make).' 

all: download-genome download-read align stats variant-stats

download-genome: $(GENOME)
download-read: $(READ1) $(READ2)
align: $(BAM) $(BAM).bai $(GENOME).fai
stats: $(STATS)
gff: ${GFF}
variant: $(VCF) $(VCF).tbi
variant-stats: $(REPORT).vcf.stats.txt $(VCF).tbi

.PHONY: batch check-design batch-reference merge
# Finish all selected sample workflows before merging their indexed VCFs.
merge: $(MERGED_VCF) $(MERGED_VCF).tbi

$(MERGED_VCF): batch $(DESIGN)
	mkdir -p $(@D)
	awk -F, 'NR > 1 { sub(/\r$$/, ""); if ($$1 != "") print "data/vcf/" $$1 "_variants.vcf.gz" }' "$(DESIGN)" > $(MERGE_LIST)
	bcftools merge --file-list $(MERGE_LIST) -O z -o $@

# GNU Parallel
batch: check-design
	@command -v parallel >/dev/null || { echo "GNU Parallel is required for batch; install it before running batch."; exit 1; }
	$(MAKE) batch-reference
	awk '{ sub(/\r$$/, ""); if (NF) print }' "$(DESIGN)" | \
		parallel --jobs $(JOBS) --halt soon,fail=1 --line-buffer \
			--colsep ',' --header : \
			'$(MAKE) -j1 all SRR_ID={Accession} N={ReadPairs} THREADS=$(THREADS)'

check-design: $(DESIGN)
	@awk -F, '\
		{ sub(/\r$$/, "") } \
		NR == 1 { \
			if ($$1 != "Accession" || $$2 != "ReadPairs") { \
				print "Expected CSV header: Accession,ReadPairs,BioProjectId"; exit 1 \
			} \
			next \
		} \
		NF == 0 { next } \
		{ \
			if ($$1 !~ /^[DES]RR[0-9]+$$/ || $$2 !~ /^[1-9][0-9]*$$/ || seen[$$1]++) { \
				print "Invalid or duplicate run/ReadPairs at line " NR; exit 1 \
			} \
			rows++ \
		} \
		END { if (!rows) { print "Add sample rows to $(DESIGN) before running batch"; exit 1 } }' "$<"

batch-reference: check-design
	$(MAKE) download-genome $(BWA_INDEX) $(GENOME).fai

$(GENOME):
	mkdir -p $(@D)
	curl -fL $(URL)/$(ASSEMBLY)_genomic.fna.gz | gzip -dc > $@

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
