## Fase0_bootstrap
### Estado: PASS
### Comandos ejecutados
```bash
# Linux / 42
cd audit && ./setup.sh

# Windows
cd audit && .\setup.ps1
```
### Evidencia
- Python >= 3.10 requerido
- Venv local: `audit/.venv/` (no commitear)
- Instala: flake8, mypy, build, mazegen editable (`pip install -e ..`)
- Imports `MazeGenerator`, `MazeSolver` OK
### Hallazgos
- Ninguno
### Requisitos del subject cubiertos / no cubiertos
III.1 Python >= 3.10 — PASS. Ver `audit/README.md` para instrucciones completas.
