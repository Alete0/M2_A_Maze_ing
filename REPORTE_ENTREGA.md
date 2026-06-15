# REPORTE DE ENTREGA — A-Maze-ing

> Auditoría de cumplimiento contra `en.subject.pdf` v2.1  
> Fecha: 15/06/2026  
> Equipo: alejandr, czuluaga  
> Referencia normativa: Capítulos III–IX del subject

---

## Resumen ejecutivo

| Área | Cumplimiento | Comentario breve |
|------|--------------|------------------|
| III — Common Instructions | **PARCIAL** | Código de producción OK; `make lint` falla en `tests/` |
| IV — Mandatory part | **PARCIAL** | Núcleo funcional sólido; falta `config.txt` por defecto |
| V — Visual representation | **PARCIAL** | Menú completo; regenerar no actualiza `OUTPUT_FILE` |
| VI — Reusability | **PARCIAL** | Paquete buildable; `.whl` no está en raíz del repo |
| VII — README | **NO CUMPLE** | Faltan Resources (IA) y gestión de equipo |
| VIII — Bonuses | **NO APLICA** | Sin bonus implementado |
| IX — Submission | **PARCIAL** | Listo con correcciones pendientes |

**Veredicto global:** el motor del laberinto, el formato de salida y la visualización cumplen los requisitos funcionales principales. Los riesgos de evaluación se concentran en **documentación (README)**, **convención de nombres (`config.txt`)**, **ubicación del wheel**, **lint sobre todo el proyecto** y **robustez del CLI**.

---

## Resultados de verificación ejecutada

Comandos ejecutados en el entorno local (Windows, Python 3.13.11):

| Comando | Resultado | Detalle |
|---------|-----------|---------|
| `python -m flake8 a_maze_ing.py parser.py encoder.py mazegen/` | **OK (0)** | Sin errores en código de producción |
| `python -m flake8 .` | **FALLO (18 errores)** | Solo en `tests/` (E501, F401) |
| `python -m mypy a_maze_ing.py parser.py encoder.py mazegen/ …` | **OK (0)** | 6 archivos fuente |
| `python -m mypy . …` (flags del subject) | **FALLO (76 errores)** | Tests sin type hints |
| `python -m pytest tests/ -v` | **OK (117/117)** | Todos pasan en ~1 s |
| `python output_validator.py maze.txt` | **OK (exit 0)** | Coherencia hex del output actual |
| `python -m build` | **OK** | `dist/mazegen-0.1.0-py3-none-any.whl` + `.tar.gz` |
| `pip install dist/mazegen-…whl` + import | **OK** | `MazeGenerator` / `MazeSolver` importables |
| `mazegen-*.whl` en raíz del repo | **AUSENTE** | Solo en `dist/` (gitignored) |
| `config.txt` en raíz | **AUSENTE** | Solo `config_maze.txt` |

> **Nota:** `make` y `python3` no están disponibles en el PATH de Windows del entorno de prueba; los equivalentes `python -m …` producen el mismo resultado que las reglas del `Makefile`.

---

## Capítulo III — Common Instructions

### III.1 — General Rules

#### III.1.1 — Python >= 3.10

- **Estado:** CUMPLE
- **Módulo:** `pyproject.toml`
- **Evidencia:** `requires-python = ">=3.10"`; entorno verificado con Python 3.13.11.
- **Observaciones:** Compatible con el requisito.

#### III.1.2 — flake8

- **Estado:** PARCIAL
- **Módulo:** Todo el proyecto
- **Evidencia:**
  - Producción (`a_maze_ing.py`, `parser.py`, `encoder.py`, `mazegen/`): **0 errores**
  - `flake8 .` (como exige el subject): **18 errores** en `tests/` (líneas largas E501, imports sin usar F401)
- **Acción recomendada:** Corregir estilo en tests o añadir configuración flake8 que excluya `tests/` **solo si** el evaluador lo permite; lo seguro es arreglar los tests.

#### III.1.3 — mypy (flags obligatorios)

- **Estado:** PARCIAL
- **Módulo:** Todo el proyecto
- **Evidencia:**
  - Código de producción: **Success: no issues found in 6 source files**
  - `mypy .` con flags del subject: **76 errores** en `tests/` (`no-untyped-def` en funciones de test)
- **Acción recomendada:** Añadir anotaciones de tipo en tests o configurar `mypy` para excluir `tests/` en `pyproject.toml` — el subject pide `mypy .` sin exclusiones explícitas.

#### III.1.4 — Type hints

- **Estado:** CUMPLE (producción) / PARCIAL (proyecto completo)
- **Evidencia por módulo:**

