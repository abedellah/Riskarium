"""Risk matrix as a standalone SVG: before and after treatment, side by side."""

from __future__ import annotations

from collections import defaultdict
from xml.sax.saxutils import escape

from .model import Case, Risk
from .scoring import level

CELL = 66
LEFT = 64
TOP = 44
PANEL_W = LEFT + 5 * CELL + 16
HEIGHT = TOP + 5 * CELL + 40
DOT = 10  # radius of a risk marker

FILL = {
    "faible": "#d4ecd0",
    "moyen": "#fbf0b2",
    "élevé": "#fdd3a4",
    "critique": "#f2a9a9",
}


def _panel(title: str, x0: int, points: dict[tuple[int, int], list[Risk]]) -> list[str]:
    out = [
        f'<text x="{x0 + LEFT + 5 * CELL / 2}" y="22" text-anchor="middle" '
        f'font-weight="bold" font-size="14">{escape(title)}</text>'
    ]
    for likelihood in range(1, 6):
        for impact in range(1, 6):
            x = x0 + LEFT + (likelihood - 1) * CELL
            y = TOP + (5 - impact) * CELL
            fill = FILL[level(likelihood * impact)]
            out.append(
                f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" '
                f'fill="{fill}" stroke="#ffffff" stroke-width="2"/>'
            )
    for n in range(1, 6):
        out.append(
            f'<text x="{x0 + LEFT + (n - 0.5) * CELL}" y="{TOP + 5 * CELL + 16}" '
            f'text-anchor="middle" font-size="12">{n}</text>'
        )
        out.append(
            f'<text x="{x0 + LEFT - 10}" y="{TOP + (5 - n + 0.5) * CELL + 4}" '
            f'text-anchor="end" font-size="12">{n}</text>'
        )
    out.append(
        f'<text x="{x0 + LEFT + 5 * CELL / 2}" y="{TOP + 5 * CELL + 34}" '
        f'text-anchor="middle" font-size="12">Vraisemblance</text>'
    )
    out.append(
        f'<text transform="translate({x0 + 14} {TOP + 5 * CELL / 2}) rotate(-90)" '
        f'text-anchor="middle" font-size="12">Impact</text>'
    )

    for (likelihood, impact), risks in points.items():
        cx0 = x0 + LEFT + (likelihood - 1) * CELL
        cy0 = TOP + (5 - impact) * CELL
        for k, risk in enumerate(sorted(risks, key=lambda r: r.id)):
            cx = cx0 + 12 + DOT + (k % 3) * (2 * DOT + 1)
            cy = cy0 + 16 + DOT + (k // 3) * (2 * DOT + 4)
            out.append(
                f"<g><title>{escape(risk.id + ' : ' + risk.title)}</title>"
                f'<circle cx="{cx}" cy="{cy}" r="{DOT}" fill="#ffffff" stroke="#333333"/>'
                f'<text x="{cx}" y="{cy + 3.5}" text-anchor="middle" font-size="9" '
                f'font-weight="bold">{escape(risk.id)}</text></g>'
            )
    return out


def render(case: Case) -> str:
    before: dict[tuple[int, int], list[Risk]] = defaultdict(list)
    after: dict[tuple[int, int], list[Risk]] = defaultdict(list)
    for risk in case.risks:
        before[(risk.likelihood, risk.impact)].append(risk)
        after[(risk.treatment.likelihood, risk.treatment.impact)].append(risk)

    width = 2 * PANEL_W
    body = _panel("Avant traitement", 0, before) + _panel("Après traitement", PANEL_W, after)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{HEIGHT}" '
        f'viewBox="0 0 {width} {HEIGHT}" font-family="Helvetica, Arial, sans-serif" '
        f'role="img" aria-label="Matrice des risques avant et après traitement">'
        f'<rect width="{width}" height="{HEIGHT}" fill="#ffffff"/>' + "".join(body) + "</svg>\n"
    )
