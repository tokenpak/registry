"""Generic JSON-schema validator over the Phase-3 TIP schemas.

Loads schemas from disk (the sibling ``schemas/`` tree in the registry
repo). A short name like ``"adapter"`` or ``"telemetry-event"`` resolves
to the right schema file.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

from .core import Finding, Severity, ValidationResult

# Short name → relative path from the registry root.
_SCHEMA_PATHS: dict[str, tuple[str, str]] = {
    "headers":                ("tip", "headers.schema.json"),
    "metadata":               ("tip", "metadata.schema.json"),
    "telemetry-event":        ("tip", "telemetry-event.schema.json"),
    "companion-journal-row":  ("tip", "companion-journal-row.schema.json"),
    "error":                  ("tip", "error.schema.json"),
    "capabilities":           ("tip", "capabilities.schema.json"),
    "compatibility":          ("tip", "compatibility.schema.json"),
    "adapter":                ("manifests", "adapter.schema.json"),
    "plugin":                 ("manifests", "plugin.schema.json"),
    "provider-profile":       ("manifests", "provider-profile.schema.json"),
    "client-profile":         ("manifests", "client-profile.schema.json"),
}


def _registry_root() -> Path:
    """Locate the registry root.

    Falls back from env var ``TOKENPAK_REGISTRY_ROOT`` to the parent
    directory of this package (the installed PyPI layout matches the
    repo layout: ``registry/{schemas,tokenpak_tip_validator}``).
    """
    import os

    env = os.environ.get("TOKENPAK_REGISTRY_ROOT")
    if env:
        return Path(env)
    # Package is installed at <root>/tokenpak_tip_validator/schema.py
    return Path(__file__).resolve().parent.parent


def load_schema(short_name: str) -> dict[str, Any]:
    """Return the parsed JSON for a TIP schema by short name."""
    if short_name not in _SCHEMA_PATHS:
        raise KeyError(
            f"unknown TIP schema name: {short_name!r}. "
            f"Valid names: {sorted(_SCHEMA_PATHS)}"
        )
    group, filename = _SCHEMA_PATHS[short_name]
    path = _registry_root() / "schemas" / group / filename
    if not path.exists():
        raise FileNotFoundError(
            f"TIP schema {short_name!r} expected at {path!s} but not found. "
            "Set TOKENPAK_REGISTRY_ROOT if running outside the registry repo."
        )
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _build_registry() -> Registry:
    """Build a referencing.Registry with every TIP schema loaded.

    Resolves both the canonical `$id` URLs
    (https://docs.tokenpak.ai/schemas/...) AND the relative filesystem paths
    (../tip/compatibility.schema.json) that manifest schemas use to
    cross-reference the compatibility schema.
    """
    resources: list[tuple[str, Resource]] = []
    for short_name, (group, filename) in _SCHEMA_PATHS.items():
        path = _registry_root() / "schemas" / group / filename
        if not path.exists():
            continue
        with path.open("r", encoding="utf-8") as f:
            schema = json.load(f)
        resource = Resource(contents=schema, specification=DRAFT202012)
        # Register by canonical $id URL
        if "$id" in schema:
            resources.append((schema["$id"], resource))
        # Also register by relative path so ../tip/...schema.json works
        # from the manifests/ directory.
        relative = f"../{group}/{filename}"
        resources.append((relative, resource))
    return Registry().with_resources(resources)


_REGISTRY: Registry | None = None


def _get_registry() -> Registry:
    global _REGISTRY
    if _REGISTRY is None:
        _REGISTRY = _build_registry()
    return _REGISTRY


def validate_against(short_name: str, document: Any) -> ValidationResult:
    """Validate ``document`` against the TIP schema named ``short_name``."""
    try:
        schema = load_schema(short_name)
    except (KeyError, FileNotFoundError) as exc:
        return ValidationResult(
            ok=False,
            validator=f"schema:{short_name}",
            findings=[
                Finding(
                    severity=Severity.ERROR,
                    code="schema.unavailable",
                    message=str(exc),
                )
            ],
        )

    validator = Draft202012Validator(schema, registry=_get_registry())
    findings: list[Finding] = []
    for error in validator.iter_errors(document):
        findings.append(
            Finding(
                severity=Severity.ERROR,
                code="schema.violation",
                message=error.message,
                path="/".join(str(p) for p in error.absolute_path) or "<root>",
                details={"schema_path": "/".join(str(p) for p in error.absolute_schema_path)},
            )
        )
    return ValidationResult(
        ok=not findings,
        validator=f"schema:{short_name}",
        findings=findings,
    )
