import io
import json
import os
import urllib.parse
import urllib.request
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_PAZY_PATH = str(PROJECT_ROOT / "data" / "raw" / "pazy" / "pazy_proteins.json")
RAW_PLASTICDB_PATH = str(PROJECT_ROOT / "data" / "raw" / "plasticdb" / "plasticdb_proteins.tsv")
RAW_UNIPROT_NEGATIVES_PATH = str(
    PROJECT_ROOT / "data" / "raw" / "uniprot" / "uniprot_esterase_negatives.tsv"
)
PAZY_API_URL = "https://api.pazy.eu/api/proteins/json/"
UNIPROT_API_URL = "https://rest.uniprot.org/uniprotkb/search"


# ==============================================================================
# Used in: notebooks/01_data_exploration_and_baseline.ipynb
# ==============================================================================


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
    Reported substrate flags indicate database annotations, not experimental negatives:
    a zero means that activity on that substrate is not reported in this snapshot.
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
        if not clean_sequence:
            continue

        substrates_list = [
            substrate.get("name", "") for substrate in entry.get("substrates", [])
        ]
        substrate_abbreviations = {
            (substrate.get("abbreviation") or "").strip().upper()
            for substrate in entry.get("substrates", [])
        }
        substrate_names = {name.strip().casefold() for name in substrates_list}

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
                "reported_on_pet": int(
                    "PET" in substrate_abbreviations
                    or "polyethylene terephthalate" in substrate_names
                ),
                "reported_on_pur": int(
                    "PUR" in substrate_abbreviations
                    or "polyurethane" in substrate_names
                ),
                "reported_on_pla": int(
                    "PLA" in substrate_abbreviations
                    or "polylactic acid" in substrate_names
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
        "Reported on PET": (
            dataset["reported_on_pet"].sum() if "reported_on_pet" in dataset.columns else 0
        ),
        "Reported on PUR": (
            dataset["reported_on_pur"].sum() if "reported_on_pur" in dataset.columns else 0
        ),
        "Reported on PLA": (
            dataset["reported_on_pla"].sum() if "reported_on_pla" in dataset.columns else 0
        ),
    }
    return pd.Series(quality_summary)


# ==============================================================================
# Used in: notebooks/02_data_curation.ipynb
# ==============================================================================


def extract_pazy_pet_positives(pazy_dataset: pd.DataFrame) -> pd.DataFrame:
    """
    Extracts only verified PET-degrading enzymes from the PAZy dataset.
    Unannotated non-PET entries are excluded rather than treated as negatives.
    """
    pet_positives = pazy_dataset[pazy_dataset["reported_on_pet"] == 1].copy()
    pet_positives["protein_id"] = "PAZY_" + pet_positives["protein_id"].astype(str)
    pet_positives["pet_degradation_label"] = 1
    pet_positives["evidence_source"] = "PAZy (verified PET)"

    selected_columns = [
        "protein_id",
        "protein_name",
        "uniprot_accession",
        "organism_name",
        "sequence_length",
        "pet_degradation_label",
        "evidence_source",
        "sequence",
    ]
    return pet_positives[selected_columns].reset_index(drop=True)


