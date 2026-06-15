## Fase2_parser
### Estado: PASS
### Comandos ejecutados
```bash
python audit/run_audit.py (phase2)
```
### Evidencia
**P1** exit=0 stderr=''
**P2** exit=1 stderr='Error: Mandatory keys are missing: WIDTH'
**P3** exit=1 stderr='Validation error on the cofiguration values: ENTRY (5,5) out of the boundaries.X: 0-4, Y: 0-4.'
**P4** exit=1 stderr="Validation error on the cofiguration values: ENTRY and EXIT can't be identical. They must be different cells."
**P5** exit=1 stderr="Validation error on the cofiguration values: PERFECT must be a boolean value ('True' or 'False')."
**P6** exit=1 stderr="Critical error reading the file: Line 2: Format invalid. Missing '='."
**P7** exit=1 stderr="Error: Configuration file 'C:\\Users\\alete\\Documents\\03_Coding\\42Malaga\\amazing\\audit\\configs\\does_not_exist_xyz.txt' not found."
**P8** exit=0 stderr=''
### Hallazgos
- Ninguno
### Requisitos del subject cubiertos / no cubiertos
IV.3: claves obligatorias — PASS con WARN en mensajes. IV.2 errores — PASS.
