"""Tests for mazegen.solver — BFS pathfinding."""

from __future__ import annotations

import pytest

from conftest import (
    GeneratedMazeFactory,
    MOCK_GRID_CORRIDOR,
    MOCK_GRID_DISCONNECTED,
    MOCK_GRID_TWO_PATHS,
    walk_path,
)
from mazegen.generator import MazeGenerator
from mazegen.solver import MazeSolver, NoSolutionError


@pytest.mark.parametrize(
    "cell,expected_neighbors",
    [
        (0b1111, []),
        (0b1110, [0]),
        (0b0101, [1, 3]),
        (0b0000, [0, 1, 2, 3]),
        (0b1010, [0, 2]),
    ],
)
def test_get_available_neighbors(
    cell: int, expected_neighbors: list[int],
) -> None:
    assert MazeSolver.get_available_neighbors(cell) == expected_neighbors


@pytest.mark.parametrize(
    "current,next_cell,expected",
    [
        ((0, 0), (0, 1), "E"),
        ((0, 1), (0, 0), "W"),
        ((0, 0), (1, 0), "S"),
        ((1, 0), (0, 0), "N"),
    ],
)
def test_direction(
    current: tuple[int, int],
    next_cell: tuple[int, int],
    expected: str,
) -> None:
    assert MazeSolver.direction(current, next_cell) == expected


def test_neighbor_coords_and_out_of_bounds() -> None:
    solver = MazeSolver(5, 5)
    assert solver.neighbor_coords((2, 2), 1) == (2, 3)
    assert solver.out_of_bounds((-1, 0)) is True
    assert solver.out_of_bounds((4, 4)) is False


def test_solve_corridor_shortest_path() -> None:
    solver = MazeSolver(5, 5)
    solver.solve(MOCK_GRID_CORRIDOR, (0, 0), (0, 4))
    assert len(solver._path_cell) == 5
    dirs = solver.get_directions()
    assert dirs == "EEEE"
    end = walk_path(MOCK_GRID_CORRIDOR, (0, 0), dirs)
    assert end == (0, 4)


def test_solve_two_paths_picks_shortest() -> None:
    solver = MazeSolver(3, 3)
    solver.solve(MOCK_GRID_TWO_PATHS, (0, 0), (2, 2))
    dirs = solver.get_directions()
    assert len(dirs) == 4
    end = walk_path(MOCK_GRID_TWO_PATHS, (0, 0), dirs)
    assert end == (2, 2)


def test_solve_disconnected_no_path() -> None:
    solver = MazeSolver(3, 3)
    solver.solve(MOCK_GRID_DISCONNECTED, (0, 0), (2, 2))
    assert solver._path_cell == []
    with pytest.raises(NoSolutionError, match="No solutions"):
        solver.get_directions()


def test_walk_path_respects_walls() -> None:
    solver = MazeSolver(5, 5)
    solver.solve(MOCK_GRID_CORRIDOR, (0, 0), (0, 4))
    walk_path(MOCK_GRID_CORRIDOR, (0, 0), solver.get_directions())


def test_solver_integration_with_generator(
    generated_maze: GeneratedMazeFactory,
) -> None:
    gen, maze, entry, exit_c = generated_maze(10, 10, (0, 0), (9, 9), seed=42)
    solver = MazeSolver(10, 10)
    solver.solve(maze, entry, exit_c)
    dirs = solver.get_directions()
    assert walk_path(maze, entry, dirs) == exit_c


def test_imperfect_maze_still_solvable() -> None:
    gen = MazeGenerator(12, 12, seed=55, perfect=False)
    gen.generate((0, 0), (11, 11))
    maze = gen.get_maze()
    solver = MazeSolver(12, 12)
    solver.solve(maze, (0, 0), (11, 11))
    dirs = solver.get_directions()
    assert walk_path(maze, (0, 0), dirs) == (11, 11)
