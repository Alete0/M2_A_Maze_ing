#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   a_maze_ing.py                                        :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: alejandr <alejandr@student.42malaga.com>     +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/06/11 10:14:34 by czuluaga            #+#    #+#            #
#   Updated: 2026/06/12 13:32:52 by alejandr           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

import sys
from mazegen import MazeGenerator
from parser import MazeConfig, load_config
from typing import Set, Tuple
from encoder import gen_maze_file

# BITMASKS
NORTH: int = 0b0001
EAST:  int = 0b0010
SOUTH: int = 0b0100
WEST:  int = 0b1000


# Type alias matching your project specifications
Coord = Tuple[int, int]


def path_to_exit(entry: Coord, path_str: str) -> Set[Coord]:
    """
    Converts a cardinal direction path string into a set of grid coordinates.

    Args:
        entry: Starting coordinate tuple as (row, col).
        path_str: String containing the sequence of steps (e.g., "NESW").

    Returns:
        Set[Coord]: A set containing all (row, col) coordinates visited by the
                    path, including the initial entry point.
    """
    # Initialize the set with the entry point
    visited_coordinates: Set[Coord] = {entry}

    current_row, current_col = entry

    # Process each cardinal character to track the exact movement
    for direction in path_str:
        if direction == 'N':
            current_row -= 1
        elif direction == 'E':
            current_col += 1
        elif direction == 'S':
            current_row += 1
        elif direction == 'W':
            current_col -= 1
        else:
            # Skip any unexpected characters gracefully without crashing
            continue

        # Add the newly reached coordinate to our path tracker
        visited_coordinates.add((current_row, current_col))

    return visited_coordinates


def print_maze(maze: list[list[int]], entry: Coord) -> None:
    """
    Print a maze using ASCII characters.
    Each cell is represented by a 4-bit value where each bit represents a wall:
    - bit 0 (NORTH): wall above
    - bit 1 (EAST): wall to the right
    - bit 2 (SOUTH): wall below
    - bit 3 (WEST): wall to the left
    If bit is 1, wall is closed. If bit is 0, wall is open.
    """
    height = len(maze)
    width = len(maze[0]) if height > 0 else 0
    # TODO: AQUI METER EL STR DE LA SOLUCION
    solution_cells = path_to_exit(entry, "SSW")

    # Build the ASCII maze
    # Each cell takes 3x3 characters: corners, walls, and the cell space
    for row_idx in range(height):
        # Print top walls of the current row
        line = ""
        for col_idx in range(width):
            line += "+"
            # Check if NORTH wall is closed
            if maze[row_idx][col_idx] & NORTH:
                line += "---"
            else:
                line += "   "
        line += "+"
        print(line)

        # Print the middle line with side walls and cell space
        line = ""
        for col_idx in range(width):
            # Check if WEST wall is closed
            if maze[row_idx][col_idx] & WEST:
                line += "|"
            else:
                line += " "
            current_cell = (row_idx, col_idx)
            if current_cell in solution_cells:
                line += " . "
            else:
                line += "   "
        # Final EAST wall of the rightmost cell
        if maze[row_idx][width - 1] & EAST:
            line += "|"
        else:
            line += " "
        print(line)

    # Print bottom walls of the last row
    line = ""
    for col_idx in range(width):
        line += "+"
        # Check if SOUTH wall is closed (only for last row)
        if maze[height - 1][col_idx] & SOUTH:
            line += "---"
        else:
            line += "   "
    line += "+"
    print(line)


if __name__ == "__main__":

    sys.setrecursionlimit(3500)

    if len(sys.argv) != 2:
        print("Usage: <config_file>")
        exit(1)

    config: MazeConfig = load_config(sys.argv[1])

    maze = MazeGenerator(width=config.width,
                         height=config.height,
                         seed=config.seed,
                         perfect=config.perfect)
    maze.generate(config.entry)
    # TODO: PASAR LA STR DE SOLUCION A GEN MAZE FILE
    gen_maze_file(config.output_file, maze.get_maze(), config.entry,
                  config.exit)
    print_maze(maze.get_maze(), config.entry)
