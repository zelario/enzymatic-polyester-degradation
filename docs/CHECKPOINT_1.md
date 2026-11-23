# Checkpoint 1: Question, Data Strategy & Organization

**Course:** Introduction to Bioinformatics (2026/27)  
**Topic:** Enzymatic Degradation of Polyesters  

---

## 1. Research Question

> **"How accurately can sequence-based models predict polyester degradation across remote homology enzyme clusters across different plastic substrates?"**

### Biological & Computational Context
Enzymes that degrade synthetic polyesters (such as cutinases, esterases, and lipases) predominantly belong to the $\alpha/\beta$-hydrolase superfamily, sharing a conserved catalytic triad (Ser-His-Asp/Glu) and a nucleophilic elbow motif ($GxSxG$). 

Standard random cross-validation splits overestimate performance because homologous enzymes (>80% sequence identity) end up in both training and test sets (**homology leakage**). This project evaluates whether sequence-based predictors can generalize across **remote homology clusters** (partitioned by MMseqs2) and across distinct polyester substrates (aromatic PET, carbamate/ester PUR, and aliphatic PLA).

---

## 2. Dataset Quality Control Check

The analysis was executed on real data from the curated **PAZy** (Plastics-Active Enzymes) database snapshot:

| Metric | Value |
| :--- | :--- |
| **Total Enzymes Loaded** | 485 |
| **Unique Sequences** | 485 (100% deduplicated) |
| **Sequences with Non-canonical Amino Acids** | 0 (all valid standard residues) |
| **Enzymes with UniProt ID** | 235 |
| **Sequence Length Range** | 176 – 766 amino acids |
| **Mean Sequence Length** | 345.4 amino acids |
| **Reported on PET** | 317 (~65.4%) |
| **Reported on PUR** | 53 (~10.9%) |
| **Reported on PLA** | 45 (~9.3%) |

---

## 3. Baseline Method & Initial Performance Metrics

Evaluated on the binary degradation task (`reported_on_pet`) using **Stratified 5-Fold Cross-Validation** (random seed 42) on 20-dimensional Amino Acid Composition (AAC) + sequence length features:

| Model | Accuracy | Precision | Recall | F1-Score | ROC-AUC |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Dummy (Most Frequent)** | 0.6536 | 0.6536 | 1.0000 | 0.7905 | 0.5000 |
| **Logistic Regression (scaled)** | 0.8804 | 0.9021 | 0.9179 | 0.9090 | 0.9530 |
| **Random Forest** | 0.9278 | 0.9587 | 0.9305 | 0.9439 | 0.9713 |

*Interpretation:* The strong performance of Random Forest on random folds provides our baseline "first number". However, because near-identical homologues exist across folds, this performance is expected to drop significantly under strict cluster-based holdouts in Checkpoint 2.

---

## 4. Team Organization & Contingency Plan (Plan B)

### Team Roles & Responsibilities

| Role | Domain Profile | Checkpoint 1 Responsibilities | Checkpoint 2 Responsibilities |
| :--- | :--- | :--- | :--- |
| **Member 1** | Machine Learning Lead | Baseline models (`src/models.py`) and 5-fold CV benchmarking. | Advanced classifiers (XGBoost / PLM) and evaluation. |
| **Member 2** | Bioinfo & Clustering Lead | Feature extraction (`src/features.py`: AAC) and QC checks. | Homology clustering (MMseqs2) and `GroupKFold` splits. |
| **Member 3** | Visuals & Reporting | Exploratory plots (`src/visualizations.py`) and dummy baseline. | Homology gap figures, confusion matrices, and slides. |
| **Member 4** | Biology Lead | Biological context, $\alpha/\beta$-hydrolase rationale, and QC design. | Taxonomic profiling and biological validation of holdout clusters. |
| **Member 5** | Biochemistry Lead | Catalytic triad/motifs (Ser-His-Asp, $GxSxG$) and substrate context. | Pfam domain mapping (`PF01083`, `PF00561`) and pocket analysis. |

### Plan B for the Data
1. **Local Snapshots:** All raw records are committed locally (`data/raw/pazy_proteins.json`), eliminating external API or server downtime risks.
2. **Secondary Databases:** If coverage for specific polyesters is insufficient, integrate additional positive/negative entries from **PlasticDB** and **PMBD**.
3. **UniProt REST API Fallback:** If sequence annotations or Pfam domains are missing, retrieve them programmatically via the UniProt REST API.
