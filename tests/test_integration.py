"""End-to-end integration tests — subject IV.5 pipeline + output_validator."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from a_maze_ing import setup_new_maze
from conftest import (
    ROOT,
    check_bidirectional,
    check_no_3x3_open,
    flood_fill,
    parse_output_file,
    run_validator,
    walk_path,
)
from encoder import gen_maze_file
from parser import load_config


def _write_config(tmp_path: Path, **overrides: str) -> Path:
    defaults = {
        "WIDTH": "12",
        "HEIGHT": "12",
        "ENTRY": "0,0",
        "EXIT": "11,11",
        "OUTPUT_FILE": str(tmp_path / "maze_out.txt"),
        "PERFECT": "True",
        "SEED": "42",
    }
    defaults.update(overrides)
    path = tmp_path / "config.txt"
    path.write_text(
        "\n".join(f"{k}={v}" for k, v in defaults.items()) + "\n",
        encoding="utf-8",
    )
    return path


def test_pipeline_programatic(tmp_path: Path) -> None:
    """load_config → setup_new_maze → gen_maze_file → parse output."""
    cfg_path = _write_config(tmp_path)
    cfg = load_config(str(cfg_path))
    maze, directions = setup_new_maze(cfg, use_seed=True)
    out = Path(cfg.output_file)
    gen_maze_file(str(out), maze.get_maze(), cfg.entry, cfg.exit, directions)

    grid, entry, exit_c, path_str = parse_output_file(out)
    assert entry == cfg.entry
    assert exit_c == cfg.exit
    assert path_str == directions
    check_bidirectional(grid)

    internal_entry = (cfg.entry[1], cfg.entry[0])
    internal_exit = (cfg.exit[1], cfg.exit[0])
    assert walk_path(grid, internal_entry, path_str) == internal_exit


def test_output_file_blank_line_and_newlines(tmp_path: Path) -> None:
    cfg_path = _write_config(tmp_path)
    cfg = load_config(str(cfg_path))
    maze, directions = setup_new_maze(cfg)
    out = Path(cfg.output_file)
    gen_maze_file(str(out), maze.get_maze(), cfg.entry, cfg.exit, directions)

    lines = out.read_text(encoding="utf-8").splitlines()
    assert lines[cfg.height] == ""


def test_output_passes_validator(tmp_path: Path) -> None:
    cfg_path = _write_config(tmp_path)
    cfg = load_config(str(cfg_path))
    maze, directions = setup_new_maze(cfg)
    out = Path(cfg.output_file)
    gen_maze_file(str(out), maze.get_maze(), cfg.entry, cfg.exit, directions)
    code, msg = run_validator(out)
    assert code == 0, msg


@pytest.mark.parametrize("seed", [1, 7, 42, 99, 123])
def test_multiple_seeds_pass_validator_and_invariants(
    tmp_path: Path, seed: int,
) -> None:
    cfg_path = _write_config(tmp_path, SEED=str(seed))
    cfg = load_config(str(cfg_path))
    maze, directions = setup_new_maze(cfg)
    out = Path(cfg.output_file)
    gen_maze_file(str(out), maze.get_maze(), cfg.entry, cfg.exit, directions)

    code, msg = run_validator(out)
    assert code == 0, msg
    grid = maze.get_maze()
    check_bidirectional(grid)
    if not cfg.perfect:
        check_no_3x3_open(grid)


def test_perfect_true_and_false_both_valid(tmp_path: Path) -> None:
    for perfect in ("True", "False"):
        cfg_path = _write_config(
            tmp_path,
            PERFECT=perfect,
            OUTPUT_FILE=str(tmp_path / f"maze_{perfect}.txt"),
        )
        cfg = load_config(str(cfg_path))
        maze, directions = setup_new_maze(cfg)
        out = Path(cfg.output_file)
        gen_maze_file(
            str(out), maze.get_maze(), cfg.entry, cfg.exit, directions,
        )
        code, _ = run_validator(out)
        assert code == 0


def test_cli_subprocess_generates_file(tmp_path: Path) -> None:
    out_file = tmp_path / "cli_maze.txt"
    cfg = _write_config(tmp_path, OUTPUT_FILE=str(out_file))
    import os

    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    result = subprocess.run(
        [sys.executable, str(ROOT / "a_maze_ing.py"), str(cfg)],
        input="4\n",
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(ROOT),
        timeout=60,
        env=env,
    )
    assert result.returncode == 0
    assert out_file.is_file()
    code, msg = run_validator(out_file)
    assert code == 0, msg


def test_connectivity_after_imperfect_generation(tmp_path: Path) -> None:
    cfg_path = _write_config(tmp_path, PERFECT="False", SEED="55")
    cfg = load_config(str(cfg_path))
    maze, _ = setup_new_maze(cfg)
    grid = maze.get_maze()
    entry = (cfg.entry[1], cfg.entry[0])
    visited = flood_fill(grid, entry)
    pattern = set(maze.pattern) if maze._pattern_fits else set()
    all_cells = {(r, c) for r in range(cfg.height) for c in range(cfg.width)}
    isolated = all_cells - visited
    assert isolated == pattern
