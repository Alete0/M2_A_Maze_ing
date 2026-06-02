### Análisis de Requisitos Innegociables

* **Lenguaje y Calidad del Código:**
    * El proyecto debe desarrollarse en Python 3.10 o superior.
    * El código debe cumplir estrictamente con el estándar `flake8`.
    * Es obligatorio incluir *type hints* para parámetros, tipos de retorno y variables utilizando el módulo `typing`.
    * El código debe pasar la validación estática de `mypy` sin errores.
    * Las funciones y clases deben documentarse mediante *docstrings* siguiendo el estándar PEP 257 (estilos Google o NumPy).
* **Gestión de Ejecución y Errores:**
    * El archivo principal debe llamarse `a_maze_ing.py` y aceptar el archivo de configuración como único argumento.
    * Deben emplearse bloques `try-except` para gestionar excepciones y prevenir cuelgues.
    * Se requiere el uso de gestores de contexto para asegurar la liberación automática de recursos (ej. archivos) y prevenir fugas.
    * Si ocurren errores (configuración inválida, sintaxis incorrecta, parámetros imposibles), el programa debe imprimir un mensaje de error claro en consola sin detenerse abruptamente.
* **Archivo de Configuración (`config.txt`):**
    * Formato estricto de un par `CLAVE=VALOR` por línea, ignorando líneas que inicien con `#`.
    * Debe contener obligatoriamente las variables `WIDTH`, `HEIGHT`, `ENTRY`, `EXIT`, `OUTPUT_FILE` y `PERFECT`.
    * Un archivo de configuración por defecto debe existir en el repositorio Git.
* **Reglas Algorítmicas del Laberinto:**
    * La generación debe ser aleatoria pero reproducible utilizando una semilla.
    * La entrada y la salida deben ser celdas diferentes ubicadas dentro de los límites y con muros en los bordes exteriores.
    * Debe existir conectividad total, prohibiendo celdas aisladas a excepción de las que formen el patrón "42".
    * Los muros deben ser coherentes bidireccionalmente entre celdas vecinas.
    * La arquitectura prohíbe áreas abiertas mayores a 2 celdas de ancho (ej. áreas de 3x3 son inválidas).
    * Si la bandera `PERFECT` está activada, el laberinto debe ser un árbol de expansión (un único camino entre la entrada y la salida).
    * El laberinto debe incluir un patrón "42" dibujado con celdas cerradas.
    * Si el tamaño de la matriz no permite dibujar el "42", se debe mostrar un error en consola.
* **Formato de Archivo de Salida:**
    * Codificación hexadecimal celda por celda representando los muros: 0 (Norte), 1 (Este), 2 (Sur), 3 (Oeste).
    * Los muros cerrados se representan con 1, y los abiertos con 0.
    * El archivo debe escribirse fila por fila, y al terminar el laberinto, incluir una línea vacía.
    * Las tres líneas finales deben contener: coordenadas de entrada, coordenadas de salida y el camino válido más corto expresado con los caracteres `N`, `E`, `S`, `W`.
    * Toda línea debe finalizar estrictamente con un salto de línea (`\n`).
* **Visualización e Interfaz:**
    * Se exige renderizado en terminal ASCII.
    * Debe soportar interacción de usuario para: regenerar el laberinto, mostrar/ocultar la solución y alterar los colores de los muros.
* **Reusabilidad y Empaquetado:**
    * La lógica generadora debe residir en una clase única (ej. `MazeGenerator`) dentro de un módulo independiente.
    * El módulo empaquetado debe llamarse `mazegen-*`, ubicarse en la raíz del repositorio y generar extensiones `.tar.gz` y `.whl` estándar de Python.
* **Makefile y Documentación:**
    * El Makefile debe incluir las reglas `install`, `run`, `debug`, `clean` y `lint`.
    * La regla `lint` requiere la ejecución de `flake8 .` y un conjunto estricto de banderas para `mypy`.
    * El archivo `README.md` tiene una estructura obligatoria. Su primera línea debe ir en cursiva detallando a los creadores de 42. Debe incluir secciones de Descripción, Instrucciones, Recursos (especificando uso de IA), Estructura de Configuración, Algoritmo, Partes Reusables y Gestión de Equipo.

---

### División de Tareas y Hoja de Ruta

