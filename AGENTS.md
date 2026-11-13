# AGENTS.md — Development Guidelines & Rules

This document serves as the operational guide for AI assistants and team members working on this repository.

---

## 1. Project Overview

* **Course:** Introduction to Bioinformatics (2026/27) — 4th Year, 1st Semester.
* **Topic:** Enzymatic Degradation of Polyesters.
* **Core Research Question:**
  > *"How well do sequence-based predictors of enzymatic polyester degradation generalise to unseen enzyme families and new polymer chemistries?"*

---

## 2. Current Development Scope

Focus strictly on the foundational stage:
1. **Data Ingestion & Quality Control:** Loading verified degraders (PAZy) and negative controls (PlasticDB), checking sequence validity, lengths, and substrate annotations.
2. **Feature Extraction:** Standard, interpretable sequence representations (e.g., Amino Acid Composition).
3. **Exploratory Analysis & Baselines:** Data distributions and simple baseline predictors evaluated via cross-validation.

> [!NOTE]
> Do not introduce downstream tools, complex language models, or advanced split workflows (e.g., MMseqs2, ESM-2, polyBERT) until the user explicitly directs to start those phases.

---

## 3. Strict Code & Engineering Rules

1. **Simplicity First (Never Ultra-Complex):**
   - Keep all code simple, transparent, and direct.
   - Avoid overengineering, deep class hierarchies, abstract wrapper layers, or unnecessary design patterns. Standard functions and pandas/scikit-learn calls are preferred.

2. **Explicit, Readable Naming (No Cryptic Abbreviations):**
   - Variable, function, and parameter names must always be clear, descriptive, and human-readable.
   - Avoid obscure, compressed, or single-letter abbreviations (e.g., prefer `sequence` over `s` or `sq`, `amino_acid_composition` over `aac_vec`, `dataset` over `df_d`, `quality_control` over `qc_res`).

3. **No Academic Terminology in Code:**
   - Do **NOT** use words like "checkpoint", "checkpoint 1", or "milestone" inside code, docstrings, comments, variable names, or notebook filenames.
   - Name files and modules purely by their scientific and functional purpose (e.g., `01_data_exploration_and_baseline.ipynb`, `data.py`, `features.py`, `models.py`).

4. **Step-by-Step, User-Directed Execution:**
   - **DO NOT build ahead of the user.** Never write features, models, machine learning pipelines, or complex workflows unless the user explicitly asks for them.
   - Address only the current specific request.

5. **Git Management:**
   - **NEVER execute `git commit` or `git push` automatically.** Leave staging and committing to the user.

6. **Environment Safety:**
   - Never create `.venv` directories inside Google Drive paths (`G:\My Drive`) to avoid sync locking and massive I/O.

7. **Code & Documentation Language:**
   - All code, docstrings, comments, console messages, and technical documentation must be strictly written in English.

---

## 4. Google Colab & Environment Pattern

When creating Jupyter notebooks, use this standard setup in the first cell:

```python
import sys
import os
from pathlib import Path

if 'google.colab' in sys.modules:
    print("🚀 Running in Google Colab!")
    if not os.path.exists("src"):
        !git clone https://github.com/zelario/enzymatic-polyester-degradation.git repo
        %cd repo
    !pip install -q rdkit biopython pandas numpy matplotlib seaborn scikit-learn
else:
    print("💻 Running locally.")

# Add project root to sys.path
project_root = Path('.').resolve()
if project_root.name == 'notebooks':
    project_root = project_root.parent
sys.path.insert(0, str(project_root))

```
