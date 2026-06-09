import sys
import random

# BITMASKS
NORTH: int = 0b0001
EAST:  int = 0b0010
SOUTH: int = 0b0100
WEST:  int = 0b1000


def print_maze(maze: list[list[int]]) -> None:
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


def get_neighbor_coords(location: tuple[int, int],
                        neighbor: int) -> tuple[int, int]:
    match neighbor:
        case 0:
            return (location[0] - 1, location[1])
        case 1:
            return (location[0], location[1] + 1)
        case 2:
            return (location[0] + 1, location[1])
        case 3:
            return (location[0], location[1] - 1)
        case _:
            raise Exception("Unknown Neighbor")


def out_of_bounds(maze: list[list[int]], coords: tuple[int, int]) -> bool:
    height: int = len(maze)
    width: int = len(maze[0])

    if coords[0] < 0 or coords[0] > height - 1:
        return True
    if coords[1] < 0 or coords[1] > width - 1:
        return True
    return False


def open_wall(maze: list[list[int]],
              location: tuple[int, int],
              neighbor_coords: tuple[int, int],
              neighbor: int) -> None:
    match neighbor:
        case 0:
            # Open North on current location
            x, y = location
            maze[x][y] &= ~NORTH
            # Open South on neighbor location
            x, y = neighbor_coords
            maze[x][y] &= ~SOUTH
        case 1:
            # Open East on current location
            x, y = location
            maze[x][y] &= ~EAST
            # Open West on neighbor location
            x, y = neighbor_coords
            maze[x][y] &= ~WEST
        case 2:
            # Open South on current location
            x, y = location
            maze[x][y] &= ~SOUTH
            # Open North on neighbor location
            x, y = neighbor_coords
            maze[x][y] &= ~NORTH
        case 3:
            # Open West on current location
            x, y = location
            maze[x][y] &= ~WEST
            # Open East on neighbor location
            x, y = neighbor_coords
            maze[x][y] &= ~EAST
        case _:
            raise Exception("Unknown neighbor, Can't open wall!!")


def backtracker(maze: list[list[int]],
                location: tuple[int, int],
                visited: list[tuple[int, int]]) -> None:

    # Add current location to visited list
    visited.append(location)

    # Loop over the four neighbours in random order
    to_visit: list[int] = random.sample([0, 1, 2, 3], k=4)
    for neighbor in to_visit:
        # Get neighbor's coords
        neighbor_coords: tuple[int, int] = get_neighbor_coords(location,
                                                               neighbor)

        # if already visited or out of bounds -> skip
        if neighbor_coords in visited or out_of_bounds(maze, neighbor_coords):
            continue

        # Open Wall
        open_wall(maze, location, neighbor_coords, neighbor)

        # Recursive call, setting the location to the neighbor just visited
        backtracker(maze, neighbor_coords, visited)


def generate_maze(maze: list[list[int]]) -> None:
    location: tuple[int, int] = (random.randint(0, len(maze) - 1),
                                 random.randint(0, len(maze[0]) - 1))
    print(location)

    # TODO: Include 42 pattern cells inside visited so the generator
    # never chages this ones
    visited: list[tuple[int, int]] = [(5, 5), (6, 5), (7, 5)]

    backtracker(maze, location, visited)


if __name__ == "__main__":

    if len(sys.argv) < 4:
        print("Usage: <width> <height> <seed>")
        exit(1)

    width: int = int(sys.argv[1])
    height: int = int(sys.argv[2])
    seed: int = int(sys.argv[3])

    random.seed(seed)

    maze: list[list[int]] = [[15 for _ in range(width)] for _ in range(height)]

    try:
        generate_maze(maze)
    except Exception as e:
        print(e)
        exit(1)

    print_maze(maze)
