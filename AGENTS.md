# AGENTS.md — Architecture Guide and Agent Guidelines

This document serves as the reference guide for any AI coding assistant or human collaborator working on this repository. It defines the biological background, the code architecture (`src/`), and how to collaboratively run notebooks on **Google Colab** via **Git**.

---

## 1. Project Context

* **Course:** Introduction to Bioinformatics (2026/27) — 4th Year, 1st Semester.
* **Topic:** Project 2 — **Enzymatic Degradation of Polyesters** ([project_2_slide.pdf](file:///g:/My%20Drive/Universidade/4º%20Ano/1º%20Semestre/BIO/bioinformatics-project/project_2_slide.pdf)).
* **Central Research Question:**
  > *"How well do sequence-based predictors of enzymatic polyester degradation generalise to unseen enzyme families and new polymer chemistries?"*

### The Biological and Computational Problem
Enzymatic plastic recycling (e.g., PET, PBAT, PBS, PCL, PLA, PUR) currently relies on only a few hundred biochemically verified enzymes (cataloged in the **PAZy** database, ~485 unique entries). These enzymes cluster into a small number of homologous families (cutinases, lipases, esterases).
* **Homology Leakage:** In a conventional random split (e.g., 80/20 train/test), nearly identical enzymes end up in both training and test folds, producing artificially inflated performance metrics.
* **The Project Challenge:** Evaluate how predictive performance degrades when testing against:
  1. **Entirely unseen enzyme families** (clustered by sequence identity using **MMseqs2**).
  2. **Novel polymer chemistries** (e.g., training on PET and evaluating on polyurethane PUR or aliphatic polyesters).

---

## 2. Architecture: Why Use `src/` Instead of Putting Everything in Notebooks?

In bioinformatics and machine learning projects, placing entire codebases inside Jupyter notebook cells leads to massive, difficult-to-version notebooks prone to hidden state errors and merge conflicts.

### Separation of Concerns:
1. **`src/` Directory (Reusable Engineering & Domain Logic):**
   * Pure, modular, and testable `.py` modules.
   * Houses core logic: data fetching and parsing (`src/data.py`), sequence and polymer feature extraction via RDKit (`src/features.py`), models and benchmark evaluation metrics (`src/models.py`), and validation splitting strategies (`src/splits.py`).
2. **`notebooks/` Directory (Narrative, Visualizations, and Reporting):**
   * Clean, readable, and concise `.ipynb` notebooks.
   * Only imports functions from `src/`, executes high-level pipelines, renders figures (sequence length distributions, confusion matrices), and displays evaluation tables for grading presentations.

---

## 3. How to Use `src/` with Google Colab in a Team (Via Git)

The project team collaborates in a distributed manner through Git (GitHub/GitLab). **Never use hardcoded Google Drive paths** (e.g., `/content/drive/My Drive/...`), because the folder structure differs across team members' computers and Google accounts.

### The Standard Pattern (Git Clone in Colab):
Google Colab provides a temporary Linux virtual machine with access to a **free T4 GPU**. To use `src/` code inside Colab:

In the **first cell** of any notebook in `notebooks/`, include the following automatic environment detection:

```python
import sys
import os
from pathlib import Path

# Check if running in Google Colab
if 'google.colab' in sys.modules:
    print("🚀 Running in Google Colab with GPU support!")
    
    # If the src/ directory is not present, clone the team repository
    if not Path('src').is_dir():
        # Replace with your team's Git repository URL:
        # !git clone https://github.com/<username>/bioinformatics-project.git repo
        # %cd repo
        pass
        
    # Install required domain libraries on the Colab VM
    !pip install -q rdkit biopython
else:
    print("💻 Running locally.")

# Add project root to sys.path to allow importing src/
sys.path.insert(0, str(Path('.').resolve()))

# Enable autoreload to reflect changes in .py files without restarting the kernel
%load_ext autoreload
%autoreload 2
```

### Transparent Imports:
After executing that cell, any team member can import directly from `src/`:

```python
from src.data import parse_pazy_to_dataframe, validate_dataset
from src.features import compute_aac, compute_polymer_features
from src.models import train_eval_baseline
```

### Key Advantages of This Model:
* **No Heavy Local Docker:** Colab already runs inside a full cloud Linux container, freeing local RAM.
* **GPU Access for Protein Language Models (ESM-2):** For Checkpoint 2, extracting ESM-2 embeddings takes minutes on a Colab GPU instead of hours on a local CPU.
* **Frictionless Synchronization:** When a teammate updates a module in `src/` and pushes to Git, others can immediately run the latest version on Colab with a simple pull or re-clone.

---

## 4. Canonical Repository Structure

```text
bioinformatics-project/
├── AGENTS.md                                # This architecture and guidelines guide
├── README.md                                # General project documentation & setup
├── .gitignore                               # Git ignore rules
├── Bioinformatics.Projects.pdf              # Official course project catalogue
├── project_2_slide.pdf                      # Slide 8 extracted (Project 2 details)
├── project_2_with_rules.pdf                 # Slides 1 to 5 (rules/deadlines) + Slide 8
│
├── data/
│   ├── raw/                                 # Immutable raw data (e.g., pazy_proteins.json)
│   └── processed/                           # Cleaned tabular datasets and CSVs
│
├── docs/
│   ├── checkpoint_1.md                      # Checkpoint 1 deliverables & metrics
│   └── checkpoint_2.md                      # Checkpoint 2 planning & generalisation splits
│
├── notebooks/                               # Clean Jupyter notebooks (executable on Colab)
│   └── 01_checkpoint_1_analysis.ipynb
│
└── src/                                     # Modular Python source code
    ├── __init__.py
    ├── data.py                              # Data ingestion and QC validation
    ├── features.py                          # AAC and molecular descriptors
    └── models.py                            # Baseline classifiers & evaluation metrics
```

---

## 5. Guidelines for AI Agents

1. **Git Management:**
   * **NEVER run `git commit` or `git push` automatically**, unless explicitly requested by the user.
   * Keep the working tree clean, transparent, and easy for the user to review.
2. **Local vs Cloud Execution:**
   * **Do not force or create unnecessary Docker setups** when the workflow is designed around Google Colab.
   * Never create Python virtual environments (`.venv`) inside directories synchronized by Google Drive (`G:\My Drive`), to avoid sync locks and thousands of small file writes.
3. **Fidelity to Project Requirements:**
   * All metrics, validation splits, and methodological choices must strictly address the biological question of **Project 2** and the evaluation criteria defined in [docs/checkpoint_1.md](file:///g:/My%20Drive/Universidade/4º%20Ano/1º%20Semestre/BIO/bioinformatics-project/docs/checkpoint_1.md) and [docs/checkpoint_2.md](file:///g:/My%20Drive/Universidade/4º%20Ano/1º%20Semestre/BIO/bioinformatics-project/docs/checkpoint_2.md).
