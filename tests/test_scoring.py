import pytest

from riskarium.model import load_case
from riskarium.scoring import horizon, level, score, summarize


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (1, "faible"),
        (4, "faible"),
        (5, "moyen"),
        (9, "moyen"),
        (10, "élevé"),
        (14, "élevé"),
        (15, "critique"),
        (25, "critique"),
    ],
)
def test_level_boundaries(value, expected):
    assert level(value) == expected


def test_score_is_likelihood_times_impact():
    assert score(4, 5) == 20
    assert score(1, 1) == 1


@pytest.mark.parametrize(
    ("value", "expected"),
    [(20, "0-3 mois"), (12, "3-6 mois"), (6, "6-12 mois"), (2, "6-12 mois")],
)
def test_horizon_follows_the_level(value, expected):
    assert horizon(value) == expected


def test_summary_counts_and_means(write_case):
    summary = summarize(load_case(write_case()))
    # R1: 4x5=20 -> critique, residual 2x4=8 -> moyen. R2: 2x2=4 -> faible, unchanged.
    assert summary.before == {"critique": 1, "élevé": 0, "moyen": 0, "faible": 1}
    assert summary.after == {"critique": 0, "élevé": 0, "moyen": 1, "faible": 1}
    assert summary.mean_before == 12.0
    assert summary.mean_after == 6.0
    assert summary.reduction_pct == 50
