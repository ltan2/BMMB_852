## Week 13 HW - Evaluate simulations
Which genes have different expression in group B versus group A? 


### Steps to run
```bash
make download-simulation-files
make all
```

To generate fp-fn report:
```bash
make fp-fn-report
```

### Scoring formula
The scoring formula that will be use to evaluate edgeR and DESeq2 is F1 score. It ranges from 0 to 1 and rewards finding genes that truly changed while penalizing false positives and false negatives. 

$$
F_1 = \frac{2TP}{2TP + FP + FN}
$$

### .CSV file
In both edger.csv and deseq2.csv:

| Column | Definition |
|---|---|
| `id` | Unique identifier for each simulated gene. |
| `status` | Simulation label. `changed` means the simulator assigned an expression difference between A and B and the gene had at least one observed read. `unchanged` is the label for all other genes. |
| `filter` | Total-count flag from the simulated counts. `pass` means at least 10 raw reads across all six samples. `fail` means fewer than 10. edgeR uses its own filter to decide which genes appear in the results. |
| `A1`, `A2`, `A3`, `B1`, `B2`, `B3` | Normalized read counts for each replicate in groups A and B. |
| `baseMean` | Mean normalized count across all six samples. |
| `baseMeanA`, `baseMeanB` | Mean normalized count in group A and group B, respectively. |
| `foldChange` | Estimated ratio of expression in group B to expression in group A. A value of `2` means expression is twice as high in B. |
| `log2FC` | Base-2 logarithm of `foldChange`. A value of `1` means expression is twice as high in B, and `-1` means it is half as high in B. |
| `PValue` | Raw p-value for the test of equal expression between A and B. |
| `FDR` | Benjamini–Hochberg adjusted p-value. The default significance cutoff is `FDR < 0.05`. |
| `falsePos` | Approximate false-positive count through that row, calculated as the row’s rank in the sorted results multiplied by its `FDR`. In the simulation, the observed false positives are the significant genes labeled `unchanged`. |

### Questions

#### 1. How many TP, FP, TN, and FN did you get?
```bash
       File Reported Omitted TP FP   TN FN     F1
  edger.csv     2191    7809 57  3 2067 64 0.6298
 deseq2.csv     2816    7184 73 10 2651 82 0.6134
```

#### 2. Do edgeR and DESeq2 produce the same results?  
Both methods detected about 47% of the changed genes they reported (57/121 for edgeR and 73/155 for DESeq2). Of the genes they called significant, 95% were truly changed for edgeR (57/60), compared with 88% for DESeq2 (73/83). That higher precision explains edgeR’s slightly higher F1 (0.630 vs. 0.613) despite its lower number of true positives.


#### 3. Which method seems to be more accurate?  
edgeR seems slightly more accurate by F1 among the genes each method reported. It scored 0.630 versus 0.613 for DESeq2. About 95% of edgeR’s significant calls were truly changed, compared with 88% for DESeq2. Both methods detected about 47% of the truly changed genes they retained. DESeq2 still detected more true changes overall (73 vs. 57). 


#### 4. If you rerun the simulation, do you get the same results?  
No, I did not. However, edgeR still performed better than DESeq2 in F1 score

```bash
       File Reported Omitted TP FP   TN FN     F1
  edger.csv     2233    7767 61  4 2125 43 0.7219
 deseq2.csv     2856    7144 70 14 2715 57 0.6635
```

#### 5. Pick a few FP or FN genes and look at the data for those genes. Explain why the method made the decision it did.

#### 5a. False positives and false negatives for edger.csv first 10 rows

```bash
 Call        id    status    A1   A2    A3   B1   B2   B log2FC    PValue     FDR
   FP GENE-5461 unchanged    18   11    15   47   97   50  2.128 0.0006801 0.02862
   FP GENE-2083 unchanged   217  161   140  344  418  386  1.143 0.0007481 0.03035
   FP GENE-9337 unchanged  4879 1179  3585   82  123    7 -5.505 0.0009176 0.03594
   FP GENE-1399 unchanged   575  203   291   65   73  103 -2.152 0.0011320 0.04148
   FP GENE-6421 unchanged    62   46    63   28   18   25 -1.268 0.0012630 0.04553
   FN GENE-7313   changed     3    6     1   16   17   19  2.330 0.0014460 0.05134
   FN GENE-1709   changed    87  120   128  191  278  267  1.130 0.0015260 0.05334
   FN GENE-3207   changed  4537 4528  4425 2074 2959 2705 -0.806 0.0015680 0.05349
   FN GENE-5411   changed   212  209   215   98  128  132 -0.833 0.0016100 0.05349
   FN GENE-8236   changed     0    3     5   24   41   18  3.312 0.0016250 0.05349
```

GENE-2083 was a false positive in edgeR. The simulator labeled it unchanged, but every B replicate had more reads (344, 418, 386) than every A replicate (217, 161, 140). edgeR estimated about 2.2 times higher expression in B and called the gene significant (FDR = 0.03035).

GENE-7313 was a false negative in edgeR. The simulator labeled it changed, and the B counts (16, 17, 19) were consistently higher than the A counts (3, 6, 1). The raw p-value was 0.001446, but after adjustment for multiple testing, the FDR was 0.05134, just above the cutoff.

#### 5b. False positives and false negatives for deseq2.csv first 10 rows

```bash
Call        id    status    A1   A2    A3   B1   B2   B3  log2FC    PValue       FDR
   FP GENE-2634 unchanged     0 3669   156    0    0    0 -26.573 1.034e-11 8.330e-10
   FP GENE-1399 unchanged   575  203   291   65   73  103  -2.150 9.392e-08 5.763e-06
   FP GENE-9337 unchanged  4879 1179  3585   82  123    7  -5.504 4.049e-07 2.268e-05
   FP GENE-9323 unchanged    55   25    64  147  265  152   1.972 9.524e-07 5.113e-05
   FP GENE-2198 unchanged    43   31    26  395   64  155   2.619 2.697e-06 1.390e-04
   FN GENE-3464   changed    83  100   105   56   16   43  -1.323 1.945e-03 5.896e-02
   FN GENE-4025   changed    56   38    55   73  102  118   0.976 3.129e-03 8.862e-02
   FN GENE-3552   changed    11   10     6    1    1    0  -3.755 3.546e-03 9.933e-02
   FN GENE-2360   changed    92   93   112  276  130  174   0.967 3.586e-03 9.937e-02
   FN GENE-5629   changed    15   11    12   30   31   32   1.292 4.066e-03 1.092e-01
```

GENE-1399 was a false positive in DESeq2. The simulator labeled it unchanged, but every replicate in group B had fewer reads (65, 73, 103) than every replicate in group A (575, 203, 291). DESeq2 estimated about 4.4-fold lower expression in B (log2FC = −2.15) and called the gene significant because its FDR (5.763 × 10⁻⁶) was below 0.05. The call was a false positive because the simulator had assigned no expression difference to this gene.

GENE-3464 was a false negative in DESeq2. The simulator labeled it changed, and the B counts (56, 16, 43) were lower than the A counts (83, 100, 105). DESeq2 estimated lower expression in B, but the adjusted p-value (FDR = 0.05896) exceeded the cutoff.

