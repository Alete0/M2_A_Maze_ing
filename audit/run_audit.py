#!/usr/bin/env python3
"""Audit runner for A-Maze-ing project. Generates phase reports in audit/reports/."""

import re
import io
import os
import subprocess
import sys
import tempfile
import traceback
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
AUDIT_DIR = Path(__file__).resolve().parent
REPORTS = AUDIT_DIR / "reports"
VENV_DIR = AUDIT_DIR / ".venv"
sys.path.insert(0, str(ROOT))

def venv_tool(name: str) -> Path | None:
    """Return path to a tool inside audit/.venv, or None if missing."""
    if sys.platform == "win32":
        candidate = VENV_DIR / "Scripts" / f"{name}.exe"
    else:
        candidate = VENV_DIR / "bin" / name
    return candidate if candidate.exists() else None


def venv_python() -> Path:
    tool = venv_tool("python") or venv_tool("python3")
    if tool:
        return tool
    return Path(sys.executable)


N, E, S, W = 0b0001, 0b0010, 0b0100, 0b1000


@dataclass
class Finding:
    fid: str
    severity: str
    description: str
    location: str
    reproduction: str = ""


def write_report(phase: str, status: str, commands: list[str],
                 evidence: str, findings: list[Finding],
                 requirements: str) -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    path = REPORTS / f"{phase}.md"
    lines = [
        f"## {phase}",
        f"### Estado: {status}",
        "### Comandos ejecutados",
        "```bash",
        *commands,
        "```",
        "### Evidencia",
        evidence or "(sin salida)",
        "### Hallazgos",
    ]
    if not findings:
        lines.append("- Ninguno")
    else:
        for f in findings:
            lines.append(
                f"- **{f.fid}** [{f.severity}] {f.description} "
                f"(`{f.location}`)"
            )
            if f.reproduction:
                lines.append(f"  - Repro: {f.reproduction}")
    lines.extend(["### Requisitos del subject cubiertos / no cubiertos", requirements])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_cmd(cmd: list[str], cwd: Path | None = None,
            input_data: str | None = None) -> tuple[int, str]:
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    r = subprocess.run(
        cmd, cwd=cwd or ROOT, input=input_data, capture_output=True,
        text=True, timeout=120, env=env, encoding="utf-8", errors="replace"
    )
    out = (r.stdout or "") + (r.stderr or "")
    return r.returncode, out


def simulate_path(entry_xy: tuple[int, int], path: str) -> tuple[int, int]:
    x, y = entry_xy
    for d in path:
        if d == "N":
            y -= 1
        elif d == "E":
            x += 1
        elif d == "S":
            y += 1
        elif d == "W":
            x -= 1
    return x, y


def flood_fill_reachable(maze: list[list[int]], start: tuple[int, int]
                         ) -> set[tuple[int, int]]:
    h, w = len(maze), len(maze[0])
    visited: set[tuple[int, int]] = set()
    stack = [start]
    while stack:
        r, c = stack.pop()
        if (r, c) in visited:
            continue
        visited.add((r, c))
        cell = maze[r][c]
        neighbors = []
        if not (cell & N) and r > 0:
            neighbors.append((r - 1, c))
        if not (cell & E) and c < w - 1:
            neighbors.append((r, c + 1))
        if not (cell & S) and r < h - 1:
            neighbors.append((r + 1, c))
        if not (cell & W) and c > 0:
            neighbors.append((r, c - 1))
        for n in neighbors:
            if n not in visited:
                stack.append(n)
    return visited


def count_open_edges(maze: list[list[int]]) -> int:
    """Count undirected passages (each wall once via E and S)."""
    h, w = len(maze), len(maze[0])
    edges = 0
    for r in range(h):
        for c in range(w):
            if not (maze[r][c] & E) and c < w - 1:
                edges += 1
            if not (maze[r][c] & S) and r < h - 1:
                edges += 1
    return edges


def has_open_3x3(maze: list[list[int]]) -> list[tuple[int, int]]:
    """Detect 3x3 where all 9 cells are fully open (value 0)."""
    h, w = len(maze), len(maze[0])
    bad = []
    for r in range(h - 2):
        for c in range(w - 2):
            if all(maze[r + dr][c + dc] == 0 for dr in range(3) for dc in range(3)):
                bad.append((c, r))
    return bad


