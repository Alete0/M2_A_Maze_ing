"""Tests for mazegen.generator — subject IV.4 maze requirements."""

from __future__ import annotations

import copy

import pytest

from conftest import (
    EAST,
    NORTH,
    SOUTH,
    WEST,
    check_bidirectional,
    check_no_3x3_open,
    count_open_edges,
    flood_fill,
)
from mazegen.generator import MazeGenerator


@pytest.mark.parametrize("w,h,seed", [(10, 10, 42), (20, 15, 99), (15, 15, 77)])
def test_invariantes_estructurales_parametrized(w, h, seed, generated_maze):
    """IV.4: bidirectional walls and spanning tree on multiple sizes."""
    entry = (0, 0)
    exit_c = (h - 1, w - 1)
    gen, maze, _, _ = generated_maze(w, h, entry, exit_c, seed=seed, perfect=True)
    check_bidirectional(maze)
    pattern_cells = len(gen.pattern) if gen._pattern_fits else 0
    vertices = w * h - pattern_cells
    assert count_open_edges(maze) == vertices - 1


def test_coherencia_bidireccional_muros(generated_maze):
    """IV.4: each neighbouring cell must have the same wall if any."""
    _, maze, _, _ = generated_maze(10, 10, (0, 0), (9, 9), seed=42, perfect=True)
    check_bidirectional(maze)


def test_perfect_maze_spanning_tree(generated_maze):
    """IV.4: perfect maze = spanning tree (V-1 open edges)."""
    w, h = 20, 15
    gen, maze, _, _ = generated_maze(w, h, (0, 0), (14, 19), seed=99, perfect=True)
    pattern_cells = len(gen.pattern) if gen._pattern_fits else 0
    vertices = w * h - pattern_cells
    assert count_open_edges(maze) == vertices - 1


def test_conectividad_total_y_aislamiento_42(generated_maze):
    """IV.4: only pattern 42 cells may be isolated."""
    w, h = 15, 15
    gen, maze, entry, _ = generated_maze(w, h, (0, 0), (14, 14), seed=77, perfect=True)
    visited = flood_fill(maze, entry)
    all_cells = {(r, c) for r in range(h) for c in range(w)}
    isolated = all_cells - visited
    pattern_cells = set(gen.pattern) if gen._pattern_fits else set()
    assert isolated == pattern_cells


def test_restriccion_densidad_sin_areas_3x3():
    """IV.4: never a 3x3 open area (imperfect mode)."""
    gen = MazeGenerator(20, 20, seed=123, perfect=False)
    gen.generate((0, 0), (19, 19))
    check_no_3x3_open(gen.get_maze())


def test_determinismo_misma_semilla():
    """IV.4: reproducibility via seed."""
    gen1 = MazeGenerator(12, 12, seed=42, perfect=True)
    gen1.generate((0, 0), (11, 11))
    maze1 = copy.deepcopy(gen1.get_maze())

    gen2 = MazeGenerator(12, 12, seed=42, perfect=True)
    gen2.generate((0, 0), (11, 11))
    assert gen1.get_maze() == maze1 == gen2.get_maze()


def test_semilla_cero_reproducible():
    """Edge: SEED=0 must still fix randomness (not treated as falsy)."""
    gen_a = MazeGenerator(10, 10, seed=0, perfect=True)
    gen_a.generate((0, 0), (9, 9))
    gen_b = MazeGenerator(10, 10, seed=0, perfect=True)
    gen_b.generate((0, 0), (9, 9))
    assert gen_a.get_maze() == gen_b.get_maze()


def test_muros_bordes_externos_cerrados(generated_maze):
    """IV.4: external borders must have closed walls."""
    _, maze, _, _ = generated_maze(10, 10, (0, 0), (9, 9), seed=5, perfect=True)
    h, w = len(maze), len(maze[0])
    for c in range(w):
        assert maze[0][c] & NORTH
        assert maze[h - 1][c] & SOUTH
    for r in range(h):
        assert maze[r][0] & WEST
        assert maze[r][w - 1] & EAST


def test_patron_42_celdas_totalmente_cerradas(generated_maze):
    """IV.4: pattern cells are fully closed (hex F = 15)."""
    gen, maze, _, _ = generated_maze(15, 15, (0, 0), (14, 14), seed=3, perfect=True)
    if not gen._pattern_fits:
        pytest.skip("Pattern does not fit")
    for r, c in gen.pattern:
        assert maze[r][c] == 15


