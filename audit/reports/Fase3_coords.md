## Fase3_coords
### Estado: PASS
### Comandos ejecutados
```bash
python audit/run_audit.py (phase3)
```
### Evidencia
4x4 path len=12 end=(3, 3) expected=(3, 3)
Output meta at blank_idx=4
entry=0,0 exit=3,3 path_len=12
### Hallazgos
- Ninguno
### Requisitos del subject cubiertos / no cubiertos
Bitmask N=1,E=2,S=4,W=8 — PASS. Coherencia output/path — ver hallazgos.
