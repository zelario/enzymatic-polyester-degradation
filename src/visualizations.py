import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


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