| Archivo | Type hints | Notas |
|---------|------------|-------|
| `a_maze_ing.py` | CUMPLE | Parámetros y retornos en todas las funciones |
| `parser.py` | CUMPLE | `MazeConfig` dataclass, `load_config` tipado |
| `encoder.py` | CUMPLE | `Grid`, `Coord`, firmas completas |
| `mazegen/generator.py` | CUMPLE | Clase y métodos tipados |
| `mazegen/solver.py` | CUMPLE | Clase y métodos tipados |
| `mazegen/__init__.py` | CUMPLE | Reexportaciones |
| `tests/*` | NO CUMPLE | Sin anotaciones en funciones de test |

#### III.1.5 — Docstrings PEP 257

- **Estado:** PARCIAL
- **Evidencia por módulo:**

| Archivo | Docstrings | Detalle |
|---------|------------|---------|
| `a_maze_ing.py` | CUMPLE | `path_to_exit`, `print_maze`, `setup_new_maze` documentadas |
| `parser.py` | CUMPLE | `load_config` con Args/Returns/Raises |
| `encoder.py` | **NO CUMPLE** | `line_to_hex` y `gen_maze_file` sin docstring |
| `mazegen/generator.py` | PARCIAL | Mayoría OK; typo en docstring de `generate` (`start` en vez de `entry`) |
| `mazegen/solver.py` | PARCIAL | `solve()` sin docstring; otros métodos sí |
| `mazegen/__init__.py` | PARCIAL | Sin docstring de módulo |

- **Acción recomendada:** Añadir docstrings en `encoder.py` y `MazeSolver.solve()`.

#### III.1.6 — Manejo de excepciones (nunca crash inesperado)

- **Estado:** PARCIAL
- **Evidencia:**
  - `parser.py` L48-68, L135-138: errores de fichero y validación → mensaje stderr + `sys.exit(1)` ✅
  - `encoder.py` L30-32: error de escritura capturado ✅
  - `mazegen/generator.py` L247-249: `except Exception` genérico imprime y `exit(1)` ⚠️
  - `mazegen/solver.py` L135-136: sin camino → `raise Exception("No solutions…")` sin mensaje al usuario ⚠️
  - `a_maze_ing.py` L175-236: `__main__` sin `try/except` global; excepciones del solver pueden crashear ⚠️
- **Acción recomendada:** Envolver `setup_new_maze` en `try/except` en el CLI; convertir "sin camino" en mensaje stderr.

#### III.1.7 — Context managers para recursos

- **Estado:** CUMPLE
- **Evidencia:** `parser.py` L49 (`with open`), `encoder.py` L20 (`with open`).

---

### III.2 — Makefile

#### III.2.1 — Regla `install`

- **Estado:** CUMPLE
- **Evidencia:** `Makefile` L7-8 → `pip install -e ".[dev]"`

#### III.2.2 — Regla `run`

- **Estado:** PARCIAL
- **Evidencia:** `Makefile` L13-14 ejecuta `a_maze_ing.py config_maze.txt`
- **Observaciones:** Funciona, pero el subject (IV.3) exige un `config.txt` por defecto en el repo, no `config_maze.txt`.

#### III.2.3 — Regla `debug`

- **Estado:** CUMPLE
- **Evidencia:** `Makefile` L16-17 → `python -m pdb a_maze_ing.py config_maze.txt`

#### III.2.4 — Regla `clean`

- **Estado:** CUMPLE
- **Evidencia:** `Makefile` L19-22 → borra `__pycache__`, `.mypy_cache`, `build/`, `dist/`, `*.egg-info/`

#### III.2.5 — Regla `lint`

- **Estado:** PARCIAL (definición correcta, ejecución falla)
- **Evidencia:** `Makefile` L24-26 con flags mypy exactos del subject
- **Observaciones:** La regla está bien escrita; al ejecutarla falla por `tests/`.

#### III.2.6 — Regla `lint-strict` (opcional)

- **Estado:** CUMPLE
- **Evidencia:** `Makefile` L28-30 → `mypy . --strict`

#### III.2.7 — Regla extra `test`

- **Estado:** EXTRA (no obligatoria)
- **Evidencia:** `Makefile` L10-11 → pytest; recomendado por III.3.

#### III.2.8 — Regla extra `build`

- **Estado:** EXTRA (útil para VI)
- **Evidencia:** `Makefile` L32-33 → `python -m build` tras `clean`

---

### III.3 — Additional Guidelines

#### III.3.1 — Tests locales

