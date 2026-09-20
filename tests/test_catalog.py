import re

from riskarium.catalog import ANNEX_A, CSF_CATEGORIES

# ISO/IEC 27001:2022 Annex A: 5.1-5.37, 6.1-6.8, 7.1-7.14, 8.1-8.34 (93 controls)
ANNEX_A_ID = re.compile(
    r"^A\.(5\.([1-9]|[12]\d|3[0-7])|6\.[1-8]|7\.([1-9]|1[0-4])|8\.([1-9]|[12]\d|3[0-4]))$"
)
CSF_ID = re.compile(r"^(GV|ID|PR|DE|RS|RC)\.[A-Z]{2}$")


def test_every_annex_a_identifier_exists_in_the_standard():
    bad = [c for c in ANNEX_A if not ANNEX_A_ID.match(c)]
    assert not bad, f"not a valid Annex A identifier: {bad}"


def test_csf_has_the_22_categories_of_version_2():
    assert len(CSF_CATEGORIES) == 22
    assert all(CSF_ID.match(c) for c in CSF_CATEGORIES)


def test_every_entry_has_a_label():
    assert all(label.strip() for label in ANNEX_A.values())
    assert all(label.strip() for label in CSF_CATEGORIES.values())
