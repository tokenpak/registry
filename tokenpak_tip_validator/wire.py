"""Wire-level TIP-1.0 conformance checks (headers + capability sets).

Complements the schema validator: checks that go beyond pure JSON
schema — e.g. "X-TokenPak-Capability's comma-separated list must parse
as valid labels", "every required header is present".
"""

from __future__ import annotations

import re
from typing import Any

from .core import Finding, Severity, ValidationResult

# Required headers per docs/protocol/transport-bindings.md §1 — request.
_REQUIRED_REQUEST_HEADERS = (
    "X-TokenPak-TIP-Version",
    "X-TokenPak-Profile",
    "X-TokenPak-Request-Id",
)

# Required headers per docs/protocol/transport-bindings.md §1 — response.
_REQUIRED_RESPONSE_HEADERS = (
    "X-TokenPak-TIP-Version",
    "X-TokenPak-Cache-Origin",
    "X-TokenPak-Request-Id",
)

_TIP_VERSION_RE = re.compile(r"^TIP-\d+\.\d+$")
_LABEL_RE = re.compile(r"^(tip|ext)\.[a-z0-9._-]+$")
_CACHE_ORIGIN_VALUES = frozenset({"proxy", "client", "unknown"})


def validate_wire_headers(
    headers: dict[str, str],
    *,
    direction: str = "response",
) -> ValidationResult:
    """Check a header dict against TIP-1.0 transport-binding rules.

    ``direction`` is ``"request"`` or ``"response"``. Required headers
    differ (request MUST set Profile; response MUST set Cache-Origin).

    Header names are compared case-insensitively because HTTP is
    case-insensitive; the canonical casing in findings mirrors the
    schema's casing.
    """
    if direction not in ("request", "response"):
        raise ValueError(f"direction must be 'request' or 'response', got {direction!r}")

    lower_headers = {k.lower(): (k, v) for k, v in headers.items()}
    findings: list[Finding] = []

    required = (
        _REQUIRED_REQUEST_HEADERS if direction == "request"
        else _REQUIRED_RESPONSE_HEADERS
    )
    for name in required:
        if name.lower() not in lower_headers:
            findings.append(
                Finding(
                    severity=Severity.ERROR,
                    code="wire.missing-required-header",
                    message=f"{direction} missing required header {name}",
                    path=name,
                )
            )

    # Format checks for present headers.
    if "x-tokenpak-tip-version" in lower_headers:
        _, value = lower_headers["x-tokenpak-tip-version"]
        if not _TIP_VERSION_RE.match(value):
            findings.append(
                Finding(
                    severity=Severity.ERROR,
                    code="wire.invalid-tip-version",
                    message=(
                        f"X-TokenPak-TIP-Version {value!r} does not match "
                        "^TIP-<major>.<minor>$"
                    ),
                    path="X-TokenPak-TIP-Version",
                )
            )

    if "x-tokenpak-cache-origin" in lower_headers:
        _, value = lower_headers["x-tokenpak-cache-origin"]
        if value not in _CACHE_ORIGIN_VALUES:
            findings.append(
                Finding(
                    severity=Severity.ERROR,
                    code="wire.invalid-cache-origin",
                    message=(
                        f"X-TokenPak-Cache-Origin {value!r} must be "
                        "one of 'proxy', 'client', 'unknown'"
                    ),
                    path="X-TokenPak-Cache-Origin",
                )
            )

    if "x-tokenpak-capability" in lower_headers:
        _, value = lower_headers["x-tokenpak-capability"]
        cap_result = validate_capability_set(
            [lbl.strip() for lbl in value.split(",") if lbl.strip()]
        )
        for finding in cap_result.findings:
            finding.path = "X-TokenPak-Capability" + (f"[{finding.path}]" if finding.path else "")
            findings.append(finding)

    # Savings headers — check format only if present.
    for hdr in ("X-TokenPak-Savings-Tokens", "X-TokenPak-Savings-Cost"):
        if hdr.lower() in lower_headers:
            _, value = lower_headers[hdr.lower()]
            pattern = r"^[0-9]+$" if "Tokens" in hdr else r"^[0-9]+(\.[0-9]+)?$"
            if not re.match(pattern, value):
                findings.append(
                    Finding(
                        severity=Severity.ERROR,
                        code="wire.invalid-savings-value",
                        message=f"{hdr} {value!r} must be a non-negative number",
                        path=hdr,
                    )
                )

    return ValidationResult(
        ok=not any(f.severity is Severity.ERROR for f in findings),
        validator=f"wire:{direction}",
        findings=findings,
    )


def validate_capability_set(labels: list[str]) -> ValidationResult:
    """Check that every label in ``labels`` parses as a valid TIP label.

    Does NOT verify labels against the registry catalog — that requires
    loading capabilities.schema.json, which is done in ``profiles.py``.
    This function is the lightweight format-only check.
    """
    findings: list[Finding] = []
    seen: set[str] = set()
    for i, label in enumerate(labels):
        if label in seen:
            findings.append(
                Finding(
                    severity=Severity.WARNING,
                    code="capability.duplicate",
                    message=f"duplicate label {label!r}",
                    path=str(i),
                )
            )
        seen.add(label)
        if not _LABEL_RE.match(label):
            findings.append(
                Finding(
                    severity=Severity.ERROR,
                    code="capability.invalid-label",
                    message=(
                        f"{label!r} is not a valid TIP capability label; "
                        "must match ^(tip|ext)\\.[a-z0-9._-]+$"
                    ),
                    path=str(i),
                )
            )
    return ValidationResult(
        ok=not any(f.severity is Severity.ERROR for f in findings),
        validator="capability-set",
        findings=findings,
    )