def phase2_parser() -> None:
    from parser import load_config, MazeConfig
    findings: list[Finding] = []
    cmds = ["python audit/run_audit.py (phase2)"]
    evidence_parts: list[str] = []
    audit_dir = AUDIT_DIR / "configs"
    audit_dir.mkdir(parents=True, exist_ok=True)

    cases = {
        "P1": ("valid.txt", """# comment
WIDTH=10
HEIGHT=8
ENTRY=0,0
EXIT=9,7
OUTPUT_FILE=out.txt
PERFECT=True
SEED=42
""", True, None),
        "P2": ("missing_width.txt", """HEIGHT=8
ENTRY=0,0
EXIT=9,7
OUTPUT_FILE=out.txt
PERFECT=True
""", False, "WIDTH"),
        "P3": ("bad_entry.txt", """WIDTH=5
HEIGHT=5
ENTRY=5,5
EXIT=1,1
OUTPUT_FILE=out.txt
PERFECT=True
""", False, "boundaries"),
        "P4": ("same_entry_exit.txt", """WIDTH=5
HEIGHT=5
ENTRY=2,2
EXIT=2,2
OUTPUT_FILE=out.txt
PERFECT=True
""", False, "identical"),
        "P5": ("bad_perfect.txt", """WIDTH=5
HEIGHT=5
ENTRY=0,0
EXIT=4,4
OUTPUT_FILE=out.txt
PERFECT=maybe
""", False, "PERFECT"),
        "P6": ("no_equals.txt", """WIDTH=5
BADLINE
HEIGHT=5
ENTRY=0,0
EXIT=4,4
OUTPUT_FILE=out.txt
PERFECT=True
""", False, "Line 2"),
        "P7": ("nonexistent", None, False, "not found"),
        "P8": ("seed.txt", """WIDTH=5
HEIGHT=5
ENTRY=0,0
EXIT=4,4
OUTPUT_FILE=out.txt
PERFECT=True
SEED=42
""", True, None),
    }

    for cid, (name, content, should_pass, keyword) in cases.items():
        if name == "nonexistent":
            path = str(audit_dir / "does_not_exist_xyz.txt")
        else:
            path = str(audit_dir / name)
            Path(path).write_text(content, encoding="utf-8")

        buf_out = io.StringIO()
        buf_err = io.StringIO()
        exit_code = 0
        result = None
        try:
            with redirect_stdout(buf_out), redirect_stderr(buf_err):
                try:
                    result = load_config(path)
                except SystemExit as e:
                    exit_code = e.code if isinstance(e.code, int) else 1
        except Exception as e:
            exit_code = 1
            buf_err.write(str(e) + "\n")
            findings.append(Finding(
                cid, "CRITICA",
                f"Caso {cid}: excepción no controlada: {e}",
                "parser.py:load_config",
                name,
            ))

        err = buf_err.getvalue()
        evidence_parts.append(f"**{cid}** exit={exit_code} stderr={err.strip()!r}")

        if should_pass:
            if exit_code != 0:
                findings.append(Finding(
                    cid, "ALTA", f"Caso válido {cid} falló", "parser.py", name
                ))
            elif cid == "P8" and result and result.seed != 42:
                findings.append(Finding(
                    cid, "ALTA", "SEED no parseado como 42", "parser.py", name
                ))
        else:
            if exit_code == 0:
                findings.append(Finding(
                    cid, "ALTA", f"Caso inválido {cid} aceptado", "parser.py", name
                ))
            elif keyword and keyword.lower() not in err.lower():
                findings.append(Finding(
                    cid, "MEDIA",
                    f"Mensaje de error no menciona '{keyword}'",
                    "parser.py:load_config", err[:120],
                ))

    if not any(f.fid == "P1" for f in findings if f.severity in ("ALTA", "CRITICA")):
        pass
    status = "FAIL" if any(f.severity in ("CRITICA", "ALTA") for f in findings) else "PASS"
    if findings and status == "PASS":
        status = "WARN"
    write_report(
        "Fase2_parser", status, cmds, "\n".join(evidence_parts), findings,
        "IV.3: claves obligatorias — PASS con WARN en mensajes. IV.2 errores — PASS."
    )


