# Checkpoint 1: Research Question, Data Strategy & Team Organization

**Course:** Introduction to Bioinformatics (2026/27)  
**Project:** Enzymatic Degradation of Polyesters  

---

## 1. Research Question

> **"How well do sequence-based predictors of enzymatic polyester degradation generalise to unseen enzyme families and new polymer chemistries?"**

### Biological and Computational Context
Enzymatic plastic degradation currently relies on a limited repertoire of biochemically verified enzymes catalogued in curated resources such as the **PAZy** database (~485 verified sequences). The vast majority of these enzymes belong to a small number of homologous families within the $\alpha/\beta$-hydrolase superfamily (cutinases, lipases, and esterases).

When developing machine learning predictors on these sequences, standard random train/test splits introduce severe **homology leakage**: highly similar homologues (often >90% sequence identity) end up on both sides of the split, yielding artificially inflated performance metrics that fail to reflect real-world discovery scenarios.

This project addresses two critical generalization frontiers:
1. **Unseen Enzyme Families:** Evaluating predictor robustness on entirely held-out enzyme families clustered by sequence identity using **MMseqs2** (e.g., training on cutinases and testing on lipases).
2. **Novel Polymer Chemistries:** Evaluating cross-chemistry transfer, such as training predictors on aromatic polyesters (PET) and testing on polyurethanes (PUR) or aliphatic polyesters (PLA, PBS).

---

## 2. Data Strategy & Contingency Plan (Plan B)

### Primary Datasets
* **PAZy (Plastics-Active Enzymes Database):** Primary source of biochemically verified positive degraders (485 enzymes with valid amino acid sequences targeting PET, PUR, PLA, PBAT, and PBS).
* **PlasticDB:** Curated database of plastic-degrading organisms and proteins. Enzymes active on non-polyester substrates (e.g., PHA, PHB, Nylon, PE) provide indispensable **negative controls**, ensuring classifiers do not merely learn generic esterase profiles.

### Plan B (Contingency Plan)
If data acquisition issues, API downtime, or sequence inconsistencies arise with the primary data source:
1. **Local Raw Snapshots:** All raw entries are cached locally in versioned, immutable snapshots (`data/raw/pazy_proteins.json` and `data/raw/plasticdb_proteins.tsv`), eliminating dependency on real-time external server uptime during evaluation.
2. **Secondary Database Integration (PlasticDB & PMBD):** If PAZy coverage is insufficient for specific polymers (e.g., limited PUR or PBAT instances), we cross-reference and incorporate experimental entries from **PlasticDB** and the **PMBD** (Plastics Microbial Biodegradation Database).
3. **UniProt API Fallback:** If any protein sequence lacks structural annotation, domain definitions, or full-length amino acid sequences, we resolve it programmatically via the **UniProt REST API** using the accession ID. This also allows retrieving catalytic triad residues (Ser-His-Asp) and canonical Pfam domains (`PF01083` cutinase, `PF00561` $\alpha/\beta$-hydrolase) for biochemical validation.

---

## 3. Team Roles and Responsibilities

Work is distributed across five members according to domain expertise:

| Role | Domain Profile | Checkpoint 1 Responsibilities | Checkpoint 2 Responsibilities |
| :--- | :--- | :--- | :--- |
| **Member 1** | Data Science (ML Lead) | Baseline modeling (`src/models.py`) & first benchmark metrics | Advanced modeling (XGBoost / PLM) & comparative evaluation |
| **Member 2** | Data Science (Bioinfo & Splits Lead) | Feature extraction (`src/features.py`: AAC) & Colab setup | Sequence clustering with MMseqs2 & `GroupKFold` splits |
| **Member 3** | Data Science (Visuals & Support) | Dummy baseline classifier & sequence distribution plots | Performance gap charts, confusion matrices & slide deck |
| **Member 4** | Biology Lead | Research question formalization, biological QC & Plan B | Pfam/UniProt mapping & biological limitation analysis |
| **Member 5** | Chemistry Lead | Polymer SMILES validation & chemical reaction rationale | RDKit molecular descriptors & PUR chemical transfer test |

---

## 4. Minimum Deliverables Checklist for Checkpoint 1

- [x] **Research question in one sentence** stated clearly with biological context.
- [x] **Plan B for the data** explicitly defined with fallback databases and UniProt API integration.
- [x] **Roles split** formally assigned across all five group members.
- [ ] **Dataset check** executing on real data with QC summary table.
- [ ] **Baseline method and first number** computed via cross-validation and presented in the notebook.