def test_mapa_pequeno_sin_patron_sigue_valido(capsys):
    """IV.4: small maze without pattern still structurally valid."""
    gen = MazeGenerator(5, 5, seed=1, perfect=True)
    gen.generate((0, 0), (4, 4))
    capsys.readouterr()
    maze = gen.get_maze()
    assert gen._pattern_fits is False
    check_bidirectional(maze)
    visited = flood_fill(maze, (0, 0))
    assert len(visited) == 5 * 5


def test_entry_en_patron_42_aborta(capsys):
    """IV.4: ENTRY on pattern → error and exit."""
    gen = MazeGenerator(15, 15, seed=1, perfect=True)
    gen.pattern_42()
    entry_on_pattern = gen.pattern[0]
    with pytest.raises(SystemExit):
        gen.generate(entry_on_pattern, (14, 14))
    assert "42" in capsys.readouterr().err


def test_perfect_false_mantiene_coherencia_y_sin_3x3():
    """IV.4: imperfect maze keeps bidirectional walls and no 3x3."""
    gen = MazeGenerator(15, 15, seed=88, perfect=False)
    gen.generate((0, 0), (14, 14))
    maze = gen.get_maze()
    check_bidirectional(maze)
    check_no_3x3_open(maze)
    pattern_cells = len(gen.pattern) if gen._pattern_fits else 0
    vertices = 15 * 15 - pattern_cells
    assert count_open_edges(maze) >= vertices - 1


def test_valores_celda_en_rango_4_bits(generated_maze):
    _, maze, _, _ = generated_maze(10, 10, (0, 0), (9, 9), seed=1, perfect=True)
    for row in maze:
        for cell in row:
            assert 0 <= cell <= 15


def test_neighbor_coords_cuatro_direcciones():
    assert MazeGenerator.neighbor_coords((2, 2), 0) == (1, 2)
    assert MazeGenerator.neighbor_coords((2, 2), 1) == (2, 3)
    assert MazeGenerator.neighbor_coords((2, 2), 2) == (3, 2)
    assert MazeGenerator.neighbor_coords((2, 2), 3) == (2, 1)


def test_neighbor_coords_invalido_lanza():
    with pytest.raises(Exception, match="Unknown"):
        MazeGenerator.neighbor_coords((0, 0), 9)


@pytest.mark.parametrize(
    "coord,expected",
    [((0, 0), False), ((-1, 0), True), ((9, 9), False), ((10, 0), True)],
)
def test_out_of_bounds(coord, expected):
    gen = MazeGenerator(10, 10)
    assert gen.out_of_bounds(coord) is expected


def test_open_wall_coherencia_cuatro_direcciones():
    gen = MazeGenerator(3, 3, perfect=True)
    gen.generate((0, 0), (2, 2))
    maze = [[15, 15, 15], [15, 15, 15], [15, 15, 15]]
    gen._maze = maze
    gen.open_wall((1, 1), (1, 2), 1)
    assert not (gen._maze[1][1] & EAST)
    assert not (gen._maze[1][2] & WEST)
    gen.open_wall((1, 1), (0, 1), 0)
    assert not (gen._maze[1][1] & NORTH)
    assert not (gen._maze[0][1] & SOUTH)


def test_g6_mensaje_error_laberinto_pequeno(capsys):
    """IV.4: print error when maze too small for 42 pattern."""
    gen = MazeGenerator(5, 5, seed=1, perfect=True)
    gen.generate((0, 0), (4, 4))
    captured = capsys.readouterr()
    assert gen._pattern_fits is False
    assert captured.err.strip() != ""


def test_g9_doble_generacion_mantiene_patron_y_grid():
    """VI: reusability — second generate must not corrupt state."""
    gen = MazeGenerator(12, 12, seed=1, perfect=True)
    gen.generate((0, 0), (11, 11))
    patron_original = list(gen.pattern)
    grid_original = copy.deepcopy(gen.get_maze())

    gen.generate((0, 0), (11, 11))
    assert list(gen.pattern) == patron_original
    assert gen.get_maze() == grid_original


def test_semillas_distintas_producen_grids_distintos():
    gen_a = MazeGenerator(10, 10, seed=1, perfect=True)
    gen_a.generate((0, 0), (9, 9))
    gen_b = MazeGenerator(10, 10, seed=2, perfect=True)
    gen_b.generate((0, 0), (9, 9))
    assert gen_a.get_maze() != gen_b.get_maze()


@pytest.mark.slow
def test_g8_limite_recursividad_50x50():
    """IV.2: must not crash on 50x50."""
    gen = MazeGenerator(50, 50, seed=1, perfect=True)
    try:
        gen.generate((0, 0), (49, 49))
    except RecursionError:
        pytest.fail("RecursionError on 50x50 maze")