- **Estado:** CUMPLE (recomendación)
- **Evidencia:** `tests/` con 117 tests en 7 archivos; cobertura de parser, encoder, generator, solver, CLI e integración.
- **Observaciones:** No se evalúan en la entrega, pero protegen la defensa.

#### III.3.2 — `.gitignore`

- **Estado:** PARCIAL
- **Evidencia:** `.gitignore` contiene `__pycache__`, `.mypy_cache`, `maze.txt`, `output_validator.py`, `dist/*`
- **Observaciones:** No lista explícitamente `.venv/`, `*.egg-info/`, `.pytest_cache/` (aunque `clean` del Makefile sí los borra parcialmente).

#### III.3.3 — Entorno virtual

- **Estado:** CUMPLE (recomendación)
- **Evidencia:** `make install` con extras dev; verificación de wheel en venv temporal exitosa.

---

## Capítulo IV — Mandatory part

### IV.1 — Summary

- **Estado:** CUMPLE
- **Flujo implementado:**

```
config_maze.txt → parser.py (MazeConfig)
                      ↓
              a_maze_ing.py
                      ↓
         mazegen/generator.py + mazegen/solver.py
                      ↓
              encoder.py → OUTPUT_FILE (hex)
                      ↓
              print_maze + menú interactivo
```

- **Observaciones:** Arquitectura modular alineada con el subject. El encoder y el parser están fuera de `mazegen/` (válido: el formato de salida puede diferir del formato interno).

---

### IV.2 — Usage

#### IV.2.1 — Nombre del fichero principal

- **Estado:** CUMPLE
- **Evidencia:** `a_maze_ing.py` existe en la raíz del repo.

#### IV.2.2 — Comando de ejecución

- **Estado:** CUMPLE
- **Evidencia:** `a_maze_ing.py` L178-180 valida `len(sys.argv) == 2`; uso: `python3 a_maze_ing.py <config_file>`.
- **Test:** `test_cli_no_arguments`, `test_cli_valid_config_writes_output`.

#### IV.2.3 — Manejo de errores

- **Estado:** PARCIAL
- **Evidencia:**
  - Config inválida / fichero no encontrado: gestionado en `parser.py` ✅
  - Parámetros imposibles (ENTRY en patrón 42): `generator.py` L238-241 → mensaje + exit ✅
  - Laberinto sin solución: `solver.py` lanza excepción no capturada en CLI ⚠️
  - Entrada de menú inválida: mensaje amigable L235-236 ✅

- **Acción recomendada:** `try/except` en `__main__` alrededor de `setup_new_maze`.

---

### IV.3 — Configuration file format

**Módulo:** `parser.py`, `config_maze.txt`

#### IV.3.1 — Formato KEY=VALUE, una por línea

- **Estado:** CUMPLE
- **Evidencia:** `parser.py` L55-60; tests `test_valid_minimal_config`, `test_line_without_equals`.

#### IV.3.2 — Comentarios `#` ignorados

- **Estado:** CUMPLE
- **Evidencia:** `parser.py` L51 (`line.split('#', 1)[0]`); test `test_comments_ignored`.

#### IV.3.3 — Claves obligatorias (6)

- **Estado:** CUMPLE
- **Evidencia:** `parser.py` L70-76 verifica `WIDTH`, `HEIGHT`, `ENTRY`, `EXIT`, `OUTPUT_FILE`, `PERFECT`; tests parametrizados por clave faltante.

#### IV.3.4 — Validaciones de tipos y límites

| Validación | Estado | Líneas `parser.py` |
|------------|--------|-------------------|
| WIDTH/HEIGHT > 0 | CUMPLE | L79-83 |
| ENTRY/EXIT formato `x,y` | CUMPLE | L85-96 |
| Coordenadas en límites | CUMPLE | L93-95 |
| ENTRY ≠ EXIT | CUMPLE | L101-103 |
| PERFECT booleano | CUMPLE | L105-112 |
| OUTPUT_FILE no vacío | CUMPLE | L114-116 |

#### IV.3.5 — Claves opcionales

- **Estado:** PARCIAL
- **Evidencia:** `SEED` (L118-120) y `ALGORITHM` (L122) parseados correctamente.
- **Observaciones:** `ALGORITHM` se almacena en `MazeConfig` pero **nunca se usa** en `MazeGenerator` (siempre backtracker).

#### IV.3.6 — Fichero de configuración por defecto en el repo

- **Estado:** NO CUMPLE
- **Evidencia:** Existe `config_maze.txt` (válido); **no existe `config.txt`** como exige el subject IV.3.
- **Acción recomendada:** Crear `config.txt` (o renombrar) y actualizar `Makefile` + `README`.

