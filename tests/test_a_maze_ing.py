"""Tests for a_maze_ing.py — CLI helpers and rendering."""

from __future__ import annotations

import subprocess
import sys
from unittest.mock import patch

from a_maze_ing import path_to_exit, print_maze, setup_new_maze
from conftest import ROOT, walk_path
from parser import MazeConfig


def test_path_to_exit_basic():
    coords = path_to_exit((0, 0), "EES")
    assert coords == {(0, 0), (0, 1), (0, 2), (1, 2)}


def test_path_to_exit_includes_entry_only_when_empty():
    assert path_to_exit((3, 4), "") == {(3, 4)}


def test_path_to_exit_ignores_invalid_chars():
    coords = path_to_exit((0, 0), "ExE")
    assert coords == {(0, 0), (0, 1), (0, 2)}


def test_setup_new_maze_swaps_config_xy_to_row_col():
    """Config (x,y) must map to internal (row,col)=(y,x)."""
    cfg = MazeConfig(
        width=10,
        height=10,
        entry=(0, 0),
        exit=(9, 9),
        output_file="o.txt",
        perfect=True,
        seed=42,
    )
    maze, directions = setup_new_maze(cfg, use_seed=True)
    internal_entry = (cfg.entry[1], cfg.entry[0])
    internal_exit = (cfg.exit[1], cfg.exit[0])
    end = walk_path(maze.get_maze(), internal_entry, directions)
    assert end == internal_exit


def test_print_maze_shows_entry_and_exit(capsys):
    maze = [[0b0101, 0b0101], [0b1111, 0b1111]]
    print_maze(maze, (0, 0), (0, 1), "", False, "\033[34m", set())
    out = capsys.readouterr().out
    assert " E " in out
    assert " X " in out


def test_print_maze_shows_path_marker(capsys):
    maze = [
        [0b0101, 0b0101, 0b0101],
        [0b1111, 0b1111, 0b1111],
    ]
    print_maze(maze, (0, 0), (0, 2), "E", True, "\033[34m", set())
    out = capsys.readouterr().out
    assert "●" in out


def test_print_maze_different_colors(capsys):
    maze = [[0b1111]]
    print_maze(maze, (0, 0), (0, 0), "", False, "\033[31m", set())
    red_out = capsys.readouterr().out
    print_maze(maze, (0, 0), (0, 0), "", False, "\033[32m", set())
    green_out = capsys.readouterr().out
    assert "\033[31m" in red_out
    assert "\033[32m" in green_out


def test_print_maze_single_cell_no_crash(capsys):
    print_maze([[15]], (0, 0), (0, 0), "", False, "\033[34m", set())
    assert capsys.readouterr().out


def test_cli_no_arguments():
    result = subprocess.run(
        [sys.executable, str(ROOT / "a_maze_ing.py")],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    assert result.returncode != 0
    out_lower = result.stdout.lower()
    err_lower = result.stderr.lower()
    assert "usage" in out_lower or "usage" in err_lower


def test_cli_invalid_config(tmp_path):
    bad = tmp_path / "bad.txt"
    bad.write_text("WIDTH=10\n", encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(ROOT / "a_maze_ing.py"), str(bad)],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    assert result.returncode != 0


def _utf8_env() -> dict[str, str]:
    import os

    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    return env


def test_cli_valid_config_writes_output(tmp_path):
    out_file = tmp_path / "out_maze.txt"
    cfg = tmp_path / "cfg.txt"
    cfg.write_text(
        f"WIDTH=12\nHEIGHT=12\nENTRY=0,0\nEXIT=11,11\n"
        f"OUTPUT_FILE={out_file}\nPERFECT=True\nSEED=99\n",
        encoding="utf-8",
    )
    result = subprocess.run(
        [sys.executable, str(ROOT / "a_maze_ing.py"), str(cfg)],
        input="4\n",
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(ROOT),
        timeout=30,
        env=_utf8_env(),
    )
    assert result.returncode == 0
    assert out_file.is_file()


def test_menu_quit_via_mock_input(capsys):
    """Cap. V: option 4 quits without crash."""
    cfg = MazeConfig(
        width=8,
        height=8,
        entry=(0, 0),
        exit=(7, 7),
        output_file="unused.txt",
        perfect=True,
        seed=1,
    )
    maze, directions = setup_new_maze(cfg)
    entry = (cfg.entry[1], cfg.entry[0])
    exit_c = (cfg.exit[1], cfg.exit[0])
    pattern_cells = (
        set(maze.pattern) if maze._pattern_fits else set()
    )

    with patch("builtins.input", side_effect=["2", "4"]):
        show_path = True
        while True:
            print_maze(
                maze.get_maze(), entry, exit_c, directions,
                show_path, "\033[34m", pattern_cells,
            )
            choice = __import__("builtins").input("Choice? ")
            if choice == "2":
                show_path = not show_path
            elif choice == "4":
                break
    assert show_path is False
