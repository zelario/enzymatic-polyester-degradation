import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# ==============================================================================
# Used in: notebooks/01_data_exploration_and_baseline.ipynb
# ==============================================================================


def plot_dataset_exploration(dataset: pd.DataFrame):
    """
    Plots the distribution of enzyme sequence lengths and the distribution
    of reported substrate degradation targets (PET, PUR, PLA).
    """
    figure, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Plot 1: Sequence length distribution
    sns.histplot(dataset["sequence_length"], bins=30, kde=True, ax=axes[0], color="#2b5c8f")
    axes[0].set_title("Distribution of Enzyme Sequence Lengths", fontweight="bold")
    axes[0].set_xlabel("Sequence Length (Amino Acids)")
    axes[0].set_ylabel("Enzyme Count")

    # Plot 2: Substrate degradation activity counts
    activity_counts = pd.Series(
        {
            "PET reported": dataset["reported_on_pet"].sum(),
            "PUR reported": dataset["reported_on_pur"].sum(),
            "PLA reported": dataset["reported_on_pla"].sum(),
            "None of these reported": (
                dataset[["reported_on_pet", "reported_on_pur", "reported_on_pla"]]
                .eq(0).all(axis=1).sum()
            ),
        }
    )

    activity_counts.plot(kind="bar", ax=axes[1], color=["#e26d5c", "#38b000", "#ffb703", "#8d99ae"])
    axes[1].set_title("Reported Substrates (Counts Can Overlap)", fontweight="bold")
    axes[1].set_ylabel("Enzyme Count")
    axes[1].tick_params(axis="x", rotation=15)

    plt.tight_layout()
    plt.show()


# ==============================================================================
# Used in: notebooks/02_data_curation.ipynb
# ==============================================================================


def plot_curated_dataset_balance(curated_dataset: pd.DataFrame):
    """
    Plots class balance and sequence length distributions by class for the curated PET dataset.
    """
    figure, axes = plt.subplots(1, 2, figsize=(14, 5))

    label_names = curated_dataset["pet_degradation_label"].map(
        {1: "PET Positive (PAZy)", 0: "Negative Control (UniProt EC 3.1.1.*)"}
    )
    class_counts = label_names.value_counts()
    class_counts.plot(kind="bar", ax=axes[0], color=["#2b5c8f", "#8d99ae"])
    axes[0].set_title("Curated Dataset Class Balance", fontweight="bold")
    axes[0].set_ylabel("Enzyme Count")
    axes[0].tick_params(axis="x", rotation=10)

    plot_frame = curated_dataset.copy()
    plot_frame["Class"] = label_names
    sns.histplot(
        data=plot_frame,
        x="sequence_length",
        hue="Class",
        bins=30,
        kde=True,
        ax=axes[1],
        palette={"PET Positive (PAZy)": "#2b5c8f", "Negative Control (UniProt EC 3.1.1.*)": "#8d99ae"},
    )
    axes[1].set_title("Sequence Length Distribution by Class", fontweight="bold")
    axes[1].set_xlabel("Sequence Length (Amino Acids)")
    axes[1].set_ylabel("Enzyme Count")

    plt.tight_layout()
    plt.show()


# ==============================================================================
# Used in: notebooks/03_homology_clustering.ipynb
# ==============================================================================


def plot_cluster_size_distributions(
    dataset: pd.DataFrame,
    identity_thresholds: list[float] | None = None,
):
    """
    Plots the distribution of sequence cluster sizes across multiple identity thresholds.
    """
    if identity_thresholds is None:
        identity_thresholds = [0.70, 0.50, 0.30]

    figure, axes = plt.subplots(1, len(identity_thresholds), figsize=(5 * len(identity_thresholds), 4), sharey=True)
    if len(identity_thresholds) == 1:
        axes = [axes]

    for axis, threshold in zip(axes, identity_thresholds):
        identity_percent = int(threshold * 100)
        cluster_sizes = dataset[f"cluster_id_{identity_percent}"].value_counts()
        sns.histplot(cluster_sizes, bins=25, ax=axis, color="#2b5c8f")
        axis.set_title(f"Cluster Sizes ({identity_percent}% Identity)", fontweight="bold")
        axis.set_xlabel("Sequences per Cluster")
        axis.set_ylabel("Number of Clusters")

    plt.tight_layout()
    plt.show()
