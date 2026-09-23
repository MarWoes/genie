"""Lookups over the gene expression dataset."""

from pathlib import Path

import pandas as pd

DATASET_PATH = Path(__file__).resolve().parent / "data" / "gene_expression.csv"


class GeneExpressionService:
    """Load the gene dataset once and provide simple lookups."""

    def __init__(self, dataset_path: str | Path = DATASET_PATH) -> None:
        self._data = pd.read_csv(dataset_path)

    def get_targets(self, cancer_name: str) -> list[str]:
        """Return genes listed for a cancer indication."""

        return self._data[self._data["cancer_indication"] == cancer_name][
            "gene"
        ].tolist()

    def get_expressions(self, genes: list[str]) -> dict[str, float]:
        """Return median expression values for the requested genes."""

        subset = self._data[self._data["gene"].isin(genes)]
        return dict(zip(subset["gene"], subset["median_value"]))
