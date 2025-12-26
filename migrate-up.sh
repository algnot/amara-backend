#!/bin/bash

set -e

TIMESTAMP=$(date +"%Y%d%m%H%M%S")

python -m alembic upgrade head
python -m alembic revision --autogenerate -m "migrate-$TIMESTAMP"
python -m alembic upgrade head

echo "Migration applied successfully at $TIMESTAMP"
