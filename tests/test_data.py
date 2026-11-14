"""Regression checks for substrate labels and the committed PAZy snapshot."""

import json
import tempfile
import unittest
from pathlib import Path

from src.data import check_dataset_quality, load_pazy_dataset


class SubstrateAnnotationTests(unittest.TestCase):
    def test_pbat_does_not_imply_pet_activity(self):
        records = [
            {
                "id": 1,
                "amino_acid_sequence": " acd\nEF ",
                "substrates": [{
                    "name": "Polybutylene adipate terephthalate",
                    "abbreviation": "PBAT",
                }],
            },
            {
                "id": 2,
                "amino_acid_sequence": "ACDEFG",
                "substrates": [
                    {"name": "Polyethylene terephthalate"},
                    {"name": "Polyurethane", "abbreviation": "PUR"},
                ],
            },
            {"id": 3, "amino_acid_sequence": " \n ", "substrates": []},
        ]
        with tempfile.TemporaryDirectory() as directory:
            snapshot = Path(directory) / "proteins.json"
            snapshot.write_text(json.dumps({"results": records}))
            dataset = load_pazy_dataset(str(snapshot))

        self.assertEqual(len(dataset), 2)
        self.assertEqual(dataset.loc[0, "sequence"], "ACDEF")
        self.assertEqual(dataset["reported_on_pet"].tolist(), [0, 1])
        self.assertEqual(dataset["reported_on_pur"].tolist(), [0, 1])
        self.assertEqual(dataset["reported_on_pla"].tolist(), [0, 0])

    def test_committed_snapshot_counts(self):
        dataset = load_pazy_dataset()
        quality = check_dataset_quality(dataset)
        self.assertEqual(len(dataset), 485)
        self.assertEqual(dataset["sequence"].nunique(), 485)
        self.assertEqual(quality["Sequences with non-canonical amino acids"], 0)
        self.assertEqual(quality["Reported on PET"], 317)
        self.assertEqual(quality["Reported on PUR"], 53)
        self.assertEqual(quality["Reported on PLA"], 45)


if __name__ == "__main__":
    unittest.main()