Se diseña una estructura desacoplada en dos tracks independientes. `alejandr` desarrollará el motor interno, los algoritmos espaciales y la validación de grafos. `czuluaga` orquestará la integración de la interfaz, el procesamiento de I/O, y la arquitectura de empaquetado pip.

#### Track A: Motor Core y Lógica Espacial (alejandr)

| Tarea | Descripción | Dependencias | Dificultad | Conceptos a Investigar |
| :--- | :--- | :--- | :--- | :--- |
| **A1. Parser de Configuración** | Módulo para leer `config.txt`, descartar comentarios (`#`), y validar la presencia de claves obligatorias. | Ninguna | 2/10 | Manejo de expresiones regulares, diccionarios, conversión de tipos dinámica y gestión de excepciones. |
| **A2. Modelado de Estructura de Datos** | Representación en memoria de la matriz. Debe asegurar muros perimetrales externos y validar las coordenadas `ENTRY`/`EXIT`. | A1 | 3/10 | Teoría de grafos, matrices adyacentes, programación orientada a objetos (clase `MazeGenerator`). |
| **A3. Motor Generador (Árbol de Expansión)** | Implementación de algoritmos para laberintos perfectos (un solo camino) o imperfectos con validación de accesibilidad global. | A2 | 8/10 | Algoritmos de generación de laberintos (Backtracker recursivo, Kruskal o Prim) y manejo seguro de la semilla de aleatoriedad. |
| **A4. Inserción del Patrón "42"** | Lógica de superposición matricial para incrustar el patrón "42" cerrado. Comprobación de límites geométricos para lanzar error si el grid es muy pequeño. | A3 | 6/10 | Aritmética de matrices, algoritmos de colisión, re-validación de conectividad tras insertar obstáculos. |
| **A5. Restricción de Densidad Espacial** | Rutina de chequeo y corrección para evitar celdas abiertas mayores de 2x2. Impide agrupaciones libres $\ge 3\times3$. | A3, A4 | 7/10 | Búsqueda local, reconocimiento de patrones en matrices booleanas. |
| **A6. Solucionador (Pathfinding)** | Módulo para encontrar y calcular el camino más corto válido. Si es perfecto, garantiza que la solución es única. | A3 | 6/10 | Algoritmos de búsqueda de caminos como A* o Breadth-First Search (BFS). Traducción de vectores a caracteres `N`, `E`, `S`, `W`. |

#### Track B: I/O, Visualización y Empaquetado (czuluaga)

| Tarea | Descripción | Dependencias | Dificultad | Conceptos a Investigar |
| :--- | :--- | :--- | :--- | :--- |
| **B1. Infraestructura Base** | Creación del esqueleto del repositorio, `.gitignore`, Makefile con reglas exigidas, y esqueleto del `README.md` estricto. | Ninguna | 3/10 | Sintaxis de automatización en GNU Make, directivas estáticas en `mypy`. |
| **B2. Conversor Hexadecimal (Output)** | Serializa el modelo de grafo a la representación de mapa de bits (0, 1, 2, 3 para N, E, S, W) usando valores hexadecimales. | Interfaz de A2 | 4/10 | Manipulación bit a bit (*Bitwise operations*), manejo de flujo de archivos I/O y *Context Managers* (`with open()`). |
| **B3. Exportador de Archivo** | Escritura de las filas en disco. Adición de salto de línea, coordenadas y la cadena de caracteres proveniente del Pathfinding al final del archivo. | B2, Interfaz de A6 | 2/10 | Formateo estricto de strings (evitar fallos invisibles como ausencia de `\n` final). |
| **B4. Renderizador Visual ASCII e Interacción** | Dibujo en terminal con caracteres de bloque. Interfaz con opciones cíclicas para regenerar, ocultar ruta y alternar esquemas de color. | B2 | 5/10 | Secuencias de escape ANSI para colorear texto en terminal. Manejo del ciclo de entrada del usuario (`input`). |
| **B5. Arquitectura de Paquete `mazegen-*`** | Desacoplamiento del archivo `a_maze_ing.py` respecto de la lógica interna para generar distribuciones construibles (`.tar.gz` y `.whl`). | A3, A6 | 6/10 | Estándares de empaquetado de Python modernos: `pyproject.toml`, módulos `build` o `setuptools`. Entornos virtuales (`venv`) para prueba de reinstalación. |