def fetch_uniprot_negative_hydrolases(
    max_records: int = 400,
    min_length: int = 150,
    max_length: int = 800,
    cache_path: str | Path = RAW_UNIPROT_NEGATIVES_PATH,
) -> pd.DataFrame:
    """
    Downloads reviewed carboxylic ester hydrolases (EC 3.1.1.*) from UniProt
    Swiss-Prot to serve as non-plastic biological negative controls.
    Caches the raw TSV locally for reproducible execution.
    """
    cache_file = Path(cache_path)
    if not cache_file.exists():
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        query_string = (
            f"(ec:3.1.1.*) AND (reviewed:true) "
            f"AND (length:[{min_length} TO {max_length}])"
        )
        encoded_query = urllib.parse.quote(query_string)
        request_url = (
            f"{UNIPROT_API_URL}?query={encoded_query}"
            f"&format=tsv&fields=accession,protein_name,organism_name,length,sequence"
            f"&size={max_records}"
        )
        request = urllib.request.Request(
            request_url,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            tsv_text = response.read().decode("utf-8")
        cache_file.write_text(tsv_text, encoding="utf-8")

    raw_uniprot = pd.read_csv(cache_file, sep="\t")
    raw_uniprot = raw_uniprot.dropna(subset=["Sequence"]).copy()
    raw_uniprot["sequence"] = (
        raw_uniprot["Sequence"].astype(str).str.replace(r"\s+", "", regex=True).str.upper()
    )

    negative_controls = pd.DataFrame(
        {
            "protein_id": "UNIPROT_" + raw_uniprot["Entry"].astype(str),
            "protein_name": raw_uniprot["Protein names"].astype(str),
            "uniprot_accession": raw_uniprot["Entry"].astype(str),
            "organism_name": raw_uniprot["Organism"].astype(str),
            "sequence_length": raw_uniprot["sequence"].str.len(),
            "pet_degradation_label": 0,
            "evidence_source": "UniProt Swiss-Prot (EC 3.1.1.* control)",
            "sequence": raw_uniprot["sequence"],
        }
    )
    return negative_controls.reset_index(drop=True)


def build_curated_pet_dataset(
    pazy_dataset: pd.DataFrame,
    negative_controls: pd.DataFrame,
    max_negatives: int | None = None,
    random_seed: int = 42,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Combines verified PAZy PET positives with UniProt Swiss-Prot negative controls.
    Removes any negative candidate whose sequence or UniProt accession appears in PAZy,
    filters out non-canonical amino acid sequences, and deduplicates exact sequences.
    """
    canonical_amino_acids = set("ACDEFGHIKLMNPQRSTVWY")

    positives = extract_pazy_pet_positives(pazy_dataset)

    pazy_sequences = set(pazy_dataset["sequence"].astype(str))
    pazy_accessions = set(
        pazy_dataset["uniprot_accession"].dropna().astype(str).str.strip()
    )

    clean_negatives = negative_controls[
        (~negative_controls["sequence"].isin(pazy_sequences))
        & (~negative_controls["uniprot_accession"].isin(pazy_accessions))
        & (negative_controls["sequence"].apply(lambda seq: not (set(seq) - canonical_amino_acids)))
    ].drop_duplicates(subset=["sequence"]).copy()

    if max_negatives is not None and len(clean_negatives) > max_negatives:
        clean_negatives = clean_negatives.sample(
            n=max_negatives, random_state=random_seed
        )

    curated_dataset = (
        pd.concat([positives, clean_negatives], ignore_index=True)
        .drop_duplicates(subset=["sequence"])
        .reset_index(drop=True)
    )

    summary_table = pd.DataFrame(
        [
            {"metric": "Total PAZy records loaded", "count": len(pazy_dataset)},
            {"metric": "PAZy non-PET records excluded (unverified)", "count": len(pazy_dataset) - len(positives)},
            {"metric": "Verified PET positives (PAZy)", "count": int((curated_dataset["pet_degradation_label"] == 1).sum())},
            {"metric": "Curated negative controls (UniProt EC 3.1.1.*)", "count": int((curated_dataset["pet_degradation_label"] == 0).sum())},
            {"metric": "Final curated dataset size", "count": len(curated_dataset)},
        ]
    )
    return curated_dataset, summary_table


# ==============================================================================
# Used in: notebooks/03_homology_clustering.ipynb
# ==============================================================================


def export_sequences_to_fasta(
    dataset: pd.DataFrame,
    output_fasta_path: str | Path,
    id_column: str = "protein_id",
    sequence_column: str = "sequence",
) -> Path:
    """
    Exports enzyme sequences from a DataFrame to a FASTA file.
    """
    output_path = Path(output_fasta_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as fasta_file:
        for _, row in dataset.iterrows():
            sequence_identifier = str(row[id_column])
            sequence = str(row[sequence_column]).strip()
            fasta_file.write(f">{sequence_identifier}\n{sequence}\n")

    return output_path
