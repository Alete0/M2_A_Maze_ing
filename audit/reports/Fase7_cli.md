## Fase7_cli
### Estado: FAIL
### Comandos ejecutados
```bash
piped stdin tests a_maze_ing.py
```
### Evidencia
argv invalid: Usage message OK
Menú con inputs variados: sin Traceback
maze.txt mtime before=1781456542.720872 after=1781456542.7884698
### Hallazgos
- **U3** [ALTA] Opción 1 regenerar no reescribe OUTPUT_FILE (no llama gen_maze_file) (`a_maze_ing.py:220-223`)
### Requisitos del subject cubiertos / no cubiertos
Cap V interacciones — parcial.
