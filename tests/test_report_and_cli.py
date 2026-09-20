from pathlib import Path

from riskarium.cli import main
from riskarium.heatmap import render as render_heatmap
from riskarium.model import load_case
from riskarium.report import render_report

BUNDLED = Path(__file__).resolve().parent.parent / "cases" / "free-mobile-2024"


def test_report_orders_risks_by_inherent_score(write_case):
    report = render_report(load_case(write_case()))
    assert report.index("| R1 |") < report.index("| R2 |")


def test_report_links_each_documented_fact_to_its_source(write_case):
    report = render_report(load_case(write_case()))
    assert "- Un fait. [S1]" in report
    assert "*(analyse, non sourcé)*" in report  # the inferred fact is flagged
    assert "- [S1] Source, 2026-01 : <https://example.org>" in report


def test_report_uses_the_french_decimal_comma(write_case):
    report = render_report(load_case(write_case()))
    assert "**12,0** avant traitement, **6,0** après" in report


def test_report_counts_the_annex_a_controls_touched(write_case):
    report = render_report(load_case(write_case()))
    assert "2 contrôles de l'Annexe A (sur 93)" in report


def test_cli_validate_accepts_a_valid_case(write_case, capsys):
    assert main(["validate", str(write_case())]) == 0
    assert "OK: 2 risks, 1 sources" in capsys.readouterr().out


def test_cli_rejects_an_invalid_case_with_a_clear_message(write_case, capsys):
    path = write_case(lambda d: d["risks"][0].update(likelihood=9))
    assert main(["validate", str(path)]) == 2
    assert "must be an integer from 1 to 5" in capsys.readouterr().err


def test_cli_reports_a_missing_file(tmp_path, capsys):
    assert main(["validate", str(tmp_path / "nope.yaml")]) == 2
    assert "error:" in capsys.readouterr().err


def test_cli_report_writes_both_files(write_case, tmp_path):
    out = tmp_path / "out"
    assert main(["report", str(write_case()), "-o", str(out)]) == 0
    assert (out / "report.md").read_text(encoding="utf-8").startswith("# Cas de test")
    assert (out / "heatmap.svg").read_text(encoding="utf-8").startswith("<svg")


def test_bundled_case_is_valid():
    case = load_case(BUNDLED / "case.yaml")
    assert len(case.risks) == 6
    assert {s.id for s in case.sources} == {"S1", "S2"}


def test_committed_outputs_are_up_to_date():
    """The report and heatmap stored in the repo must match what the code produces now."""
    case = load_case(BUNDLED / "case.yaml")

    def stored(name: str) -> str:
        return (BUNDLED / name).read_text(encoding="utf-8").replace("\r\n", "\n")

    assert stored("report.md") == render_report(case), "run: riskarium report ... to refresh"
    assert stored("heatmap.svg") == render_heatmap(case), "run: riskarium report ... to refresh"
