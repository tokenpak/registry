"""Core result types for tokenpak-tip-validator.

Every validator returns a ``ValidationResult`` — one uniform shape so
callers can compose results across validators (e.g. schema + profile
+ wire headers all feed one report).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Severity(Enum):
    """Severity of a conformance finding."""

    ERROR = "error"     # MUST violations — fails conformance
    WARNING = "warning"  # SHOULD violations — conformance passes but operator should see
    INFO = "info"       # informational observations (optional capability not set, etc.)


@dataclass(slots=True)
class Finding:
    """A single conformance observation."""

    severity: Severity
    code: str           # canonical finding code, e.g. "schema.missing-required-field"
    message: str
    path: str = ""      # JSON path (e.g. ".capabilities[0]") or header name
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ValidationResult:
    """Aggregate result returned by every validator.

    ``ok`` is True iff there are zero ERROR findings. WARNING and INFO
    findings do not affect ``ok`` — callers who want stricter semantics
    inspect the findings list directly.
    """

    ok: bool
    findings: list[Finding] = field(default_factory=list)
    validator: str = ""  # which validator produced this (schema/profile/wire/capability)

    def merge(self, other: "ValidationResult") -> "ValidationResult":
        """Combine two results (AND over ok, concat findings)."""
        return ValidationResult(
            ok=self.ok and other.ok,
            findings=self.findings + other.findings,
            validator=self.validator + "+" + other.validator if other.validator else self.validator,
        )

    def errors(self) -> list[Finding]:
        return [f for f in self.findings if f.severity is Severity.ERROR]

    def warnings(self) -> list[Finding]:
        return [f for f in self.findings if f.severity is Severity.WARNING]

    def summary(self) -> str:
        """Single-line summary suitable for CLI output."""
        e, w = len(self.errors()), len(self.warnings())
        label = "PASS" if self.ok else "FAIL"
        return f"{label} [{self.validator}] errors={e} warnings={w}"
