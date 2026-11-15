## Week 12 - Generate a count matrix

Match reads against known transcripts and estimate their abundance

### Special thanks

The Makefile and design.csv were obtained from the Biostar Handbook, written by Dr. Istvan Albert

### Env setup. get data, generate counts

```bash
# env setup
pixi add salmon

# download data and design.csv 
make data

# generate count for every sample
make batch
```

### Combining all transcript level counts into a matrix
```bash
Rscript src/combine_transcript_counts.r
```

The prompt for the above script is as follow:
```text
I used the make batch command from the [Makefile](week12_hw/Makefile) and generated counts of transcripts&#x20;

I need a simple R script that can combine these counts into a single count matrix where the rows are transcript name (name column of .sf file), and columns are sample (sample column in design.csv file) and the values are `NumReads`

place the resulting code into the src/combine_transcript_counts.r file.
```

It generated for me an inefficient hashing comparison so i told it to rewrite:

```text
youre hasing twice with setequal and rownames. Rewrite to be faster
```

### Combine the resulting transcript-level counts into another gene-level count matrix.

```bash
Rscript src/combine_gene_from_transcript.r
```

The prompt for the above script is as follow:
```text
I have a matrix of transcript count in transcript_counts.tsv. I want to create a gene count matrix from it. You may refer the transcript to gene name by looking at gtf/chr22.gff.&#x20;

The resulting matrix row should be the gene name (common gene name, not ensemble name ) and column are sample and values are values are combination of transcript count of same gene within each sample

Write a simple R script to do that and place script in src/combine_gene_from_transcript.r
```

### Ensure that both count matrices also have gene names associated with each row.

gene_counts.tsv
```text
gene_name	HBR_1	HBR_2	HBR_3	UHR_1	UHR_2	UHR_3
U2	0	0	0	0	0	0
CU459211.1	0	0	0	0	0	0
CU104787.1	0	0	0	0	0	0
BAGE5	0	0	0	0	0	0
ACTR3BP6	0	0	0	0	0	0
5_8S_rRNA	0	0	0	0	0	0
AC137488.1	0	0	0	0	0	0
AC137488.2	0	0	0	0	0	0
CU013544.1	0	0	0	0	0	0
CT867976.1	0	0	0	0	0	0
CT867977.1	0	0	0	0	0	0
CT978678.1	0	0	0	0	0	0
CU459202.1	0	0	0	0	0	0
AC116618.1	0	0	0	0	0	0
CU463998.1	0	0	0	0	0	0
CU463998.3	0	0	0	0	0	0
CU463998.2	0	0	0	0	0	0
U6	0	0	0	0	0	0
```

### Refer to your previous assignment that visually identified highly expressed genes. Does your count matrix support the visually identified behavior?

In week 11, I looked at EWSR1 and SYNGR1 for highly expressed genes and  for zero expression. Here are my conclusions from week 11:

EWSR1:
```text
The EWSR1 gene around chr22:29,261,792-29,305,428 appears to show strong expression with substantial RNA-seq coverage and peaks across all 6 samples. At one inspected position within EWSR1, the exon coverage appear to be around 10-12 for HBR and 20-40 for UHR
```

Looking at the gene_counts matrix, they agree
```bash
gene_name	HBR_1	HBR_2	HBR_3	UHR_1	UHR_2	UHR_3
EWSR1	326.999	341	347	895	646.998	815.999
```

In week 11 I wrote about SYNGR1:
```text
SYNGR1 gene generally showed higher expression in HBR than UHR across all three replicates. The mean assigned read count was 874 in HBR and 48 in UHR, corresponding to an approximately 18.2-fold increase in HBR using unnormalized counts.
In a specific SYNGR1-001 transcript, the HBR value is much higher than UBR, about 23x fold
```

Looking at the gene_counts matrix, they agree
```bash
gene_name	HBR_1	HBR_2	HBR_3	UHR_1	UHR_2	UHR_3
SYNGR1	758	992.001	857	51	46.001	41
```

OR11H1:
```text
The OR11H1 gene appears to not have any detectable expression in any of the 6 samples. No RNA-seq coverage was observed across the gene
```

Looking at the gene_counts matrix, they agree
```bash
gene_name	HBR_1	HBR_2	HBR_3	UHR_1	UHR_2	UHR_3
OR11H1	0	0	0	0	0	0
```

### Write about some of your experiences with AI prompting/programming. Describe the challenges you experienced while getting the process to work.

Just like writing, AI code generation loves to be lengthy and unnecessary with checks that nobody cares, nested for loops, unecessary hash sets. Need to prune your script