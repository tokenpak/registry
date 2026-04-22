# Changelog

All notable changes to this repo are recorded here. Covers both the `tokenpak-tip-validator` Python package and the registry's published schemas.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). The Python package follows [Semantic Versioning](https://semver.org/); schemas follow the TIP-1.0 version-shape rule from `01-architecture-standard.md §11.7` (`-v<MAJOR>` only in `$id`).

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

- **`registry.json` `$schema` field** — the reference pointed at `https://tokenpak.ai/schemas/registry-v1.json`, which never existed as a real schema file. Per `2026-04-22-schema-id-url-rollout.md` and Kevin's constraint (no invented canonical artifacts), the dangling reference has been removed rather than silently repointed. A proper registry-index schema will be introduced via a separate follow-up proposal (tracked: `2026-04-22-registry-index-schema-followup.md` in the tokenpak vault). Until then, `registry.json` declares no schema conformance — consistent with its actual current state.

### Governance

- `01-architecture-standard.md §11.7` is now the authoritative source for schema `$id` URL form. Future schemas in this repo MUST follow it; drift is caught (for now) by a manual grep against tracked `$id`s. A CI regex gate is proposed in §11.7 future-drift-prevention.

## [0.1.0] — pre-2026-04-22

Initial release of the `tokenpak-tip-validator` conformance package and its underlying TIP-1.0 + manifest schema set. See git log for detail.
