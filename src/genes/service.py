"""Lookups over the gene expression dataset."""

import logging
from pathlib import Path

import pandas as pd

DATASET_PATH = Path(__file__).resolve().parent / "data" / "gene_expression.csv"
logger = logging.getLogger(__name__)


class GeneExpressionService:
    """Load take-home gene expression data once."""

    def __init__(self) -> None:
        self._data = pd.read_csv(DATASET_PATH)
        self._canonical_symbols: dict[str, str] = dict(
            zip(self._data["gene"], self._data["canonical_gene"])
        )
        logger.info(
            "Loaded gene expression data (%d rows, %d cancer types)",
            len(self._data),
            self._data["cancer_indication"].nunique(),
        )

    def get_targets(self, cancer_name: str) -> list[str]:
        """Return genes listed for a cancer indication."""

        return self._data[self._data["cancer_indication"] == cancer_name][
            "canonical_gene"
        ].tolist()

    def get_cancer_types(self) -> list[str]:
        """Return the unique cancer indications in take-home data order."""

        return self._data["cancer_indication"].drop_duplicates().tolist()

    def get_canonical_symbol(self, gene_symbol: str) -> str | None:
        """Return the take-home dataset's canonical symbol, if present."""

        return self._canonical_symbols.get(gene_symbol)

    def get_expressions(self, genes: list[str]) -> dict[str, float]:
        """Return median expression values for the requested genes."""

        canonical_genes = [
            self._canonical_symbols[gene]
            for gene in genes
            if gene in self._canonical_symbols
        ]
        subset = self._data[self._data["canonical_gene"].isin(canonical_genes)]
        return dict(zip(subset["canonical_gene"], subset["median_value"]))