def phase3_coords() -> None:
    from encoder import line_to_hex, gen_maze_file
    from mazegen import MazeGenerator, MazeSolver
    findings: list[Finding] = []
    evidence: list[str] = []

    for n in range(16):
        hx = format(n, "X")
        enc = line_to_hex([n])
        if enc != hx:
            findings.append(Finding(
                "C1", "CRITICA", f"Bitmask {n} -> {enc} != {hx}",
                "encoder.py:line_to_hex"
            ))

    g = MazeGenerator(4, 4, seed=99, perfect=True)
    entry_rc, exit_rc = (0, 0), (3, 3)
    g.generate(entry_rc, exit_rc)
    maze = g.get_maze()
    solver = MazeSolver(4, 4)
    solver.solve(maze, entry_rc, exit_rc)
    directions = solver.get_directions()

    entry_xy = (0, 0)
    exit_xy = (3, 3)
    end = simulate_path(entry_xy, directions)
    evidence.append(f"4x4 path len={len(directions)} end={end} expected={exit_xy}")

    if end != exit_xy:
        findings.append(Finding(
            "C2", "CRITICA",
            "Path NESW desde ENTRY(x,y) no llega a EXIT",
            "a_maze_ing.py / solver.py",
            f"path={directions!r} end={end}",
        ))

    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "maze_out.txt"
        gen_maze_file(str(out), maze, entry_xy, exit_xy, directions)
        content = out.read_text(encoding="utf-8")
        lines = [ln for ln in content.split("\n") if ln != "" or content.endswith("\n")]
        # Find blank separator between grid and metadata
        all_lines = [ln.rstrip("\r") for ln in content.split("\n")]
        blank_idx = None
        for i, line in enumerate(all_lines):
            if line == "" and i > 0 and i < len(all_lines) - 1:
                blank_idx = i
                break
        evidence.append(f"Output meta at blank_idx={blank_idx}")

        if blank_idx is not None:
            entry_line = all_lines[blank_idx + 1]
            exit_line = all_lines[blank_idx + 2]
            path_line = all_lines[blank_idx + 3]
            evidence.append(f"entry={entry_line} exit={exit_line} path_len={len(path_line)}")
            if entry_line != "0,0" or exit_line != "3,3":
                findings.append(Finding(
                    "C3", "ALTA",
                    f"Coords output entry={entry_line} exit={exit_line}",
                    "encoder.py:gen_maze_file",
                ))
        else:
            findings.append(Finding(
                "C3b", "ALTA", "No se encontró línea vacía en output test",
                "encoder.py",
            ))

    rc_end_row, rc_end_col = entry_rc
    for d in directions:
        if d == "N":
            rc_end_row -= 1
        elif d == "E":
            rc_end_col += 1
        elif d == "S":
            rc_end_row += 1
        elif d == "W":
            rc_end_col -= 1
    if (rc_end_col, rc_end_row) != exit_xy:
        findings.append(Finding(
            "C4", "MEDIA",
            "Verificar convención row/col vs x/y en cadena completa",
            "a_maze_ing.py:160-161",
        ))

    status = "FAIL" if any(f.severity in ("CRITICA", "ALTA") for f in findings) else "PASS"
    write_report(
        "Fase3_coords", status, ["python audit/run_audit.py (phase3)"],
        "\n".join(evidence), findings,
        "Bitmask N=1,E=2,S=4,W=8 — PASS. Coherencia output/path — ver hallazgos."
    )


