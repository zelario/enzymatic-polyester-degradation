# ==============================================================================
# Used in: notebooks/03_homology_clustering.ipynb
# ==============================================================================

from collections import Counter
from pathlib import Path
import shutil
import subprocess
import pandas as pd
from sklearn.cluster import AgglomerativeClustering
from sklearn.feature_extraction import DictVectorizer
from sklearn.preprocessing import normalize


def _find_mmseqs_executable() -> str | None:
    """Finds the MMseqs2 executable in PATH or the local Windows install folder."""
    local_windows_exe = Path.home() / ".local" / "mmseqs" / "mmseqs" / "bin" / "mmseqs.exe"
    if local_windows_exe.exists():
        return str(local_windows_exe)

    executable = shutil.which("mmseqs")
    if executable is not None:
        return executable

    return None


def run_mmseqs2_clustering(
    input_fasta_path: str | Path,
    output_directory: str | Path,
    min_sequence_identity: float = 0.3,
    coverage: float = 0.8,
) -> pd.Series:
    """
    Runs MMseqs2 clustering (createdb -> cluster -> createtsv) on a FASTA file
    and returns a Series mapping each protein_id to an integer cluster_id.
    """
    mmseqs_executable = _find_mmseqs_executable()
    if mmseqs_executable is None:
        raise EnvironmentError("MMseqs2 binary ('mmseqs') not found in PATH.")

    identity_percent = int(min_sequence_identity * 100)
    run_directory = Path(output_directory) / f"mmseqs_id{identity_percent}"
    temporary_directory = run_directory / "tmp"
    if run_directory.exists():
        shutil.rmtree(run_directory, ignore_errors=True)
    run_directory.mkdir(parents=True, exist_ok=True)
    temporary_directory.mkdir(parents=True, exist_ok=True)

    sequence_db = run_directory / "sequenceDB"
    cluster_db = run_directory / "clusterDB"
    cluster_tsv_path = run_directory / f"clusters_{identity_percent}_cluster.tsv"

    subprocess.run(
        [mmseqs_executable, "createdb", str(input_fasta_path), str(sequence_db)],
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        [
            mmseqs_executable,
            "cluster",
            str(sequence_db),
            str(cluster_db),
            str(temporary_directory),
            "--min-seq-id",
            str(min_sequence_identity),
            "-c",
            str(coverage),
            "--cov-mode",
            "0",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        [
            mmseqs_executable,
            "createtsv",
            str(sequence_db),
            str(sequence_db),
            str(cluster_db),
            str(cluster_tsv_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    cluster_table = pd.read_csv(
        cluster_tsv_path,
        sep="\t",
        names=["representative_id", "member_id"],
        dtype=str,
    )
    representative_to_index = {
        representative: index
        for index, representative in enumerate(cluster_table["representative_id"].unique())
    }
    cluster_table["cluster_id"] = cluster_table["representative_id"].map(
        representative_to_index
    )
    return cluster_table.set_index("member_id")["cluster_id"]


def cluster_sequences_by_kmers(
    dataset: pd.DataFrame,
    min_sequence_similarity: float = 0.3,
    kmer_size: int = 3,
    id_column: str = "protein_id",
    sequence_column: str = "sequence",
) -> pd.Series:
    """
    Pure-Python sequence clustering using normalized k-mer cosine distance and
    agglomerative clustering. Used locally when MMseqs2 is unavailable.
    """
    kmer_profiles = [
        Counter(
            sequence[position : position + kmer_size]
            for position in range(max(len(sequence) - kmer_size + 1, 0))
        )
        for sequence in dataset[sequence_column]
    ]

    vectorizer = DictVectorizer(sparse=True)
    kmer_matrix = vectorizer.fit_transform(kmer_profiles)
    normalized_matrix = normalize(kmer_matrix, norm="l2").toarray()

    distance_threshold = 1.0 - min_sequence_similarity
    clustering_model = AgglomerativeClustering(
        n_clusters=None,
        distance_threshold=distance_threshold,
        metric="cosine",
        linkage="average",
    )
    cluster_labels = clustering_model.fit_predict(normalized_matrix)
    return pd.Series(cluster_labels, index=dataset[id_column].astype(str))


def cluster_dataset_by_identity(
    dataset: pd.DataFrame,
    input_fasta_path: str | Path,
    output_directory: str | Path,
    identity_thresholds: list[float] | None = None,
    coverage: float = 0.8,
    id_column: str = "protein_id",
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Clusters sequences across multiple similarity thresholds.
    Uses MMseqs2 if available in PATH, otherwise falls back to k-mer clustering.
    """
    if identity_thresholds is None:
        identity_thresholds = [0.70, 0.50, 0.30]

    clustered_dataset = dataset.copy()
    clustered_dataset[id_column] = clustered_dataset[id_column].astype(str)
    use_mmseqs2 = _find_mmseqs_executable() is not None
    clustering_method = "MMseqs2" if use_mmseqs2 else "k-mer cosine clustering"
    print(f"Clustering sequences using: {clustering_method}")

    summary_records = []
    for threshold in identity_thresholds:
        identity_percent = int(threshold * 100)
        column_name = f"cluster_id_{identity_percent}"

        if use_mmseqs2:
            cluster_mapping = run_mmseqs2_clustering(
                input_fasta_path=input_fasta_path,
                output_directory=output_directory,
                min_sequence_identity=threshold,
                coverage=coverage,
            )
        else:
            cluster_mapping = cluster_sequences_by_kmers(
                dataset=clustered_dataset,
                min_sequence_similarity=threshold,
                id_column=id_column,
            )

        clustered_dataset[column_name] = clustered_dataset[id_column].map(cluster_mapping)

        cluster_sizes = clustered_dataset[column_name].value_counts()
        summary_records.append(
            {
                "threshold": f"{identity_percent}%",
                "method": clustering_method,
                "total_clusters": len(cluster_sizes),
                "singleton_clusters": int((cluster_sizes == 1).sum()),
                "largest_cluster_size": int(cluster_sizes.max()),
                "median_cluster_size": float(cluster_sizes.median()),
            }
        )

    return clustered_dataset, pd.DataFrame(summary_records)
