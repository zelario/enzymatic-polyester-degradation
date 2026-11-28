# Enzymatic Degradation of Polyesters

> *"How accurately can sequence-based models predict enzymatic PET degradation across remote homology enzyme clusters?"*

## Notebooks

1. `notebooks/00_scope_exploration.ipynb` — Exploratory analysis of the PAZy snapshot and baseline scope.
2. `notebooks/01_data_curation.ipynb` — Verified PET positives (PAZy) + UniProt Swiss-Prot `EC 3.1.1.*` negative controls.
3. `notebooks/02_homology_clustering.ipynb` — MMseqs2 sequence clustering at 70%, 50%, and 30% identity.

## Running

- **Google Colab:** Open the desired notebook from GitHub in [Google Colab](https://colab.research.google.com/).
- **Locally:**
  ```bash
  pip install biopython scikit-learn pandas numpy matplotlib seaborn
  jupyter lab
  ```

## Docs

- [Checkpoint 1](docs/CHECKPOINT_1.md)
- [Checkpoint 2](docs/CHECKPOINT_2.md)
- [Data Sources](docs/DATA_SOURCES.md)
- [Agents & Architecture Guide](AGENTS.md)
