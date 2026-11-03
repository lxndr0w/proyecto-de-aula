# El Archivo Perdido

Juego serio en Python 3 y Pygame para el curso de Estructuras de Datos. El catálogo de la
biblioteca se dañó y el jugador recorre las salas para recoger fragmentos y reconstruirlo.

## Instalación

Se necesita Python 3.10 o superior. Desde la raíz del proyecto:

```bash
pip install -r requirements.txt
```

Se usa `pygame-ce`, que se importa igual que `pygame` (`import pygame`) y tiene versiones
para las versiones recientes de Python.

## Ejecución

```bash
python main.py
```

## Cómo se juega

1. En el menú se elige **Iniciar partida**, **Cargar partida** o **Salir**.
2. En el **Vestíbulo** se escribe el nombre, las vidas (entero) y la precisión (0 a 100).
   `TAB` cambia de campo y `ENTER` confirma. Si un dato no es válido, se muestra el error y se
   puede corregir.
3. Se recorren las salas en orden:
   - **Estanterías** (lista): agregar, buscar, eliminar y ordenar fragmentos.
   - **Mapas** (tupla): moverse por la cuadrícula escribiendo `(fila, columna)` hasta encontrar el fragmento.
   - **Fichas** (diccionario): consultar un fragmento por código y pedir una clave.
   - **Sellos** (conjuntos): quitar códigos repetidos y ver unión, intersección y diferencia.
4. Al terminar cada etapa hay una pregunta conceptual. Si se acierta, suma 10 puntos; si no,
   se pierde una vida y se puede seguir. Cada etapa superada entrega un fragmento.
5. Al final se muestra el resumen y se puede guardar el puntaje.

La Sala Central y el árbol binario de búsqueda se implementan en la semana 3.

## Módulos

- `main.py`: punto de entrada.
- `juego.py`: ventana de Pygame, pantallas y navegación. Llama a `estructuras.py` y `persistencia.py`.
- `estructuras.py`: operaciones de listas, tuplas, diccionarios y conjuntos.
- `persistencia.py`: guardar y cargar partidas y la tabla de puntajes.

### Funciones de `estructuras.py` que usa `juego.py`

`crear_fragmento`, `agregar_fragmento`, `buscar_fragmento`, `eliminar_fragmento`,
`ordenar_fragmentos`, `obtener_codigos_por_sala`, `crear_posicion`, `desempaquetar_posicion`,
`consultar_ficha`, `eliminar_duplicados` y `operaciones_conjuntos`.

### Funciones de `persistencia.py` que usa `juego.py`

| Función | Devuelve |
| --- | --- |
| `guardar_partida(datos_partida)` | `(exito: bool, mensaje: str)` |
| `cargar_partida()` | `(datos: dict o None, mensaje: str)` |
| `guardar_puntaje(registro)` | `(exito: bool, mensaje: str)` |

`datos_partida` contiene `jugador`, `sala_actual`, `fragmentos`, `pistas`, `aciertos`,
`respondidas` e `intentos`. `registro` contiene `nombre`, `puntaje`, `fecha`,
`fragmentos_validos` e `intentos`.

## Pruebas

```bash
python -m unittest discover -s test -v
```
