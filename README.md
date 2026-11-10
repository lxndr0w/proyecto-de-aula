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
5. En cualquier sala el botón **Guardar** escribe la partida en `data/partida.json`.
   **Cargar partida** en el menú la retoma en la sala donde iba.
6. Al completar las cinco etapas de recolección se accede a la Sala Central (árbol binario
   de búsqueda): se depuran fragmentos duplicados, se reconstruye el catálogo ordenado en          inorden y se buscan fragmentos por código comparando el número de comparaciones frente a la     búsqueda secuencial.
7. Al final se muestra el resumen, la tabla de puntajes y el botón **Guardar puntaje**,
   que agrega el resultado a `data/puntajes.json`.

Si no hay partida guardada, el archivo está dañado o le faltan datos, el juego lo avisa en
pantalla y sigue en el menú.

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

### Clases y funciones de `arbol.py`
`Nodo`, `ArbolBinarioBusqueda`,`insertar`, `buscar`, `inorden`, `verificar_orden`, `altura`,
`busqueda_secuencial`, `reconstruir_catalogo`, `comparar_busquedas`, `experimento_comparaciones`.


### Funciones de `persistencia.py` que usa `juego.py`

| Función | Devuelve |
| --- | --- |
| `guardar_partida(datos_partida)` | `True` si se escribió el archivo, `False` si no |
| `cargar_partida()` | el diccionario de la partida, o `None` si el archivo no existe o está dañado |
| `guardar_puntaje(registro)` | `True` si se agregó a la tabla, `False` si no |
| `cargar_puntajes()` | la lista de registros de la tabla (vacía si no hay archivo) |

Las rutas salen de `persistencia.DATA_DIR`, `RUTA_PARTIDA` y `RUTA_PUNTAJES`. `juego.py`
crea la carpeta `data/` antes de guardar si todavía no existe.

`datos_partida` contiene `jugador` (nombre, vida, puntaje, nivel, precision, activo),
`sala_actual`, `fragmentos` (lista de diccionarios), `pistas` (listas `a` y `b`), `aciertos`,
`respondidas` e `intentos`. `registro` contiene `nombre`, `puntaje`, `fecha`,
`fragmentos_validos` e `intentos`.

## Pruebas

La carpeta `test` contiene las pruebas unitarias del proyecto:

- `test_estructuras.py`
- `test_arbol.py`
- `test_persistencia.py`

Las pruebas verifican:

- **Estructuras de datos:** operaciones de listas, tuplas, diccionarios y conjuntos.
- **Árbol binario de búsqueda:** inserción, búsqueda, recorrido inorden, reconstrucción del catálogo y comparación de búsquedas.
- **Persistencia:** guardado y recuperación de partidas y puntajes, manejo de archivos inexistentes o dañados y creación de rutas de almacenamiento.

Para ejecutar todas las pruebas desde la raíz del proyecto:

```bash
python -m unittest discover -s test -v
```

