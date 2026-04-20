"""tokenpak-tip-validator — conformance tooling for TIP-1.0.

Third parties and the TokenPak reference implementation both use this
package to prove conformance to TIP-1.0. Public surface:

    validate_against(schema_name, document) -> ValidationResult
        Generic JSON-schema validator over any of the 10 Phase-3 TIP
        schemas by short name ("headers", "metadata", "telemetry-event",
        "error", "capabilities", "compatibility", "adapter",
        "plugin", "provider-profile", "client-profile").

    validate_profile(profile_name, component) -> ValidationResult
        Cross-schema profile compliance check. Verifies a component's
        declared capabilities + manifest satisfy every required and
        profile-specific requirement for the named TIP-1.0 profile.

    validate_wire_headers(headers) -> ValidationResult
        Check that an inbound/outbound HTTP header dict satisfies the
        TIP-1.0 transport-binding rules (REQUIRED headers present,
        format constraints, capability-list syntax).

    validate_capability_set(labels) -> ValidationResult
        Check that every label in a capability set parses as tip.*/ext.*
        and that tip.* labels are in the registry catalog.

All validators return a single ``ValidationResult`` shape
(:class:`ValidationResult`), which carries a boolean ``ok`` plus a list
of ``Finding`` records for failures. CLI usage:

    python -m tokenpak_tip_validator --schema adapter < manifest.json
    python -m tokenpak_tip_validator --profile tip-proxy \\
        --capabilities "tip.compression.v1,tip.cache.provider-observer,..." \\
        --manifest proxy-manifest.json
"""

from __future__ import annotations

from .core import Finding, ValidationResult
from .profiles import validate_profile
from .schema import validate_against
from .wire import validate_capability_set, validate_wire_headers

__all__ = [
    "Finding",
    "ValidationResult",
    "validate_against",
    "validate_profile",
    "validate_wire_headers",
    "validate_capability_set",
]

__version__ = "0.1.0"
