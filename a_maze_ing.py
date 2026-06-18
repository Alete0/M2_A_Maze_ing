#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   a_maze_ing.py                                        :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: alejandr <alejandr@student.42malaga.com>     +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/06/11 10:14:34 by czuluaga            #+#    #+#            #
#   Updated: 2026/06/18 15:26:19 by alejandr           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

import sys
from mazegen import MazeGenerator, MazeSolver
from mazegen.generator import InvalidPlacementError
from mazegen.solver import NoSolutionError
from parser import MazeConfig, load_config
from typing import Set, Tuple
from encoder import gen_maze_file
from os import system, name

# BITMASKS
NORTH: int = 0b0001
EAST: int = 0b0010
SOUTH: int = 0b0100
WEST: int = 0b1000


# Type alias matching your project specifications
Coord = Tuple[int, int]

PATTERN_COLOR = "\033[90m"


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


def print_maze(maze: list[list[int]], entry: Coord, exit: Coord,
               solution: str, print_path: bool, color: str,
               pattern_cells: Set[Coord]) -> None:
    """
    Print a maze using ASCII characters.
    Each cell is represented by a 4-bit value where each bit represents a wall:
    - bit 0 (NORTH): wall above
    - bit 1 (EAST): wall to the right
    - bit 2 (SOUTH): wall below
    - bit 3 (WEST): wall to the left
    If bit is 1, wall is closed. If bit is 0, wall is open.
    """

    # Local reset constant to prevent color bleeding into the menu
    RESET = "\033[0m"
    PATH_COLOR = "\033[33m"

    height = len(maze)
    width = len(maze[0]) if height > 0 else 0
    solution_cells = path_to_exit(entry, solution)

    # Build the ASCII maze
    # Each cell takes 3x3 characters: corners, walls, and the cell space
    for row_idx in range(height):
        # Print top walls of the current row
        line = ""
        for col_idx in range(width):
            line += color + "█" + RESET
            # Check if NORTH wall is closed
            if maze[row_idx][col_idx] & NORTH:
                line += color + "███" + RESET
            else:
                line += "   "
        line += color + "█" + RESET
        print(line)

        # Print the middle line with side walls and cell space
        line = ""
        for col_idx in range(width):
            # Check if WEST wall is closed
            if maze[row_idx][col_idx] & WEST:
                line += color + "█" + RESET
            else:
                line += " "
            current_cell = (row_idx, col_idx)
            if current_cell == entry:
                line += " E "
            elif current_cell == exit:
                line += " X "
            elif current_cell in solution_cells and print_path:
                line += PATH_COLOR + " ● " + RESET
            elif current_cell in pattern_cells:
                line += PATTERN_COLOR + "███" + RESET
            else:
                line += "   "
        # Final EAST wall of the rightmost cell
        if maze[row_idx][width - 1] & EAST:
            line += color + "█" + RESET
        else:
            line += " "
        print(line)

    # Print bottom walls of the last row
    line = ""
    for col_idx in range(width):
        line += color + "█" + RESET
        # Check if SOUTH wall is closed (only for last row)
        if maze[height - 1][col_idx] & SOUTH:
            line += color + "███" + RESET
        else:
            line += "   "
    line += color + "█" + RESET
    print(line)


# Helper function to encapsulate maze creation and solving logic
def setup_new_maze(
    config: MazeConfig, use_seed: bool = True
) -> tuple[MazeGenerator, str]:
    """
    Instantiates, generates, and solves a maze based on the configuration.
    Allows disabling the seed for random re-generation.
    """
    # If use_seed is True, use the config seed; otherwise,
    # force None for true randomness
    current_seed = config.seed if use_seed else None

    # 1. Create the generator instance
    maze = MazeGenerator(
        width=config.width,
        height=config.height,
        seed=current_seed,
        perfect=config.perfect
    )

    # 2. Adjust coordinate axes if necessary and dig the walls
    # Assuming internal matrix notation (row, col)
    entry_coord = (config.entry[1], config.entry[0])
    exit_coord = (config.exit[1], config.exit[0])

    maze.generate(entry_coord, exit_coord)

    # 3. Instantiate solver and find the shortest path
    maze_solution = MazeSolver(config.width, config.height)
    maze_solution.solve(maze.get_maze(), entry_coord, exit_coord)

    # Return both the configured engine and the calculated path directions
    return maze, maze_solution.get_directions()


_NO_PATH_MSG = (
    "No path from ENTRY to EXIT in the generated maze."
)


def _report_fatal_error(message: str) -> None:
    print(f"Error: {message}", file=sys.stderr)
    sys.exit(1)


def save_output(
    config: MazeConfig, maze: MazeGenerator, directions: str
) -> None:
    """Write the maze grid and solution to the configured output file."""
    gen_maze_file(
        config.output_file,
        maze.get_maze(),
        config.entry,
        config.exit,
        path_solution=directions,
    )


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: <config_file>")
        exit(1)

    config: MazeConfig = load_config(sys.argv[1])

    # FIRST CALL: Initial setup using the file's original seed
    try:
        maze, directions = setup_new_maze(config, use_seed=True)
    except NoSolutionError:
        _report_fatal_error(_NO_PATH_MSG)
    except InvalidPlacementError as exc:
        _report_fatal_error(str(exc))
    except Exception as exc:
        _report_fatal_error(str(exc))

    save_output(config, maze, directions)

    # Static list of ANSI escape codes for the wall colors
    # 34m = Blue, 32m = Green, 35m = Magenta, 36m = Cyan, 31m = Red
    WALL_COLORS = ["\033[34m", "\033[32m", "\033[35m", "\033[36m", "\033[31m"]
    ANSI_RESET = "\033[0m"

    # State variable to track the active color index
    current_color_idx = 0

    show_path = True

    entry_coord = (config.entry[1], config.entry[0])
    exit_coord = (config.exit[1], config.exit[0])

    while True:
        if name == 'nt':
            _ = system('cls')
        else:
            _ = system('clear')
        pattern_cells = maze.get_maze_pattern()
        if not pattern_cells:
            print("Error: Maze size too small to fit the '42' pattern.",
                  file=sys.stderr)
        print_maze(
            maze.get_maze(),
            entry_coord,
            exit_coord,
            directions,
            show_path,
            WALL_COLORS[current_color_idx],
            pattern_cells,
        )

        print("=== A-Maze-ing ===")
        print("1. Re-generate a new maze")
        print("2. Show/Hide path from entry to exit")
        print("3. Rotate maze colors")
        print("4. Quit")

        try:
            choice = input("Choice? (1-4): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSee you soon!")
            break

        if choice == "1":
            # Passing use_seed=False guarantees a completely fresh layout
            try:
                maze, directions = setup_new_maze(config, use_seed=False)
            except NoSolutionError:
                print(f"Error: {_NO_PATH_MSG}", file=sys.stderr)
                continue
            except InvalidPlacementError as exc:
                print(f"Error: {exc}", file=sys.stderr)
                continue
            except Exception as exc:
                print(f"Error: {exc}", file=sys.stderr)
                continue
            save_output(config, maze, directions)
            print("New maze generated successfully!")
        elif choice == "2":
            show_path = not show_path
        elif choice == "3":
            # Rotate color index safely using modular arithmetic
            current_color_idx = (current_color_idx + 1) % len(WALL_COLORS)
            print("Maze color rotated successfully!")
        elif choice == "4":
            print("See you soon!")
            break
        else:
            print("Invalid option. Try again")
