"""Scoring rules. Deliberately simple so they can be explained in two minutes.

score = likelihood x impact                 (each rated 1 to 5, so 1 to 25)

critique : 15 to 25      élevé : 10 to 14      moyen : 5 to 9      faible : 1 to 4
"""

from __future__ import annotations

from dataclasses import dataclass

from .model import Case

LEVELS = ("critique", "élevé", "moyen", "faible")  # most to least severe

HORIZONS = {
    "critique": "0-3 mois",
    "élevé": "3-6 mois",
    "moyen": "6-12 mois",
    "faible": "6-12 mois",
}


def score(likelihood: int, impact: int) -> int:
    return likelihood * impact


def level(value: int) -> str:
    if value >= 15:
        return "critique"
    if value >= 10:
        return "élevé"
    if value >= 5:
        return "moyen"
    return "faible"


def horizon(value: int) -> str:
    """Treatment horizon, driven by the level of the inherent risk."""
    return HORIZONS[level(value)]


@dataclass(frozen=True)
class Summary:
    before: dict[str, int]  # number of risks per level, before treatment
    after: dict[str, int]  # number of risks per level, after treatment
    mean_before: float
    mean_after: float

    @property
    def reduction_pct(self) -> int:
        return round(100 * (self.mean_before - self.mean_after) / self.mean_before)


def summarize(case: Case) -> Summary:
    before = {lv: 0 for lv in LEVELS}
    after = {lv: 0 for lv in LEVELS}
    for risk in case.risks:
        before[level(risk.inherent)] += 1
        after[level(risk.residual)] += 1
    n = len(case.risks)
    return Summary(
        before=before,
        after=after,
        mean_before=sum(r.inherent for r in case.risks) / n,
        mean_after=sum(r.residual for r in case.risks) / n,
    )
