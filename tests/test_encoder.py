"""Tests for encoder.py — subject IV.5 output file format."""

from __future__ import annotations

import pytest

from conftest import run_validator
from encoder import gen_maze_file, line_to_hex


@pytest.mark.parametrize(
    "value,expected",
    [
        (0, "0"),
        (1, "1"),
        (2, "2"),
        (3, "3"),
        (4, "4"),
        (5, "5"),
        (6, "6"),
        (7, "7"),
        (8, "8"),
        (9, "9"),
        (10, "A"),
        (11, "B"),
        (12, "C"),
        (13, "D"),
        (14, "E"),
        (15, "F"),
    ],
)
def test_line_to_hex_truth_table(value, expected):
    """IV.5: each hex digit encodes wall bits 0..F."""
    assert line_to_hex([value]) == expected


def test_line_to_hex_subject_examples():
    """IV.5: 3 = N+E closed; A = E+W closed."""
    assert line_to_hex([3]) == "3"
    assert line_to_hex([10]) == "A"


def test_line_to_hex_full_row():
    assert line_to_hex([0, 3, 10, 15]) == "03AF"


def test_gen_maze_file_structure(tmp_path):
    """IV.5 + HOJA_DE_RUTA §1.6: hex rows, blank line, entry, exit, path."""
    maze = [[15, 0], [0, 15]]
    out = tmp_path / "maze.txt"
    gen_maze_file(str(out), maze, (0, 0), (1, 1), "ES")

    raw = out.read_bytes()
    assert raw.endswith(b"\n")
    lines = raw.decode("utf-8").splitlines()
    assert lines[0] == "F0"
    assert lines[1] == "0F"
    assert lines[2] == ""
    assert lines[3] == "0,0"
    assert lines[4] == "1,1"
    assert lines[5] == "ES"


def test_gen_maze_file_all_lines_end_with_newline(tmp_path):
    maze = [[0]]
    out = tmp_path / "single.txt"
    gen_maze_file(str(out), maze, (0, 0), (0, 0), "")
    data = out.read_bytes()
    assert data.endswith(b"\n")
    parts = data.decode("utf-8").splitlines()
    assert parts[0] == "0"
    assert parts[1] == ""
    assert parts[2] == "0,0"
    assert parts[3] == "0,0"
    assert parts[4] == ""


def test_gen_maze_file_empty_path_solution(tmp_path):
    maze = [[15]]
    out = tmp_path / "nopath.txt"
    gen_maze_file(str(out), maze, (0, 0), (0, 0), path_solution="")
    content = out.read_text(encoding="utf-8")
    assert content.split("\n")[4] == ""


def test_gen_maze_file_passes_output_validator(tmp_path):
    """Round-trip: generated file must pass subject output_validator.py."""
    maze = [
        [0b1111, 0b0111, 0b1111],
        [0b0101, 0b0000, 0b1010],
        [0b1111, 0b1110, 0b1111],
    ]
    out = tmp_path / "valid_maze.txt"
    gen_maze_file(str(out), maze, (0, 0), (2, 2), "EES")
    code, output = run_validator(out)
    assert code == 0, output


def test_gen_maze_file_write_error(capsys, tmp_path):
    bad_path = str(tmp_path / "missing" / "dir" / "out.txt")
    with pytest.raises(SystemExit) as exc:
        gen_maze_file(bad_path, [[0]], (0, 0), (0, 0))
    assert exc.value.code == 1
    assert "error" in capsys.readouterr().err.lower()
