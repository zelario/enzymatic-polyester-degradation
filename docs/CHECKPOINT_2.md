# Checkpoint 2: Homology Clustering, Model Comparison & Evaluation

**Course:** Introduction to Bioinformatics (2026/27)  
**Topic:** Enzymatic Degradation of Polyesters  

---

## 1. Research Question

> **"How accurately can sequence-based models predict enzymatic PET degradation across remote homology enzyme clusters?"**

To evaluate true generalization to unseen enzyme families without homology leakage, we enforce **homology-reduced splits** via **MMseqs2** on a balanced, curated dataset of verified PET degraders and biological negative controls.

---

## 2. Dataset Curation & Analysis Pipeline

1. **Dataset Curation (`notebooks/02_data_curation.ipynb`):**
   - **Verified Positives (317):** Retain only PAZy enzymes with verified PET degradation (`reported_on_pet == 1`). The 168 PAZy enzymes annotated only on other plastics (e.g., PA, PUR, PLA) are **excluded** rather than falsely labeled as `0`, because "not reported" is not experimental inactivity.
   - **Biological Hard Negatives (317):** Retrieve reviewed carboxylic ester hydrolases (`EC 3.1.1.*`, 150–800 amino acids) from **UniProt Swiss-Prot** (`data/raw/uniprot/uniprot_esterase_negatives.tsv`), excluding any sequence or accession overlapping with PAZy. Using natural esterases of matching length forces the classifier to learn PET-specific determinants rather than trivially separating enzymes from random non-enzymatic proteins.
   - **Output:** Balanced 634-sequence dataset (`data/processed/curated/curated_pet_dataset.csv`).

2. **Sequence Clustering (`notebooks/03_homology_clustering.ipynb`):**
   - Export all 634 curated sequences (positives + negative controls) to FASTA format.
   - Cluster sequences using **MMseqs2** (`createdb` $\rightarrow$ `cluster` $\rightarrow$ `createtsv`, coverage `0.8`, `--cov-mode 0`) at three progressively stricter sequence identity thresholds: **70%**, **50%**, and **30%** (the homology *twilight zone*).
   - Save cluster assignments (`data/processed/clustering/curated_pet_clusters.csv`) for reproducible group-aware evaluation.

3. **Feature Engineering (Current Focus — Before Final Modeling):**
   - *Working input file:* `data/processed/clustering/curated_pet_clusters.csv` (634 sequences: 317 PET positives + 317 UniProt `EC 3.1.1.*` controls, with MMseqs2 cluster IDs at 70%, 50%, and 30%).
   - *Rationale:* Simple Amino Acid Composition (AAC) and exploratory models from the initial setup were purely preliminary sanity checks. Our current focus is designing **biologically meaningful enzyme features** before selecting and training the final two models:
     1. **Physicochemical & Biophysical Properties:** Hydrophobicity (GRAVY — critical for binding hydrophobic PET), Aromaticity (Trp/Tyr/Phe involved in $\pi$-stacking with terephthalate rings), Isoelectric Point (pI), Net Charge, Instability Index, and Aliphatic Index.
     2. **Sequence-Order & Catalytic Motifs:** Dipeptide Composition (400-dim) and conserved catalytic signatures (such as the $\alpha/\beta$-hydrolase nucleophilic elbow motif `GxSxG` and disulfide-forming cysteine counts/patterns).
     3. **Evolutionary / Structural Embeddings (Optional):** Pre-trained Protein Language Model embeddings (e.g., ESM-2) to capture remote homology context.

4. **Homology-Aware Cross-Validation & Model Selection (Next Step):**
   - Use `StratifiedGroupKFold` (5 folds) with MMseqs2 `cluster_id` as the grouping variable so no sequence cluster is shared between training and validation folds.
   - Select and compare at least two models (e.g., `RandomForestClassifier`, `LogisticRegression`, or Gradient Boosting — final selection to be decided after feature engineering).

