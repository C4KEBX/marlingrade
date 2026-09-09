"""Shared address normalization tests. Extracted from analytics/metrics.py's
private _normalize_address so absentee-detection and enrichment address-
matching (enrich/permits.py, enrich/code_violations.py) never silently diverge."""

from __future__ import annotations

from marlin_engine.normalize.address import normalize_address


def test_normalize_address_empty_string_for_falsy_input() -> None:
    assert normalize_address("") == ""
    assert normalize_address(None) == ""  # type: ignore[arg-type]


def test_normalize_address_uppercases_and_collapses_whitespace() -> None:
    assert normalize_address("100  main st") == "100 MAIN ST"


def test_normalize_address_canonicalizes_street_suffix_synonyms() -> None:
    assert normalize_address("100 MAIN STREET") == "100 MAIN ST"
    assert normalize_address("100 MAIN DRIVE") == "100 MAIN DR"


def test_normalize_address_strips_unit_markers() -> None:
    assert normalize_address("210 LAVACA ST APT 3402") == "210 LAVACA ST"
    assert normalize_address("210 LAVACA ST #4") == "210 LAVACA ST"


def test_normalize_address_strips_punctuation() -> None:
    assert normalize_address("100 Main St.,") == "100 MAIN ST"
