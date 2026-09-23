"""Lookups over the gene expression dataset."""

import logging
from pathlib import Path

import pandas as pd

DATASET_PATH = Path(__file__).resolve().parent / "data" / "gene_expression.csv"
logger = logging.getLogger(__name__)


class GeneExpressionService:
    """Load gene expression data once."""

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

    def get_cancer_types(self) -> list[str]:
        """Return the unique cancer indications in dataset order."""

        return self._data["cancer_indication"].drop_duplicates().tolist()

    def get_genes(self) -> list[str]:
        """Return unique canonical genes in dataset order."""

        return self._data["canonical_gene"].drop_duplicates().tolist()

    def get_canonical_symbol(self, gene_symbol: str) -> str | None:
        """Return the dataset's canonical symbol, if present."""

        return self._canonical_symbols.get(gene_symbol)

    def get_expressions_for_cancer(self, cancer_name: str) -> dict[str, float]:
        """Return canonical gene-to-expression values for one cancer."""

        subset = self._data[self._data["cancer_indication"] == cancer_name]
        return dict(zip(subset["canonical_gene"], subset["median_value"]))

    def get_expressions_for_gene(self, gene_symbol: str) -> dict[str, float]:
        """Return cancer-to-expression values for a gene or dataset alias."""

        canonical_symbol = self._canonical_symbols.get(gene_symbol, gene_symbol)
        subset = self._data[self._data["canonical_gene"] == canonical_symbol]
        return dict(zip(subset["cancer_indication"], subset["median_value"]))
