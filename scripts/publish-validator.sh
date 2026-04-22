#!/usr/bin/env bash
# publish-validator.sh — build + upload tokenpak-tip-validator to TestPyPI / PyPI
#
# Used by Initiative 2 task packets TV-02 (TestPyPI dry-run) and TV-03 (PyPI
# publish, gated on DECISION-P4-PUBLISH).
#
# Tokens source: /home/sue/.openclaw/.env (chmod 600; outside git)
# Pointer doc:   ~/vault/02_COMMAND_CENTER/private/validator-pypi-credentials-pointer.md
#
# Usage:
#   bash scripts/publish-validator.sh --testpypi   # TV-02 rehearsal
#   bash scripts/publish-validator.sh --pypi       # TV-03 production publish
#
# Safety:
#   - DOES NOT echo token values
#   - DOES NOT commit any .pypirc to git
#   - TestPyPI is always an acceptable rehearsal; PyPI upload is irreversible
#
# Exit codes:
#   0 — upload succeeded + install-smoke green
#   1 — build failed
#   2 — token env var missing
#   3 — upload failed
#   4 — install-smoke failed

set -euo pipefail

ENV_FILE="${TOKENPAK_PYPI_ENV:-/home/sue/.openclaw/.env}"
REGISTRY_ROOT="${REGISTRY_ROOT:-/home/sue/registry}"

MODE=""
while [ $# -gt 0 ]; do
  case "$1" in
    --testpypi) MODE=testpypi; shift ;;
    --pypi)     MODE=pypi; shift ;;
    *)          echo "unknown arg: $1" >&2; exit 1 ;;
  esac
done

if [ -z "$MODE" ]; then
  echo "error: specify --testpypi or --pypi" >&2
  exit 1
fi

# ---- Source credentials (tolerant of non-KEY=VALUE lines) ----
if [ ! -f "$ENV_FILE" ]; then
  echo "error: credentials file not found at $ENV_FILE" >&2
  echo "see ~/vault/02_COMMAND_CENTER/private/validator-pypi-credentials-pointer.md" >&2
  exit 2
fi
# Extract KEY=VALUE lines only; skip comments, bare words, blanks.
# Evaluates under `set -a` so exports are automatic; never echoes values.
while IFS= read -r line; do
  # Skip comments + blanks + lines without = or with invalid key shape
  case "$line" in
    ''|'#'*) continue ;;
  esac
  [[ "$line" =~ ^[A-Za-z_][A-Za-z0-9_]*= ]] || continue
  export "${line?}"
done < "$ENV_FILE"

if [ "$MODE" = "testpypi" ]; then
  TOKEN_VAR="TEST_PYPI"
  REPO_FLAG="--repository-url https://test.pypi.org/legacy/"
  # TestPyPI doesn't mirror all deps (jsonschema, referencing, ...);
  # fall back to production PyPI for transitive installs.
  INSTALL_INDEX="--index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/"
else
  TOKEN_VAR="PYPI_TIP_VALIDATOR"
  REPO_FLAG=""
  INSTALL_INDEX=""
fi

if [ -z "${!TOKEN_VAR:-}" ]; then
  echo "error: $TOKEN_VAR not set in $ENV_FILE" >&2
  exit 2
fi

# ---- Build ----
cd "$REGISTRY_ROOT"
rm -rf dist/
echo "[publish-validator] building $MODE artifacts..."
python3 -m build || { echo "error: build failed" >&2; exit 1; }
ls -la dist/

# ---- Upload ----
echo "[publish-validator] uploading to $MODE..."
# shellcheck disable=SC2086
python3 -m twine upload \
  $REPO_FLAG \
  --username __token__ \
  --password "${!TOKEN_VAR}" \
  --non-interactive \
  dist/* \
  || { echo "error: upload failed" >&2; exit 3; }

# ---- Install smoke ----
SMOKE_VENV="/tmp/tip-validator-smoke-$$"
echo "[publish-validator] install-smoke from fresh venv..."
python3 -m venv "$SMOKE_VENV"
# shellcheck disable=SC2086
"$SMOKE_VENV/bin/pip" install $INSTALL_INDEX tokenpak-tip-validator==0.1.0 \
  || { echo "error: install failed" >&2; rm -rf "$SMOKE_VENV"; exit 4; }

# Try CLI against a golden case
GOLDEN="$REGISTRY_ROOT/test_vectors/golden/tip-proxy.json"
if [ -f "$GOLDEN" ]; then
  "$SMOKE_VENV/bin/python" -m tokenpak_tip_validator --profile tip-proxy "$GOLDEN" \
    || { echo "error: CLI golden-case smoke failed" >&2; rm -rf "$SMOKE_VENV"; exit 4; }
fi

rm -rf "$SMOKE_VENV"

echo "[publish-validator] $MODE upload + smoke: PASS"
