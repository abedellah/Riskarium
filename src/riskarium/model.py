"""Data model and validation of a case file (YAML)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from .catalog import ANNEX_A, CSF_CATEGORIES

DECISIONS = ("reduce", "accept", "transfer", "avoid")
FACT_KINDS = ("documented", "inferred")


class CaseError(ValueError):
    """Raised when a case file is invalid."""


@dataclass(frozen=True)
class Source:
    id: str
    title: str
    url: str
    date: str


@dataclass(frozen=True)
class Fact:
    text: str
    kind: str  # "documented" (stated in a source) or "inferred" (analyst reasoning)
    source: str | None  # source id, mandatory when documented


@dataclass(frozen=True)
class Treatment:
    decision: str
    actions: tuple[str, ...]
    likelihood: int  # target after treatment
    impact: int  # target after treatment


@dataclass(frozen=True)
class Risk:
    id: str
    title: str
    scenario: str
    likelihood: int
    impact: int
    facts: tuple[Fact, ...]
    iso_controls: tuple[str, ...]
    nist_csf: tuple[str, ...]
    regulations: tuple[str, ...]
    treatment: Treatment

    @property
    def inherent(self) -> int:
        return self.likelihood * self.impact

    @property
    def residual(self) -> int:
        return self.treatment.likelihood * self.treatment.impact

    @property
    def confidence(self) -> str:
        """How much of the rating rests on documented facts rather than on inference."""
        documented = sum(1 for f in self.facts if f.kind == "documented")
        if documented == len(self.facts):
            return "élevée"
        if documented:
            return "moyenne"
        return "faible"


@dataclass(frozen=True)
class Case:
    title: str
    organisation: str
    context: str
    disclaimer: str
    sources: tuple[Source, ...]
    risks: tuple[Risk, ...]


def _get(data: dict[str, Any], key: str, where: str) -> Any:
    if key not in data or data[key] in (None, "", []):
        raise CaseError(f"{where}: missing field '{key}'")
    return data[key]


def _rating(value: Any, name: str, where: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= 5:
        raise CaseError(f"{where}: '{name}' must be an integer from 1 to 5, got {value!r}")
    return value


def _known(items: list[str], catalog: dict[str, str], name: str, where: str) -> tuple[str, ...]:
    for item in items:
        if item not in catalog:
            raise CaseError(f"{where}: unknown {name} '{item}'")
    return tuple(items)


def _parse_source(raw: dict[str, Any]) -> Source:
    where = f"source {raw.get('id', '?')}"
    return Source(
        id=str(_get(raw, "id", where)),
        title=str(_get(raw, "title", where)),
        url=str(_get(raw, "url", where)),
        date=str(_get(raw, "date", where)),
    )


def _parse_risk(raw: dict[str, Any], source_ids: set[str]) -> Risk:
    rid = str(_get(raw, "id", "risk"))
    where = f"risk {rid}"

    facts = []
    for f in _get(raw, "facts", where):
        kind = str(_get(f, "kind", f"{where} fact"))
        if kind not in FACT_KINDS:
            raise CaseError(f"{where}: fact kind must be one of {FACT_KINDS}, got '{kind}'")
        src = f.get("source")
        if kind == "documented" and src not in source_ids:
            raise CaseError(f"{where}: documented fact needs a known source, got {src!r}")
        facts.append(Fact(text=str(_get(f, "text", f"{where} fact")), kind=kind, source=src))

    t = _get(raw, "treatment", where)
    decision = str(_get(t, "decision", f"{where} treatment"))
    if decision not in DECISIONS:
        raise CaseError(f"{where}: decision must be one of {DECISIONS}, got '{decision}'")
    likelihood = _rating(_get(raw, "likelihood", where), "likelihood", where)
    impact = _rating(_get(raw, "impact", where), "impact", where)
    target_l = _rating(_get(t, "likelihood", f"{where} treatment"), "target likelihood", where)
    target_i = _rating(_get(t, "impact", f"{where} treatment"), "target impact", where)
    if target_l > likelihood or target_i > impact:
        raise CaseError(f"{where}: the treatment cannot raise likelihood or impact")

    return Risk(
        id=rid,
        title=str(_get(raw, "title", where)),
        scenario=str(_get(raw, "scenario", where)),
        likelihood=likelihood,
        impact=impact,
        facts=tuple(facts),
        iso_controls=_known(list(_get(raw, "iso_controls", where)), ANNEX_A, "ISO control", where),
        nist_csf=_known(list(raw.get("nist_csf") or []), CSF_CATEGORIES, "CSF category", where),
        regulations=tuple(str(r) for r in raw.get("regulations") or []),
        treatment=Treatment(
            decision=decision,
            actions=tuple(str(a) for a in _get(t, "actions", f"{where} treatment")),
            likelihood=target_l,
            impact=target_i,
        ),
    )


def load_case(path: str | Path) -> Case:
    """Read and validate a case file. Raises CaseError with a precise message."""
    try:
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise CaseError(f"invalid YAML: {exc}") from exc
    if not isinstance(data, dict):
        raise CaseError("the case file must contain a mapping at the top level")

    sources = tuple(_parse_source(s) for s in _get(data, "sources", "case"))
    ids = [s.id for s in sources]
    if len(set(ids)) != len(ids):
        raise CaseError("duplicate source id")

    risks = tuple(_parse_risk(r, set(ids)) for r in _get(data, "risks", "case"))
    risk_ids = [r.id for r in risks]
    if len(set(risk_ids)) != len(risk_ids):
        raise CaseError("duplicate risk id")

    return Case(
        title=str(_get(data, "title", "case")),
        organisation=str(_get(data, "organisation", "case")),
        context=str(_get(data, "context", "case")).strip(),
        disclaimer=str(_get(data, "disclaimer", "case")).strip(),
        sources=sources,
        risks=risks,
    )
