# Checkpoint 1: Question, Data Strategy and Organization

**Course:** Introduction to Bioinformatics (2026/27)

## Research questions and experimental scope

To address the instructor's requirement that each group establishes an extension beyond the generic syllabus prompt, we structure the candidate research questions corresponding to the course baseline and the two project strands:

### General baseline
> *"How well do sequence-based predictors of enzymatic polyester degradation generalise to unseen enzyme families and new polymer chemistries?"*
* **Scope:** Broad exploratory baseline question from the project description slide. It spans both biological homology and chemical transfer simultaneously without scoping specific training subsets or substrate thresholds.

### Enzyme-based (Primary candidate)
> *"How well do sequence-based predictors generalise across remote homology enzyme clusters when evaluated independently on polymers with sufficient experimental coverage (PET, PUR, and PLA)?"*
* **Scope:** Isolates the biological homology dimension. Rather than cross-evaluating different chemistries, it tests whether sequence models can identify degrading enzymes across distant families (evaluating homology collapse thresholds using MMseqs2) separately within each plastic category that possesses sufficient sample coverage (PET: 317, PUR: 53, PLA: 45).

### Plastic-based
> *"How effectively do sequence-based predictors trained on aromatic polyesters (PET) transfer zero-shot to predict degradation of aliphatic polyesters (PLA) and polyurethanes (PUR)?"*
* **Scope:** Isolates the chemical substrate dimension. It tests whether sequence representations learned from the dominant PET annotations retain predictive validity when transferred across polymer bond classes (ester vs. carbamate/ester) and backbone flexibilities (rigid aromatic rings vs. flexible aliphatic chains).

Random splits can place closely related sequences in both training and validation,
so a strong random-fold baseline alone does not answer these questions. The later
analysis will compare performance under sequence-group and chemistry holdouts.
Those workflows are not implemented yet.

## Data available

The local PAZy snapshot contains 505 records, of which 485 have distinct non-empty
sequences using canonical amino acid symbols. Exact substrate annotations identify
317 sequences reported on PET, 53 on PUR and 45 on PLA. Counts overlap.

The loader, quality checks, features, plots and three baseline models are
implemented. The baseline target is **PET annotation status**: missing activity
reports are not verified negatives. Old numerical results were removed because
the previous PET labels incorrectly included some PBAT annotations. Use the
corrected notebook outputs for the exploratory results and their limitations.

PlasticDB data is not currently included. The notebook generates a readable
processed CSV from the PAZy snapshot. See
[Data Sources](DATA_SOURCES.md) for the distinction between existing and planned work.

## Data contingency plan

1. Use the versioned PAZy snapshot if the API is unavailable.
2. If coverage is insufficient, investigate PlasticDB and PMBD and preserve assay
   evidence, including explicit negative outcomes and experimental conditions.
3. Retrieve missing sequences or annotations through UniProt when accession IDs
   are available. This integration remains planned.

Activity on a different polymer or an absent database annotation is not sufficient
to assign a negative label. If experimental negatives remain insufficient, retain
an explicitly scoped annotation task and discuss its limitations with the instructor.

## Proposed responsibilities by domain

| Area | Checkpoint 1 (Current) | Checkpoint 2 & Final (Planned) |
| :--- | :--- | :--- |
| **Biology** | Research question, biological rationale (cutinases/esterases), data QC, and contingency plan. | Domain annotation, homology cluster interpretation, and biological analysis of results. |
| **Chemistry** | Polymer structures (SMILES for PET, PUR, PLA) and chemical differences (ester vs. urethane bonds). | Chemical descriptors validation and enzyme-substrate compatibility analysis. |
| **Data Science (Features)** | Sequence feature extraction (amino acid composition - AAC) and Colab setup. | Advanced representations (k-mers and protein embeddings). |
| **Data Science (Modeling)** | Baseline ML pipeline (Random Forest and Logistic Regression with 5-fold CV) and initial metrics. | Group-aware validation (StratifiedGroupKFold with MMseqs2 clusters) and unseen family evaluation. |
| **Data Science (Visualization & Support)** | Dummy baseline (reference threshold) and exploratory plots (sequence lengths and substrate counts). | Generalization gap figures (random vs. cluster splits), summary tables, and final report. |

## Deliverable status

- [x] Research question stated (structured baseline and specific extension options).
- [x] Local real-data snapshot available.
- [x] Data contingency plan documented.
- [x] Quality checks and exploratory baseline code implemented.
- [x] Corrected notebook executed end to end with outputs retained; two data regression tests passed.
- [x] Division of responsibilities across group areas defined.
- [ ] Resolve experimental negative evidence before interpreting results as activity prediction.

The notebook's random-fold annotation benchmark is preliminary. It does not yet
measure generalization to unseen families or polymer chemistries.

## Corrected exploratory results

The corrected local run uses 485 sequences and 21 features, five stratified folds
and random seed 42. Logistic regression includes scaling within the training folds.

| Model | Mean accuracy | Mean F1 | Mean ROC-AUC |
| --- | ---: | ---: | ---: |
| Dummy (most frequent) | 0.6536 | 0.7905 | 0.5000 |
| Logistic regression | 0.8804 | 0.9090 | 0.9530 |
| Random forest | 0.9278 | 0.9439 | 0.9710 |

These are annotation prediction results using random folds, not validated activity
prediction or unseen-family results. They replace the earlier mislabeled benchmark.
