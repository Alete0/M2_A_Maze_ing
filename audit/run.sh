#!/usr/bin/env bash
# Ejecuta la auditoría completa (Linux / 42)
set -euo pipefail
cd "$(dirname "$0")"

if [[ ! -x .venv/bin/python ]]; then
  echo "No existe audit/.venv. Ejecuta primero: ./setup.sh"
  exit 1
fi

export PYTHONIOENCODING=utf-8
.venv/bin/python run_audit.py

echo ""
echo "Informes en: audit/reports/"
echo "Resumen:    audit/reports/Fase9_consolidate.md"
