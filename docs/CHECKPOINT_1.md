# Checkpoint 1: Question, Data Strategy and Organization

**Course:** Introduction to Bioinformatics (2026/27)

## Research question

> How well do sequence-based predictors of enzymatic polyester degradation generalise to unseen enzyme families and new polymer chemistries?

Random splits can place closely related sequences in both training and validation,
so a strong random-fold baseline alone does not answer this question. The later
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

## Proposed responsibilities

The assignment limits groups to four students. The previous five-member table was
inconsistent with that limit. The four workstreams below are a proposal; actual
member assignments still need to be recorded.

| Workstream | Initial responsibilities | Later responsibilities |
| --- | --- | --- |
| Data and biological evidence | Snapshot QC, sequence and assay review | Domain annotation and biological interpretation |
| Features and evaluation | Sequence features and exploratory baselines | Sequence grouping and comparative evaluation |
| Chemistry | Review substrate labels and negative evidence | Validate chemical representations and transfer tests |
| Reproducibility and communication | Colab setup, plots and documentation | Results figures, report and defence preparation |

## Deliverable status

- [x] Research question stated.
- [x] Local real-data snapshot available.
- [x] Data contingency plan documented.
- [x] Quality checks and exploratory baseline code implemented.
- [x] Corrected notebook executed end to end with outputs retained; two data regression tests passed.
- [ ] Record actual responsibilities for the group members.
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
