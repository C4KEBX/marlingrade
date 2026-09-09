"""Address normalization shared by absentee-detection (analytics/metrics.py) and
enrichment address-matching (enrich/permits.py, enrich/code_violations.py).
Extracted from analytics/metrics.py so the two never silently diverge -- an
address-matching bug fixed in one caller must be fixed for both."""

from __future__ import annotations

import re

# USPS-style suffix synonyms (spec §5.3: "ST/STREET, DR/DRIVE") -- collapsed to a
# single canonical token so the same real address written two ways still compares
# equal. Not exhaustive; covers the suffixes that actually show up in TCAD data.
_SUFFIX_SYNONYMS = {
    "STREET": "ST", "DRIVE": "DR", "AVENUE": "AVE", "BOULEVARD": "BLVD",
    "LANE": "LN", "ROAD": "RD", "COURT": "CT", "CIRCLE": "CIR", "PLACE": "PL",
    "TRAIL": "TRL", "PARKWAY": "PKWY", "HIGHWAY": "HWY", "COVE": "CV",
    "TERRACE": "TER", "LOOP": "LP", "BEND": "BND", "CROSSING": "XING",
}
# Unit/apartment markers -- everything from the marker to the end of the string is
# dropped (spec §5.3 "unit stripping"): comparison is street number + street name,
# not which unit within a building.
_UNIT_TOKEN_RE = re.compile(r"(\b(APT|UNIT|STE|SUITE|BLDG|BUILDING)\b|#).*$")


def normalize_address(addr: str) -> str:
    """Upper-cases, strips punctuation, drops unit/suite markers, and
    canonicalizes USPS street-suffix synonyms (STREET -> ST, DRIVE -> DR, etc.)
    so the same real address written two different ways compares equal."""
    if not addr:
        return ""
    s = addr.upper()
    s = re.sub(r"[.,]", "", s)
    s = _UNIT_TOKEN_RE.sub("", s).strip()
    s = re.sub(r"\s+", " ", s).strip()
    return " ".join(_SUFFIX_SYNONYMS.get(tok, tok) for tok in s.split())