#### IV.3.7 — Contenido de `config_maze.txt` actual

```
WIDTH=10
HEIGHT=10
ENTRY=2,2
EXIT=8,8
OUTPUT_FILE=maze.txt
PERFECT=False
```

- Válido para el parser ✅
- 10×10 cumple mínimo patrón 42 (9×7) ✅
- Sin `SEED` → no determinista entre ejecuciones (permitido)

---

### IV.4 — Maze Requirements

**Módulo principal:** `mazegen/generator.py`  
**Tests:** `tests/test_generator.py`, helpers en `tests/conftest.py`

#### IV.4.1 — Generación aleatoria con reproducibilidad por semilla

- **Estado:** CUMPLE
- **Evidencia:** `generator.py` L233-234 `random.seed(self._seed)`; tests `test_determinismo_misma_semilla`, `test_semilla_cero_reproducible`.
- **Observación menor:** Usa `random.seed()` global en vez de `random.Random(seed)` inyectado (recomendado en HOJA_DE_RUTA, no obligatorio en subject).

#### IV.4.2 — Celdas con 0–4 muros (N, E, S, O)

- **Estado:** CUMPLE
- **Evidencia:** Inicialización a `15` (todos cerrados); `open_wall` modifica bits N=1, E=2, S=4, W=8; test `test_valores_celda_en_rango_4_bits`.

#### IV.4.3 — ENTRY y EXIT distintas, dentro de límites

- **Estado:** CUMPLE
- **Evidencia:** Validado en `parser.py`; test `test_entry_equals_exit`.

#### IV.4.4 — Conectividad total (excepto patrón "42")

- **Estado:** CUMPLE
- **Evidencia:** `test_conectividad_total_y_aislamiento_42` — `flood_fill` desde entry alcanza todas las celdas excepto las del patrón.

#### IV.4.5 — Muros en bordes externos

- **Estado:** CUMPLE
- **Evidencia:** Grid inicializado a `15`; DFS no abre hacia fuera; test `test_muros_bordes_externos_cerrados`.

#### IV.4.6 — Coherencia bidireccional de muros

- **Estado:** CUMPLE
- **Evidencia:** `open_wall` actualiza ambas celdas (L106-134); `check_bidirectional` en conftest; tests en generator e integración.

#### IV.4.7 — Densidad: sin áreas 3×3 abiertas; pasillos ≤ 2 celdas

- **Estado:** CUMPLE
- **Evidencia:**
  - Modo imperfecto: `_fix_density()` L257-303 cierra muros en ventanas 3×3; test `test_restriccion_densidad_sin_areas_3x3`.
  - Modo perfecto: spanning tree no puede formar 3×3 totalmente abierto (sin ciclos).
- **Observación:** `_fix_density` no re-verifica conectividad ENTRY→EXIT tras cada cierre (riesgo teórico bajo; tests de integración pasan).

#### IV.4.8 — Patrón "42" visible (celdas totalmente cerradas, hex `F`)

- **Estado:** CUMPLE
- **Evidencia:**
  - Plantilla de 18 celdas en `generator.py` L35-38.
  - Celdas del patrón se añaden a `visited` antes del DFS → permanecen en valor `15` (`F`).
  - Test `test_patron_42_celdas_totalmente_cerradas`.

#### IV.4.9 — Mapa pequeño: mensaje de error, generación sin patrón

- **Estado:** CUMPLE
- **Evidencia:** `pattern_42()` L211-215 imprime en stderr y retorna `[]`; test `test_mapa_pequeno_sin_patron_sigue_valido`, `test_g6_mensaje_error_laberinto_pequeno`.

#### IV.4.10 — PERFECT=True: exactamente un camino entry→exit

- **Estado:** CUMPLE
- **Evidencia:** DFS genera spanning tree; test `test_perfect_maze_spanning_tree` verifica `#aristas_abiertas = V - 1` (excluyendo celdas 42).

#### IV.4.11 — PERFECT=False: laberinto con bucles controlados

- **Estado:** CUMPLE
- **Evidencia:** `imperfect_walls()` L138-171 abre muros extra; test `test_perfect_false_mantiene_coherencia_y_sin_3x3`.

#### IV.4.12 — ENTRY/EXIT sobre patrón 42

- **Estado:** CUMPLE (comportamiento defensivo)
- **Evidencia:** `generator.py` L238-241 → error stderr + `sys.exit(1)`; test `test_entry_en_patron_42_aborta`.

#### IV.4.13 — Límite de recursión en laberintos grandes

