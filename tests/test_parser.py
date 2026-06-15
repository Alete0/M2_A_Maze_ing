"""Tests for parser.py — subject IV.3 configuration format."""

from __future__ import annotations

import pytest

from parser import MazeConfig, load_config


def test_valid_minimal_config(write_config):
    """IV.3: all mandatory keys produce a valid MazeConfig."""
    path = write_config(
        "WIDTH=20\n"
        "HEIGHT=15\n"
        "ENTRY=0,0\n"
        "EXIT=19,14\n"
        "OUTPUT_FILE=out.txt\n"
        "PERFECT=True\n"
    )
    cfg = load_config(str(path))
    assert cfg == MazeConfig(
        width=20,
        height=15,
        entry=(0, 0),
        exit=(19, 14),
        output_file="out.txt",
        perfect=True,
        seed=None,
        algorithm="backtracker",
    )


def test_comments_ignored(write_config):
    """IV.3: lines starting with # are comments."""
    path = write_config(
        "# header comment\n"
        "WIDTH=10\n"
        "HEIGHT=10\n"
        "ENTRY=1,1  # inline not supported but line parses\n"
        "EXIT=8,8\n"
        "OUTPUT_FILE=maze.txt\n"
        "PERFECT=false\n"
    )
    cfg = load_config(str(path))
    assert cfg.width == 10
    assert cfg.perfect is False


def test_keys_normalized_to_uppercase(write_config):
    path = write_config(
        "width=5\n"
        "height=5\n"
        "entry=0,0\n"
        "exit=4,4\n"
        "output_file=x.txt\n"
        "perfect=1\n"
    )
    cfg = load_config(str(path))
    assert cfg.width == 5
    assert cfg.perfect is True


@pytest.mark.parametrize(
    "perfect_val,expected",
    [
        ("True", True),
        ("false", False),
        ("1", True),
        ("0", False),
        ("yes", True),
        ("NO", False),
    ],
)
def test_perfect_boolean_variants(write_config, perfect_val, expected):
    path = write_config(
        f"WIDTH=10\nHEIGHT=10\nENTRY=0,0\nEXIT=9,9\n"
        f"OUTPUT_FILE=o.txt\nPERFECT={perfect_val}\n"
    )
    cfg = load_config(str(path))
    assert cfg.perfect is expected


def test_optional_seed_and_algorithm(write_config):
    path = write_config(
        "WIDTH=10\nHEIGHT=10\nENTRY=0,0\nEXIT=9,9\n"
        "OUTPUT_FILE=o.txt\nPERFECT=True\n"
        "SEED=42\nALGORITHM=prim\n"
    )
    cfg = load_config(str(path))
    assert cfg.seed == 42
    assert cfg.algorithm == "prim"


@pytest.mark.parametrize(
    "entry,exit_coord",
    [((0, 0), (9, 9)), ((0, 9), (9, 0)), ((9, 9), (0, 0))],
)
def test_boundary_coordinates(write_config, entry, exit_coord):
    path = write_config(
        f"WIDTH=10\nHEIGHT=10\n"
        f"ENTRY={entry[0]},{entry[1]}\n"
        f"EXIT={exit_coord[0]},{exit_coord[1]}\n"
        "OUTPUT_FILE=o.txt\nPERFECT=True\n"
    )
    cfg = load_config(str(path))
    assert cfg.entry == entry
    assert cfg.exit == exit_coord


def test_file_not_found(capsys):
    """IV.2: missing config file → clear error, exit 1."""
    with pytest.raises(SystemExit) as exc:
        load_config("this_file_does_not_exist_42.txt")
    assert exc.value.code == 1
    assert "not found" in capsys.readouterr().err.lower()


@pytest.mark.parametrize(
    "missing_key",
    ["WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"],
)
def test_missing_mandatory_key(write_config, capsys, missing_key):
    keys = {
        "WIDTH": "10",
        "HEIGHT": "10",
        "ENTRY": "0,0",
        "EXIT": "9,9",
        "OUTPUT_FILE": "o.txt",
        "PERFECT": "True",
    }
    del keys[missing_key]
    content = "\n".join(f"{k}={v}" for k, v in keys.items()) + "\n"
    path = write_config(content)
    with pytest.raises(SystemExit) as exc:
        load_config(str(path))
    assert exc.value.code == 1
    assert missing_key in capsys.readouterr().err


def test_line_without_equals(write_config, capsys):
    path = write_config(
        "WIDTH=10\nBADLINE\nHEIGHT=10\nENTRY=0,0\nEXIT=9,9\n"
        "OUTPUT_FILE=o.txt\nPERFECT=True\n"
    )
    with pytest.raises(SystemExit):
        load_config(str(path))
    err = capsys.readouterr().err.lower()
    assert "format" in err or "=" in err


def test_invalid_width_zero(write_config, capsys):
    path = write_config(
        "WIDTH=0\nHEIGHT=10\nENTRY=0,0\nEXIT=9,9\n"
        "OUTPUT_FILE=o.txt\nPERFECT=True\n"
    )
    with pytest.raises(SystemExit):
        load_config(str(path))
    assert capsys.readouterr().err.strip()


def test_invalid_width_non_numeric(write_config, capsys):
    path = write_config(
        "WIDTH=abc\nHEIGHT=10\nENTRY=0,0\nEXIT=9,9\n"
        "OUTPUT_FILE=o.txt\nPERFECT=True\n"
    )
    with pytest.raises(SystemExit):
        load_config(str(path))


def test_entry_malformed(write_config, capsys):
    path = write_config(
        "WIDTH=10\nHEIGHT=10\nENTRY=0\nEXIT=9,9\n"
        "OUTPUT_FILE=o.txt\nPERFECT=True\n"
    )
    with pytest.raises(SystemExit):
        load_config(str(path))


def test_entry_out_of_bounds(write_config, capsys):
    path = write_config(
        "WIDTH=10\nHEIGHT=10\nENTRY=10,0\nEXIT=9,9\n"
        "OUTPUT_FILE=o.txt\nPERFECT=True\n"
    )
    with pytest.raises(SystemExit):
        load_config(str(path))
    assert "boundar" in capsys.readouterr().err.lower()


def test_exit_out_of_bounds(write_config, capsys):
    path = write_config(
        "WIDTH=10\nHEIGHT=10\nENTRY=0,0\nEXIT=0,10\n"
        "OUTPUT_FILE=o.txt\nPERFECT=True\n"
    )
    with pytest.raises(SystemExit):
        load_config(str(path))


def test_entry_equals_exit(write_config, capsys):
    """IV.4: ENTRY and EXIT must be different."""
    path = write_config(
        "WIDTH=10\nHEIGHT=10\nENTRY=5,5\nEXIT=5,5\n"
        "OUTPUT_FILE=o.txt\nPERFECT=True\n"
    )
    with pytest.raises(SystemExit):
        load_config(str(path))
    err = capsys.readouterr().err.lower()
    assert "identical" in err or "different" in err


def test_invalid_perfect_value(write_config, capsys):
    path = write_config(
        "WIDTH=10\nHEIGHT=10\nENTRY=0,0\nEXIT=9,9\n"
        "OUTPUT_FILE=o.txt\nPERFECT=maybe\n"
    )
    with pytest.raises(SystemExit):
        load_config(str(path))


def test_empty_output_file(write_config, capsys):
    path = write_config(
        "WIDTH=10\nHEIGHT=10\nENTRY=0,0\nEXIT=9,9\n"
        "OUTPUT_FILE=\nPERFECT=True\n"
    )
    with pytest.raises(SystemExit):
        load_config(str(path))
