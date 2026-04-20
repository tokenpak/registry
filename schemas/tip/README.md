# TIP-1.0 Schemas

Machine-readable JSON schemas for the TokenPak Integration Protocol.
Normative text for each schema lives in the docs repo at
[`docs/protocol/`](https://github.com/tokenpak/docs/tree/main/docs/protocol).

## Schemas

| File | Covers |
|---|---|
| `headers.schema.json` | Canonical `X-TokenPak-*` wire headers. |
| `metadata.schema.json` | Request/response metadata fields. |
| `telemetry-event.schema.json` | One row per request in the telemetry store. |
| `error.schema.json` | Canonical TIP error envelope. |
| `capabilities.schema.json` | Authoritative capability label set. |
| `compatibility.schema.json` | Version range + profile compatibility rules. |

Manifest schemas live in a sibling directory: `schemas/manifests/`.

## Versioning

Schemas are versioned with the TIP spec. `TIP-1.0` schemas live at this path;
future `TIP-1.1` or `TIP-2.0` schemas will live under versioned subdirectories
once the need arises.

## Status

**Phase 1 stubs — 2026-04-20.** Each schema below is a minimal
`$id` + `title` + `$schema` declaration. Normative field sets land in Phase 3
of the TIP rollout (see `D2` in the TokenPak Architecture Standard §10).
