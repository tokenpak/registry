# TIP-1.0 Manifest Schemas

JSON schemas for the four manifest kinds defined by TIP-1.0:

- `adapter.schema.json` — per-client adapters (Claude Code, Cursor, etc.).
- `plugin.schema.json` — optional TokenPak plugins.
- `provider-profile.schema.json` — per-provider outbound profiles.
- `client-profile.schema.json` — per-client inbound profiles (CLI/TUI/API/etc.).

## Status

**Phase 1 stub — 2026-04-20.** Schemas below are minimal placeholders.
Normative field sets land in Phase 3 (see `D2` in the TokenPak Architecture
Standard §10).

## Reference loader

`tokenpak/core/contracts/manifests.py` resolves these schemas at runtime
and validates incoming manifests against them.
