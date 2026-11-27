RSCRIPT ?= Rscript
BIOSTAR_RSCRIPT_BASEURL = https://data.biostarhandbook.com/rscript
COUNTS = simulated_counts.csv
DESIGN = simulated_design.csv
ANALYSIS = edger.csv deseq2.csv

.PHONY: all simulate download-simulation-files run-edger run-deseq2 calc-confusion-matrix

all: simulate download-simulation-files calc-confusion-matrix

simulate: src/simulate_counts.r
	$(RSCRIPT) src/simulate_counts.r -o $(COUNTS) -d $(DESIGN)

download-simulation-files: simulate

run-edger: edger.csv
	@echo "Evaluating $< against $(COUNTS) to report confusion matrix counts and F1."
	$(RSCRIPT) src/evaluate_results.r $(COUNTS) $<

run-deseq2: deseq2.csv
	@echo "Evaluating $< against $(COUNTS) to report confusion matrix counts and F1."
	$(RSCRIPT) src/evaluate_results.r $(COUNTS) $<

edger.csv: src/edger.r $(COUNTS) $(DESIGN)
	$(RSCRIPT) src/edger.r -c $(COUNTS) -d $(DESIGN) -o $@

deseq2.csv: src/deseq2.r $(COUNTS) $(DESIGN)
	$(RSCRIPT) src/deseq2.r -c $(COUNTS) -d $(DESIGN) -o $@

calc-confusion-matrix: $(COUNTS) $(ANALYSIS)
	@echo "Evaluating $(ANALYSIS) against $(COUNTS) to report confusion matrix counts and F1."
	$(RSCRIPT) src/evaluate_results.r $(COUNTS) $(ANALYSIS)

fp-fn-report: $(COUNTS) $(ANALYSIS)
	@echo "Reporting false positives and false negatives for $(ANALYSIS)."
	$(RSCRIPT) src/evaluate_results.r --fp-fn-report $(COUNTS) $(ANALYSIS)

src/simulate_counts.r src/edger.r src/deseq2.r:
	mkdir -p src
	curl -fsSL "$(BIOSTAR_RSCRIPT_BASEURL)/$(@F:.r=.2026.r)" -o "$@.tmp"
	mv "$@.tmp" "$@"

clean:
	rm *.csv
