SRR_ID ?=
N   ?= 10000
FILES ?=
FASTP_OPTS = --cut_front --cut_tail --cut_mean_quality 20

define validate_files
if [ -z "$(strip $(FILES))" ]; then \
	echo 'Usage: make $(1) FILES="read1.fastq [read2.fastq]"' >&2; exit 2; \
fi; \
set -- $(FILES); \
for f do [ -f "$$f" ] || { echo "File not found: $$f" >&2; exit 2; }; done;
endef

.PHONY: all download qc trim qc-trim clean
.DELETE_ON_ERROR:

all:
	@echo 'Run qc, trim, or qc-trim explicitly with FILES="read1.fastq [read2.fastq]".'

initialization:
	mkdir -p data/fastq data/trimmed data/qc/raw data/qc/trimmed

download: initialization
	fastq-dump -X $(N) --split-files --outdir data/fastq $(SRR_ID)
	@PATH=/usr/bin:/bin:/usr/sbin:/sbin:$$PATH; export PATH; \
	GENOME_NAME=$$(esearch -db sra -query '$(SRR_ID)[Accession]' | efetch -format runinfo \
	    | awk -F, 'NR==1{for(i=1;i<=NF;i++)if($$i=="ScientificName")c=i} NR==2{print $$c}'); \
	GENOME_NAME=$$(printf '%s' "$$GENOME_NAME" | tr -c 'A-Za-z0-9._-' '_'); \
	[ -n "$$GENOME_NAME" ] || GENOME_NAME=$(SRR_ID); \
	echo "Renaming $(SRR_ID) -> $$GENOME_NAME"; \
	for f in data/fastq/$(SRR_ID)*.fastq; do \
	    mv "$$f" "data/fastq/$$GENOME_NAME$${f#data/fastq/$(SRR_ID)}"; \
	done

# QC visualization on the raw reads
qc:
	@$(call validate_files,qc) \
	fastqc --outdir data/qc/raw "$$@"
	rm data/qc/raw/*.zip

# Trim adapters + low-quality bases
trim:
	@$(call validate_files,trim) \
	case $$# in \
	  2) fastp $(FASTP_OPTS) --detect_adapter_for_pe \
	          --in1 "$$1" --in2 "$$2" \
	          --out1 "data/trimmed/$$(basename $$1)" --out2 "data/trimmed/$$(basename $$2)" ;; \
	  1) fastp $(FASTP_OPTS) \
	          --in1 "$$1" --out1 "data/trimmed/$$(basename $$1)" ;; \
	  *) echo 'trim accepts one single-end file or two paired-end files.' >&2; exit 2 ;; \
	esac

# QC visualization on already-trimmed reads
qc-trim:
	@$(call validate_files,qc-trim) \
	fastqc --outdir data/qc/trimmed "$$@"
	rm data/qc/trimmed/*.zip

clean:
	rm -rf data
