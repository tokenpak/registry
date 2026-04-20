"""CLI entry point: ``python -m tokenpak_tip_validator``.

Examples:

    # Validate a manifest file against the adapter schema
    python -m tokenpak_tip_validator --schema adapter --input manifest.json

    # Validate a component's profile compliance
    python -m tokenpak_tip_validator --profile tip-proxy \\
        --capabilities "tip.compression.v1,tip.cache.provider-observer,tip.telemetry.wire-side"

    # Validate HTTP headers from a capture
    python -m tokenpak_tip_validator --wire response --input headers.json

Exit codes:
    0   conformance passed (no ERROR findings)
    1   conformance failed (≥1 ERROR finding)
    2   invalid CLI usage
"""

from __future__ import annotations

import argparse
import json
import sys

from .core import Severity, ValidationResult
from .profiles import validate_profile
from .schema import validate_against
from .wire import validate_capability_set, validate_wire_headers


def _print_result(result: ValidationResult) -> None:
    print(result.summary())
    for finding in result.findings:
        marker = {
            Severity.ERROR: "✗",
            Severity.WARNING: "!",
            Severity.INFO: "i",
        }[finding.severity]
        path = f" @ {finding.path}" if finding.path else ""
        print(f"  {marker} [{finding.code}] {finding.message}{path}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m tokenpak_tip_validator",
        description="TIP-1.0 conformance validator",
    )
    parser.add_argument(
        "--schema",
        choices=[
            "headers", "metadata", "telemetry-event", "error",
            "capabilities", "compatibility",
            "adapter", "plugin", "provider-profile", "client-profile",
        ],
        help="Validate the input document against a specific TIP schema",
    )
    parser.add_argument(
        "--profile",
        choices=["tip-proxy", "tip-companion", "tip-adapter", "tip-plugin", "tip-dashboard-consumer"],
        help="Check profile compliance",
    )
    parser.add_argument(
        "--capabilities",
        help="Comma-separated capability labels (for --profile)",
    )
    parser.add_argument(
        "--manifest",
        help="Path to manifest JSON (for --profile, optional cross-check)",
    )
    parser.add_argument(
        "--wire",
        choices=["request", "response"],
        help="Validate a header dict for a wire request or response",
    )
    parser.add_argument(
        "--input",
        help="Path to input JSON file; defaults to stdin",
    )

    args = parser.parse_args(argv)

    modes_set = sum(
        1 for x in (args.schema, args.profile, args.wire) if x is not None
    )
    if modes_set != 1:
        parser.error("Exactly one of --schema, --profile, --wire must be given")
        return 2

    if args.input:
        try:
            with open(args.input, encoding="utf-8") as f:
                document = json.load(f)
        except FileNotFoundError:
            print(f"error: input file not found: {args.input}", file=sys.stderr)
            return 2
        except json.JSONDecodeError as exc:
            print(f"error: input is not valid JSON: {exc}", file=sys.stderr)
            return 2
    elif args.schema or args.wire:
        try:
            document = json.load(sys.stdin)
        except json.JSONDecodeError as exc:
            print(f"error: stdin is not valid JSON: {exc}", file=sys.stderr)
            return 2
    else:
        document = None  # --profile may not need a document

    if args.schema:
        result = validate_against(args.schema, document)

    elif args.wire:
        if not isinstance(document, dict):
            print("error: --wire expects a JSON object (header dict)", file=sys.stderr)
            return 2
        result = validate_wire_headers(document, direction=args.wire)

    else:  # --profile
        if not args.capabilities:
            parser.error("--profile requires --capabilities")
            return 2
        caps = [c.strip() for c in args.capabilities.split(",") if c.strip()]
        manifest = None
        if args.manifest:
            try:
                with open(args.manifest, encoding="utf-8") as f:
                    manifest = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError) as exc:
                print(f"error: --manifest: {exc}", file=sys.stderr)
                return 2
        result = validate_profile(args.profile, capabilities=caps, manifest=manifest)

    _print_result(result)
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
