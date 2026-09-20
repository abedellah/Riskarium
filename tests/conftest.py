import copy
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
import yaml

BASE: dict[str, Any] = {
    "title": "Cas de test",
    "organisation": "Organisation fictive",
    "context": "Contexte.",
    "disclaimer": "Avertissement.",
    "sources": [{"id": "S1", "title": "Source", "url": "https://example.org", "date": "2026-01"}],
    "risks": [
        {
            "id": "R1",
            "title": "Risque un",
            "scenario": "Scénario.",
            "likelihood": 4,
            "impact": 5,
            "facts": [{"kind": "documented", "source": "S1", "text": "Un fait."}],
            "iso_controls": ["A.8.5"],
            "nist_csf": ["PR.AA"],
            "regulations": ["RGPD, art. 32"],
            "treatment": {
                "decision": "reduce",
                "actions": ["Faire quelque chose"],
                "likelihood": 2,
                "impact": 4,
            },
        },
        {
            "id": "R2",
            "title": "Risque deux",
            "scenario": "Scénario.",
            "likelihood": 2,
            "impact": 2,
            "facts": [
                {"kind": "documented", "source": "S1", "text": "Un fait."},
                {"kind": "inferred", "source": None, "text": "Une hypothèse."},
            ],
            "iso_controls": ["A.8.16"],
            "treatment": {
                "decision": "accept",
                "actions": ["Accepter"],
                "likelihood": 2,
                "impact": 2,
            },
        },
    ],
}

WriteCase = Callable[[Callable[[dict[str, Any]], None] | None], Path]


@pytest.fixture
def write_case(tmp_path: Path) -> WriteCase:
    """Write a valid case file, optionally altered by `mutate`, and return its path."""

    def _write(mutate: Callable[[dict[str, Any]], None] | None = None) -> Path:
        data = copy.deepcopy(BASE)
        if mutate:
            mutate(data)
        path = tmp_path / "case.yaml"
        path.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
        return path

    return _write
