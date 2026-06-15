"""Shared fixtures and maze validation helpers for the test suite."""

from __future__ import annotations

import sys
from collections.abc import Callable
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from mazegen.generator import MazeGenerator  # noqa: E402

# Subject IV.5 bit masks
NORTH = 0b0001
EAST = 0b0010
SOUTH = 0b0100
WEST = 0b1000

Coord = tuple[int, int]
Grid = list[list[int]]

WriteConfig = Callable[[str], Path]
GeneratedMazeFactory = Callable[
    ..., tuple[MazeGenerator, Grid, Coord, Coord]
]


def check_bidirectional(maze: Grid) -> None:
    """IV.4: neighbouring cells must share wall state on both sides."""
    height = len(maze)
    width = len(maze[0]) if height else 0
    for r in range(height):
        for c in range(width):
            if c < width - 1:
                east_ok = (
                    bool(maze[r][c] & EAST) == bool(maze[r][c + 1] & WEST)
                )
                assert east_ok, f"E/W incoherence at ({r},{c})"
            if r < height - 1:
                south_ok = bool(maze[r][c] & SOUTH) == bool(
                    maze[r + 1][c] & NORTH
                )
                assert south_ok, f"N/S incoherence at ({r},{c})"


def flood_fill(maze: Grid, start: Coord) -> set[Coord]:
    """Return all cells reachable from start without crossing closed walls."""
    height = len(maze)
    width = len(maze[0]) if height else 0
    visited: set[Coord] = set()
    stack = [start]
    while stack:
        r, c = stack.pop()
        if (r, c) in visited:
            continue
        visited.add((r, c))
        cell = maze[r][c]
        if not (cell & NORTH) and r > 0:
            stack.append((r - 1, c))
        if not (cell & SOUTH) and r < height - 1:
            stack.append((r + 1, c))
        if not (cell & EAST) and c < width - 1:
            stack.append((r, c + 1))
        if not (cell & WEST) and c > 0:
            stack.append((r, c - 1))
    return visited


def check_no_3x3_open(maze: Grid) -> None:
    """IV.4: corridors cannot form a fully open 3x3 area."""
    height = len(maze)
    width = len(maze[0]) if height else 0
    for r in range(height - 2):
        for c in range(width - 2):
            is_open = True
            for sub_r in range(r, r + 3):
                for sub_c in range(c, c + 2):
                    if maze[sub_r][sub_c] & EAST:
                        is_open = False
            for sub_r in range(r, r + 2):
                for sub_c in range(c, c + 3):
                    if maze[sub_r][sub_c] & SOUTH:
                        is_open = False
            assert not is_open, f"3x3 open area at ({r},{c})"


def count_open_edges(maze: Grid) -> int:
    """Count undirected open passages (east/south edges only)."""
    height = len(maze)
    width = len(maze[0]) if height else 0
    edges = 0
    for r in range(height):
        for c in range(width):
            if c < width - 1 and not (maze[r][c] & EAST):
                edges += 1
            if r < height - 1 and not (maze[r][c] & SOUTH):
                edges += 1
    return edges


def walk_path(maze: Grid, entry: Coord, directions: str) -> Coord:
    """Walk a NESW path; raise AssertionError if a closed wall is crossed."""
    r, c = entry
    for step in directions:
        if step == "N":
            assert not (maze[r][c] & NORTH), f"Cannot go N from ({r},{c})"
            r -= 1
        elif step == "S":
            assert not (maze[r][c] & SOUTH), f"Cannot go S from ({r},{c})"
            r += 1
        elif step == "E":
            assert not (maze[r][c] & EAST), f"Cannot go E from ({r},{c})"
            c += 1
        elif step == "W":
            assert not (maze[r][c] & WEST), f"Cannot go W from ({r},{c})"
            c -= 1
        else:
            continue
    return (r, c)


# Top-row corridor from (0,0) to (0,4)
MOCK_GRID_CORRIDOR: Grid = [
    [13, 5, 5, 5, 7],
    [15, 15, 15, 15, 15],
    [15, 15, 15, 15, 15],
    [15, 15, 15, 15, 15],
    [15, 15, 15, 15, 15],
]

# 3x3 fully open interior — multiple shortest paths of length 4
MOCK_GRID_TWO_PATHS: Grid = [
    [0, 0, 0],
    [0, 0, 0],
    [0, 0, 0],
]

# Disconnected: (0,0) isolated from (2,2)
MOCK_GRID_DISCONNECTED: Grid = [
    [0b1111, 0b1111, 0b1111],
    [0b1111, 0b1111, 0b1111],
    [0b1111, 0b1111, 0b1111],
]


@pytest.fixture
def project_root() -> Path:
    return ROOT


@pytest.fixture
def write_config(tmp_path: Path) -> WriteConfig:
    """Factory: write a KEY=VALUE config file and return its path."""

    def _write(content: str) -> Path:
        path = tmp_path / "config.txt"
        path.write_text(content, encoding="utf-8")
        return path

    return _write


@pytest.fixture
def generated_maze() -> GeneratedMazeFactory:
    """Factory returning (generator, maze, entry, exit) after generate()."""

    def _generate(
        width: int,
        height: int,
        entry: Coord,
        exit_coord: Coord,
        seed: int | None = 42,
        perfect: bool = True,
    ) -> tuple[MazeGenerator, Grid, Coord, Coord]:
        gen = MazeGenerator(width, height, seed=seed, perfect=perfect)
        gen.generate(entry, exit_coord)
        return gen, gen.get_maze(), entry, exit_coord

    return _generate


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        'slow: marks tests as slow (deselect with \'-m "not slow"\')',
    )


def run_validator(output_path: Path) -> tuple[int, str]:
    """Run subject output_validator.py on a maze output file."""
    import subprocess

    validator = ROOT / "output_validator.py"
    if not validator.is_file():
        pytest.skip("output_validator.py not found")
    result = subprocess.run(
        [sys.executable, str(validator), str(output_path)],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    return result.returncode, result.stdout + result.stderr


def parse_output_file(path: Path) -> tuple[Grid, Coord, Coord, str]:
    """Parse hex grid + metadata from OUTPUT_FILE format."""
    lines = path.read_text(encoding="utf-8").splitlines()
    grid_end = lines.index("")
    grid = [[int(ch, 16) for ch in row] for row in lines[:grid_end]]
    entry_parts = lines[grid_end + 1].split(",")
    exit_parts = lines[grid_end + 2].split(",")
    entry = (int(entry_parts[0]), int(entry_parts[1]))
    exit_c = (int(exit_parts[0]), int(exit_parts[1]))
    path_solution = lines[grid_end + 3] if len(lines) > grid_end + 3 else ""
    return grid, entry, exit_c, path_solution
