# Week 8: Predict variant effects

Select a few variants that fall in a coding sequence. If the VCF has none, choose a different sample.
# DRR730103 DRR730104 DRR730105

Predict the effect of each variant either by eye or with a software tool.

Record the reference codon, the alternate codon, and the amino acid change. Use the genetic code for your organism.

Write a README.md that a reviewer can follow.

What to put in the README

Which variants did you annotate, and which gene does each one fall in?

For each variant, what is the reference codon, the alternate codon, and the amino acid change?

## Loading variants in IGV

Load `data/fasta/GCF_000346735.1.fna` as the reference genome, then open
`data/vcf/DRR730103_variants.vcf.gz` as a track. Keep its matching
`.vcf.gz.tbi` index in the same directory. The Makefile creates this index
with `bcftools index --tbi`; create it for an existing VCF with:

```bash
cd week8_hw
make data/vcf/DRR730103_variants.vcf.gz.tbi
```

Run this in the project's Pixi environment (`pixi shell` from the project root).
If IGV reports `Self-suppression not permitted`, check `~/igv/igv0.log`.
In this session the underlying error was `OutOfMemoryError: Java heap space`:
IGV used its non-indexed reader with only a `.csi` index present. Create the
`.tbi` index, quit and restart IGV, then reload the VCF.
