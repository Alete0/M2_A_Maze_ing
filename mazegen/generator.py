#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   generator.py                                         :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: czuluaga <czuluaga@student.42malaga.com>     +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/06/11 10:09:14 by czuluaga            #+#    #+#            #
#   Updated: 2026/06/11 15:25:20 by czuluaga           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

import random


class MazeGenerator:
    def __init__(self, width: int, height: int, seed: int | None = None,
                 perfect: bool = True) -> None:
        self._maze: list[list[int]] = [[15 for _ in range(width)]
                                       for _ in range(height)]
        self._width: int = width
        self._height: int = height
        self._seed: int | None = seed
        self._perfect: bool = perfect
        self._pattern_fits: bool = True

    # BITMASKS: class attributes
    NORTH: int = 0b0001
    EAST: int = 0b0010
    SOUTH: int = 0b0100
    WEST:  int = 0b1000

    pattern: list[tuple[int, int]] = [(0, 0), (1, 0), (2, 0), (2, 1), (2, 2),
                                      (3, 2), (4, 2), (0, 4), (0, 5), (0, 6),
                                      (1, 6), (2, 6), (2, 5), (2, 4), (3, 4),
                                      (4, 4), (4, 5), (4, 6)]

    @staticmethod
    def neighbor_coords(current_location: tuple[int, int],
                        neighbor: int) -> tuple[int, int]:
        """Calculates the neighbor coordinates relative to the current cell
        location.

        Args:
            current_location (tuple[int, int]): Current cell location
            neighbor (int): Neighbor descriptor
            0 -> North
            1 -> East
            2 -> South
            3 -> West

        Raises:
            Exception: In case the neighbor descriptor in not known

        Returns:
            tuple[int, int]: Relative neighbor coordinates
        """
        match neighbor:
            case 0:
                return (current_location[0] - 1, current_location[1])
            case 1:
                return (current_location[0], current_location[1] + 1)
            case 2:
                return (current_location[0] + 1, current_location[1])
            case 3:
                return (current_location[0], current_location[1] - 1)
            case _:
                raise Exception("Unknown Neighbor")

    def out_of_bounds(self, cell_coords: tuple[int, int]) -> bool:
        """Checks if the cell coords given is inside the maze

        Args:
            cell_coords (tuple[int, int]): Cell coords to check

        Returns:
            bool: True if coords are out of bounds, False otherwise
        """
        if cell_coords[0] < 0 or cell_coords[0] > self._height - 1:
            return True
        if cell_coords[1] < 0 or cell_coords[1] > self._width - 1:
            return True
        return False

    def open_wall(self,
                  location: tuple[int, int],
                  neighbor_coords: tuple[int, int],
                  neighbor: int) -> None:
        """Opens wall between neighbors

        Args:
            location (tuple[int, int]): Current cell location
            neighbor_coords (tuple[int, int]): Neighbor cell location
            neighbor (int): Describe the relative position of the neighbor
            0 -> North
            1 -> East
            2 -> South
            3 -> West

        Raises:
            Exception: If the neighbor descriptor is none of the previous
            values
        """
        match neighbor:
            case 0:
                # Open North on current location
                x, y = location
                self._maze[x][y] &= ~self.NORTH
                # Open South on neighbor location
                x, y = neighbor_coords
                self._maze[x][y] &= ~self.SOUTH
            case 1:
                # Open East on current location
                x, y = location
                self._maze[x][y] &= ~self.EAST
                # Open West on neighbor location
                x, y = neighbor_coords
                self._maze[x][y] &= ~self.WEST
            case 2:
                # Open South on current location
                x, y = location
                self._maze[x][y] &= ~self.SOUTH
                # Open North on neighbor location
                x, y = neighbor_coords
                self._maze[x][y] &= ~self.NORTH
            case 3:
                # Open West on current location
                x, y = location
                self._maze[x][y] &= ~self.WEST
                # Open East on neighbor location
                x, y = neighbor_coords
                self._maze[x][y] &= ~self.EAST
            case _:
                raise Exception("Unknown neighbor, Can't open wall!!")

    def imperfect_walls(self) -> None:
        # Defining sets needed
        available_cells: set[tuple[int, int]] = set()
        pattern_cells: set[tuple[int, int]] = set()
        maze_cells: set[tuple[int, int]] = set()

        # Get coords for every cell in maze
        for i in range(self._height):
            for j in range(self._width):
                maze_cells.add((i, j))

        if self._pattern_fits:
            # Get the coords from the pattern cells
            pattern_cells = set(self.pattern)
            # get the cells not in 42 pattern with sets difference
            available_cells = maze_cells.difference(pattern_cells)
        else:
            available_cells = maze_cells

        # Choose a random number of walls to open
        random_cells: list[tuple[int, int]] = list()
        random_cells = random.sample(available_cells,
                                     k=random.randint(1, len(available_cells)))
        #   Open a random wall until no more changes needed to be
        for cell in random_cells:
            for n in random.sample([0, 1, 2, 3], k=4):
                n_coords: tuple[int, int] = self.neighbor_coords(cell, n)
                if n_coords in pattern_cells or self.out_of_bounds(n_coords):
                    continue
                else:
                    self.open_wall(cell, n_coords, n)
                    break

    def backtracker(self,
                    location: tuple[int, int],
                    visited: list[tuple[int, int]]) -> None:
        """Recursive DFS to generate the maze walls

        Args:
            location (tuple[int, int]): Any cell coords
            visited (list[tuple[int, int]]): List of already visited cells
        """
        # Add current location to visited list
        visited.append(location)

        # Loop over the four neighbours in random order
        to_visit: list[int] = random.sample([0, 1, 2, 3], k=4)
        for neighbor in to_visit:
            # Get neighbor's coords
            neighbor_cell: tuple[int, int] = self.neighbor_coords(location,
                                                                  neighbor)

            # if already visited or out of bounds -> skip
            if neighbor_cell in visited or self.out_of_bounds(neighbor_cell):
                continue

            # Open Wall
            self.open_wall(location, neighbor_cell, neighbor)

            # Recursive call, setting the location to the neighbor just visited
            self.backtracker(neighbor_cell, visited)

    def pattern_42(self) -> list[tuple[int, int]]:
        """Takes the deafult pattern inside the class and applies an x and
        y offset to it's coordinates

        Returns:
            list[tuple[int, int]]: Returns the pattern after offset
            has been applied.
        """
        # If maze is too small 42 pattern does not fit
        if self._height < 7 or self._width < 9:
            self._pattern_fits = False
            return []

        # Else calculate offset to apply to default pattern
        x_offset: int = int(self._width / 2) - 3
        y_offset: int = int(self._height / 2) - 2

        self.pattern = [(cell[0] + y_offset, cell[1] + x_offset)
                        for cell in self.pattern]
        return self.pattern

    def generate(self, entry: tuple[int, int]) -> None:
        """Generate the maze.
        If there is a seed it sets the random module seed to that value

        Args:
            start (tuple[int, int]): Starting point of the maze
        """
        if self._seed:
            random.seed(self._seed)

        try:
            # TODO: Check if entry or exit is a cell from the 42 pattern
            visited: list[tuple[int, int]] = []
            visited += self.pattern_42()
            self.backtracker(entry, visited)
        except Exception as e:
            print(e)
            exit(1)
        # After generation, if PERFECT is false -> open some walls
        if self._perfect is False:
            self.imperfect_walls()

    def get_maze(self) -> list[list[int]]:
        return self._maze
