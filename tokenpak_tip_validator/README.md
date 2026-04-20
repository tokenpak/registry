# tokenpak-tip-validator

Conformance validator for the **TokenPak Integration Protocol (TIP-1.0)**.

Install:

```bash
pip install tokenpak-tip-validator
```

## Use

**Validate a manifest:**

```bash
python -m tokenpak_tip_validator --schema adapter --input my-manifest.json
```

**Check profile compliance:**

```bash
python -m tokenpak_tip_validator \
    --profile tip-proxy \
    --capabilities "tip.compression.v1,tip.cache.provider-observer,tip.telemetry.wire-side"
```

**Validate wire headers:**

```bash
python -m tokenpak_tip_validator --wire response --input captured-headers.json
```

## Library API

```python
from tokenpak_tip_validator import (
    validate_against, validate_profile,
    validate_wire_headers, validate_capability_set,
)

result = validate_against("adapter", my_manifest)
if result.ok:
    print("PASS")
else:
    for f in result.errors():
        print(f"FAIL {f.code}: {f.message}")
```

Every validator returns a `ValidationResult` with `ok: bool` and a
list of `Finding` records (severity + code + message + path).

## Schemas

Six TIP schemas:

- `headers` — wire headers
- `metadata` — request/response metadata
- `telemetry-event` — telemetry store rows
- `error` — canonical error envelope
- `capabilities` — capability label catalog
- `compatibility` — version ranges + peer requirements

Four manifest schemas:

- `adapter`, `plugin`, `provider-profile`, `client-profile`

## Profiles

Five TIP-1.0 profiles:

- `tip-proxy`
- `tip-companion`
- `tip-adapter`
- `tip-plugin`
- `tip-dashboard-consumer`

Profile requirement tables: https://tokenpak.ai/protocol/profiles

## Docs

- Protocol spec: https://tokenpak.ai/protocol
- Conformance guide: https://tokenpak.ai/protocol/conformance
- TIP-1.0 schemas: https://github.com/tokenpak/registry

## License

Apache 2.0
