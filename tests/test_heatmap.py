import xml.etree.ElementTree as ET
from collections import Counter

from riskarium.heatmap import render
from riskarium.model import load_case

NS = {"svg": "http://www.w3.org/2000/svg"}


def test_svg_is_well_formed_and_shows_every_risk_twice(write_case):
    root = ET.fromstring(render(load_case(write_case())))
    labels = Counter(t.text for t in root.iterfind(".//svg:g/svg:text", NS))
    assert labels == {"R1": 2, "R2": 2}  # once before, once after treatment


def test_risks_in_the_same_cell_do_not_overlap(write_case):
    def same_cell(d):
        d["risks"][1].update(likelihood=4, impact=5)
        d["risks"][1]["treatment"].update(likelihood=2, impact=4)

    root = ET.fromstring(render(load_case(write_case(same_cell))))
    centres = [(c.get("cx"), c.get("cy")) for c in root.iterfind(".//svg:g/svg:circle", NS)]
    assert len(centres) == len(set(centres)) == 4


def test_special_characters_in_titles_are_escaped(write_case):
    def nasty(d):
        d["risks"][0]["title"] = "A < B & C"

    svg = render(load_case(write_case(nasty)))
    ET.fromstring(svg)  # would raise on unescaped markup
    assert "A &lt; B &amp; C" in svg