- **Estado:** CUMPLE
- **Evidencia:** `a_maze_ing.py` L176 `sys.setrecursionlimit(3500)`; test `@slow` `test_g8_limite_recursividad_50x50`.

---

### IV.5 — Output File Format

**Módulo:** `encoder.py`  
**Tests:** `tests/test_encoder.py`, `tests/test_integration.py`

#### IV.5.1 — Un dígito hexadecimal por celda, fila por fila

- **Estado:** CUMPLE
- **Evidencia:** `line_to_hex` L8-9 → `format(cell, "X")` mayúsculas; tabla de verdad 0–F en tests.

#### IV.5.2 — Codificación de bits (N=1, E=2, S=4, W=8; 1=cerrado)

- **Estado:** CUMPLE
- **Evidencia:** Tests `test_line_to_hex_subject_examples` (valores 3 y A del subject).

#### IV.5.3 — Línea vacía tras la matriz

- **Estado:** CUMPLE
- **Evidencia:** `encoder.py` L23 `f.write("\n")`; test `test_gen_maze_file_structure`.

#### IV.5.4 — Tres líneas finales: ENTRY, EXIT, ruta NESW

- **Estado:** CUMPLE
- **Evidencia:** `encoder.py` L25-28; ejemplo real en `maze.txt` L12-14.

#### IV.5.5 — Todas las líneas terminan en `\n`

- **Estado:** CUMPLE
- **Evidencia:** `newline='\n'` en `open()`; test `test_gen_maze_file_all_lines_end_with_newline`.

#### IV.5.6 — Coordenadas en formato config (x,y), no interno (row,col)

- **Estado:** CUMPLE
- **Evidencia:** `gen_maze_file` recibe `config.entry` / `config.exit` (x,y); `a_maze_ing.py` L188-189 pasa coordenadas del config.

#### IV.5.7 — Validación con script del subject

- **Estado:** CUMPLE
- **Evidencia:** `output_validator.py maze.txt` → exit 0; tests `test_gen_maze_file_passes_output_validator`, `test_output_passes_validator`, seeds múltiples.

#### IV.5.8 — Ejemplo de salida actual (`maze.txt`)

```
9513955553
852A85393E
… (10 filas hex)
          ← línea vacía
2,2       ← ENTRY
8,8       ← EXIT
NNESSSEESSSSSEESEN
```

---

## Capítulo V — Visual representation

**Módulo:** `a_maze_ing.py` (`print_maze` + bucle de menú)

#### V.1 — Render ASCII en terminal

- **Estado:** CUMPLE
- **Evidencia:** `print_maze` L68-137 — muros `█`, entrada `E`, salida `X`, ruta `●` amarilla.

#### V.2 — Elementos visibles: muros, entrada, salida, ruta

- **Estado:** CUMPLE
- **Evidencia:** Tests `test_print_maze_shows_entry_and_exit`, `test_print_maze_shows_path_marker`.

#### V.3 — Interacción: regenerar laberinto

- **Estado:** PARCIAL
- **Evidencia:** Opción 1 L222-225 llama `setup_new_maze(config, use_seed=False)` ✅
- **Gap:** No llama `gen_maze_file` → **`OUTPUT_FILE` no se actualiza** tras regenerar.
- **Acción recomendada:** Tras opción 1, reescribir el fichero de salida.

#### V.4 — Interacción: mostrar/ocultar ruta más corta

- **Estado:** CUMPLE
- **Evidencia:** Opción 2 L226-227 alterna `show_path`.

#### V.5 — Interacción: cambiar colores de muros

- **Estado:** CUMPLE
- **Evidencia:** Opción 3 L228-231; 5 colores ANSI (`WALL_COLORS` L193); test `test_print_maze_different_colors`.

#### V.6 — Opcional: color específico para patrón "42"

- **Estado:** NO CUMPLE (opcional)
- **Observaciones:** No implementado; no penaliza si el resto cumple.

#### V.7 — Entradas inválidas del menú

- **Estado:** CUMPLE
- **Evidencia:** L235-236 mensaje sin crash; test `test_menu_quit_via_mock_input`.

#### V.8 — Convención de coordenadas pantalla vs config

- **Estado:** CUMPLE
- **Evidencia:** Swap `(x,y) → (row,col)` en L161-163, L201-202; test `test_setup_new_maze_swaps_config_xy_to_row_col`.

---

## Capítulo VI — Code reusability requirements

#### VI.1 — Clase única `MazeGenerator` en módulo standalone

- **Estado:** CUMPLE
- **Evidencia:** `mazegen/generator.py`; exportada en `mazegen/__init__.py`.

