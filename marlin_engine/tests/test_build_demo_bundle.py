from __future__ import annotations
import json
from pathlib import Path
import pytest

DB = Path("data/farmsignal.duckdb")
pytestmark = pytest.mark.skipif(not DB.exists(), reason="demo DuckDB not present")


def test_bundle_builds_and_has_expected_shape(tmp_path: Path) -> None:
    from scripts.build_demo_bundle import build
    out = tmp_path / "data"
    build(db_path=DB, out_dir=out)

    zips = json.loads((out / "zips.json").read_text())
    assert {z["zip"] for z in zips} == {"78749", "78748", "78745", "78739", "78735", "78736", "78652"}
    focus = next(z for z in zips if z["zip"] == "78749")
    assert focus["sfr_count"] > 9000
    assert set(focus["distribution"]) == {"A", "B", "C", "D", "F"}
    assert sum(b["pct"] for b in focus["distribution"].values()) == pytest.approx(100, abs=1.0)

    parcels = json.loads((out / "parcels-78749.json").read_text())
    assert len(parcels) == focus["sfr_count"]
    p = parcels[0]
    assert p["grade"] in {"A", "B", "C", "D", "F"}
    assert 0 <= p["score"] <= 100
    assert isinstance(p["breakdown"], list)
    assert p["owner_type"] in {"occupant", "entity"}

    grades = json.loads((out / "grades.json").read_text())
    assert [c[0] for c in grades["cutoffs"]] == ["A", "B", "C", "D", "F"]
