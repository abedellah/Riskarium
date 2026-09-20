import pytest

from riskarium.model import CaseError, load_case


def risk(data, index=0):
    return data["risks"][index]


def test_valid_case_loads(write_case):
    case = load_case(write_case())
    assert [r.id for r in case.risks] == ["R1", "R2"]
    assert case.risks[0].inherent == 20
    assert case.risks[0].residual == 8


@pytest.mark.parametrize("bad", [0, 6, -1, "4", 4.5, True, None])
def test_rating_outside_1_to_5_is_rejected(write_case, bad):
    with pytest.raises(CaseError):
        load_case(write_case(lambda d: risk(d).update(likelihood=bad)))


def test_unknown_iso_control_is_rejected(write_case):
    with pytest.raises(CaseError, match="unknown ISO control 'A.9.99'"):
        load_case(write_case(lambda d: risk(d).update(iso_controls=["A.9.99"])))


def test_unknown_csf_category_is_rejected(write_case):
    with pytest.raises(CaseError, match="unknown CSF category"):
        load_case(write_case(lambda d: risk(d).update(nist_csf=["XX.YY"])))


def test_documented_fact_needs_a_known_source(write_case):
    def unknown_source(d):
        risk(d)["facts"][0]["source"] = "S9"

    with pytest.raises(CaseError, match="known source"):
        load_case(write_case(unknown_source))


def test_documented_fact_without_source_is_rejected(write_case):
    def no_source(d):
        risk(d)["facts"][0]["source"] = None

    with pytest.raises(CaseError, match="known source"):
        load_case(write_case(no_source))


def test_inferred_fact_may_have_no_source(write_case):
    assert load_case(write_case())  # R2 carries an inferred fact without a source


def test_unknown_fact_kind_is_rejected(write_case):
    def bad_kind(d):
        risk(d)["facts"][0]["kind"] = "rumour"

    with pytest.raises(CaseError, match="fact kind"):
        load_case(write_case(bad_kind))


def test_treatment_cannot_raise_the_risk(write_case):
    def worse(d):
        risk(d)["treatment"]["impact"] = 5
        risk(d)["impact"] = 4

    with pytest.raises(CaseError, match="cannot raise"):
        load_case(write_case(worse))


def test_unknown_decision_is_rejected(write_case):
    def bad(d):
        risk(d)["treatment"]["decision"] = "ignore"

    with pytest.raises(CaseError, match="decision"):
        load_case(write_case(bad))


@pytest.mark.parametrize("missing", ["title", "sources", "risks", "disclaimer"])
def test_missing_top_level_field_is_rejected(write_case, missing):
    with pytest.raises(CaseError, match=missing):
        load_case(write_case(lambda d: d.pop(missing)))


def test_duplicate_risk_id_is_rejected(write_case):
    with pytest.raises(CaseError, match="duplicate risk id"):
        load_case(write_case(lambda d: risk(d, 1).update(id="R1")))


def test_duplicate_source_id_is_rejected(write_case):
    def dup(d):
        d["sources"].append(dict(d["sources"][0]))

    with pytest.raises(CaseError, match="duplicate source id"):
        load_case(write_case(dup))


def test_top_level_must_be_a_mapping(tmp_path):
    path = tmp_path / "case.yaml"
    path.write_text("- just\n- a list\n", encoding="utf-8")
    with pytest.raises(CaseError, match="mapping"):
        load_case(path)


def test_invalid_yaml_is_reported(tmp_path):
    path = tmp_path / "case.yaml"
    path.write_text("title: [unclosed\n", encoding="utf-8")
    with pytest.raises(CaseError, match="invalid YAML"):
        load_case(path)


def test_confidence_reflects_how_much_is_documented(write_case):
    def all_kinds(d):
        risk(d, 1)["facts"] = [{"kind": "inferred", "source": None, "text": "Hypothèse."}]

    case = load_case(write_case(all_kinds))
    assert case.risks[0].confidence == "élevée"  # every fact documented
    assert case.risks[1].confidence == "faible"  # nothing documented
    mixed = load_case(write_case())
    assert mixed.risks[1].confidence == "moyenne"  # one of two documented