#### VI.2 — Acceso a estructura generada

- **Estado:** CUMPLE
- **Evidencia:** `MazeGenerator.get_maze()` → `list[list[int]]`.

#### VI.3 — Acceso a solución

- **Estado:** CUMPLE
- **Evidencia:** `MazeSolver.solve()` + `get_directions()` → cadena NESW.

#### VI.4 — Formato interno ≠ formato de salida

- **Estado:** CUMPLE
- **Evidencia:** Grid interno en `mazegen/`; codificación hex en `encoder.py` (raíz).

#### VI.5 — Documentación de uso (instanciación, parámetros, ejemplo)

- **Estado:** PARCIAL
- **Evidencia:** `README.md` L35-55 con ejemplo completo.
- **Observaciones:** Falta sección Resources; ejemplo en README usa `exit_coord` como kwarg pero la firma real es `generate(entry, exit_coord)` posicional — funciona pero conviene alinear nombres.

#### VI.6 — Paquete `mazegen-*` en raíz del repositorio

- **Estado:** NO CUMPLE
- **Evidencia:** Subject VI: *"the file must be located at the root of your git repository"*.
- **Situación actual:** Artefactos solo en `dist/` (gitignored); **ningún `.whl` en raíz**.
- **Acción recomendada:** Copiar `mazegen-0.1.0-py3-none-any.whl` a la raíz y commitearlo (o ajustar `.gitignore`).

#### VI.7 — Build estándar `.whl` + `.tar.gz`

- **Estado:** CUMPLE
- **Evidencia:** `python -m build` generó ambos en `dist/` (verificado 15/06/2026).

#### VI.8 — Elementos para rebuild en evaluación

- **Estado:** CUMPLE
- **Evidencia:** `pyproject.toml` + fuentes `mazegen/`; `pip install` del wheel verificado en venv limpio.

#### VI.9 — `pyproject.toml`

- **Estado:** PARCIAL
- **Evidencia:** `name = "mazegen"`, `version = "0.1.0"`, `requires-python >= 3.10`, `poetry-core` como backend.
- **Observaciones:** Sin sección `[tool.poetry.packages]` explícita, pero el build funciona y produce wheel importable.

---

## Capítulo VII — README Requirements

**Archivo:** `README.md` (55 líneas) + `resources.txt` (3 URLs, no integradas)

| # | Requisito | Estado | Detalle |
|---|-----------|--------|---------|
| VII.1 | Primera línea en cursiva con logins 42 | **CUMPLE** | L1: `alejandr, czuluaga` |
| VII.2 | Sección Description | **CUMPLE** | L5-6 |
| VII.3 | Sección Instructions | **CUMPLE** | L8-14 (make targets) |
| VII.4 | Sección **Resources** (referencias + uso de IA) | **NO CUMPLE** | `resources.txt` existe pero no está en README; sin mención de IA |
| VII.5 | Formato completo del config | **CUMPLE** | L16-29 |
| VII.6 | Algoritmo elegido | **CUMPLE** | L31-32 Recursive Backtracker |
| VII.7 | Por qué ese algoritmo | **CUMPLE** | L33 |
| VII.8 | Código reutilizable y cómo usarlo | **CUMPLE** | L35-55 con ejemplo pip + Python |
| VII.9 | Gestión de equipo (roles, planificación, herramientas) | **NO CUMPLE** | Sección ausente |

### Referencias disponibles en `resources.txt` (pendientes de integrar en README)

1. https://www.cs.cmu.edu/~112-n22/notes/student-tp-guides/Mazes.pdf  
2. https://weblog.jamisbuck.org/2011/2/7/maze-generation-algorithm-recap.html  
3. https://medium.com/@luthfisauqi17_68455/artificial-intelligence-search-problem-solve-maze-using-breadth-first-search-bfs-algorithm-255139c6e1a3  

---

## Capítulo VIII — Bonuses

| Bonus posible | Estado |
|---------------|--------|
| Múltiples algoritmos (`ALGORITHM=prim`, etc.) | NO — clave parseada, no implementada |
| Animación durante generación | NO |
| MLX gráfico | NO — se eligió ASCII (válido según subject) |
| Color específico patrón 42 | NO (opcional) |

---

## Capítulo IX — Submission and peer-evaluation

#### IX.1 — Nombres de ficheros correctos

- **Estado:** PARCIAL
- **CUMPLE:** `a_maze_ing.py`, `Makefile`, `README.md`, `pyproject.toml`, `mazegen/`
- **NO CUMPLE:** `config.txt` (solo `config_maze.txt`)