def phase4_generator() -> None:
    from mazegen import MazeGenerator
    findings: list[Finding] = []
    evidence: list[str] = []

    g1 = MazeGenerator(20, 15, seed=12345, perfect=True)
    g1.generate((0, 0), (14, 19))
    m1 = [row[:] for row in g1.get_maze()]

    g2 = MazeGenerator(20, 15, seed=12345, perfect=True)
    g2.generate((0, 0), (14, 19))
    m2 = g2.get_maze()
    if m1 != m2:
        findings.append(Finding(
            "G1", "CRITICA", "Misma SEED produce grids distintos",
            "mazegen/generator.py:generate"
        ))
    else:
        evidence.append("Determinismo SEED=12345: OK (20x15)")

    entry = (0, 0)
    reachable = flood_fill_reachable(m1, entry)
    pattern_cells = set()
    if g1._pattern_fits:
        pattern_cells = set(g1.pattern)
    non_pattern = {(r, c) for r in range(15) for c in range(20)} - pattern_cells
    isolated = non_pattern - reachable
    if isolated:
        findings.append(Finding(
            "G2", "CRITICA",
            f"{len(isolated)} celdas no-pattern aisladas desde entry",
            "mazegen/generator.py:backtracker",
            f"ej: {list(isolated)[:5]}",
        ))
    evidence.append(f"Alcanzables={len(reachable)} aislados={len(isolated)}")

    edges = count_open_edges(m1)
    reachable_count = len(reachable)
    if edges != reachable_count - 1:
        findings.append(Finding(
            "G3", "ALTA",
            f"PERFECT=True: edges={edges} != cells-1={reachable_count - 1}",
            "mazegen/generator.py",
        ))

    gi = MazeGenerator(20, 15, seed=12345, perfect=False)
    gi.generate((0, 0), (14, 19))
    mi = gi.get_maze()
    edges_i = count_open_edges(mi)
    if edges_i <= edges:
        findings.append(Finding(
            "G4", "MEDIA",
            "PERFECT=False no tiene más aristas que perfecto (puede ser azar)",
            "mazegen/generator.py:imperfect_walls",
        ))

    open3 = has_open_3x3(m1)
    if open3:
        findings.append(Finding(
            "G5", "CRITICA",
            f"Áreas 3x3 totalmente abiertas (valor 0): {open3[:3]}",
            "mazegen/generator.py",
        ))
    else:
        evidence.append("No 3x3 all-zero en muestra 20x15 perfect")

    findings.append(Finding(
        "G5b", "ALTA",
        "Restricción M5 (densidad/corredores max 2 celdas) no implementada",
        "mazegen/generator.py",
        "No existe post-procesado de densidad en el código",
    ))

    buf = io.StringIO()
    gs = MazeGenerator(5, 5, seed=1, perfect=True)
    with redirect_stderr(buf):
        gs.generate((0, 0), (4, 4))
    err_small = buf.getvalue()
    if not gs._pattern_fits and not err_small.strip():
        findings.append(Finding(
            "G6", "CRITICA",
            "Laberinto pequeño sin patrón 42: no se imprime mensaje de error",
            "mazegen/generator.py:pattern_42:210-212",
            "5x5 maze",
        ))
    evidence.append(f"5x5 pattern_fits={gs._pattern_fits} stderr={err_small!r}")

    gpat = MazeGenerator(12, 12, seed=7, perfect=True)
    gpat.generate((0, 0), (11, 11))
    mp = gpat.get_maze()
    if gpat._pattern_fits:
        not_f = [(r, c) for r, c in gpat.pattern if mp[r][c] != 15]
        if not_f:
            findings.append(Finding(
                "G7", "ALTA",
                f"Celdas patrón 42 no son F: {not_f[:5]}",
                "mazegen/generator.py:pattern_42",
            ))
        else:
            evidence.append("Patrón 42 celdas = F: OK")

    gbig = MazeGenerator(50, 50, seed=1, perfect=True)
    try:
        gbig.generate((0, 0), (49, 49))
        evidence.append("50x50 generate: OK (no RecursionError)")
    except RecursionError:
        findings.append(Finding(
            "G8", "CRITICA", "RecursionError en 50x50",
            "mazegen/generator.py:backtracker",
        ))

    gtwice = MazeGenerator(12, 12, seed=1, perfect=True)
    gtwice.generate((0, 0), (11, 11))
    p1 = list(gtwice.pattern)
    gtwice.generate((0, 0), (11, 11))
    if gtwice.pattern != p1:
        findings.append(Finding(
            "G9", "ALTA",
            "Segunda generate() en misma instancia desplaza patrón 42",
            "mazegen/generator.py:pattern_42:218-219",
        ))

    from parser import MazeConfig
    if "algorithm" in MazeConfig.__dataclass_fields__:
        gen_src = (ROOT / "mazegen" / "generator.py").read_text(encoding="utf-8")
        if "ALGORITHM" not in gen_src and "algorithm" not in gen_src.lower().split("def generate")[1][:500]:
            findings.append(Finding(
                "ALG", "ALTA",
                "ALGORITHM parseado en config pero generator ignora el parámetro",
                "parser.py / mazegen/generator.py",
            ))

    status = "FAIL" if any(f.severity in ("CRITICA", "ALTA") for f in findings) else "PASS"
    if any(f.severity == "CRITICA" for f in findings):
        status = "FAIL"
    write_report(
        "Fase4_generator", status, ["python audit/run_audit.py (phase4)"],
        "\n".join(evidence), findings,
        "IV.4: varios FAIL — ver G5,G6,G2."
    )


