# Prepara el entorno de auditoría (Windows / PowerShell)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "==> Creando venv en audit/.venv"
python -m venv .venv

Write-Host "==> Instalando herramientas"
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\pip.exe install flake8 mypy build
.\.venv\Scripts\pip.exe install -e ..

Write-Host "==> Verificando imports del proyecto"
.\.venv\Scripts\python.exe -c "from mazegen import MazeGenerator, MazeSolver; print('OK')"

Write-Host ""
Write-Host "Listo. Ejecuta la auditoría con: .\run.ps1"