#### IX.2 — Preparación para modificación en vivo

- **Estado:** PARCIAL
- **Recomendación:** Ensayar explicación oral de:
  - `open_wall` y coherencia bidireccional (`generator.py` L87-136)
  - `_fix_density` y detección 3×3 (`generator.py` L257-303)
  - Formato de salida (`encoder.py` L12-28)
  - BFS en `solver.py` L83-117

#### IX.3 — Rebuild del paquete en defensa

- **Estado:** CUMPLE
- **Evidencia:** `python -m build` + `pip install dist/mazegen-*.whl` verificados.

#### IX.4 — Artefactos huérfanos en el repo

| Archivo | Descripción | Riesgo |
|---------|-------------|--------|
| `maze` | Laberinto ASCII pre-renderizado (~45 KB), no referenciado | Bajo — confusión en evaluación |
| `maze.txt` | Output generado (gitignored parcialmente) | Bajo |
| `HOJA_DE_RUTA.md` | Documento interno de planificación | Ninguno — útil para defensa |
| `en.subject.pdf` | Subject (untracked en git status inicial) | Verificar si debe commitearse |

---

## Auditoría módulo a módulo (referencia rápida)

### `a_maze_ing.py` — CLI y render

| Aspecto | Estado |
|---------|--------|
| Punto de entrada | CUMPLE |
| Argumentos CLI | CUMPLE |
| Orquestación pipeline | CUMPLE |
| Render ASCII | CUMPLE |
| Menú interactivo | PARCIAL (regenerar sin actualizar output) |
| Manejo global errores | PARCIAL |
| Docstrings / types | CUMPLE |

### `parser.py` — Config

| Aspecto | Estado |
|---------|--------|
| Formato KEY=VALUE | CUMPLE |
| Validaciones | CUMPLE |
| Context manager | CUMPLE |
| Docstrings / types | CUMPLE |
| Typo "cofiguration" L136 | Menor |
| `ALGORITHM` no propagado | PARCIAL |

### `encoder.py` — Salida hex

| Aspecto | Estado |
|---------|--------|
| Formato IV.5 | CUMPLE |
| Context manager | CUMPLE |
| Docstrings | NO CUMPLE |
| Validador subject | CUMPLE |

### `mazegen/generator.py` — Motor

| Aspecto | Estado |
|---------|--------|
| Generación DFS | CUMPLE |
| Semilla | CUMPLE |
| Patrón 42 | CUMPLE |
| Densidad 3×3 | CUMPLE |
| PERFECT True/False | CUMPLE |
| Docstrings | PARCIAL |
| `random` global | Menor |

### `mazegen/solver.py` — Pathfinding

| Aspecto | Estado |
|---------|--------|
| BFS camino más corto | CUMPLE |
| Traducción NESW | CUMPLE |
| Sin camino | PARCIAL (excepción cruda) |
| Docstring `solve()` | NO CUMPLE |

### `mazegen/__init__.py` — Paquete

| Aspecto | Estado |
|---------|--------|
| Exportaciones | CUMPLE |

### `Makefile` — Automatización

| Regla | Estado |
|-------|--------|
| install, run, debug, clean, lint, lint-strict | CUMPLE (definición) |
| lint ejecución completa | PARCIAL (falla en tests) |
| CONFIG = config_maze.txt | PARCIAL |

### `tests/` — Suite local

| Aspecto | Estado |
|---------|--------|
| Cobertura funcional | CUMPLE (117 tests) |
| flake8 / mypy | NO CUMPLE |
| output_validator E2E | CUMPLE |

---

## Tabla resumen por capítulo

| Capítulo | Ítems auditados | CUMPLE | PARCIAL | NO CUMPLE |
|----------|-----------------|--------|---------|-----------|
| III.1 | 7 | 2 | 5 | 0 |
| III.2 | 6 | 5 | 1 | 0 |
| III.3 | 3 | 2 | 1 | 0 |
| IV.1–IV.2 | 4 | 3 | 1 | 0 |
| IV.3 | 7 | 5 | 1 | 1 |
| IV.4 | 13 | 13 | 0 | 0 |
| IV.5 | 8 | 8 | 0 | 0 |
| V | 8 | 5 | 1 | 1 (opcional) |
| VI | 9 | 5 | 3 | 1 |
| VII | 9 | 7 | 0 | 2 |
| VIII | 4 | 0 | 0 | 4 (bonus) |
| IX | 4 | 1 | 3 | 0 |

**Estimación cumplimiento obligatorio (sin bonus ni opcionales):** ~82 % CUMPLE, ~15 % PARCIAL, ~3 % NO CUMPLE.

