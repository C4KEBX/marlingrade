"""Owner entity detection + name cleaning. Spec §5.2. Implemented in S4 — see FARMSIGNAL_30_DAY_PLAN.md."""

from __future__ import annotations

import re

import pandas as pd

# Spec §5.2, verbatim keyword list. Word-boundary + case-insensitive matching --
# short keywords like "TR"/"LP" would false-positive as substrings otherwise
# (e.g. "TR" inside "TRAVIS", "CORP" inside "CORPUS") without \b on both sides.
_ENTITY_KEYWORDS = [
    "LLC", "L L C", "LP", "LTD", "INC", "CORP", "TRUST", "TR", "TRUSTEE",
    "PARTNERS", "PROPERTIES", "HOMES", "INVESTMENTS", "HOLDINGS", "BANK",
    "HOA", "CHURCH", "CITY OF", "COUNTY", "ISD", "FUND", "CAPITAL", "VENTURES",
]
_ENTITY_RE = re.compile(r"\b(?:" + "|".join(re.escape(k) for k in _ENTITY_KEYWORDS) + r")\b", re.IGNORECASE)


def is_entity_owner(owner_name: str | None) -> bool:
    """True if `owner_name` matches an entity/institutional keyword (spec §5.2).
    Entities are scored differently (§5.5) and labeled "Investor/Entity-owned" in
    the report, never "homeowner"."""
    if not owner_name:
        return False
    return _ENTITY_RE.search(owner_name) is not None


def entity_owner_mask(owner_names: pd.Series) -> pd.Series:
    """Vectorized form of is_entity_owner for bulk parcel processing."""
    return owner_names.fillna("").str.contains(_ENTITY_RE)
