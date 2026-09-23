import pytest

from src.evaluations.service import calculate_metrics


def test_metrics_for_zero_partial_and_full_success() -> None:
    metrics = calculate_metrics([0, 2, 3])

    assert metrics[0]["pass_at_k"] == pytest.approx(5 / 9)
    assert metrics[0]["pass_hat_k"] == pytest.approx(5 / 9)
    assert metrics[1]["pass_at_k"] == pytest.approx(2 / 3)
    assert metrics[1]["pass_hat_k"] == pytest.approx(4 / 9)
    assert metrics[2]["pass_at_k"] == pytest.approx(2 / 3)
    assert metrics[2]["pass_hat_k"] == pytest.approx(1 / 3)
