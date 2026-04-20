# TIP-1.0 Conformance Test Vectors

JSON fixtures consumed by `tokenpak_tip_validator` to prove TIP-1.0
conformance for a component (TokenPak reference implementation or a
third-party implementation).

## Layout

```
test_vectors/
├── headers/            — header-correctness vectors
├── manifests/          — manifest-correctness vectors (4 manifest kinds)
├── telemetry/          — telemetry-event-correctness vectors
├── capabilities/       — capability-set-correctness vectors
├── compatibility/      — compatibility-labeling vectors
└── golden/             — end-to-end per-profile scenarios
```

Each fixture is a JSON file with frontmatter in a top-level
`_meta` object:

```json
{
  "_meta": {
    "expect": "pass" | "fail",
    "schema": "adapter",
    "area": "manifest",
    "description": "human-readable scenario"
  },
  "_data": { ... the actual document under test ... }
}
```

## Running

```bash
# Validate one fixture
jq '._data' test_vectors/manifests/valid-claude-code-adapter.json \
  | python -m tokenpak_tip_validator --schema adapter

# Run the full suite (pytest)
pytest tests/test_conformance_suite.py
```
