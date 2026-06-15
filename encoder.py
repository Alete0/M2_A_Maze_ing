import sys
from typing import Tuple

Coord = Tuple[int, int]
Grid = list[list[int]]


def line_to_hex(row: list[int]) -> str:
    """Encode a maze row as a hexadecimal string.

    Each cell bitmask (0-15) is written as one uppercase hex digit (0-F).

    Args:
        row: One row of the internal maze grid (cell wall bitmasks).

    Returns:
        Concatenated hex digits for the row, without separators.
    """
    return "".join(f"{cell:X}" for cell in row)


def gen_maze_file(
        output_path: str,
        maze: Grid,
        entry_c: Coord,
        exit_c: Coord,
        path_solution: str = ""
) -> None:
    """Write the maze and solution metadata to the subject output file.

    The file contains the hex grid (one row per line), a blank line,
    entry and exit coordinates in ``x,y`` config format, and the shortest
    path as a NESW direction string.

    Args:
        output_path: Destination file path (``OUTPUT_FILE`` from config).
        maze: Internal grid of cell wall bitmasks.
        entry_c: Entry coordinates as ``(x, y)``.
        exit_c: Exit coordinates as ``(x, y)``.
        path_solution: Shortest path from entry to exit (NESW characters).

    Raises:
        SystemExit: If the output file cannot be written.
    """
    try:
        with open(output_path, 'w', newline='\n', encoding='utf-8') as f:
            for row in maze:
                f.write(line_to_hex(row) + "\n")
            f.write("\n")

            f.write(f"{entry_c[0]},{entry_c[1]}\n")
            f.write(f"{exit_c[0]},{exit_c[1]}\n")

            f.write(f"{path_solution}\n")

    except IOError as e:
        print(f"Critical error writing to output file: {e}", file=sys.stderr)
        sys.exit(1)
