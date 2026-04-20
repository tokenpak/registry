"""End-to-end test suite for tokenpak-tip-validator.

Every JSON fixture under ``test_vectors/`` is run through the validator
it declares in its ``_meta`` block. The test enforces that:

- ``expect: "pass"`` fixtures produce a ValidationResult with ok=True.
- ``expect: "fail"`` fixtures produce ok=False; and if the fixture
  declares an ``expected_error_code``, at least one error finding
  matches that code.
- Golden cases (one per profile) validate schema + capability-set
  + profile compliance together.

Run from the registry repo root:

    pytest tests/test_conformance_suite.py -v
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

import pytest

REGISTRY_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REGISTRY_ROOT))
os.environ.setdefault("TOKENPAK_REGISTRY_ROOT", str(REGISTRY_ROOT))

from tokenpak_tip_validator import (  # noqa: E402
    validate_against,
    validate_capability_set,
    validate_profile,
    validate_wire_headers,
)


def _load_fixture(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _iter_fixtures(*groups: str):
    """Yield (id, fixture_dict) for each JSON file in the named groups."""
    base = REGISTRY_ROOT / "test_vectors"
    for group in groups:
        for path in sorted((base / group).glob("*.json")):
            yield pytest.param(_load_fixture(path), id=f"{group}/{path.stem}")


@pytest.mark.parametrize("fixture", list(_iter_fixtures("headers")))
def test_wire_header_vectors(fixture: dict[str, Any]):
    meta = fixture["_meta"]
    assert meta["validator"] == "wire"
    result = validate_wire_headers(fixture["_data"], direction=meta["direction"])
    if meta["expect"] == "pass":
        assert result.ok, f"expected pass but got errors: {result.errors()}"
    else:
        assert not result.ok, "expected fail but validation passed"
        expected = meta.get("expected_error_code")
        if expected:
            codes = [f.code for f in result.errors()]
            assert expected in codes, (
                f"expected error code {expected!r} but got {codes}"
            )


@pytest.mark.parametrize(
    "fixture",
    list(_iter_fixtures("manifests", "telemetry", "compatibility")),
)
def test_schema_vectors(fixture: dict[str, Any]):
    meta = fixture["_meta"]
    assert meta["validator"] == "schema"
    result = validate_against(meta["schema"], fixture["_data"])
    if meta["expect"] == "pass":
        assert result.ok, f"expected pass but got errors: {result.errors()}"
    else:
        assert not result.ok, "expected fail but validation passed"


@pytest.mark.parametrize("fixture", list(_iter_fixtures("capabilities")))
def test_capability_set_vectors(fixture: dict[str, Any]):
    meta = fixture["_meta"]
    assert meta["validator"] == "capability-set"
    result = validate_capability_set(fixture["_data"])
    if meta["expect"] == "pass":
        assert result.ok
    else:
        assert not result.ok
        expected = meta.get("expected_error_code")
        if expected:
            codes = [f.code for f in result.errors()]
            assert expected in codes


@pytest.mark.parametrize("fixture", list(_iter_fixtures("golden")))
def test_golden_profile_compliance(fixture: dict[str, Any]):
    """Each golden case MUST pass profile validation for its profile."""
    meta = fixture["_meta"]
    assert meta["validator"] == "profile"
    result = validate_profile(
        meta["profile"],
        capabilities=fixture["_capabilities"],
        manifest=fixture.get("_manifest"),
    )
    assert result.ok, (
        f"golden case for {meta['profile']!r} failed profile compliance: "
        f"{[(f.code, f.message) for f in result.errors()]}"
    )


def test_cli_help_does_not_error():
    """Calling the CLI with --help should exit cleanly."""
    from tokenpak_tip_validator.__main__ import main

    with pytest.raises(SystemExit) as exc:
        main(["--help"])
    assert exc.value.code == 0


def test_cli_schema_mode_valid_adapter():
    """CLI should exit 0 for a valid adapter fixture."""
    import io
    from contextlib import redirect_stdout

    from tokenpak_tip_validator.__main__ import main

    fixture = _load_fixture(
        REGISTRY_ROOT / "test_vectors/manifests/valid-claude-code-adapter.json"
    )
    # Write fixture data to a temp file
    import tempfile

    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(fixture["_data"], f)
        tmp_path = f.name

    try:
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = main(["--schema", "adapter", "--input", tmp_path])
        assert code == 0, buf.getvalue()
        assert "PASS" in buf.getvalue()
    finally:
        os.unlink(tmp_path)


def test_all_five_profiles_have_golden_cases():
    """Every TIP-1.0 profile must have at least one golden case."""
    golden_dir = REGISTRY_ROOT / "test_vectors/golden"
    found_profiles = set()
    for path in golden_dir.glob("*.json"):
        fixture = _load_fixture(path)
        found_profiles.add(fixture["_meta"]["profile"])
    expected = {
        "tip-proxy", "tip-companion", "tip-adapter",
        "tip-plugin", "tip-dashboard-consumer",
    }
    missing = expected - found_profiles
    assert not missing, f"profiles without golden cases: {sorted(missing)}"


def test_validator_rejects_unknown_schema_name():
    """Asking for a schema that doesn't exist gives a clean error."""
    result = validate_against("not-a-real-schema", {})
    assert not result.ok
    assert result.errors()[0].code == "schema.unavailable"


def test_validator_rejects_unknown_profile():
    """Asking for a profile that doesn't exist gives a clean error."""
    result = validate_profile("tip-something-invented", capabilities=[])
    assert not result.ok
    assert result.errors()[0].code == "profile.unknown"
