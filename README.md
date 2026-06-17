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

## Maze Generation Algorithm
**Chosen Algorithm:** Recursive Backtracker (Depth-First Search).
**Why we chose this algorithm:** The project strictly requires the capability to generate "perfect" mazes (a single valid path between the entry and exit). Recursive Backtracker naturally yields a spanning tree, ensuring total connectivity without isolated cells or inaccessible areas. It is computationally predictable and its implementation through recursive DFS is highly defensible during peer evaluation.

## Code Reusability
The core generation and solving logic is strictly isolated in the `mazegen` package, completely independent of the CLI parser or hex encoder. 

**How to reuse:**
After running `make build`, install the wheel from the repository root:
`pip install mazegen-0.1.0-py3-none-any.whl`.

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
```

## Resources

### References

- [Mazes — CMU student guide](https://www.cs.cmu.edu/~112-n22/notes/student-tp-guides/Mazes.pdf) — maze representation, wall encoding, and general maze concepts.
- [Maze generation algorithm recap — Jamis Buck](https://weblog.jamisbuck.org/2011/2/7/maze-generation-algorithm-recap.html) — overview of maze generation algorithms; we used this to choose and justify Recursive Backtracker.
- [Solve a maze with BFS — Medium article](https://medium.com/@luthfisauqi17_68455/artificial-intelligence-search-problem-solve-maze-using-breadth-first-search-bfs-algorithm-255139c6e1a3) — shortest-path search; informed our BFS-based `MazeSolver`.

### Use of AI

We used **Google Gemini** as a helper assistant during the project. It did **not** write or modify production code.

Gemini helped us with:

- **Clarifying concepts** — wall bitmasks (N/E/S/W), perfect vs imperfect mazes, the "42" pattern constraints, and coordinate conventions (config `x,y` vs internal `row,col`).
- **Tests** — ideas for edge cases and test structure in `tests/`; we reviewed and wrote the final assertions ourselves.
- **Documentation** — drafting and improving parts of this README and related project documentation.

## Team Management

### Roles

| Area | Primary owner | Notes |
|------|---------------|-------|
| `mazegen/generator.py` | **czuluaga** | Recursive Backtracker, pattern 42, density rules, perfect/imperfect modes |
| `mazegen/solver.py` | **czuluaga** | BFS shortest path, N/E/S/W direction string |
| `parser.py` | **alejandr** | Config format, validation, error handling |
| `tests/` | **alejandr** | Unit and integration tests across all modules |
| ASCII rendering & interactive menu (`a_maze_ing.py`) | **Both** | Terminal display, path toggle, colors, menu |
| `encoder.py` | **Both** | Hex output format and integration with the pipeline |
| `Makefile`, `pyproject.toml`, packaging | **Both** | Install, lint, build, wheel generation |
| `README.md` | **Both** | Project documentation |

### Planning

Before writing code, we planned the full architecture in detail: module split, data flow (config → generation → solving → encoding → display), mandatory subject constraints, and the order of implementation. That upfront planning kept responsibilities clear and reduced rework.

Implementation order:

1. Configuration parser and default `config.txt`
2. Reusable maze core in `mazegen` (generation and solving)
3. Hex encoder and output validation
4. CLI, ASCII rendering, and interactive menu
5. Package build and test suite

As the project evolved, we adjusted timing on tests and packaging, but the original module boundaries stayed the same.

### Coordination

We are both on-site 42 students and coordinated **in person** during lab sessions: short syncs on progress, pair reviews on tricky parts (pattern 42, bidirectional walls, output format), and git-based integration of each other's work.

### What worked / what we would improve

**Worked well:** planning before coding; isolating `mazegen` from the CLI; tests catching regressions early; Recursive Backtracker matching the perfect-maze requirement.

**To improve:** run full-project `make lint` earlier; finalize README sections (Resources, team roles) during development, not at the end.

### Tools

- **Git** — version control and integration of features
- **Python 3.10+** — language and type hints
- **pytest** — local test suite
- **flake8 / mypy** — linting (`make lint`)
- **python -m build** — `mazegen` wheel and sdist
- **In-person coordination** — planning and reviews during 42 campus sessions