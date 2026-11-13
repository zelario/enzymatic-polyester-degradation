import json
import os
import urllib.request
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_PAZY_PATH = str(PROJECT_ROOT / "data" / "raw" / "pazy_proteins.json")
RAW_PLASTICDB_PATH = str(PROJECT_ROOT / "data" / "raw" / "plasticdb_proteins.tsv")
PAZY_API_URL = "https://api.pazy.eu/api/proteins/json/"


def download_pazy_dataset(destination_path: str = RAW_PAZY_PATH) -> str:
    """
    Downloads the PAZy dataset from the official public API if not already present.
    """
    if os.path.exists(destination_path):
        return destination_path

    os.makedirs(os.path.dirname(destination_path), exist_ok=True)
    request = urllib.request.Request(
        PAZY_API_URL,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    )
    with urllib.request.urlopen(request) as response:
        data_bytes = response.read()

    with open(destination_path, "wb") as output_file:
        output_file.write(data_bytes)

    return destination_path


def load_pazy_dataset(file_path: str = RAW_PAZY_PATH) -> pd.DataFrame:
    """
    Loads the PAZy dataset into a pandas DataFrame.
    Filters out entries without amino acid sequences and standardizes sequence format.
    """
    if not os.path.exists(file_path):
        download_pazy_dataset(file_path)

    with open(file_path, "r", encoding="utf-8") as json_file:
        raw_content = json.load(json_file)

    records = []
    for entry in raw_content.get("results", []):
        sequence = entry.get("amino_acid_sequence")
        if not sequence:
            continue

        # Standardize amino acid sequence: remove whitespace and convert to uppercase
        clean_sequence = "".join(sequence.split()).upper()

        substrates_list = [
            substrate.get("name", "") for substrate in entry.get("substrates", [])
        ]
        substrates_text = " ".join(substrates_list).lower()

        organism_info = entry.get("organism") or {}

        records.append(
            {
                "protein_id": str(entry.get("id")),
                "protein_name": entry.get("name"),
                "sequence": clean_sequence,
                "sequence_length": len(clean_sequence),
                "uniprot_accession": entry.get("uniprot_accession"),
                "organism_name": organism_info.get("scientific_name"),
                "reported_substrates": ", ".join(substrates_list),
                "active_on_pet": int(
                    "terephthalate" in substrates_text or "pet" in substrates_text
                ),
                "active_on_pur": int(
                    "polyurethane" in substrates_text or "pur" in substrates_text
                ),
                "active_on_pla": int(
                    "lactic" in substrates_text or "pla" in substrates_text
                ),
            }
        )

    return pd.DataFrame(records)


def check_dataset_quality(dataset: pd.DataFrame) -> pd.Series:
    """
    Computes quality control summary metrics for an enzyme sequence dataset.
    """

    canonical_amino_acids = set("ACDEFGHIKLMNPQRSTVWY")
    non_canonical_count = sum(
        1 for sequence in dataset["sequence"] if set(sequence) - canonical_amino_acids
    )

    quality_summary = {
        "Total enzymes": len(dataset),
        "Unique sequences": dataset["sequence"].nunique(),
        "With UniProt ID": (
            dataset["uniprot_accession"].notna().sum()
            if "uniprot_accession" in dataset.columns
            else None
        ),
        "Sequences with non-canonical amino acids": non_canonical_count,
        "Mean sequence length": round(dataset["sequence_length"].mean(), 1),
        "Min / Max sequence length": f"{dataset['sequence_length'].min()} - {dataset['sequence_length'].max()}",
        "Active on PET": (
            dataset["active_on_pet"].sum() if "active_on_pet" in dataset.columns else 0
        ),
        "Active on PUR": (
            dataset["active_on_pur"].sum() if "active_on_pur" in dataset.columns else 0
        ),
        "Active on PLA": (
            dataset["active_on_pla"].sum() if "active_on_pla" in dataset.columns else 0
        ),
    }
    return pd.Series(quality_summary)
