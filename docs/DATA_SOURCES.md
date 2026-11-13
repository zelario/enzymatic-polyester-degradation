# Data Sources and Computational Tools Guide

This document provides a comprehensive, accessible breakdown of every data source and computational tool specified in the **Enzymatic Polyester Degradation** assignment slide (`docs/description.pdf`, slide 8).

---

## Overview: The Core Research Goal

> **"How well do sequence-based predictors of enzymatic polyester degradation generalise to unseen enzyme families and new polymer chemistries?"**

To answer this question, our pipeline connects the **biological space** (enzyme sequences and evolutionary families) with the **chemical space** (polymer repeat units and functional groups).

```
[ Biological Space: Enzymes ]                 [ Chemical Space: Polymers ]
  • PAZy (Verified degraders)                   • Polymer SMILES (Repeat units)
  • PlasticDB (Negative controls & variety)     • RDKit (Physicochemical properties)
  • PMBD (Literature cross-checks)              • polyBERT (Polymer embeddings)
  • UniProt (Canonical families & active sites)
                   \                                     /
                    \                                   /
                     ▼                                 ▼
                    [ MMseqs2 Sequence Clustering ]
                    [ Generalization Splits (Held-Out Families & Chemistries) ]
                                     │
                                     ▼
                      [ Machine Learning Classifier ]
```

---

## 1. Enzyme Datasets (The Biological Space)

