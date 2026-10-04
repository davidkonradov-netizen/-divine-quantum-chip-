#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/../src/hemisphere"

echo "== Ejecutando test_roles.py =="
python test_roles.py