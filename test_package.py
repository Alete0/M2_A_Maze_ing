#!/usr/bin/env python3
import sys

# Paso 1: Verificar la importación del paquete desde el entorno virtual
try:
    from mazegen import MazeGenerator, MazeSolver
    print("✅ Paquete 'mazegen' importado correctamente desde el entorno virtual.")
except ImportError as e:
    print(f"❌ Error al importar 'mazegen': {e}")
    print("Modo de resolución: Asegúrate de haber ejecutado 'make install' previamente.")
    sys.exit(1)

# Parámetros de prueba en formato interno (row, col)
width, height = 10, 10
entry_cell = (0, 0)
exit_cell = (9, 9)

# Paso 2: Probar el generador (MazeGenerator)
print(f"\n1. Probando MazeGenerator ({width}x{height}, perfecto=True)...")
try:
    # Instanciación con firma exacta de generator.py
    generator = MazeGenerator(width=width, height=height, seed=42, perfect=True)
    generator.generate(entry_cell, exit_cell)
    maze_grid = generator.get_maze()
    
    print("   ✅ Laberinto generado con éxito.")
    print(f"   Dimensión de la matriz devuelta: {len(maze_grid)} filas x {len(maze_grid[0])} columnas.")
except Exception as e:
    print(f"   ❌ Error fallido en la generación: {e}")
    sys.exit(1)

# Paso 3: Probar el solucionador (MazeSolver)
print("\n2. Probando MazeSolver...")
try:
    # Instanciación y resolución con firmas exactas de solver.py
    solver = MazeSolver(width=width, height=height)
    solver.solve(maze_grid, entry_cell, exit_cell)
    directions = solver.get_directions()
    
    print("   ✅ Solución BFS calculada con éxito.")
    print(f"   Ruta de escape obtenida (NESW): {directions}")
except Exception as e:
    print(f"   ❌ Error fallido en la resolución: {e}")
    sys.exit(1)

print("\n🎉 Resultado: El paquete 'mazegen' está correctamente aislado y operativo.")