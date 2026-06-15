## Fase4_generator
### Estado: FAIL
### Comandos ejecutados
```bash
python audit/run_audit.py (phase4)
```
### Evidencia
Determinismo SEED=12345: OK (20x15)
Alcanzables=282 aislados=0
No 3x3 all-zero en muestra 20x15 perfect
5x5 pattern_fits=False stderr=''
Patrón 42 celdas = F: OK
50x50 generate: OK (no RecursionError)
### Hallazgos
- **G5b** [ALTA] Restricción M5 (densidad/corredores max 2 celdas) no implementada (`mazegen/generator.py`)
  - Repro: No existe post-procesado de densidad en el código
- **G6** [CRITICA] Laberinto pequeño sin patrón 42: no se imprime mensaje de error (`mazegen/generator.py:pattern_42:210-212`)
  - Repro: 5x5 maze
- **G9** [ALTA] Segunda generate() en misma instancia desplaza patrón 42 (`mazegen/generator.py:pattern_42:218-219`)
- **ALG** [ALTA] ALGORITHM parseado en config pero generator ignora el parámetro (`parser.py / mazegen/generator.py`)
### Requisitos del subject cubiertos / no cubiertos
IV.4: varios FAIL — ver G5,G6,G2.
