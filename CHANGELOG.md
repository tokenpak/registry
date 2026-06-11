# Changelog

All notable changes to this repo are recorded here. Covers both the `tokenpak-tip-validator` Python package and the registry's published schemas.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). The Python package follows [Semantic Versioning](https://semver.org/); schemas follow the TIP-1.0 version-shape rule from `01-architecture-standard.md §11.7` (`-v<MAJOR>` only in `$id`).

## [Unreleased] — Provider-Native Compatibility Foundation: reasoning usage

### Added

- **`schemas/tip/reasoning-usage-v1.schema.json`** — Normalized reasoning-usage object. Captures visible_output_tokens / reasoning_tokens / total_output_tokens / total_billable_tokens / reasoning_effort split for reasoning models (Anthropic extended thinking, OpenAI o-series, Gemini thinking, future providers). Parsing is dispatched dynamically from a per-provider registry in `tokenpak/services/providers/<provider>/usage_parser.py`; provider names MUST NOT be hardcoded. `$id`: `https://docs.tokenpak.ai/schemas/tip/reasoning-usage-v1.json`.

### Changed

- **`schemas/tip/telemetry-event.schema.json`** — Additively extended with five optional reasoning-usage fields: `reasoning_tokens`, `visible_output_tokens`, `total_billable_tokens`, `reasoning_effort`, `reasoning_usage_source`. Existing required fields unchanged. Receivers that don't recognize the new fields ignore them.

### Notes

- TIP version impact: **none**. Both additions are fully additive within TIP-1.x.
- OSS-side parser registry + monitor.db migration land in the `tokenpak` package.
- Raw provider usage objects MUST NOT be persisted inline in telemetry — `provider_usage_ref` carries an opaque sha256-12-char-prefix hash only. Privacy posture defers to the persistence-path audit.
- Hard-cap consumption (reasoning-aware Spend Guard) is deferred to a follow-up Pro-runtime packet per the foundation-vs-runtime distinction rule.

## [Unreleased] — MultiPak Pro registry artifacts

### Added

- **`schemas/tip/pak-v1.schema.json`** — Pak schema (Portable AI Knowledge bundle). 5 canonical subtypes (`vault`, `interaction`, `decision`, `recall`, `handoff`) per the MultiPak specification. Mirrors the OSS dataclass at `tokenpak.tip.pak.Pak`. `$id`: `https://docs.tokenpak.ai/schemas/tip/pak-v1.json`.
- **`schemas/tip/context-package-v1.schema.json`** — Context Package schema. 6 delivery levels (`no_memory`–`full_restore`), 6 coverage states, embedded `PolicyDecision` per the MultiPak specification. Mirrors `tokenpak.tip.context_package.ContextPackage`. `$id`: `https://docs.tokenpak.ai/schemas/tip/context-package-v1.json`.
- **`capability-catalog.json`** — 10 new capability labels:
  - `tip.pak.capture`, `tip.pak.index`, `tip.pak.recall`, `tip.pak.hydrate`, `tip.pak.promote`
  - `tip.context.package`, `tip.context.handoff`, `tip.context.resume`, `tip.context.coverage`, `tip.context.policy`
  - All 10 declare profile `tip-paid-local-daemon` (Pro daemon `provider_kind: paid-local-daemon`).
- **`schemas/tip/capabilities.schema.json`** — extended the `profiles` enum with `tip-paid-local-daemon`.

### Notes

- TIP version impact: **none**. Capability addition is fully additive within TIP-1.x ("Capability codes" row). Receivers that don't recognize the new capabilities ignore them.
- OSS-side dataclasses + tests landed in the `tokenpak` package.
- License-validation egress contract: Pak content / Context Package content / hydration events MUST NOT cross the `license.tokenpak.ai` boundary. The structural disjointness check lives in the OSS-side test suite (`tests/tip/test_multipak_contracts.py::TestPrivacyContract`); the runtime enforcement lives in the closed-source Pro daemon.

## [0.1.1] — 2026-04-22

### Changed

- **Schema `$id` URLs migrated from apex to `docs.tokenpak.ai`** per the canonical form fixed by `01-architecture-standard.md §11.7`:
  - All 7 schemas under `schemas/tip/` rewrote their `$id` from `https://tokenpak.ai/schemas/tip/<name>-v1.json` to `https://docs.tokenpak.ai/schemas/tip/<name>-v1.json`.
  - All 4 schemas under `schemas/manifests/` rewrote their `$id` from `https://tokenpak.ai/schemas/manifests/<name>-v1.json` to `https://docs.tokenpak.ai/schemas/manifests/<name>-v1.json`.
  - Cross-schema `$ref`s (four manifest schemas pointing at `schemas/tip/compatibility-v1.json`) updated to match.
  - Every inline protocol URL inside schema `description` strings rewrote `tokenpak.ai/protocol/*` → `docs.tokenpak.ai/protocol/*`.
- **`tokenpak_tip_validator/schema.py` docstring** updated to reference the new `docs.tokenpak.ai/schemas/...` URL pattern. The `_build_registry()` function reads `$id` dynamically from each schema file, so no code-level URL change was needed.
- **Top-level documentation links** (`README.md`, `pyproject.toml` `Documentation` field, `tokenpak_tip_validator/README.md`) rewritten to the docs subdomain.

### Breaking

- The `$id` change is technically a compatibility break for any JSON Schema validator that caches schemas by `$id`. Known consumer footprint at time of release is limited to `tokenpak` itself plus `tokenpak_tip_validator` (both internally consistent after this release). External consumers pinning to the 0.1.0 URLs will need to refetch against the 0.1.1 `$id`s.

### Removed

- **`registry.json` `$schema` field** — the reference pointed at `https://tokenpak.ai/schemas/registry-v1.json`, which never existed as a real schema file. Per the schema-id URL policy (no invented canonical artifacts), the dangling reference has been removed rather than silently repointed. A proper registry-index schema will be introduced via a separate follow-up proposal. Until then, `registry.json` declares no schema conformance — consistent with its actual current state.

### Governance

- `01-architecture-standard.md §11.7` is now the authoritative source for schema `$id` URL form. Future schemas in this repo MUST follow it; drift is caught (for now) by a manual grep against tracked `$id`s. A CI regex gate is proposed in §11.7 future-drift-prevention.

## [0.1.0] — pre-2026-04-22

Initial release of the `tokenpak-tip-validator` conformance package and its underlying TIP-1.0 + manifest schema set. See git log for detail.
