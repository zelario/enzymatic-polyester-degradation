# Enzymatic Degradation of Polyesters

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/)

---

## Research Question

> *"How well do sequence-based predictors of enzymatic polyester degradation generalise to unseen enzyme families and new polymer chemistries?"*

The goal is to test whether machine learning predictors of plastic-degrading enzymes can generalize when evaluated on:
1. **Unseen enzyme families** (clustered with MMseqs2 to prevent homology leakage).
2. **Novel polymer chemistries** (e.g., trained on PET and tested on PUR or aliphatic polyesters).

---

## Current Status

The repository contains a local PAZy snapshot with 505 records, including 485 distinct
non-empty sequences. Exact substrate annotations identify 317 sequences reported on
PET, 53 on PUR and 45 on PLA; counts can overlap. PlasticDB is not yet included.
The notebook generates a processed CSV for easier reading.

The notebook implements quality checks and an exploratory annotation benchmark.
`reported_on_pet = 0` means PET activity is not reported, not experimentally disproved.
Experimental negative labels and evaluations on unseen families and chemistries are
still required to answer the research question.

## Reading the Dataset

Run the data ingestion cell in the notebook to view a compact table and generate
`data/processed/pazy_clean.csv`. The CSV has one enzyme per row (485 in the current
snapshot), with its name, organism, sequence length, reported substrates, annotation
flags, UniProt accession and complete sequence. The long sequence column is last.
Open it in Excel or LibreOffice using UTF-8 encoding and a comma separator, or load
it in Python with `pd.read_csv(csv_path)`. Empty cells mean missing information;
`reported_on_* = 0` means not reported, not experimentally inactive.

The JSON is the original source and contains additional nested information not
included in this simplified export. Regenerate the CSV by rerunning the notebook
after changes to the loader or snapshot. This CSV is versioned for convenient
team access; other processed files remain ignored by Git.

---

## How to Run

### Option 1: Google Colab (Recommended)
1. Push this repository to GitHub.
2. Open [Google Colab](https://colab.research.google.com/) -> **GitHub** tab -> select your repo -> open `notebooks/01_data_exploration_and_baseline.ipynb`.
3. Run the first cell to automatically clone the repo and load `src/`.

### Option 2: Locally
```bash
pip install rdkit biopython scikit-learn pandas numpy matplotlib seaborn
jupyter lab
```

---

## Project Documentation

* [Checkpoint 1: Question, Data Strategy & Team Roles](docs/CHECKPOINT_1.md)
* [Data Sources and Computational Tools Guide](docs/DATA_SOURCES.md)
* [Agents & Architecture Guide](AGENTS.md)

