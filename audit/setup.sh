#!/usr/bin/env bash
# Prepara el entorno de auditoría (Linux / macOS / 42)
set -euo pipefail
cd "$(dirname "$0")"

echo "==> Creando venv en audit/.venv"
python3 -m venv .venv

echo "==> Instalando herramientas"
.venv/bin/pip install --upgrade pip
.venv/bin/pip install flake8 mypy build
.venv/bin/pip install -e ..

echo "==> Verificando imports del proyecto"
.venv/bin/python -c "from mazegen import MazeGenerator, MazeSolver; print('OK')"

echo ""
echo "Listo. Ejecuta la auditoría con: ./run.sh"
