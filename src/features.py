import pandas as pd

STANDARD_AMINO_ACIDS = list("ACDEFGHIKLMNPQRSTVWY")


def calculate_amino_acid_composition(sequence: str) -> dict:
    """
    Calculates the relative frequency of each of the 20 standard amino acids in a sequence.
    """
    clean_sequence = sequence.upper()
    total_length = len(clean_sequence)

    if total_length == 0:
        return {f"composition_{amino_acid}": 0.0 for amino_acid in STANDARD_AMINO_ACIDS}

    amino_acid_counts = {amino_acid: 0 for amino_acid in STANDARD_AMINO_ACIDS}
    for character in clean_sequence:
        if character in amino_acid_counts:
            amino_acid_counts[character] += 1

    return {
        f"composition_{amino_acid}": amino_acid_counts[amino_acid] / total_length
        for amino_acid in STANDARD_AMINO_ACIDS
    }


def extract_sequence_features(
    dataset: pd.DataFrame, sequence_column: str = "sequence"
) -> pd.DataFrame:
    """
    Extracts sequence length and 20-dimensional amino acid composition features from a dataset.
    """
    composition_records = [
        calculate_amino_acid_composition(seq) for seq in dataset[sequence_column]
    ]
    features_dataframe = pd.DataFrame(composition_records, index=dataset.index)
    features_dataframe["sequence_length"] = dataset[sequence_column].str.len()

    return features_dataframe
