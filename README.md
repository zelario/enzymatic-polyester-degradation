# Enzymatic Degradation of Polyesters

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/)

---

## Research Question

> *"How well do sequence-based predictors of enzymatic polyester degradation generalise to unseen enzyme families and new polymer chemistries?"*

The goal is to test whether machine learning predictors of plastic-degrading enzymes can generalize when evaluated on:
1. **Unseen enzyme families** (clustered with MMseqs2 to prevent homology leakage).
2. **Novel polymer chemistries** (e.g., trained on PET and tested on PUR or aliphatic polyesters).

---

## How to Run

### Option 1: Google Colab (Recommended)
1. Push this repository to GitHub.
2. Open [Google Colab](https://colab.research.google.com/) -> **GitHub** tab -> select your repo -> open `notebooks/01_checkpoint_1_analysis.ipynb`.
3. Run the first cell to automatically clone the repo and load `src/`.

### Option 2: Locally
```bash
pip install rdkit biopython scikit-learn pandas numpy matplotlib seaborn
jupyter lab
```

