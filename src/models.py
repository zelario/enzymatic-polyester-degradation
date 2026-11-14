import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


def evaluate_baseline_models(
    features: pd.DataFrame,
    target: pd.Series,
    cross_validation_folds: int = 5,
    random_seed: int = 42,
) -> pd.DataFrame:
    """
    Evaluates baseline classifiers using Stratified K-Fold cross-validation.
    Returns a comparative summary table with mean performance metrics.
    """
    cross_validator = StratifiedKFold(
        n_splits=cross_validation_folds, shuffle=True, random_state=random_seed
    )
    metric_names = ["accuracy", "precision", "recall", "f1", "roc_auc"]

    candidate_models = {
        "Dummy (Most Frequent)": DummyClassifier(strategy="most_frequent"),
        "Logistic Regression (AAC)": make_pipeline(
            StandardScaler(),
            LogisticRegression(max_iter=1000, random_state=random_seed),
        ),
        "Random Forest (AAC)": RandomForestClassifier(
            n_estimators=100, random_state=random_seed
        ),
    }

    benchmark_records = []
    for model_name, classifier in candidate_models.items():
        cross_validation_results = cross_validate(
            classifier,
            features,
            target,
            cv=cross_validator,
            scoring=metric_names,
        )

        benchmark_records.append(
            {
                "model": model_name,
                "accuracy": round(
                    float(np.mean(cross_validation_results["test_accuracy"])), 4
                ),
                "precision": round(
                    float(np.mean(cross_validation_results["test_precision"])), 4
                ),
                "recall": round(
                    float(np.mean(cross_validation_results["test_recall"])), 4
                ),
                "f1_score": round(
                    float(np.mean(cross_validation_results["test_f1"])), 4
                ),
                "roc_auc": round(
                    float(np.mean(cross_validation_results["test_roc_auc"])), 4
                ),
            }
        )

    return pd.DataFrame(benchmark_records)