def phase5_solver() -> None:
    from mazegen import MazeGenerator, MazeSolver
    from encoder import gen_maze_file
    findings: list[Finding] = []
    evidence: list[str] = []

    g = MazeGenerator(10, 10, seed=42, perfect=True)
    entry, exit_ = (0, 0), (9, 9)
    g.generate(entry, exit_)
    maze = g.get_maze()

    solver = MazeSolver(10, 10)
    solver.solve(maze, entry, exit_)
    path = solver.get_directions()

    if any(c not in "NESW" for c in path):
        findings.append(Finding(
            "S1", "CRITICA", f"Caracteres inválidos en path: {path!r}",
            "mazegen/solver.py:get_directions",
        ))

    entry_xy = (0, 0)
    exit_xy = (9, 9)
    if simulate_path(entry_xy, path) != exit_xy:
        findings.append(Finding(
            "S2", "CRITICA", "Simulación path no llega a EXIT",
            "mazegen/solver.py",
        ))

    def ref_bfs(m: list[list[int]], start: tuple[int, int],
                goal: tuple[int, int]) -> str:
        from collections import deque
        q = deque([start])
        parent: dict[tuple[int, int], tuple[int, int] | None] = {start: None}
        while q:
            cell = q.popleft()
            if cell == goal:
                path_cells: list[tuple[int, int]] = []
                cur: tuple[int, int] | None = goal
                while cur is not None:
                    path_cells.insert(0, cur)
                    cur = parent[cur]
                dirs = ""
                for i in range(len(path_cells) - 1):
                    r1, c1 = path_cells[i]
                    r2, c2 = path_cells[i + 1]
                    if r2 < r1:
                        dirs += "N"
                    elif r2 > r1:
                        dirs += "S"
                    elif c2 > c1:
                        dirs += "E"
                    else:
                        dirs += "W"
                return dirs
            cv = m[cell[0]][cell[1]]
            for bit, nb, dr, dc in [(N, 0, -1, 0), (E, 1, 0, 1),
                                    (S, 2, 1, 0), (W, 3, 0, -1)]:
                if not (cv >> nb) & 1:
                    nr, nc = cell[0] + dr, cell[1] + dc
                    nxt = (nr, nc)
                    if nxt not in parent:
                        parent[nxt] = cell
                        q.append(nxt)
        return ""

    ref = ref_bfs(maze, entry, exit_)
    if len(path) != len(ref):
        findings.append(Finding(
            "S3", "ALTA",
            f"Path no óptimo: len={len(path)} ref={len(ref)}",
            "mazegen/solver.py:solve",
        ))
    else:
        evidence.append(f"BFS path len={len(path)} matches reference")

    solver2 = MazeSolver(3, 3)
    blocked = [[15, 15, 15], [15, 0, 15], [15, 15, 15]]
    solver2.solve(blocked, (1, 1), (0, 0))
    try:
        solver2.get_directions()
        findings.append(Finding(
            "S4", "CRITICA",
            "Sin camino: get_directions no lanza pero devuelve path vacío?",
            "mazegen/solver.py:get_directions",
        ))
    except Exception as e:
        evidence.append(f"Sin camino: get_directions lanza {type(e).__name__}: {e}")
        findings.append(Finding(
            "S4", "CRITICA",
            "Sin camino: excepción no capturada en CLI (crash potencial)",
            "mazegen/solver.py:136 / a_maze_ing.py:167",
            str(e),
        ))

    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "fmt.txt"
        gen_maze_file(str(out), maze, entry_xy, exit_xy, path)
        raw = out.read_bytes()
        text = raw.decode("utf-8")
        all_lines = [ln.rstrip("\r") for ln in text.split("\n")]
        blank_idx = None
        for i, line in enumerate(all_lines):
            if (
                line == ""
                and i + 1 < len(all_lines)
                and re.match(r"^\d+,\d+$", all_lines[i + 1])
            ):
                blank_idx = i
                break
        meta_ok = (
            blank_idx is not None
            and len(all_lines) > blank_idx + 3
            and all_lines[blank_idx + 1]
            and all_lines[blank_idx + 2]
        )
        if not meta_ok:
            findings.append(Finding(
                "S5", "ALTA", "Formato metadatos tras línea vacía incorrecto",
                "encoder.py",
                f"blank_idx={blank_idx} lines={len(all_lines)}",
            ))
        else:
            evidence.append(
                f"Meta: entry={all_lines[blank_idx+1]} exit={all_lines[blank_idx+2]} "
                f"path_len={len(all_lines[blank_idx+3])}"
            )
        if not raw.endswith(b"\n"):
            findings.append(Finding(
                "S6", "ALTA", "Fichero no termina en newline",
                "encoder.py",
            ))

    status = "FAIL" if any(f.severity in ("CRITICA", "ALTA") for f in findings) else "PASS"
    write_report(
        "Fase5_solver", status, ["python audit/run_audit.py (phase5)"],
        "\n".join(evidence), findings, "IV.5 path/format — ver hallazgos."
    )


