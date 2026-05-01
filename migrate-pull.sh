#!/bin/sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON_BIN="${VIRTUAL_ENV:+$VIRTUAL_ENV/bin/python}"

if [ -z "$PYTHON_BIN" ] || [ ! -x "$PYTHON_BIN" ]; then
  PYTHON_BIN="$SCRIPT_DIR/.venv/bin/python"
fi

if [ ! -x "$PYTHON_BIN" ]; then
  echo "Python interpreter not found. Activate a virtualenv or create $SCRIPT_DIR/.venv." >&2
  exit 1
fi

ALEMBIC_BIN="$SCRIPT_DIR/.venv/bin/alembic"

if [ ! -f "$ALEMBIC_BIN" ]; then
  echo "Alembic executable not found at $ALEMBIC_BIN. Install dependencies first." >&2
  exit 1
fi

TIMESTAMP=$(date +"%Y%d%m%H%M%S")

"$PYTHON_BIN" "$ALEMBIC_BIN" upgrade head

echo "Migration pulled successfully at $TIMESTAMP"