---

## Checklist pre-entrega

Marca antes de subir al repositorio de evaluación:

- [ ] Crear `config.txt` por defecto (o renombrar `config_maze.txt`) y actualizar Makefile/README
- [ ] Copiar `mazegen-0.1.0-py3-none-any.whl` a la **raíz** del repo
- [ ] Completar README: sección **Resources** + uso de **IA**
- [ ] Completar README: sección **Team management** (roles, planificación, herramientas)
- [ ] Hacer que `make lint` pase en todo el proyecto (`flake8 .` + `mypy .`)
- [ ] Añadir docstrings en `encoder.py` y `MazeSolver.solve()`
- [ ] Tras regenerar (menú 1), reescribir `OUTPUT_FILE`
- [ ] Envolver `main` en `try/except` con mensajes claros
- [ ] Corregir typo "cofiguration" en `parser.py` L136
- [ ] Verificar `python output_validator.py maze.txt` tras cambios
- [ ] Verificar `python -m build` + install en venv limpio
- [ ] Ensayar defensa oral: DFS, patrón 42, densidad, BFS, encoder

---

## Acciones prioritarias

### Prioridad ALTA (riesgo de penalización en evaluación)

1. **`config.txt` ausente** — El subject exige un fichero de configuración por defecto con ese nombre en el repo.
2. **README incompleto** — Faltan Resources (con URLs y uso de IA) y gestión de equipo (obligatorio VII).
3. **`mazegen-*.whl` no en raíz** — Subject VI lo exige explícitamente en la raíz del git.
4. **`make lint` falla** — El subject pide `flake8 .` y `mypy .` sin exclusiones; actualmente fallan por `tests/`.

### Prioridad MEDIA

5. Regenerar laberinto (menú 1) no actualiza `OUTPUT_FILE`.
6. `encoder.py` sin docstrings (III.1).
7. `MazeSolver.solve()` sin docstring; excepción si no hay camino.
8. CLI sin `try/except` global en `__main__`.
9. `ALGORITHM` parseado pero ignorado — documentar o implementar.

### Prioridad BAJA

10. Typo `"cofiguration"` en parser.
11. `random.Random(seed)` vs `random.seed()` global.
12. Color distinto para patrón 42 (opcional).
13. Archivo `maze` huérfano en raíz.
14. `.gitignore` incompleto (`.venv/`, `.pytest_cache/`).

---

## Riesgos en defensa (qué poder explicar)

| Tema | Pregunta probable del evaluador | Dónde está la respuesta |
|------|--------------------------------|-------------------------|
| Algoritmo | ¿Por qué Recursive Backtracker? | README L31-33; genera spanning tree |
| Patrón 42 | ¿Cómo se inserta sin romper rutas? | Celdas marcadas `visited` antes del DFS; valor `F` |
| Coherencia | ¿Cómo garantizáis muros bidireccionales? | `open_wall` modifica ambas celdas |
| Densidad | ¿Qué es un 3×3 prohibido? | `_fix_density` — 9 celdas sin muros interiores |
| Salida hex | ¿Qué significa el dígito `A`? | Bits E+W cerrados (1010) |
| Coordenadas | ¿(x,y) o (fila,col)? | Config usa (x,y); interno (row,col) con swap en CLI |
| Semilla | ¿SEED=0 funciona? | Sí — test `test_semilla_cero_reproducible` |
| Paquete | ¿Cómo reutilizar mazegen? | README ejemplo; `pip install` del wheel |

---

## Comandos de verificación reproducibles

```bash
# Lint (como exige el subject)
flake8 .
mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports \
  --disallow-untyped-defs --check-untyped-defs

# Lint solo producción (estado actual OK)
flake8 a_maze_ing.py parser.py encoder.py mazegen/
mypy a_maze_ing.py parser.py encoder.py mazegen/ \
  --warn-return-any --warn-unused-ignores --ignore-missing-imports \
  --disallow-untyped-defs --check-untyped-defs

# Tests
python -m pytest tests/ -v

# Validador del subject
python output_validator.py maze.txt

# Build e instalación
python -m build
python -m venv test_env
test_env/Scripts/pip install dist/mazegen-0.1.0-py3-none-any.whl   # Windows
# source test_env/bin/activate && pip install dist/mazegen-*.whl   # Linux/macOS
python -c "from mazegen import MazeGenerator; print('OK')"

# Ejecución
python a_maze_ing.py config_maze.txt
```

---

*Informe generado automáticamente como parte de la auditoría pre-entrega del proyecto A-Maze-ing.*