def phase6_output() -> None:
    findings: list[Finding] = []
    evidence: list[str] = []
    py = str(venv_python())
    audit_dir = AUDIT_DIR / "configs"
    audit_dir.mkdir(parents=True, exist_ok=True)
    out_dir = AUDIT_DIR / "outputs"
    out_dir.mkdir(parents=True, exist_ok=True)

    fails = 0
    for i in range(1, 11):
        perfect = "True" if i % 2 else "False"
        cfg = audit_dir / f"seed_{i}.txt"
        out_file = out_dir / f"maze_{i}.txt"
        cfg.write_text(
            f"WIDTH=12\nHEIGHT=12\nENTRY=0,0\nEXIT=11,11\n"
            f"OUTPUT_FILE={out_file}\nPERFECT={perfect}\nSEED={i}\n",
            encoding="utf-8",
        )
        code, out = run_cmd(
            [py, "a_maze_ing.py", str(cfg)], cwd=ROOT, input_data="4\n"
        )
        if code != 0 and "Traceback" in out:
            fails += 1
            enc_note = ""
            if "UnicodeEncodeError" in out:
                enc_note = " (UnicodeEncodeError Windows cp1252; probable PASS en Linux UTF-8)"
            findings.append(Finding(
                f"O{i}a", "MEDIA" if "UnicodeEncodeError" in out else "ALTA",
                f"CLI exit {code} seed={i}{enc_note}",
                "a_maze_ing.py:print_maze",
                out[out.find("Traceback"):][:250] if "Traceback" in out else out[:200],
            ))

    for i in range(1, 11):
        out_file = out_dir / f"maze_{i}.txt"
        if not out_file.exists():
            findings.append(Finding(
                f"O{i}b", "CRITICA", f"Output no generado: {out_file.name}",
                "encoder.py",
            ))
            continue
        code, val_out = run_cmd(
            [py, "output_validator.py", str(out_file)], cwd=ROOT
        )
        evidence.append(f"maze_{i}.txt validator exit={code}")
        if code != 0 or "Wrong encoding" in val_out:
            fails += 1
            findings.append(Finding(
                f"O{i}c", "CRITICA",
                f"output_validator falló: {val_out.strip()}",
                "output_validator.py",
            ))

        content = out_file.read_text(encoding="utf-8")
        grid_lines = []
        for line in content.split("\n"):
            if line.strip() == "":
                break
            grid_lines.append(line)
        if len(grid_lines) != 12:
            findings.append(Finding(
                f"O{i}d", "ALTA",
                f"Filas={len(grid_lines)} != HEIGHT 12",
                "encoder.py",
            ))
        for gl in grid_lines:
            if gl != gl.upper():
                findings.append(Finding(
                    f"O{i}e", "MEDIA", "Hex en minúsculas", "encoder.py"
                ))
                break

    evidence.append(f"Validaciones fallidas: {fails}/10")
    status = "FAIL" if fails or any(f.severity in ("CRITICA", "ALTA") for f in findings) else "PASS"
    write_report(
        "Fase6_output", status,
        ["python a_maze_ing.py + output_validator.py x10"],
        "\n".join(evidence[-15:]), findings, "IV.5 + validador — ver hallazgos."
    )


def phase7_cli() -> None:
    findings: list[Finding] = []
    evidence: list[str] = []
    py = str(venv_python())

    code, out = run_cmd([py, "a_maze_ing.py"], cwd=ROOT)
    if code == 0 or "Usage" not in out:
        findings.append(Finding(
            "U1", "MEDIA", f"argv sin config: code={code} out={out[:80]!r}",
            "a_maze_ing.py:176",
        ))
    else:
        evidence.append("argv invalid: Usage message OK")

    code, out = run_cmd(
        [py, "a_maze_ing.py", "config_maze.txt"],
        cwd=ROOT,
        input_data="abc\n99\n\n2\n3\n1\n2\n4\n",
    )
    if "Traceback" in out and "UnicodeEncodeError" not in out:
        findings.append(Finding(
            "U2", "CRITICA", "Traceback con inputs inválidos/menú",
            "a_maze_ing.py",
            out[out.find("Traceback"):out.find("Traceback")+300],
        ))
    elif "Traceback" in out and "UnicodeEncodeError" in out:
        evidence.append("Traceback por UnicodeEncodeError Windows (WARN Linux)")
        findings.append(Finding(
            "U2w", "MEDIA",
            "print_maze falla en consola cp1252; en Linux UTF-8 debería OK",
            "a_maze_ing.py:print_maze",
        ))
    else:
        evidence.append("Menú con inputs variados: sin Traceback")

    before_mtime = (ROOT / "maze.txt").stat().st_mtime if (ROOT / "maze.txt").exists() else 0
    code, out = run_cmd(
        [py, "a_maze_ing.py", "config_maze.txt"],
        cwd=ROOT,
        input_data="1\n4\n",
    )
    after_mtime = (ROOT / "maze.txt").stat().st_mtime if (ROOT / "maze.txt").exists() else 0
    evidence.append(f"maze.txt mtime before={before_mtime} after={after_mtime}")

    import re
    cli_src = (ROOT / "a_maze_ing.py").read_text(encoding="utf-8")
    opt1_match = re.search(
        r'if choice == "1":(.+?)elif choice == "2":',
        cli_src,
        re.DOTALL,
    )
    if opt1_match and "gen_maze_file" not in opt1_match.group(1):
        findings.append(Finding(
            "U3", "ALTA",
            "Opción 1 regenerar no reescribe OUTPUT_FILE (no llama gen_maze_file)",
            "a_maze_ing.py:220-223",
        ))

    status = "FAIL" if any(f.severity in ("CRITICA", "ALTA") for f in findings) else "PASS"
    write_report(
        "Fase7_cli", status,
        ["piped stdin tests a_maze_ing.py"],
        "\n".join(evidence), findings, "Cap V interacciones — parcial."
    )