---

## 3. Results

*Table to be populated after running the homology-split evaluation:*

| Split Strategy | Identity Threshold | Model & Features | Accuracy | F1-Score | ROC-AUC | PR-AUC |
| :--- | :---: | :--- | :---: | :---: | :---: | :---: |
| **Cluster Split (MMseqs2)** | 70% | Logistic Regression (AAC) | *TBD* | *TBD* | *TBD* | *TBD* |
| **Cluster Split (MMseqs2)** | 70% | Random Forest (AAC) | *TBD* | *TBD* | *TBD* | *TBD* |
| **Cluster Split (MMseqs2)** | 50% | Random Forest (AAC) | *TBD* | *TBD* | *TBD* | *TBD* |
| **Cluster Split (MMseqs2)** | 30% | Random Forest (AAC) | *TBD* | *TBD* | *TBD* | *TBD* |
| **Cluster Split (MMseqs2)** | 30% | Model + Dipeptide / ESM-2 | *TBD* | *TBD* | *TBD* | *TBD* |

---

## 4. Identified Limitations

1. **Single-Polymer Scope Limits Polymer-Side Chemistry Modeling:** Focusing primary training exclusively on PET (because other polymers in PAZy have insufficient sample sizes for multi-fold homology splits: PUR = 53, PLA = 45, PBAT = 21) restricts direct polymer-side descriptor modeling (e.g., RDKit repeat-unit features), since the substrate is constant across all 634 training records. Chemical analysis therefore shifts to enzyme physicochemical properties (aromaticity, hydrophobicity/GRAVY, charge) and mechanistic contrast against natural soluble esters.
2. **Putative Background Negatives vs. Assayed Negatives:** Because PAZy and PlasticDB do not systematically archive negative laboratory assays, the 317 UniProt Swiss-Prot `EC 3.1.1.*` controls represent *putative biological hard negatives* (well-characterized natural esterases absent from PAZy) rather than enzymes experimentally proven inactive on PET in wet-lab assays.
3. **Loss of Sequence Order in AAC:** Global amino acid composition discards positional information and cannot explicitly detect conserved catalytic motifs (such as the `GxSxG` nucleophilic elbow or the `Ser-His-Asp` catalytic triad).
4. **Cluster Size Skew at Strict Thresholds:** At 30% sequence identity, some enzyme families form large clusters while others become singletons, which can introduce variance across `StratifiedGroupKFold` test folds.
5. **Operational Clusters vs. Structural Families:** MMseqs2 clusters reflect primary sequence similarity; remote structural homologues within the $\alpha/\beta$-hydrolase fold may share <25% sequence identity yet retain conserved active-site geometry.

---

## 5. Planned Exploratory Extension (Final Evaluation)

* **Zero-Shot Cross-Polymer Chemistry Study:** As a secondary exploratory analysis using the PET-trained models, evaluate zero-shot recognition on the excluded PAZy non-PET enzymes to test whether sequence features learned on aromatic PET transfer better to **aromatic/cyclic polyesters** (PBAT, PEF) than to **aliphatic polyesters** (PLA, PBS) or **polyurethanes** (PUR).

---

## 6. Deliverable Status

- [x] Research question scoped to PET degradation across remote homology clusters.
- [x] Dataset curation notebook created (`notebooks/02_data_curation.ipynb`) with verified PET positives and UniProt Swiss-Prot `EC 3.1.1.*` negative controls.
- [x] Homology clustering notebook created (`notebooks/03_homology_clustering.ipynb`).
- [x] Curated dataset and MMseqs2 clusters generated (`data/processed/clustering/curated_pet_clusters.csv`).
- [ ] `StratifiedGroupKFold` evaluation run end-to-end across all thresholds.
- [ ] At least two methods/representations compared under homology-reduced splits.
- [ ] Final metrics, plots, and limitation analysis populated above.
