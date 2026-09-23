import pytest

from src.genes.service import GeneExpressionService


@pytest.fixture(scope="module")
def gene_service() -> GeneExpressionService:
    return GeneExpressionService()


def test_get_genes_returns_unique_canonical_symbols_in_csv_order(
    gene_service: GeneExpressionService,
) -> None:
    genes = gene_service.get_genes()
    assert genes[:5] == ["BRCA2", "BRCA1", "TP53", "GATA3", "CDH1"]
    assert len(genes) == len(set(genes)) == 53


def test_get_genes_uses_canonical_symbols(
    gene_service: GeneExpressionService,
) -> None:
    assert "ERBB2" in gene_service.get_genes()
    assert "HER2" not in gene_service.get_genes()


def test_get_expressions_for_cancer_returns_empty_dict_for_unknown_indication(
    gene_service: GeneExpressionService,
) -> None:
    assert gene_service.get_expressions_for_cancer("unknown") == {}


def test_get_cancer_types_returns_unique_indications_in_csv_order(
    gene_service: GeneExpressionService,
) -> None:
    assert gene_service.get_cancer_types() == [
        "breast",
        "lung",
        "prostate",
        "gastric",
        "glioblastoma",
        "colorectal",
        "melanoma",
        "ovarian",
        "pancreatic",
        "renal",
    ]


def test_get_canonical_symbol_maps_dataset_alias_to_canonical_symbol(
    gene_service: GeneExpressionService,
) -> None:
    assert gene_service.get_canonical_symbol("HER2") == "ERBB2"
    assert gene_service.get_canonical_symbol("ERBB2") == "ERBB2"


def test_get_canonical_symbol_returns_none_for_unknown_symbol(
    gene_service: GeneExpressionService,
) -> None:
    assert gene_service.get_canonical_symbol("NOT_A_GENE") is None


def test_get_expressions_for_cancer_returns_all_values(
    gene_service: GeneExpressionService,
) -> None:
    assert gene_service.get_expressions_for_cancer("lung") == {
        "ALK": 0.215,
        "RET": 0.763,
        "ROS1": 0.102,
        "STK11": 0.38,
        "KRAS": 0.359,
    }


def test_get_expressions_for_gene_accepts_alias(
    gene_service: GeneExpressionService,
) -> None:
    assert gene_service.get_expressions_for_gene("HER2") == {
        "breast": 0.42,
        "gastric": 0.67,
    }


def test_get_expressions_for_gene_keeps_cancer_values_separate(
    gene_service: GeneExpressionService,
) -> None:
    assert gene_service.get_expressions_for_gene("KRAS") == {
        "lung": 0.359,
        "gastric": 0.355,
        "colorectal": 0.885,
        "ovarian": 0.003,
        "pancreatic": 0.241,
    }
