"""Owner entity detection tests. Spec §5.2."""

from __future__ import annotations

import pandas as pd

from marlin_engine.normalize.owners import entity_owner_mask, is_entity_owner


def test_is_entity_owner_true_for_llc_suffix() -> None:
    assert is_entity_owner("SMITH PROPERTY MANAGEMENT LLC") is True


def test_is_entity_owner_true_for_spaced_l_l_c() -> None:
    assert is_entity_owner("ACME HOLDINGS L L C") is True


def test_is_entity_owner_true_for_trust_and_trustee() -> None:
    assert is_entity_owner("SMITH FAMILY TRUST") is True
    assert is_entity_owner("SMITH JOHN TR") is True
    assert is_entity_owner("SMITH JOHN TRUSTEE") is True


def test_is_entity_owner_true_for_government_and_institutional_keywords() -> None:
    assert is_entity_owner("CITY OF AUSTIN") is True
    assert is_entity_owner("TRAVIS COUNTY") is True
    assert is_entity_owner("AUSTIN ISD") is True
    assert is_entity_owner("FIRST BAPTIST CHURCH") is True


def test_is_entity_owner_false_for_ordinary_person_name() -> None:
    assert is_entity_owner("SMITH JOHN A") is False
    assert is_entity_owner("CHANDLER CHRISTOPHER N & ALLISON M") is False


def test_is_entity_owner_does_not_false_positive_on_substrings() -> None:
    """Word-boundary matching -- 'TR' must not match inside 'TRAVIS', 'CORP' must not
    match inside a surname like 'CORPUS', etc."""
    assert is_entity_owner("TRAVIS SARAH") is False
    assert is_entity_owner("CORPUS MARIA") is False
    assert is_entity_owner("BANKSTON WILLIAM") is False


def test_is_entity_owner_false_for_missing_name() -> None:
    assert is_entity_owner(None) is False
    assert is_entity_owner("") is False


def test_entity_owner_mask_vectorized_matches_scalar() -> None:
    names = pd.Series(["SMITH JOHN A", "ACME HOLDINGS LLC", None, "CITY OF AUSTIN"])
    mask = entity_owner_mask(names)
    assert mask.tolist() == [False, True, False, True]