### A. PAZy (Plastics-Active Enzymes Database)
* **What it is:** A curated database developed by the University of Stuttgart collecting only **biochemically verified** plastic-degrading enzymes tested in physical laboratory assays.
* **Website / API:** [pazy.eu](https://www.pazy.eu) | API: `https://api.pazy.eu/api/proteins/json/`
* **Contents in our repository:** `data/raw/pazy_proteins.json` and `data/processed/pazy_clean.csv`.
* **Exact contents:**
  * **505 total records**, of which **485 have verified, full amino acid sequences** (20 entries are literature mentions without sequence).
  * Enzyme names (e.g., `IsPETase`, `LCC`, `TfCut2`).
  * Source organisms (e.g., *Ideonella sakaiensis*, *Thermobifida fusca*).
  * UniProt accession codes (e.g., `A0A0K8P6T7`).
  * Target substrates:
    - **PET (Polyethylene terephthalate):** 328 enzymes
    - **PUR (Polyurethane):** 53 enzymes
    - **PLA (Polylactic acid):** 45 enzymes
    - **PBAT (Polybutylene adipate terephthalate):** 21 enzymes
    - **PBS (Polybutylene succinate):** 18 enzymes
* **Role in the project:** Provides our **primary positive training examples** for PET and PUR degradation.

---

### B. PlasticDB
* **What it is:** An online database (University of Auckland) cataloging microorganisms and protein sequences reported in literature to biodegrade plastics.
* **Website:** [plasticdb.org](https://plasticdb.org)
* **Contents in our repository:** `data/raw/plasticdb_proteins.tsv` and `data/processed/plasticdb_clean.csv`.
* **Exact contents:**
  * **329 total entries** (311 unique protein sequences).
  * Covers a broad spectrum of polymers: PET (186), PHA (59), PCL (49), PHB (46), PLA (31), PUR (19), Nylon (10), PE (4), PS (1).
  * **Overlap:** 105 sequences overlap with PAZy. **206 sequences are completely new**.
* **Role in the project (Negative Controls):**
  The assignment slide states: *"PlasticDB and PMBD for further reported enzymes and organisms; keep negative results"*.
  * If a machine learning model is trained only on enzymes that degrade PET, it simply learns what a generic esterase or cutinase looks like, not what specifically enables PET degradation.
  * The 206 enzymes that degrade PHA, PHB, Nylon, or PE—but **do not** degrade PET or PUR—provide **essential negative controls** to prevent positive prediction bias.

---

### C. PMBD (Plastics Microbial Biodegradation Database)
* **What it is:** A specialized database indexing plastic-degrading bacterial and fungal strains, experimental degradation conditions, and associated gene sequences.
* **Website:** `http://pmbd.genome-mining.cn/home`
* **Role in the project:**
  * Serves as a **validation and cross-referencing source**.
  * Used to resolve ambiguous experimental reports or confirm whether a candidate organism was verified by weight loss, enzymatic clearing zone, or chemical byproduct analysis (GC-MS).

---

### D. UniProt (Universal Protein Resource)
* **What it is:** The global gold-standard repository of protein sequence and functional annotation.
* **Role in the project:**
  1. **Canonical sequence retrieval:** Resolves full-length sequences via accession IDs.
  2. **Domain and family annotations:** Maps enzymes to **Pfam** and **InterPro** families (e.g., *alpha/beta hydrolase fold* `PF00561`, cutinase `PF01083`, fungal lipases).
  3. **Catalytic site verification:** Identifies the catalytic triad (typically Ser-His-Asp) to verify active enzymes and distinguish functional esterases from non-catalytic structural homologues.
  4. **Homology negative controls:** Enables retrieval of sequence homologues from the same family that do not have plastic degradation activity.

---

## 2. Sequence Clustering & Validation Splits (The Generalization Test)

### MMseqs2 (Many-against-Many sequence searching)
* **What it is:** An ultra-fast bioinformatic tool for sequence searching and clustering.
* **Crucial distinction:** **MMseqs2 is NOT a dataset**; it is an algorithm/software.
* **Why it is essential (The Homology Leakage Problem):**
  * In a standard random 80/20 train/test split, highly similar homologues (e.g., 95% identical cutinases) end up in both training and test folds.
  * The model appears to achieve 98% accuracy, but it is merely memorizing near-duplicate sequences (*homology leakage*).
* **How we use it:**
  1. Export all enzyme sequences into a FASTA file (`data/processed/pazy_sequences.fasta`).
  2. Run `mmseqs easy-cluster` at defined sequence identity thresholds (e.g., 30% or 50% identity).
  3. MMseqs2 groups the enzymes into distinct clusters (families).
  4. We perform a **Held-Out Family Split (GroupKFold)**: train on clusters A and B, evaluate on cluster C.
  5. This directly answers the first half of the research question: *How well does the predictor perform on completely unseen enzyme families?*

---

## 3. Polymer Chemistry (The Chemical Space)

Enzymes do not act in isolation; they interact with specific chemical functional groups (ester bonds in PET/PLA vs urethane bonds in PUR). To test generalization across polymer chemistries, plastics must be represented mathematically.

### A. Polymer Repeat Units (SMILES)
Polymers are long repeating chains. We represent each polymer by its canonical monomer or repeat-unit formula:
* **PET:** `O=C(c1ccc(C(=O)OCCO)cc1)OCCO` (Aromatic polyester; 2 ester bonds, 1 benzene ring)
* **PUR:** `O=C(Nc1ccc(Cc2ccc(NC(=O)OCCCCO)cc2)cc1)OCCCCO` (Polyurethane; 2 urethane bonds)
* **PLA:** `CC(O)C(=O)OC(C)C(=O)O` (Aliphatic polyester; 2 ester bonds)
* **PBAT:** `O=C(CCCC(=O)OCCCCOC(=O)c1ccc(C(=O)OCCCC)cc1)` (Aliphatic-aromatic copolyester)
* **PBS:** `O=C(CCC(=O)OCCCCO)OCCCCO` (Aliphatic polyester)

### B. RDKit
* **What it is:** An open-source cheminformatics toolkit in Python.
* **How we use it:**
  * Takes each polymer's repeat-unit SMILES and computes numerical molecular descriptors:
    - Molecular weight (`MolWt`)
    - Lipophilicity / partition coefficient (`MolLogP`)
    - Polar surface area (`TPSA`)
    - Hydrogen bond donors/acceptors (`HBD`, `HBA`)
    - Count of ester bonds vs urethane bonds
* **Role in the project:** Provides physical chemistry features for each polymer.

### C. polyBERT
* **What it is:** A chemical language model (Kuenneth & Ramprasad, *Nat Commun* 2023) pretrained on over 100 million polymer structures.
* **How it is used (Checkpoint 2 option):**
  * Takes polymer SMILES and generates dense numerical embeddings (vectors) capturing polymer physical chemistry.

---

## Summary Matrix

| Resource | Category | Physical Form in Repo | Role in Project |
| :--- | :--- | :--- | :--- |
| **PAZy** | Database | `data/raw/pazy_proteins.json`<br>`data/processed/pazy_clean.csv` | Core positive verified examples (PET, PUR, PLA degraders) |
| **PlasticDB** | Database | `data/raw/plasticdb_proteins.tsv`<br>`data/processed/plasticdb_clean.csv` | Negative controls & diversity (PHA, PHB, PE, Nylon degraders) |
| **PMBD** | Database | Web resource / cross-check | Experimental assay verification and literature backup |
| **UniProt** | Database / API | REST queries via Accession ID | Canonical sequences, catalytic triad, Pfam/InterPro families |
| **MMseqs2** | Software / Tool | Bioinformatic clustering executable | Groups enzymes by homology to build true held-out family splits |
| **RDKit** | Cheminformatics Library | Python package (`rdkit.Chem`) | Calculates molecular descriptors for polymer repeat units |
| **polyBERT** | Pretrained Model | Transformer embeddings | Dense polymer representations for novel chemistry testing |
