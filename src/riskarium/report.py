"""Markdown report (in French) generated from a validated case."""

from __future__ import annotations

from collections import defaultdict

from .catalog import ANNEX_A, ANNEX_A_TOTAL, CSF_CATEGORIES
from .model import Case, Risk
from .scoring import HORIZONS, LEVELS, horizon, level, summarize

DECISION_FR = {
    "reduce": "Réduire",
    "accept": "Accepter",
    "transfer": "Transférer",
    "avoid": "Éviter",
}


def _cell(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def _num(value: float) -> str:
    return f"{value:.1f}".replace(".", ",")  # French decimal comma


def _badge(value: int) -> str:
    lv = level(value)
    return lv


def _ordered(case: Case) -> list[Risk]:
    return sorted(case.risks, key=lambda r: (-r.inherent, r.id))


def _synthesis(case: Case) -> list[str]:
    s = summarize(case)
    lines = ["| Niveau | Avant traitement | Après traitement |", "|---|---:|---:|"]
    for lv in LEVELS:
        lines.append(f"| {lv} | {s.before[lv]} | {s.after[lv]} |")
    lines += [
        "",
        f"Score moyen : **{_num(s.mean_before)}** avant traitement, **{_num(s.mean_after)}** "
        f"après (soit **-{s.reduction_pct} %**).",
    ]
    return lines


def _register(case: Case) -> list[str]:
    lines = [
        "| ID | Risque | V | I | Score | Niveau | Confiance | Horizon |",
        "|---|---|:-:|:-:|:-:|---|---|---|",
    ]
    for r in _ordered(case):
        lines.append(
            f"| {r.id} | {_cell(r.title)} | {r.likelihood} | {r.impact} | {r.inherent} "
            f"| {_badge(r.inherent)} | {r.confidence} | {horizon(r.inherent)} |"
        )
    return lines


def _risk_sheet(r: Risk) -> list[str]:
    lines = [f"### {r.id} : {r.title}", "", f"**Scénario.** {r.scenario}", "", "**Faits.**"]
    for f in r.facts:
        tag = f"[{f.source}]" if f.kind == "documented" else "*(analyse, non sourcé)*"
        lines.append(f"- {f.text} {tag}")
    lines += ["", "**Référentiels.**"]
    lines.append("- ISO/IEC 27001:2022 : " + ", ".join(f"{c} {ANNEX_A[c]}" for c in r.iso_controls))
    if r.nist_csf:
        lines.append(
            "- NIST CSF 2.0 : " + ", ".join(f"{c} ({CSF_CATEGORIES[c]})" for c in r.nist_csf)
        )
    if r.regulations:
        lines.append("- Réglementation : " + ", ".join(r.regulations))
    t = r.treatment
    lines += ["", f"**Traitement : {DECISION_FR[t.decision]}.**"]
    lines += [f"- {a}" for a in t.actions]
    lines += [
        "",
        f"Risque inhérent : {r.likelihood} × {r.impact} = **{r.inherent}** ({_badge(r.inherent)}). "
        f"Risque résiduel visé : {t.likelihood} × {t.impact} = **{r.residual}** "
        f"({_badge(r.residual)}). Confiance dans la cotation : {r.confidence}.",
        "",
    ]
    return lines


def _coverage(case: Case) -> list[str]:
    by_control: dict[str, list[str]] = defaultdict(list)
    for r in _ordered(case):
        for c in r.iso_controls:
            by_control[c].append(r.id)
    lines = [
        f"{len(by_control)} contrôles de l'Annexe A (sur {ANNEX_A_TOTAL}) sont concernés.",
        "",
        "| Contrôle | Intitulé | Risques |",
        "|---|---|---|",
    ]
    for c in sorted(by_control, key=lambda x: [int(p) for p in x[2:].split(".")]):
        lines.append(f"| {c} | {ANNEX_A[c]} | {', '.join(by_control[c])} |")
    return lines


def _roadmap(case: Case) -> list[str]:
    lines: list[str] = []
    for hz in dict.fromkeys(HORIZONS.values()):  # keeps the order, drops duplicates
        rows = [r for r in _ordered(case) if horizon(r.inherent) == hz]
        if not rows:
            continue
        lines += [f"### {hz}", ""]
        for r in rows:
            lines.append(
                f"- **{r.id}** ({_badge(r.inherent)}) : " + " ; ".join(r.treatment.actions)
            )
        lines.append("")
    return lines


def render_report(case: Case) -> str:
    out = [
        f"# {case.title}",
        "",
        f"> **Avertissement.** {case.disclaimer}",
        "",
        "## Contexte",
        "",
        case.context,
        "",
        "## Synthèse",
        "",
        *_synthesis(case),
        "",
        "![Matrice des risques](heatmap.svg)",
        "",
        "## Registre des risques",
        "",
        *_register(case),
        "",
        "## Fiches risque",
        "",
    ]
    for r in _ordered(case):
        out += _risk_sheet(r)
    out += [
        "## Couverture ISO/IEC 27001 (Annexe A)",
        "",
        *_coverage(case),
        "",
        "## Feuille de route",
        "",
        "L'horizon découle du niveau du risque inhérent : critique 0-3 mois, "
        "élevé 3-6 mois, moyen ou faible 6-12 mois.",
        "",
        *_roadmap(case),
        "## Sources",
        "",
    ]
    out += [f"- [{s.id}] {s.title}, {s.date} : <{s.url}>" for s in case.sources]
    out += [
        "",
        "## Méthode",
        "",
        "- **Score** = vraisemblance (1 à 5) × impact (1 à 5). Seuils : critique ≥ 15, "
        "élevé 10 à 14, moyen 5 à 9, faible ≤ 4.",
        "- **Confiance** : *élevée* si tous les faits d'un risque sont sourcés, *moyenne* si "
        "certains relèvent de l'analyse, *faible* si aucun n'est sourcé.",
        "- Les cotations sont un jugement d'analyste ; les faits, eux, renvoient à une source.",
        "",
    ]
    return "\n".join(out)
