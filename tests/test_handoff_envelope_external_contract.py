"""Pins the handoff-envelope schema's external-consumer contract surface.

The private ``tokenpak-paid`` PAKPlan handoff-envelope bridge
(``tokenpak_paid/pakplan/schemas/handoff_envelope.py``) re-implements a
minimal, dependency-free check of this schema's normative shape rather than
installing this package (the ``schemas/`` tree is not shipped as packaged
data — see ``tokenpak_tip_validator/schema.py``). That means drift between
this schema and the private module's hardcoded constants is invisible to
either repo's CI on its own.

This test is the registry-side half of that guard: it pins the exact fields
the private consumer depends on (``$id``, the ``schema_version`` const, the
top-level ``required`` set, and the ``stop.condition`` enum). If this test
fails, the private PAKPlan bridge's ``REQUIRED_TOP_LEVEL_FIELDS``,
``ALLOWED_STOP_CONDITIONS``, ``SCHEMA_VERSION``, and ``PUBLIC_SCHEMA_ID``
constants need a coordinated update in the same change.
"""

from __future__ import annotations

import json
from pathlib import Path

REGISTRY_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = REGISTRY_ROOT / "schemas" / "tip" / "handoff-envelope-v1.schema.json"

# Mirrors tokenpak_paid/pakplan/schemas/handoff_envelope.py in the tokenpak-paid
# repo. Keep these two definitions in sync by hand; this test is what makes
# the drift visible instead of silent.
EXPECTED_SCHEMA_ID = "https://docs.tokenpak.ai/schemas/tip/handoff-envelope-v1.json"
EXPECTED_SCHEMA_VERSION = "1.0"
EXPECTED_REQUIRED_TOP_LEVEL_FIELDS = frozenset(
    {
        "schema_version",
        "session_id",
        "correlation_id",
        "identity",
        "trigger",
        "objective",
        "explanation",
        "ordering_hints",
        "stop",
        "created_at",
    }
)
EXPECTED_ALLOWED_STOP_CONDITIONS = frozenset(
    {
        "none",
        "manual_review",
        "missing_required_context",
        "policy_block",
        "budget_exceeded",
        "operator_required",
    }
)


def _load_schema() -> dict:
    with SCHEMA_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def test_schema_id_matches_external_consumer_contract():
    schema = _load_schema()
    assert schema["$id"] == EXPECTED_SCHEMA_ID


def test_schema_version_const_matches_external_consumer_contract():
    schema = _load_schema()
    assert schema["properties"]["schema_version"]["const"] == EXPECTED_SCHEMA_VERSION


def test_required_top_level_fields_match_external_consumer_contract():
    schema = _load_schema()
    assert set(schema["required"]) == EXPECTED_REQUIRED_TOP_LEVEL_FIELDS


def test_stop_condition_enum_matches_external_consumer_contract():
    schema = _load_schema()
    enum = schema["properties"]["stop"]["properties"]["condition"]["enum"]
    assert set(enum) == EXPECTED_ALLOWED_STOP_CONDITIONS
