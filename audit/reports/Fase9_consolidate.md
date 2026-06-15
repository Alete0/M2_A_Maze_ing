# Informe final de auditoría — A-Maze-ing

## Resumen ejecutivo

**Veredicto: NO APTO para evaluación** hasta corregir al menos los hallazgos CRITICOS/ALTAS del subject.

Entorno de auditoría: venv en `audit/.venv`. Evaluación objetivo: **Linux 42**. Los crashes por `UnicodeEncodeError` en `print_maze` (carácter █) son específicos de consola cp1252; en Linux UTF-8 probablemente no reproducen.

## Matriz de cumplimiento

| Requisito | Estado | Referencia |
|-----------|--------|------------|
| Python >= 3.10 | **PASS** | Fase0 |
| flake8 (fuentes proyecto) | **PASS** | Fase1 |
| mypy (flags subject) | **FAIL** | Fase1 — setup_new_maze sin return type |
| No crash / try-except | **FAIL** | Fase5 S4 — get_directions sin camino |
| python3 a_maze_ing.py config | **PASS** | Fase6 — output generado antes del menú |
| Config KEY=VALUE + validación | **PASS** | Fase2 |
| Generación aleatoria + SEED | **PASS** | Fase4 |
| Muros coherentes (validador) | **PASS** | Fase6 — 10/10 output_validator |
| Conectividad total (excepto 42) | **PASS** | Fase4 — 0 aislados en 20x15 |
| Bordes externos cerrados | **PASS** | Fase4 |
| Sin áreas 3×3 / densidad M5 | **FAIL** | Fase4 G5b — no implementado |
| Patrón 42 visible | **PASS** | Fase4 |
| Fallback 42 maze pequeño + mensaje | **FAIL** | Fase4 G6 |
| PERFECT = spanning tree | **PASS** | Fase4 — tras fix conteo aristas |
| OUTPUT hex + metadatos + \n | **PASS** | Fase5/Fase6 |
| Render ASCII + 4 interacciones | **PASS** | Fase7 — Linux; WARN Windows cp1252 |
| mazegen pip package .whl+.tar.gz | **PASS** | Fase8 |
| config.txt en repo (nombre) | **WARN** | usa config_maze.txt |
| README / Makefile completos | **WARN** | fuera alcance |
| ALGORITHM config usado | **FAIL** | parseado pero ignorado |
| Regenerar reescribe OUTPUT_FILE | **FAIL** | Fase7 U3 — opción 1 no llama encoder |

## Hallazgos CRITICA / ALTA (prioridad defensa)

| ID | Sev | Descripción | Ubicación |
|----|-----|-------------|-----------|
| G6 | CRITICA | Laberinto pequeño sin patrón 42: no imprime mensaje de error en consola | `generator.py:210-212` |
| G5b | ALTA | Restricción de densidad (corredores ≤2, no 3×3) no implementada | `generator.py` |
| S4 | CRITICA | Sin camino: `get_directions()` lanza Exception → crash en CLI | `solver.py:136`, `a_maze_ing.py:167` |
| G9 | ALTA | Segunda `generate()` en misma instancia desplaza patrón 42 | `generator.py:218-219` |
| L2 | ALTA | mypy falla: `setup_new_maze` sin anotación de retorno | `a_maze_ing.py:141` |
| ALG | ALTA | Clave `ALGORITHM` parseada pero nunca usada | `parser.py` / `generator.py` |
| U3 | ALTA | Regenerar (opción 1) no reescribe OUTPUT_FILE | `a_maze_ing.py:220-223` |

## Hallazgos MEDIA / BAJA

| ID | Sev | Descripción |
|----|-----|-------------|
| L3 | MEDIA | `load_config` sin docstring PEP257 |
| U2w | MEDIA | `print_maze` con Unicode en Windows cp1252 (no aplica Linux) |
| CFG | BAJA | Config por defecto: `config_maze.txt` vs `config.txt` del subject |
| DOC | BAJA | README/Makefile incompletos (fuera de alcance) |

## Qué sí funciona bien

- Parser robusto (9 casos P1–P8 PASS).
- Determinismo con SEED verificado.
- `output_validator.py` pasa en 10 configs (PERFECT True/False).
- Patrón 42 con celdas `F` en laberinto 12×12.
- Conectividad desde entry: 0 celdas aisladas en prueba 20×15.
- Build `mazegen-0.1.0.whl` + `.tar.gz` e import API OK.
- Coherencia bitmask hex y coords en OUTPUT_FILE.

## Informes por fase

- [Fase0_bootstrap](Fase0_bootstrap.md)
- [Fase1_lint](Fase1_lint.md)
- [Fase2_parser](Fase2_parser.md)
- [Fase3_coords](Fase3_coords.md)
- [Fase4_generator](Fase4_generator.md)
- [Fase5_solver](Fase5_solver.md)
- [Fase6_output](Fase6_output.md)
- [Fase7_cli](Fase7_cli.md)
- [Fase8_packaging](Fase8_packaging.md)

## Anexo — configs de prueba

Ubicación: `audit/configs/` (P1–P8, seed_1..seed_10).
Outputs: `audit/outputs/maze_*.txt`.
Re-ejecutar: ver `audit/README.md` (sección Ejecución).
