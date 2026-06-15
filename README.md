*This project has been created as part of the 42 curriculum by alejandr, czuluaga.*

# A-Maze-ing

## Description
A parametric and interactive maze generator written in Python. This program parses a configuration file, generates a random maze (with an option for a single-path "perfect" spanning tree), embeds a mandatory "42" visual pattern, calculates the shortest path from entry to exit, and renders the result in a terminal using an interactive ASCII interface.

## Instructions
The project uses a `Makefile` for standard operations.
- **Install dependencies:** `make install`
- **Run the program:** `make run` (Executes `python3 a_maze_ing.py config.txt`)
- **Debug mode:** `make debug`
- **Lint the codebase:** `make lint` (Runs `flake8` and strict `mypy`)
- **Build the reusable package:** `make build` (Generates `.whl` and `.tar.gz` in the `dist/` directory)

## Configuration File Format
The program reads a plain text file (default: `config.txt`). Lines starting with `#` are ignored. The format relies on `KEY=VALUE` pairs.

**Mandatory Keys:**
- `WIDTH`: Maze width in cells (e.g., `WIDTH=12`).
- `HEIGHT`: Maze height in cells (e.g., `HEIGHT=12`).
- `ENTRY`: Entry coordinates as `x,y` (e.g., `ENTRY=0,0`).
- `EXIT`: Exit coordinates as `x,y` (e.g., `EXIT=11,11`).
- `OUTPUT_FILE`: Hexadecimal output filename (e.g., `OUTPUT_FILE=maze.txt`).
- `PERFECT`: Boolean (`True`/`False`). `True` generates a single-path spanning tree. `False` generates a maze with controlled loops.

**Optional Keys:**
- `SEED`: Integer for reproducible generation (e.g., `SEED=42`).
- `ALGORITHM`: Generation algorithm (e.g., `ALGORITHM=backtracker`).

## Maze Generation Algorithm
**Chosen Algorithm:** Recursive Backtracker (Depth-First Search).
**Why we chose this algorithm:** The project strictly requires the capability to generate "perfect" mazes (a single valid path between the entry and exit). Recursive Backtracker naturally yields a spanning tree, ensuring total connectivity without isolated cells or inaccessible areas. It is computationally predictable and its implementation through recursive DFS is highly defensible during peer evaluation.

## Code Reusability
The core generation and solving logic is strictly isolated in the `mazegen` package, completely independent of the CLI parser or hex encoder. 

**How to reuse:**
After running `make build`, install the generated package in your environment: 
`pip install dist/mazegen-0.1.0-py3-none-any.whl`.

```python
from mazegen import MazeGenerator, MazeSolver

# 1. Instantiate and Generate
generator = MazeGenerator(width=15, height=15, seed=42, perfect=True)
generator.generate(entry=(0, 0), exit_coord=(14, 14))

# 2. Access internal grid structure
maze_grid = generator.get_maze()

# 3. Solve the maze
solver = MazeSolver(width=15, height=15)
solver.solve(maze_grid, entry=(0, 0), exit=(14, 14))
solution = solver.get_directions() # Returns 'N', 'E', 'S', 'W' path string