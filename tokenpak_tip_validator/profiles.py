"""Profile compliance checker.

Cross-schema validation: given a component's manifest + its published
capability set + (optionally) a representative wire-header dict, verify
it satisfies every requirement of the named TIP-1.0 profile.

Profile requirement tables live in ``docs/protocol/profiles.md`` in the
docs repo; this module encodes them programmatically. When a profile's
requirements change (MINOR bump), both this module and profiles.md
update in the same PR.
"""

from __future__ import annotations

from dataclasses import dataclass

from .core import Finding, Severity, ValidationResult
from .schema import load_schema, validate_against


@dataclass(frozen=True)
class ProfileRequirement:
    """One requirement row from a profile's table."""

    capability: str     # capability label that must be published
    required: bool      # True = MUST, False = SHOULD (warning, not error)
    reason: str = ""    # human-readable explanation


# Per docs/protocol/profiles.md — TIP-1.0 profile requirement tables.
_PROFILE_REQUIREMENTS: dict[str, list[ProfileRequirement]] = {
    "tip-proxy": [
        ProfileRequirement("tip.compression.v1", True, "runs TIP-1.0 compression"),
        ProfileRequirement("tip.cache.provider-observer", True, "reports cache hits honestly"),
        ProfileRequirement("tip.telemetry.wire-side", True, "writes one telemetry row per request"),
        ProfileRequirement("tip.byte-preserved-passthrough", False,
                           "required if serving any provider with billing_routing_depends_on_body_bytes=true"),
        ProfileRequirement("tip.routing.fallback-chain", False, "required if user-facing routing is supported"),
        ProfileRequirement("tip.security.dlp-redaction", False, "required if the proxy claims DLP support"),
    ],
    "tip-companion": [
        ProfileRequirement("tip.preview.local", True, "provides local-only preview (never invokes a provider)"),
        ProfileRequirement("tip.companion.prompt-packaging", True, "packages prompts client-side"),
        ProfileRequirement("tip.companion.memory-capsule", False, "required if capsules are offered"),
        ProfileRequirement("tip.companion.session-journal", False, "required if journal is exposed"),
    ],
    "tip-adapter": [
        # Either client-integration OR framework-bridge — enforced below.
    ],
    "tip-plugin": [
        ProfileRequirement("tip.plugin.hook-point", True, "registers hooks at documented pipeline stages"),
    ],
    "tip-dashboard-consumer": [
        # Either dashboard.read-only OR alerts.threshold-notifier — enforced below.
    ],
}


def _validate_adapter_capabilities(capabilities: frozenset[str]) -> list[Finding]:
    findings: list[Finding] = []
    has_client = "tip.adapter.client-integration" in capabilities
    has_framework = "tip.adapter.framework-bridge" in capabilities
    if not (has_client or has_framework):
        findings.append(
            Finding(
                severity=Severity.ERROR,
                code="profile.adapter.missing-kind",
                message=(
                    "tip-adapter requires one of tip.adapter.client-integration or "
                    "tip.adapter.framework-bridge in capabilities"
                ),
            )
        )
    if has_client and has_framework:
        findings.append(
            Finding(
                severity=Severity.WARNING,
                code="profile.adapter.both-kinds",
                message=(
                    "tip-adapter claims both client-integration and framework-bridge; "
                    "verify this is intentional and matches manifest.adapter_kind"
                ),
            )
        )
    return findings


def _validate_dashboard_consumer_capabilities(capabilities: frozenset[str]) -> list[Finding]:
    findings: list[Finding] = []
    has_dashboard = "tip.dashboard.read-only" in capabilities
    has_alerts = "tip.alerts.threshold-notifier" in capabilities
    if not (has_dashboard or has_alerts):
        findings.append(
            Finding(
                severity=Severity.ERROR,
                code="profile.dashboard-consumer.missing-kind",
                message=(
                    "tip-dashboard-consumer requires one of tip.dashboard.read-only or "
                    "tip.alerts.threshold-notifier in capabilities"
                ),
            )
        )
    return findings


