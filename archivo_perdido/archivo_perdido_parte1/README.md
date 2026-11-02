# El Archivo Perdido — Parte 1

Primera entrega del prototipo del proyecto de Estructuras de Datos. Esta parte contiene el punto de entrada, la ventana de Pygame y el **Vestíbulo**, donde se registran y validan los datos iniciales del jugador.

## Requisitos

- Python 3.10 o superior.
- Pygame (se instala con `requirements.txt`).

## Instalación y ejecución

Abre una terminal en esta carpeta y ejecuta:

```bash
python -m venv .venv
```

En Windows:

```bash
.venv\Scripts\activate
```

Instala la dependencia e inicia el juego:

```bash
pip install -r requirements.txt
python main.py
```

## Cómo probar el Vestíbulo

1. Escribe el nombre del jugador.
2. Presiona `TAB` para pasar al campo de vidas.
3. Escribe un entero igual o mayor que 1.
4. Presiona `TAB` y escribe una precisión entre 0 y 100. Se acepta punto o coma decimal.
5. Presiona `ENTER` para validar y registrar al jugador.
6. En la pantalla de bienvenida se muestran los datos y sus tipos, junto con la pregunta «¿Por qué hay que validar antes de utilizar el puntaje?».
7. Selecciona `CONTINUAR` para finalizar el vestíbulo o `SALIR` para cerrar el juego. También puedes presionar `ESC` en cualquier momento.

Prueba también entradas incorrectas: nombre vacío, letras en el campo de vidas, una precisión fuera del rango o texto en el campo decimal. El juego debe mostrar el error sin cerrarse.

## Qué demuestra esta parte

- `str`: nombre del jugador.
- `int`: vida, puntaje y nivel.
- `float`: precisión.
- `bool`: estado activo de la partida.
- Conversión de texto a entero y decimal con `try/except` y validaciones de rango.
- Interfaz inicial implementada con Pygame.

## Siguiente parte

La Parte 2 añadirá la sala de Estanterías y el inventario implementado con una lista: insertar, eliminar, buscar, ordenar y utilizar una comprensión de listas.

## Trabajo colaborativo y GitHub

Cada integrante debe revisar, probar y comprender el código antes de modificarlo. Los commits deben corresponder a cambios reales realizados por quien los registra; no se deben inventar autores ni contribuciones. En el informe final se debe declarar el apoyo de herramientas de IA, de acuerdo con las instrucciones de la asignatura.
