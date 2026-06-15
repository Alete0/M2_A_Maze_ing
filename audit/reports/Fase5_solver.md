## Fase5_solver
### Estado: FAIL
### Comandos ejecutados
```bash
python audit/run_audit.py (phase5)
```
### Evidencia
BFS path len=24 matches reference
Sin camino: get_directions lanza Exception: No solutions available for the maze
Meta: entry=0,0 exit=9,9 path_len=24
### Hallazgos
- **S4** [CRITICA] Sin camino: excepción no capturada en CLI (crash potencial) (`mazegen/solver.py:136 / a_maze_ing.py:167`)
  - Repro: No solutions available for the maze
### Requisitos del subject cubiertos / no cubiertos
IV.5 path/format — ver hallazgos.