def _catalog_labels() -> frozenset[str]:
    """Load the authoritative TIP-1.0 capability label set.

    Sources `capability-catalog.json` at the registry root (the
    authoritative file published Phase 3 WS-B). Falls back to the
    `examples[0].labels` block inside `capabilities.schema.json` so the
    validator still works in environments where the catalog file
    hasn't been vendored yet.
    """
    import json
    from .schema import _registry_root  # local import to avoid a cycle

    catalog_path = _registry_root() / "capability-catalog.json"
    if catalog_path.exists():
        with catalog_path.open("r", encoding="utf-8") as f:
            catalog = json.load(f)
        return frozenset(entry["id"] for entry in catalog.get("labels", []))

    # Fallback: use the examples embedded in the schema.
    cat = load_schema("capabilities")
    examples = cat.get("examples", [])
    if not examples:
        return frozenset()
    labels = examples[0].get("labels", [])
    return frozenset(entry["id"] for entry in labels)


def validate_profile(
    profile_name: str,
    *,
    capabilities: list[str],
    manifest: dict | None = None,
) -> ValidationResult:
    """Check that a component satisfies the TIP-1.0 profile ``profile_name``.

    ``capabilities`` is the component's published capability set.
    ``manifest`` is the validated manifest dict (pass result of
    ``validate_against`` first; this function assumes the manifest is
    schema-valid if provided).
    """
    if profile_name not in _PROFILE_REQUIREMENTS:
        return ValidationResult(
            ok=False,
            validator=f"profile:{profile_name}",
            findings=[
                Finding(
                    severity=Severity.ERROR,
                    code="profile.unknown",
                    message=(
                        f"unknown profile {profile_name!r}. Valid profiles: "
                        f"{sorted(_PROFILE_REQUIREMENTS)}"
                    ),
                )
            ],
        )

    cap_set = frozenset(capabilities)
    findings: list[Finding] = []

    # Catalog check — warn on unknown tip.* labels.
    catalog = _catalog_labels()
    if catalog:
        for label in cap_set:
            if label.startswith("tip.") and label not in catalog:
                findings.append(
                    Finding(
                        severity=Severity.WARNING,
                        code="profile.capability.not-in-catalog",
                        message=(
                            f"{label!r} is not in the TIP-1.0 capability catalog; "
                            "if it's a legitimate addition, update capabilities.schema.json"
                        ),
                    )
                )

    # Profile-specific capability requirements.
    for req in _PROFILE_REQUIREMENTS[profile_name]:
        if req.capability not in cap_set:
            severity = Severity.ERROR if req.required else Severity.WARNING
            findings.append(
                Finding(
                    severity=severity,
                    code=(
                        "profile.missing-required-capability" if req.required
                        else "profile.missing-optional-capability"
                    ),
                    message=(
                        f"{profile_name} "
                        + ("requires" if req.required else "recommends")
                        + f" capability {req.capability!r}"
                        + (f" — {req.reason}" if req.reason else "")
                    ),
                )
            )

    # Multi-kind profile handling.
    if profile_name == "tip-adapter":
        findings.extend(_validate_adapter_capabilities(cap_set))
    elif profile_name == "tip-dashboard-consumer":
        findings.extend(_validate_dashboard_consumer_capabilities(cap_set))

    # If a manifest is provided, cross-check kind matches.
    if manifest is not None:
        kind = manifest.get("kind")
        expected = {
            "tip-proxy": None,  # proxy has no manifest kind in TIP-1.0
            "tip-companion": None,
            "tip-adapter": "adapter",
            "tip-plugin": "plugin",
            "tip-dashboard-consumer": None,
        }.get(profile_name)
        if expected and kind != expected:
            findings.append(
                Finding(
                    severity=Severity.ERROR,
                    code="profile.manifest-kind-mismatch",
                    message=(
                        f"{profile_name} expects manifest kind={expected!r}, got {kind!r}"
                    ),
                    path="kind",
                )
            )

    return ValidationResult(
        ok=not any(f.severity is Severity.ERROR for f in findings),
        validator=f"profile:{profile_name}",
        findings=findings,
    )
