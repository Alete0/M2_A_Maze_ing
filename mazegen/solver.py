#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   solver.py                                            :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: czuluaga <czuluaga@student.42malaga.com>     +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/06/12 10:50:56 by czuluaga            #+#    #+#            #
#   Updated: 2026/06/12 13:35:49 by czuluaga           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

class MazeSolver:
    def __init__(self, width: int, height: int) -> None:
        self._directions: str = ""
        self._path_cell: list[tuple[int, int]] = []
        self._width: int = width
        self._height: int = height

    # BITMASKS: class attributes
    NORTH: int = 0b0001
    EAST:  int = 0b0010
    SOUTH: int = 0b0100
    WEST:  int = 0b1000

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

    @staticmethod
    def get_available_neighbors(cell: int) -> list[int]:
        neighbors: list[int] = []
        for n in range(4):
            if not (cell >> n) & 1:
                neighbors.append(n)
        return neighbors

    def solve(self,
              maze: list[list[int]],
              entry: tuple[int, int], exit: tuple[int, int]):

        # Init vars needed
        queue: list[tuple[int, int]] = []
        visited: list[tuple[int, int]] = []

        queue.append(entry)

        while queue:
            cell: tuple[int, int] = queue.pop(0)

            if cell is exit:
                break

            visited.append(cell)

            cell_value: int = maze[cell[0]][cell[1]]
            neighbors: list[int] = self.get_available_neighbors(cell_value)

            for neighbor in neighbors:
                n: tuple[int, int] = self.neighbor_coords(cell, neighbor)
                if n not in visited and not self.out_of_bounds(n):
                    queue.append(n)

        pass
