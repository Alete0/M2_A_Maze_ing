import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from mazegen.generator import MazeGenerator

# Máscaras de bits (subject IV.5)
NORTH = 0b0001
EAST = 0b0010
SOUTH = 0b0100
WEST = 0b1000

# =====================================================================
# 1. PRUEBAS DE EXIGENCIA MATEMÁTICA Y ESTRUCTURAL
# =====================================================================

def test_coherencia_bidireccional_muros():
    """
    SUBJECT IV.4: "each neighbouring cell must have the same wall if any".
    Verifica que si la celda A tiene una pared Este, su vecina Este tiene una pared Oeste.
    """
    gen = MazeGenerator(10, 10, seed=42, perfect=True)
    gen.generate((0, 0), (9, 9))
    maze = gen.get_maze()

    for r in range(10):
        for c in range(10):
            # Comprobar pared Este vs Oeste del vecino
            if c < 9:
                tiene_este = bool(maze[r][c] & EAST)
                vecino_tiene_oeste = bool(maze[r][c+1] & WEST)
                assert tiene_este == vecino_tiene_oeste, f"Incoherencia horizontal en {(r,c)} y {(r, c+1)}"
            
            # Comprobar pared Sur vs Norte del vecino
            if r < 9:
                tiene_sur = bool(maze[r][c] & SOUTH)
                vecino_tiene_norte = bool(maze[r+1][c] & NORTH)
                assert tiene_sur == vecino_tiene_norte, f"Incoherencia vertical en {(r,c)} y {(r+1, c)}"

def test_perfect_maze_spanning_tree():
    """
    SUBJECT IV.4: "exactly one path between the entry and the exit".
    Demostración matemática: Un Spanning Tree perfecto en un grafo de V vértices tiene exactamente V-1 aristas.
    """
    w, h = 20, 15
    gen = MazeGenerator(w, h, seed=99, perfect=True)
    gen.generate((0, 0), (14, 19))
    maze = gen.get_maze()

    # Vértices (Celdas válidas)
    total_cells = w * h
    pattern_cells = len(gen.pattern) if gen._pattern_fits else 0
    vertices = total_cells - pattern_cells

    # Aristas (Pasillos abiertos). Contamos solo Este y Sur para no duplicar.
    aristas = 0
    for r in range(h):
        for c in range(w):
            if c < w - 1 and (maze[r][c] & EAST) == 0:
                aristas += 1
            if r < h - 1 and (maze[r][c] & SOUTH) == 0:
                aristas += 1

    assert aristas == vertices - 1, f"Fallo estructural: No es un Spanning Tree. Vértices={vertices}, Aristas={aristas}"

def test_conectividad_total_y_aislamiento_42():
    """
    SUBJECT IV.4: "The structure ensures full connectivity and no isolated cells".
    Las únicas celdas aisladas DEBEN ser exclusivamente las del patrón 42.
    """
    w, h = 15, 15
    gen = MazeGenerator(w, h, seed=77, perfect=True)
    gen.generate((0, 0), (14, 14))
    maze = gen.get_maze()

    visited = set()
    stack = [(0, 0)] # Entry

    # Flood Fill
    while stack:
        r, c = stack.pop()
        if (r, c) in visited: continue
        visited.add((r, c))
        
        cell = maze[r][c]
        if not (cell & NORTH) and r > 0: stack.append((r - 1, c))
        if not (cell & SOUTH) and r < h - 1: stack.append((r + 1, c))
        if not (cell & EAST) and c < w - 1: stack.append((r, c + 1))
        if not (cell & WEST) and c > 0: stack.append((r, c - 1))

    todas_las_celdas = {(r, c) for r in range(h) for c in range(w)}
    celdas_aisladas = todas_las_celdas - visited
    celdas_patron = set(gen.pattern) if gen._pattern_fits else set()

    assert celdas_aisladas == celdas_patron, "Fallo: Hay celdas aisladas que no pertenecen al patrón 42, o el patrón no está aislado."

def test_restriccion_densidad_sin_areas_3x3():
    """
    SUBJECT IV.4: "never a 3x3 open area".
    """
    gen = MazeGenerator(20, 20, seed=123, perfect=False)
    gen.generate((0, 0), (19, 19))
    maze = gen.get_maze()

    for r in range(18):
        for c in range(18):
            is_open = True
            for sub_r in range(r, r + 3):
                for sub_c in range(c, c + 2):
                    if (maze[sub_r][sub_c] & EAST) != 0: is_open = False
            for sub_r in range(r, r + 2):
                for sub_c in range(c, c + 3):
                    if (maze[sub_r][sub_c] & SOUTH) != 0: is_open = False
            assert not is_open, f"Fallo G5b: Área 3x3 vacía en {(r, c)}"

# =====================================================================
# 2. PRUEBAS DE DEUDA TÉCNICA Y BUGS PENDIENTES
# =====================================================================

def test_g6_mensaje_error_laberinto_pequeno(capsys):
    """
    SUBJECT IV.4: "Print an error message on the console in that case".
    """
    gen = MazeGenerator(5, 5, seed=1, perfect=True)
    gen.generate((0, 0), (4, 4))
    
    captured = capsys.readouterr()
    assert gen._pattern_fits is False
    assert captured.err.strip() != "", "CRÍTICO G6: No se imprimió error en sys.stderr para mapa 5x5"

def test_g9_doble_generacion_corrompe_patron():
    """
    SUBJECT VI: "Code reusability requirements".
    La clase debe mantener integridad si se reutiliza.
    """
    gen = MazeGenerator(12, 12, seed=1, perfect=True)
    
    gen.generate((0, 0), (11, 11))
    patron_original = list(gen.pattern)
    
    gen.generate((0, 0), (11, 11))
    patron_segunda_vez = list(gen.pattern)
    
    assert patron_original == patron_segunda_vez, "CRÍTICO G9: El patrón 42 muta destructivamente en la segunda llamada."

def test_g8_limite_recursividad_50x50():
    """
    SUBJECT IV.2: "It must never crash unexpectedly".
    """
    gen = MazeGenerator(50, 50, seed=1, perfect=True)
    try:
        gen.generate((0, 0), (49, 49))
    except RecursionError:
        pytest.fail("CRÍTICO G8: RecursionError al generar mapa de 50x50. El DFS excede el límite del sistema.")