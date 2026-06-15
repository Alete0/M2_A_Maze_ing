# Ejecuta la auditoría completa (Windows)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "No existe audit/.venv. Ejecuta primero: .\setup.ps1" -ForegroundColor Yellow
    exit 1
}

.\.venv\Scripts\python.exe run_audit.py
Write-Host ""
Write-Host "Informes en: audit\reports\"
Write-Host "Resumen:    audit\reports\Fase9_consolidate.md"