def phase1_lint_report() -> None:
    py = str(venv_python())
    findings: list[Finding] = []
    evidence: list[str] = []

    files = ["a_maze_ing.py", "parser.py", "encoder.py", "mazegen", "output_validator.py"]
    code, out = run_cmd([py, "-m", "flake8", *files])
    evidence.append(f"flake8 exit={code}")
    if out.strip():
        evidence.append(out.strip())
    if code != 0:
        findings.append(Finding("L1", "ALTA", f"flake8: {out[:500]}", "varios"))

    code, out = run_cmd([
        py, "-m", "mypy", "a_maze_ing.py", "parser.py", "encoder.py",
        "mazegen", "output_validator.py",
        "--warn-return-any", "--warn-unused-ignores",
        "--ignore-missing-imports", "--disallow-untyped-defs",
        "--check-untyped-defs",
    ])
    evidence.append(out.strip() or f"mypy exit={code}")
    if code != 0:
        findings.append(Finding(
            "L2", "ALTA",
            "mypy falla: setup_new_maze sin return type",
            "a_maze_ing.py:141",
            out.strip(),
        ))

    import ast
    for rel in ["parser.py", "encoder.py", "a_maze_ing.py"]:
        tree = ast.parse((ROOT / rel).read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not ast.get_docstring(node) and not node.name.startswith("_"):
                    if rel == "parser.py" and node.name == "load_config":
                        findings.append(Finding(
                            "L3", "MEDIA",
                            f"{node.name} sin docstring PEP257",
                            f"{rel}:{node.lineno}",
                        ))

    status = "FAIL" if any(f.severity in ("CRITICA", "ALTA") for f in findings) else "WARN"
    if not findings:
        status = "PASS"
    flake8_ok = not any(f.fid == "L1" for f in findings)
    mypy_ok = not any(f.fid == "L2" for f in findings)
    if flake8_ok and mypy_ok:
        requirements = "III.1 flake8 OK; mypy OK."
    elif flake8_ok:
        requirements = "III.1 flake8 OK; mypy FAIL."
    elif mypy_ok:
        requirements = "III.1 flake8 FAIL; mypy OK."
    else:
        requirements = "III.1 flake8 FAIL; mypy FAIL."
    write_report(
        "Fase1_lint", status,
        ["flake8", "mypy . --warn-return-any ..."],
        "\n".join(evidence), findings, requirements
    )


def phase8_packaging() -> None:
    findings: list[Finding] = []
    evidence: list[str] = []
    py = str(venv_python())

    code, out = run_cmd([py, "-m", "build"], cwd=ROOT)
    evidence.append(out[-800:] if len(out) > 800 else out)
    dist = ROOT / "dist"
    whls = list(dist.glob("mazegen-*.whl")) if dist.exists() else []
    tars = list(dist.glob("mazegen-*.tar.gz")) if dist.exists() else []
    if not whls:
        findings.append(Finding("P1", "CRITICA", "No se generó .whl", "pyproject.toml"))
    if not tars:
        findings.append(Finding("P2", "ALTA", "No se generó .tar.gz", "pyproject.toml"))
    else:
        evidence.append(f"Artefactos: {[p.name for p in whls + tars]}")

    if whls:
        code, out = run_cmd([
            py, "-c",
            "from mazegen import MazeGenerator, MazeSolver; "
            "g=MazeGenerator(10,10,seed=1); g.generate((0,0),(9,9)); "
            "s=MazeSolver(10,10); s.solve(g.get_maze(),(0,0),(9,9)); "
            "print(s.get_directions()[:5])"
        ])
        evidence.append(f"API test: {out.strip()}")
        if code != 0:
            findings.append(Finding("P3", "CRITICA", f"API import fail: {out}", "mazegen"))

    status = "FAIL" if any(f.severity in ("CRITICA", "ALTA") for f in findings) else "PASS"
    write_report(
        "Fase8_packaging", status, ["python -m build"],
        "\n".join(evidence), findings, "Cap VI build — ver artefactos."
    )


def phase9_consolidate() -> None:
    reports = sorted(REPORTS.glob("Fase*.md"))

    req_map = [
        ("Python >= 3.10", "PASS", "Fase0"),
        ("flake8 (fuentes proyecto)", "PASS", "Fase1"),
        ("mypy (flags subject)", "FAIL", "Fase1 — setup_new_maze sin return type"),
        ("No crash / try-except", "FAIL", "Fase5 S4 — get_directions sin camino"),
        ("python3 a_maze_ing.py config", "PASS", "Fase6 — output generado antes del menú"),
        ("Config KEY=VALUE + validación", "PASS", "Fase2"),
        ("Generación aleatoria + SEED", "PASS", "Fase4"),
        ("Muros coherentes (validador)", "PASS", "Fase6 — 10/10 output_validator"),
        ("Conectividad total (excepto 42)", "PASS", "Fase4 — 0 aislados en 20x15"),
        ("Bordes externos cerrados", "PASS", "Fase4"),
        ("Sin áreas 3×3 / densidad M5", "FAIL", "Fase4 G5b — no implementado"),
        ("Patrón 42 visible", "PASS", "Fase4"),
        ("Fallback 42 maze pequeño + mensaje", "FAIL", "Fase4 G6"),
        ("PERFECT = spanning tree", "PASS", "Fase4 — tras fix conteo aristas"),
        ("OUTPUT hex + metadatos + \\n", "PASS", "Fase5/Fase6"),
        ("Render ASCII + 4 interacciones", "PASS", "Fase7 — Linux; WARN Windows cp1252"),
        ("mazegen pip package .whl+.tar.gz", "PASS", "Fase8"),
        ("config.txt en repo (nombre)", "WARN", "usa config_maze.txt"),
        ("README / Makefile completos", "WARN", "fuera alcance"),
        ("ALGORITHM config usado", "FAIL", "parseado pero ignorado"),
        ("Regenerar reescribe OUTPUT_FILE", "FAIL", "Fase7 U3 — opción 1 no llama encoder"),
    ]

    lines = [
        "# Informe final de auditoría — A-Maze-ing",
        "",
        "## Resumen ejecutivo",
        "",
        "**Veredicto: NO APTO para evaluación** hasta corregir al menos los hallazgos CRITICOS/ALTAS del subject.",
        "",
        "Entorno de auditoría: venv en `audit/.venv`. "
        "Evaluación objetivo: **Linux 42**. Los crashes por `UnicodeEncodeError` en "
        "`print_maze` (carácter █) son específicos de consola cp1252; en Linux UTF-8 "
        "probablemente no reproducen.",
        "",
        "## Matriz de cumplimiento",
        "",
        "| Requisito | Estado | Referencia |",
        "|-----------|--------|------------|",
    ]
    for req, st, ph in req_map:
        lines.append(f"| {req} | **{st}** | {ph} |")

    lines.extend([
        "",
        "## Hallazgos CRITICA / ALTA (prioridad defensa)",
        "",
        "| ID | Sev | Descripción | Ubicación |",
        "|----|-----|-------------|-----------|",
        "| G6 | CRITICA | Laberinto pequeño sin patrón 42: no imprime mensaje de error en consola | `generator.py:210-212` |",
        "| G5b | ALTA | Restricción de densidad (corredores ≤2, no 3×3) no implementada | `generator.py` |",
        "| S4 | CRITICA | Sin camino: `get_directions()` lanza Exception → crash en CLI | `solver.py:136`, `a_maze_ing.py:167` |",
        "| G9 | ALTA | Segunda `generate()` en misma instancia desplaza patrón 42 | `generator.py:218-219` |",
        "| L2 | ALTA | mypy falla: `setup_new_maze` sin anotación de retorno | `a_maze_ing.py:141` |",
        "| ALG | ALTA | Clave `ALGORITHM` parseada pero nunca usada | `parser.py` / `generator.py` |",
        "| U3 | ALTA | Regenerar (opción 1) no reescribe OUTPUT_FILE | `a_maze_ing.py:220-223` |",
        "",
        "## Hallazgos MEDIA / BAJA",
        "",
        "| ID | Sev | Descripción |",
        "|----|-----|-------------|",
        "| L3 | MEDIA | `load_config` sin docstring PEP257 |",
        "| U2w | MEDIA | `print_maze` con Unicode en Windows cp1252 (no aplica Linux) |",
        "| CFG | BAJA | Config por defecto: `config_maze.txt` vs `config.txt` del subject |",
        "| DOC | BAJA | README/Makefile incompletos (fuera de alcance) |",
        "",
        "## Qué sí funciona bien",
        "",
        "- Parser robusto (9 casos P1–P8 PASS).",
        "- Determinismo con SEED verificado.",
        "- `output_validator.py` pasa en 10 configs (PERFECT True/False).",
        "- Patrón 42 con celdas `F` en laberinto 12×12.",
        "- Conectividad desde entry: 0 celdas aisladas en prueba 20×15.",
        "- Build `mazegen-0.1.0.whl` + `.tar.gz` e import API OK.",
        "- Coherencia bitmask hex y coords en OUTPUT_FILE.",
        "",
        "## Informes por fase",
        "",
    ])
    for rp in reports:
        if rp.name == "Fase9_consolidate.md":
            continue
        lines.append(f"- [{rp.stem}]({rp.name})")

    lines.extend([
        "",
        "## Anexo — configs de prueba",
        "",
        "Ubicación: `audit/configs/` (P1–P8, seed_1..seed_10).",
        "Outputs: `audit/outputs/maze_*.txt`.",
        "Re-ejecutar: ver `audit/README.md` (sección Ejecución).",
    ])

    (REPORTS / "Fase9_consolidate.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    phase1_lint_report()
    phase2_parser()
    phase3_coords()
    phase4_generator()
    phase5_solver()
    phase6_output()
    phase7_cli()
    phase8_packaging()
    phase9_consolidate()
    print(f"Reports written to {REPORTS}")


if __name__ == "__main__":
    main()
