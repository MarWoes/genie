import pytest

from src.genes.service import GeneExpressionService


@pytest.fixture(scope="module")
def gene_service() -> GeneExpressionService:
    return GeneExpressionService()


def test_get_targets_returns_genes_for_indication_in_csv_order(
    gene_service: GeneExpressionService,
) -> None:
    assert gene_service.get_targets("lung") == ["ALK", "RET", "ROS1", "STK11", "KRAS"]


def test_get_targets_returns_empty_list_for_unknown_indication(
    gene_service: GeneExpressionService,
) -> None:
    assert gene_service.get_targets("unknown") == []


def test_get_expressions_returns_values_for_requested_genes(
    gene_service: GeneExpressionService,
) -> None:
    assert gene_service.get_expressions(["ALK", "RET", "NOT_A_GENE"]) == {
        "ALK": 0.215,
        "RET": 0.763,
    }


def test_get_expressions_uses_last_row_for_genes_repeated_across_indications(
    gene_service: GeneExpressionService,
) -> None:
    # This matches dict(zip(...)) behavior in the original example.
    assert gene_service.get_expressions(["KRAS"]) == {"KRAS": 0.241}
