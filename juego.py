"""Interfaz gráfica y navegación de El Archivo Perdido.

Este módulo dibuja las pantallas con Pygame y llama a las funciones de
estructuras.py, persistencia.py y arbol.py. No repite la lógica de esos módulos.
"""

from datetime import datetime
import os
import sys

import pygame  # pyright: ignore[reportMissingImports]

import arbol
import estructuras
import persistencia


# Configuración de la ventana
ANCHO = 1000
ALTO = 680
FPS = 60

# Orden en que se recorren las cinco etapas de recolección.
SALAS = ["vestibulo", "estanterias", "mapas", "fichas", "sellos"]

# Tamaño de la cuadrícula de la Sala de Mapas.
TAMANO_MAPA = 6

# Niveles que caben en un estante al ubicar el catálogo reconstruido.
# El primer fragmento, ya ordenado por código, queda en la tupla (1, 1).
# El sexto abre el estante 2. Es el mismo criterio que usa arbol.py.
NIVELES_POR_ESTANTE = 5

# Ubicaciones que se listan en pantalla antes de resumir el resto.
MAX_UBICACIONES_VISIBLES = 8

# Puntos que se suman por cada pregunta bien contestada.
PUNTOS_POR_ACIERTO = 10

# Pregunta conceptual de cada sala: (pregunta, opciones, índice de la correcta).
PREGUNTAS = {
    "vestibulo": (
        "¿Por qué hay que validar antes de usar el puntaje?",
        [
            "Porque lo que se escribe puede no ser un número y el programa fallaría.",
            "Porque Python convierte cualquier texto a número automáticamente.",
            "No hace falta validar, el puntaje siempre es correcto.",
        ],
        0,
    ),
    "estanterias": (
        "¿Por qué el inventario va en una lista y no en un diccionario?",
        [
            "Porque una lista busca por clave más rápido que un diccionario.",
            "Porque la lista guarda el orden y permite ordenar, insertar y eliminar.",
            "Porque un diccionario no puede guardar textos.",
        ],
        1,
    ),
    "mapas": (
        "¿En qué se diferencia algo que se puede cambiar de algo que no?",
        [
            "No hay diferencia entre una lista y una tupla.",
            "Una tupla se puede cambiar con posicion[0] = 5.",
            "Una lista se puede modificar; una tupla no, hay que crear otra nueva.",
        ],
        2,
    ),
    "fichas": (
        "¿Qué pasa si pido una clave que no existe?",
        [
            "Con ficha[clave] sale KeyError; con ficha.get(clave) se obtiene None.",
            "Python crea la clave automáticamente con valor cero.",
            "El diccionario devuelve la primera clave que tenga.",
        ],
        0,
    ),
    "sellos": (
        "¿Por qué un conjunto quita duplicados y no guarda el orden?",
        [
            "Porque ordena los elementos de menor a mayor.",
            "Porque guarda cada elemento una sola vez y los ubica por su hash.",
            "Porque borra el último elemento repetido de la lista.",
        ],
        1,
    ),
}

# Fragmento que gana el jugador al superar cada sala: (codigo, titulo, valor).
PREMIOS = {
    "vestibulo": (901, "Registro del explorador", 5),
    "estanterias": (902, "Índice de estanterías", 10),
    "mapas": (903, "Plano de la biblioteca", 10),
    "fichas": (904, "Fichero antiguo", 10),
    "sellos": (905, "Sello del archivo", 15),
}

# Colores
FONDO = (18, 25, 43)
PANEL = (29, 40, 64)
PANEL_CLARO = (39, 53, 82)
BLANCO = (245, 247, 250)
GRIS = (177, 188, 205)
NARANJA = (245, 139, 61)
AZUL = (91, 165, 230)
ROJO = (239, 93, 108)
VERDE = (87, 190, 140)


class Jugador:
    """Datos del jugador: nombre (str), vida, puntaje y nivel (int), precision (float) y activo (bool)."""

    def __init__(self, nombre, vida, puntaje, nivel, precision, activo):
        self.nombre = nombre
        self.vida = vida
        self.puntaje = puntaje
        self.nivel = nivel
        self.precision = precision
        self.activo = activo

    def a_diccionario(self):
        """Devuelve los datos del jugador en un diccionario para poder guardarlos en JSON."""
        return {
            "nombre": self.nombre,
            "vida": self.vida,
            "puntaje": self.puntaje,
            "nivel": self.nivel,
            "precision": self.precision,
            "activo": self.activo,
        }


class CampoTexto:
    """Caja de texto sencilla, porque Pygame no trae una."""

    def __init__(self, etiqueta, rectangulo, texto=""):
        self.etiqueta = etiqueta
        self.rectangulo = rectangulo
        self.texto = texto


class Boton:
    """Botón de una pantalla: la acción que ejecuta, el texto que muestra y su rectángulo."""

    def __init__(self, accion, texto, rectangulo):
        self.accion = accion
        self.texto = texto
        self.rectangulo = rectangulo


def convertir_entero(valor, minimo=0):
    """Convierte un texto a entero y revisa que no sea menor que el mínimo.

    Parámetros:
        valor: texto que se desea convertir.
        minimo: valor entero mínimo permitido.
    Retorna:
        Una tupla (valido, numero, mensaje). Si no es válido, numero es None.
    """
    try:
        numero = int(valor.strip())
    except ValueError:
        return False, None, "Escribe un número entero válido."

    if numero < minimo:
        return False, None, f"El valor debe ser como mínimo {minimo}."

    return True, numero, ""


def convertir_decimal(valor, minimo=0.0, maximo=100.0):
    """Convierte un texto a decimal y revisa que esté dentro del rango.

    Parámetros:
        valor: texto que se desea convertir.
        minimo: límite inferior permitido.
        maximo: límite superior permitido.
    Retorna:
        Una tupla (valido, numero, mensaje). Si no es válido, numero es None.
    """
    try:
        # Se acepta tanto coma como punto decimal.
        numero = float(valor.strip().replace(",", "."))
    except ValueError:
        return False, None, "Escribe un número decimal válido (ejemplo: 95.5)."

    if numero < minimo or numero > maximo:
        return False, None, f"El valor debe estar entre {minimo} y {maximo}."

    return True, numero, ""


def crear_jugador(nombre, vida_texto, precision_texto):
    """Valida los datos del formulario y crea el jugador.

    Parámetros:
        nombre: nombre escrito por el usuario.
        vida_texto: cantidad de vidas escrita como texto.
        precision_texto: precisión escrita como texto.
    Retorna:
        Una tupla (jugador, mensaje). Si algún dato falla, jugador es None.
    """
    nombre_limpio = nombre.strip()
    if nombre_limpio == "":
        return None, "El nombre no puede quedar vacío."

    vida_valida, vida, mensaje = convertir_entero(vida_texto, minimo=1)
    if not vida_valida:
        return None, "Vida: " + mensaje

    precision_valida, precision, mensaje = convertir_decimal(precision_texto)
    if not precision_valida:
        return None, "Precisión: " + mensaje

    jugador = Jugador(nombre_limpio, vida, 0, 1, precision, True)
    return jugador, ""


def _texto_codigos(codigos, limite=12):
    """Resume una lista de códigos para mostrarla en una sola línea.

    Parámetros:
        codigos: códigos que se quieren mostrar.
        limite: cantidad máxima de códigos visibles.
    Retorna:
        Un texto con los códigos separados por comas.
    """
    if len(codigos) == 0:
        return "(ninguno)"
    if len(codigos) <= limite:
        return ", ".join(str(codigo) for codigo in codigos)
    visibles = ", ".join(str(codigo) for codigo in codigos[:limite])
    return f"{visibles}... ({len(codigos)} en total)"


def leer_fragmentos_guardados(ruta=None):
    """Lee los fragmentos de la partida guardada en JSON.

    Parámetros:
        ruta: archivo de partida. Si no se indica, se usa data/partida.json.
    Retorna:
        Una tupla (fragmentos, mensaje). Si la lectura falla, fragmentos es None
        y mensaje explica el problema. Una lista vacía sí es una lectura válida.
    """
    if ruta is None:
        ruta = persistencia.RUTA_PARTIDA

    if not os.path.isfile(ruta):
        return None, "Error: no existe el archivo de la partida."

    datos = persistencia.cargar_partida(ruta)
    if not isinstance(datos, dict):
        return None, "Error: el archivo de la partida tiene datos incorrectos."

    fragmentos = datos.get("fragmentos")
    if not isinstance(fragmentos, list):
        return None, "Error: el archivo de la partida tiene datos incompletos."

    return fragmentos, ""


def reconstruir_fragmentos(fragmentos):
    """Valida, depura e inserta los fragmentos en el árbol de búsqueda.

    Parámetros:
        fragmentos: lista de diccionarios leída desde la partida.
    Retorna:
        Un diccionario con pasos, mensaje, arbol, ubicaciones y ordenado.
        arbol queda en None cuando no hay fragmentos utilizables.
    """
    if not isinstance(fragmentos, list):
        return {
            "pasos": ["2. Los datos guardados no son una lista de fragmentos."],
            "mensaje": "Error: el archivo de la partida tiene datos incompletos.",
            "arbol": None,
            "ubicaciones": {},
            "ordenado": False,
        }

    validos = []
    incorrectos = 0
    for fragmento in fragmentos:
        if not isinstance(fragmento, dict):
            incorrectos += 1
            continue
        try:
            limpio = estructuras.crear_fragmento(
                fragmento["codigo"],
                fragmento["titulo"],
                fragmento["sala"],
                fragmento["valor"],
            )
        except (KeyError, TypeError, ValueError):
            incorrectos += 1
            continue
        validos.append(limpio)

    codigos = [fragmento["codigo"] for fragmento in validos]
    try:
        _, descartados = estructuras.eliminar_duplicados(codigos)
    except (TypeError, ValueError):
        return {
            "pasos": ["2. No se pudieron depurar los códigos con un conjunto."],
            "mensaje": "Error: los fragmentos guardados tienen datos incorrectos.",
            "arbol": None,
            "ubicaciones": {},
            "ordenado": False,
        }

    unicos = []
    vistos = set()
    for fragmento in validos:
        if fragmento["codigo"] in vistos:
            continue
        vistos.add(fragmento["codigo"])
        unicos.append(fragmento)

    if len(unicos) == 1:
        quedan = "Queda 1 fragmento."
    else:
        quedan = f"Quedan {len(unicos)} fragmentos."
    if descartados == 1:
        repetidos = "1 código repetido"
    else:
        repetidos = f"{descartados} códigos repetidos"
    pasos = [f"2. Depuración: un conjunto descartó {repetidos}. {quedan}"]
    if incorrectos == 1:
        pasos.append("   Se omitió 1 fragmento con datos incorrectos.")
    elif incorrectos:
        pasos.append(f"   Se omitieron {incorrectos} fragmentos con datos incorrectos.")

    if len(unicos) == 0:
        return {
            "pasos": pasos,
            "mensaje": "Error: no hay fragmentos válidos para reconstruir el catálogo.",
            "arbol": None,
            "ubicaciones": {},
            "ordenado": False,
        }

    ordenados = estructuras.ordenar_fragmentos(unicos)
    ubicaciones = {}
    pasos.append(
        "3. Ubicación: tupla (estante, nivel). Hay 5 niveles por estante y el orden es el del código."
    )
    for indice, fragmento in enumerate(ordenados):
        estante = indice // NIVELES_POR_ESTANTE + 1
        nivel = indice % NIVELES_POR_ESTANTE + 1
        posicion = estructuras.crear_posicion(estante, nivel)
        ubicaciones[fragmento["codigo"]] = posicion
        if indice < MAX_UBICACIONES_VISIBLES:
            estante, nivel = estructuras.desempaquetar_posicion(posicion)
            titulo = fragmento["titulo"]
            if len(titulo) > 32:
                titulo = titulo[:31] + "..."
            pasos.append(f"   {fragmento['codigo']} | {titulo} | (estante {estante}, nivel {nivel})")
    ocultos = len(ordenados) - MAX_UBICACIONES_VISIBLES
    if ocultos == 1:
        pasos.append("   ... y 1 fragmento más.")
    elif ocultos > 1:
        pasos.append(f"   ... y {ocultos} fragmentos más.")

    try:
        catalogo = arbol.reconstruir_catalogo(unicos)["arbol"]
    except (KeyError, TypeError, ValueError):
        return {
            "pasos": pasos + ["4. No se pudieron insertar los fragmentos en el árbol."],
            "mensaje": "Error: no se pudo reconstruir el catálogo.",
            "arbol": None,
            "ubicaciones": ubicaciones,
            "ordenado": False,
        }

    pasos.append(
        f"4. Inserción: se insertaron {catalogo.tamano} fragmentos en el árbol, usando el código como clave."
    )
    codigos_ordenados = [fragmento["codigo"] for fragmento in catalogo.inorden()]
    ordenado = catalogo.verificar_orden()
    if ordenado:
        pasos.append(
            f"5. Inorden: {_texto_codigos(codigos_ordenados)}. Los códigos quedaron en orden ascendente."
        )
        mensaje = "Catálogo reconstruido. El recorrido inorden está ordenado."
    else:
        pasos.append(
            f"5. Inorden: {_texto_codigos(codigos_ordenados)}. Los códigos no quedaron ordenados."
        )
        mensaje = "Error: el recorrido inorden no quedó ordenado."

    return {
        "pasos": pasos,
        "mensaje": mensaje,
        "arbol": catalogo,
        "ubicaciones": ubicaciones,
        "ordenado": ordenado,
    }


def dibujar_texto(pantalla, fuente, texto, posicion, color=BLANCO):
    """Dibuja una línea de texto en la posición (x, y) indicada."""
    superficie = fuente.render(texto, True, color)
    pantalla.blit(superficie, posicion)


def dibujar_boton(pantalla, fuente, texto, rectangulo, principal=True):
    """Dibuja un botón con el texto centrado. Si es principal se pinta naranja."""
    if principal:
        color_fondo = NARANJA
        color_texto = FONDO
    else:
        color_fondo = PANEL_CLARO
        color_texto = BLANCO
    pygame.draw.rect(pantalla, color_fondo, rectangulo, border_radius=10)
    etiqueta = fuente.render(texto, True, color_texto)
    pantalla.blit(etiqueta, etiqueta.get_rect(center=rectangulo.center))


def dibujar_campo(pantalla, fuente, campo, enfocado):
    """Dibuja la etiqueta y la caja de un CampoTexto. El campo con foco lleva borde naranja."""
    rectangulo = campo.rectangulo
    dibujar_texto(pantalla, fuente, campo.etiqueta, (rectangulo.x, rectangulo.y - 26), GRIS)
    if enfocado:
        borde = NARANJA
    else:
        borde = (83, 101, 132)
    pygame.draw.rect(pantalla, PANEL_CLARO, rectangulo, border_radius=10)
    pygame.draw.rect(pantalla, borde, rectangulo, width=2, border_radius=10)
    texto = fuente.render(campo.texto, True, BLANCO)
    pantalla.blit(texto, (rectangulo.x + 12, rectangulo.y + 9))


class Juego:
    """Guarda el estado de la partida y controla las pantallas."""

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("El Archivo Perdido")
        self.pantalla = pygame.display.set_mode((ANCHO, ALTO))
        self.reloj = pygame.time.Clock()
        self.fuentes = {
            "titulo": pygame.font.SysFont("arial", 42, bold=True),
            "subtitulo": pygame.font.SysFont("arial", 27, bold=True),
            "normal": pygame.font.SysFont("arial", 20),
            "pequena": pygame.font.SysFont("arial", 16),
        }

        self.estado = "menu"
        self.mensaje = ""
        self.ejecutando = True
        self.jugador = None

        # Campos de texto de la pantalla actual y el que recibe el teclado.
        self.campos = []
        self.foco = 0

        # Botones de la pantalla actual.
        self.botones = []
        self.reto_superado = False

        # Lista de fragmentos recolectados (cada fragmento es un diccionario).
        self.inventario = []

        # Datos de la Sala de Mapas.
        self.objetivo = estructuras.crear_posicion(3, 4)
        self.recorrido = []

        # Datos de la Sala de Fichas.
        self.ficha_actual = None

        # Datos de la Sala de Sellos: dos pistas con códigos repetidos.
        self.pistas = {
            "a": [101, 102, 102, 105, 107, 107],
            "b": [102, 105, 105, 110, 110, 110],
        }
        self.resultados_sellos = []

        # Progreso de las preguntas.
        self.sala_pregunta = None
        self.respuesta_correcta = False
        self.aciertos = 0
        self.respondidas = 0
        self.intentos = 0

        # Tabla de puntajes que se muestra al final.
        self.puntajes = []
        self.puntaje_guardado = False

        # Sala Central: árbol reconstruido, ubicaciones y pasos visibles.
        self.arbol_catalogo = None
        self.ubicaciones_catalogo = {}
        self.pasos_sala = []

        self.botones_menu = [
            Boton("iniciar", "Iniciar partida", pygame.Rect(370, 300, 260, 50)),
            Boton("cargar", "Cargar partida", pygame.Rect(370, 370, 260, 50)),
            Boton("salir", "Salir", pygame.Rect(370, 440, 260, 50)),
        ]

    # ------------------------------------------------------------------
    # Menú principal
    # ------------------------------------------------------------------
    def dibujar_menu(self):
        """Muestra el título y las opciones de inicio."""
        self.pantalla.fill(FONDO)
        pygame.draw.rect(self.pantalla, NARANJA, (0, 0, ANCHO, 9))
        dibujar_texto(self.pantalla, self.fuentes["pequena"], "PROYECTO DE ESTRUCTURAS DE DATOS", (330, 130), AZUL)
        dibujar_texto(self.pantalla, self.fuentes["titulo"], "EL ARCHIVO PERDIDO", (290, 160))
        dibujar_texto(
            self.pantalla,
            self.fuentes["normal"],
            "El catálogo de la biblioteca ha desaparecido. Ayúdanos a reconstruirlo.",
            (190, 225),
            GRIS,
        )

        for boton in self.botones_menu:
            principal = boton.accion == "iniciar"
            dibujar_boton(self.pantalla, self.fuentes["normal"], boton.texto, boton.rectangulo, principal)

        self.dibujar_mensaje((300, 510))

    def clic_menu(self, posicion):
        """Atiende los clics del menú principal."""
        for boton in self.botones_menu:
            if boton.rectangulo.collidepoint(posicion):
                if boton.accion == "iniciar":
                    self.abrir_registro()
                elif boton.accion == "cargar":
                    self.cargar()
                elif boton.accion == "salir":
                    self.ejecutando = False

    # ------------------------------------------------------------------
    # Ayudas comunes
    # ------------------------------------------------------------------
    def dibujar_encabezado(self, titulo, descripcion):
        """Limpia la pantalla y dibuja el título de la sala y el estado del jugador."""
        self.pantalla.fill(FONDO)
        pygame.draw.rect(self.pantalla, NARANJA, (0, 0, ANCHO, 9))
        dibujar_texto(self.pantalla, self.fuentes["subtitulo"], titulo, (40, 25))
        dibujar_texto(self.pantalla, self.fuentes["pequena"], descripcion, (40, 62), GRIS)

        if self.jugador is not None:
            estado_jugador = f"{self.jugador.nombre}  |  Vida: {self.jugador.vida}  |  Puntaje: {self.jugador.puntaje}  |  Nivel: {self.jugador.nivel}  |  Precisión: {self.jugador.precision:.1f}%"
            dibujar_texto(self.pantalla, self.fuentes["pequena"], estado_jugador, (40, ALTO - 30), AZUL)

    def dibujar_campos(self):
        """Dibuja todos los campos de texto de la pantalla actual."""
        for indice, campo in enumerate(self.campos):
            dibujar_campo(self.pantalla, self.fuentes["normal"], campo, indice == self.foco)

    def dibujar_botones(self):
        """Dibuja los botones de la pantalla actual. El de terminar va en naranja."""
        for boton in self.botones:
            principal = boton.accion == "terminar"
            dibujar_boton(self.pantalla, self.fuentes["normal"], boton.texto, boton.rectangulo, principal)

    def boton_presionado(self, posicion):
        """Devuelve la acción del botón que está en la posición del clic, o None si no hay ninguno."""
        for boton in self.botones:
            if boton.rectangulo.collidepoint(posicion):
                return boton.accion
        return None

    def leer_entero(self, indice_campo, nombre, minimo=0):
        """Lee un entero del campo indicado. Si el texto no sirve, guarda el error y devuelve None."""
        valido, numero, mensaje = convertir_entero(self.campos[indice_campo].texto, minimo)
        if not valido:
            self.mensaje = f"Error: {nombre}: {mensaje}"
            return None
        return numero

    def dibujar_inventario(self, x, y, maximo=8):
        """Muestra hasta 'maximo' fragmentos del inventario empezando en (x, y)."""
        titulo = f"Inventario ({len(self.inventario)} fragmentos)"
        dibujar_texto(self.pantalla, self.fuentes["normal"], titulo, (x, y), NARANJA)

        if len(self.inventario) == 0:
            dibujar_texto(self.pantalla, self.fuentes["pequena"], "Todavía no hay fragmentos.", (x, y + 32), GRIS)
            return

        for indice, fragmento in enumerate(self.inventario[:maximo]):
            linea = f"Código {fragmento['codigo']}  |  {fragmento['titulo']}  |  {fragmento['sala']}  |  valor {fragmento['valor']}"
            dibujar_texto(self.pantalla, self.fuentes["pequena"], linea, (x, y + 32 + indice * 26))

        if len(self.inventario) > maximo:
            restantes = len(self.inventario) - maximo
            dibujar_texto(self.pantalla, self.fuentes["pequena"], f"... y {restantes} más", (x, y + 32 + maximo * 26), GRIS)

    def dibujar_mensaje(self, posicion):
        """Muestra el último mensaje; en rojo si empieza por Error y en verde si no."""
        if self.mensaje != "":
            if self.mensaje.startswith("Error"):
                color = ROJO
            else:
                color = VERDE
            dibujar_texto(self.pantalla, self.fuentes["pequena"], self.mensaje, posicion, color)

    # ------------------------------------------------------------------
    # Preguntas y avance entre salas
    # ------------------------------------------------------------------
    def terminar_sala(self):
        """Muestra la pregunta conceptual de la sala que se acaba de superar."""
        self.sala_pregunta = self.estado
        self.estado = "pregunta"
        self.mensaje = ""
        self.campos = []

        pregunta, opciones, correcta = PREGUNTAS[self.sala_pregunta]
        self.botones = []
        for indice in range(len(opciones)):
            texto = f"{indice + 1}. {opciones[indice]}"
            rectangulo = pygame.Rect(40, 230 + indice * 70, 920, 52)
            self.botones.append(Boton("opcion_" + str(indice), texto, rectangulo))

    def responder(self, indice):
        """Revisa la opción elegida, actualiza el puntaje y entrega el fragmento de la sala."""
        pregunta, opciones, correcta = PREGUNTAS[self.sala_pregunta]
        self.respondidas += 1
        self.respuesta_correcta = indice == correcta

        if self.respuesta_correcta:
            self.aciertos += 1
            self.jugador.puntaje += PUNTOS_POR_ACIERTO
        else:
            # Una respuesta incorrecta gasta un intento, pero se puede seguir.
            self.intentos += 1
            self.jugador.vida -= 1

        self.jugador.precision = self.aciertos / self.respondidas * 100
        self.jugador.nivel += 1

        codigo, titulo, valor = PREMIOS[self.sala_pregunta]
        premio = estructuras.crear_fragmento(codigo, titulo, self.sala_pregunta.capitalize(), valor)
        estructuras.agregar_fragmento(self.inventario, premio)

        if self.jugador.vida <= 0:
            self.jugador.activo = False

        self.estado = "respuesta"
        self.botones = [Boton("continuar", "Continuar", pygame.Rect(760, 595, 200, 42))]

    def abrir_sala(self, sala):
        """Abre la sala de recolección indicada y le agrega el botón de guardar."""
        if sala == "mapas":
            self.abrir_mapas()
        elif sala == "fichas":
            self.abrir_fichas()
        elif sala == "sellos":
            self.abrir_sellos()
        else:
            self.abrir_estanterias()

        # En todas las salas se puede guardar la partida.
        self.botones.append(Boton("guardar", "Guardar", pygame.Rect(40, 595, 150, 42)))

    def avanzar_sala(self):
        """Abre la sala siguiente. Después de Sellos abre la Sala Central.

        Si el jugador se queda sin vidas antes de la última sala, pasa al resumen.
        """
        indice = SALAS.index(self.sala_pregunta)

        if indice == len(SALAS) - 1:
            self.abrir_sala_central()
        elif not self.jugador.activo:
            self.abrir_fin()
        else:
            self.abrir_sala(SALAS[indice + 1])

    def dibujar_pregunta(self):
        """Muestra la pregunta conceptual y sus opciones."""
        pregunta, opciones, correcta = PREGUNTAS[self.sala_pregunta]
        self.dibujar_encabezado("Pregunta de la sala", "Elige la opción correcta para ganar puntos.")
        dibujar_texto(self.pantalla, self.fuentes["subtitulo"], pregunta, (40, 140))
        for boton in self.botones:
            dibujar_boton(self.pantalla, self.fuentes["normal"], boton.texto, boton.rectangulo, False)

    def dibujar_respuesta(self):
        """Informa si la respuesta fue correcta y muestra el avance."""
        self.dibujar_encabezado("Resultado", "Así va tu partida.")
        pregunta, opciones, correcta = PREGUNTAS[self.sala_pregunta]
        if self.respuesta_correcta:
            dibujar_texto(self.pantalla, self.fuentes["titulo"], "¡Respuesta correcta!", (40, 110), VERDE)
            detalle = f"Ganaste {PUNTOS_POR_ACIERTO} puntos."
        else:
            dibujar_texto(self.pantalla, self.fuentes["titulo"], "Respuesta incorrecta", (40, 110), ROJO)
            detalle = f"Perdiste una vida. La correcta era: {opciones[correcta]}"
        dibujar_texto(self.pantalla, self.fuentes["normal"], detalle, (40, 170))

        codigo, titulo, valor = PREMIOS[self.sala_pregunta]
        dibujar_texto(self.pantalla, self.fuentes["normal"], f"Fragmento obtenido: {codigo} - {titulo}", (40, 205), NARANJA)

        salas_superadas = SALAS.index(self.sala_pregunta) + 1
        avance = f"Avance: {salas_superadas} de {len(SALAS)} etapas  |  Intentos fallidos: {self.intentos}"
        dibujar_texto(self.pantalla, self.fuentes["normal"], avance, (40, 240), AZUL)
        self.dibujar_inventario(40, 290)
        self.dibujar_botones()

    # ------------------------------------------------------------------
    # Guardar y cargar con persistencia.py
    # ------------------------------------------------------------------
    def datos_partida(self):
        """Reúne en un diccionario todo lo que se guarda de la partida."""
        return {
            "jugador": self.jugador.a_diccionario(),
            "sala_actual": self.estado,
            "fragmentos": self.inventario,
            "pistas": self.pistas,
            "aciertos": self.aciertos,
            "respondidas": self.respondidas,
            "intentos": self.intentos,
        }

    def crear_carpeta_data(self):
        """Crea la carpeta data/ si no existe, porque ahí escribe persistencia.py.

        Retorna:
            True si la carpeta existe o se pudo crear; False si hubo un error del sistema.
        """
        try:
            os.makedirs(persistencia.DATA_DIR, exist_ok=True)
            return True
        except OSError:
            return False

    def guardar(self):
        """Guarda la partida actual con persistencia.guardar_partida, que devuelve True o False."""
        exito = False
        if self.crear_carpeta_data():
            exito = persistencia.guardar_partida(self.datos_partida())

        if exito:
            self.mensaje = "Partida guardada en data/partida.json."
        else:
            self.mensaje = "Error: no se pudo guardar la partida."

    def cargar(self):
        """Carga la partida con persistencia.cargar_partida y abre la sala donde iba el jugador.

        cargar_partida devuelve None si el archivo no existe o está dañado.
        Si el archivo existe pero le faltan datos, se avisa y se sigue en el menú.
        """
        datos = persistencia.cargar_partida()
        if datos is None:
            self.mensaje = "Error: no hay una partida guardada o el archivo está dañado."
            return

        try:
            datos_jugador = datos["jugador"]
            jugador = Jugador(
                datos_jugador["nombre"],
                int(datos_jugador["vida"]),
                int(datos_jugador["puntaje"]),
                int(datos_jugador["nivel"]),
                float(datos_jugador["precision"]),
                bool(datos_jugador["activo"]),
            )
            sala = datos["sala_actual"]

            # agregar_fragmento valida cada ficha y descarta códigos repetidos.
            inventario = []
            for fragmento in datos["fragmentos"]:
                estructuras.agregar_fragmento(inventario, fragmento)

            pistas = {"a": list(datos["pistas"]["a"]), "b": list(datos["pistas"]["b"])}
            aciertos = int(datos["aciertos"])
            respondidas = int(datos["respondidas"])
            intentos = int(datos["intentos"])
        except (KeyError, TypeError, ValueError):
            self.mensaje = "Error: el archivo de la partida tiene datos incompletos."
            return

        if not isinstance(jugador.nombre, str) or sala not in (*SALAS, "sala_central"):
            self.mensaje = "Error: el archivo de la partida tiene datos incompletos."
            return

        self.jugador = jugador
        self.inventario = inventario
        self.pistas = pistas
        self.aciertos = aciertos
        self.respondidas = respondidas
        self.intentos = intentos
        if sala == "sala_central":
            self.abrir_sala_central(guardar_antes=False)
            if not self.mensaje.startswith("Error"):
                self.mensaje = f"Partida de {self.jugador.nombre} cargada."
        else:
            self.abrir_sala(sala)
            self.mensaje = f"Partida de {self.jugador.nombre} cargada."

    def guardar_puntaje(self):
        """Agrega el resultado final a la tabla con persistencia.guardar_puntaje."""
        if self.puntaje_guardado:
            self.mensaje = "Error: este puntaje ya se guardó."
            return

        registro = {
            "nombre": self.jugador.nombre,
            "puntaje": self.jugador.puntaje,
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "fragmentos_validos": len(self.inventario),
            "intentos": self.intentos,
        }

        exito = False
        if self.crear_carpeta_data():
            exito = persistencia.guardar_puntaje(registro)

        if exito:
            self.puntaje_guardado = True
            self.puntajes = persistencia.cargar_puntajes()
            self.mensaje = "Puntaje guardado en data/puntajes.json."
        else:
            self.mensaje = "Error: no se pudo guardar el puntaje."

    # ------------------------------------------------------------------
    # Pantalla final de la recolección
    # ------------------------------------------------------------------
    def abrir_fin(self):
        """Prepara la pantalla final de la semana 2."""
        self.estado = "fin"
        self.mensaje = ""
        self.puntaje_guardado = False
        # La tabla se lee una sola vez aquí y no en cada dibujo, para no abrir el archivo 60 veces por segundo.
        self.puntajes = persistencia.cargar_puntajes()
        self.botones = [
            Boton("guardar_puntaje", "Guardar puntaje", pygame.Rect(530, 595, 210, 42)),
            Boton("salir", "Salir", pygame.Rect(760, 595, 200, 42)),
        ]

    def dibujar_puntajes(self, x, y, maximo=8):
        """Muestra los mejores puntajes guardados, de mayor a menor."""
        dibujar_texto(self.pantalla, self.fuentes["normal"], "Tabla de puntajes", (x, y), NARANJA)
        if len(self.puntajes) == 0:
            dibujar_texto(self.pantalla, self.fuentes["pequena"], "Todavía no hay puntajes guardados.", (x, y + 32), GRIS)
            return

        ordenados = sorted(self.puntajes, key=lambda registro: registro.get("puntaje", 0), reverse=True)
        for indice, registro in enumerate(ordenados[:maximo]):
            linea = f"{indice + 1}. {registro.get('nombre', '?')}  |  {registro.get('puntaje', 0)} pts  |  {registro.get('fecha', '')}"
            dibujar_texto(self.pantalla, self.fuentes["pequena"], linea, (x, y + 32 + indice * 26))

    def dibujar_fin(self):
        """Muestra el resumen de la partida y la tabla de puntajes."""
        self.dibujar_encabezado("Fin de la recolección", "Resumen de la partida y tabla de puntajes.")
        if self.jugador.activo:
            dibujar_texto(self.pantalla, self.fuentes["titulo"], "¡Recolectaste los fragmentos!", (40, 110), VERDE)
        else:
            dibujar_texto(self.pantalla, self.fuentes["titulo"], "Te quedaste sin vidas", (40, 110), ROJO)

        resumen = f"Puntaje: {self.jugador.puntaje}  |  Aciertos: {self.aciertos} de {self.respondidas}  |  Intentos fallidos: {self.intentos}"
        dibujar_texto(self.pantalla, self.fuentes["normal"], resumen, (40, 175))
        self.dibujar_inventario(40, 225, maximo=10)
        self.dibujar_puntajes(560, 225)
        self.dibujar_mensaje((40, 560))
        self.dibujar_botones()

    def accion_fin(self, accion):
        """Atiende los botones de la pantalla final."""
        if accion == "guardar_puntaje":
            self.guardar_puntaje()
        elif accion == "salir":
            self.ejecutando = False

    # ------------------------------------------------------------------
    # Vestíbulo: registro del jugador
    # ------------------------------------------------------------------
    def abrir_registro(self):
        """Prepara los campos del formulario de registro."""
        self.estado = "registro"
        self.mensaje = ""
        self.foco = 0
        self.campos = [
            CampoTexto("Nombre del jugador", pygame.Rect(100, 250, 800, 42)),
            CampoTexto("Vidas iniciales (entero)", pygame.Rect(100, 340, 380, 42), "3"),
            CampoTexto("Precisión inicial (0 a 100)", pygame.Rect(520, 340, 380, 42), "100"),
        ]
        self.boton_registrar = pygame.Rect(700, 470, 200, 45)

    def dibujar_registro(self):
        """Muestra el formulario de registro del vestíbulo."""
        self.dibujar_encabezado("Vestíbulo", "Registra los datos de tu explorador.")
        dibujar_texto(self.pantalla, self.fuentes["titulo"], "EL ARCHIVO PERDIDO", (100, 120))
        self.dibujar_campos()
        dibujar_texto(self.pantalla, self.fuentes["pequena"], "Usa TAB para cambiar de campo y ENTER para continuar.", (100, 410), GRIS)
        self.dibujar_mensaje((100, 440))
        dibujar_boton(self.pantalla, self.fuentes["normal"], "Comenzar", self.boton_registrar)

    def registrar_jugador(self):
        """Valida el formulario y, si todo está bien, crea el jugador."""
        jugador, mensaje = crear_jugador(self.campos[0].texto, self.campos[1].texto, self.campos[2].texto)
        if jugador is None:
            # La partida no se cierra: se muestra el error y se puede corregir.
            self.mensaje = "Error: " + mensaje
            return

        self.jugador = jugador
        self.mensaje = ""
        self.campos = []
        self.estado = "bienvenida"
        self.boton_continuar = pygame.Rect(700, 560, 200, 45)

    def dibujar_bienvenida(self):
        """Muestra el resumen del jugador después de validar el registro."""
        self.dibujar_encabezado("Vestíbulo", "Tu explorador quedó registrado correctamente.")
        dibujar_texto(self.pantalla, self.fuentes["titulo"], f"¡Bienvenido, {self.jugador.nombre}!", (60, 110))

        datos = [
            f"Nombre (str): {self.jugador.nombre}",
            f"Vida (int): {self.jugador.vida}",
            f"Puntaje (int): {self.jugador.puntaje}",
            f"Nivel (int): {self.jugador.nivel}",
            f"Precisión (float): {self.jugador.precision:.1f}%",
            f"Partida activa (bool): {self.jugador.activo}",
        ]
        for indice, dato in enumerate(datos):
            dibujar_texto(self.pantalla, self.fuentes["normal"], dato, (80, 200 + indice * 38))

        dibujar_boton(self.pantalla, self.fuentes["normal"], "Continuar", self.boton_continuar)

    def clic_bienvenida(self, posicion):
        """Al presionar Continuar termina el vestíbulo y sale su pregunta."""
        if self.boton_continuar.collidepoint(posicion):
            self.estado = "vestibulo"
            self.terminar_sala()

    # ------------------------------------------------------------------
    # Sala de Estanterías: listas
    # ------------------------------------------------------------------
    def abrir_estanterias(self):
        """Prepara los campos y botones de la Sala de Estanterías."""
        self.estado = "estanterias"
        self.mensaje = ""
        self.foco = 0
        self.reto_superado = False
        self.campos = [
            CampoTexto("Código", pygame.Rect(40, 125, 200, 42)),
            CampoTexto("Título", pygame.Rect(270, 125, 420, 42)),
            CampoTexto("Valor", pygame.Rect(720, 125, 240, 42)),
        ]
        self.botones = [
            Boton("agregar", "Agregar", pygame.Rect(40, 185, 170, 42)),
            Boton("buscar", "Buscar", pygame.Rect(225, 185, 170, 42)),
            Boton("eliminar", "Eliminar", pygame.Rect(410, 185, 170, 42)),
            Boton("ordenar", "Ordenar", pygame.Rect(595, 185, 170, 42)),
            Boton("terminar", "Terminar sala", pygame.Rect(760, 595, 200, 42)),
        ]

    def dibujar_estanterias(self):
        """Muestra el inventario y las operaciones de la lista."""
        self.dibujar_encabezado(
            "Sala de Estanterías",
            "El inventario es una lista: agrega, busca, elimina y ordena fragmentos por código.",
        )
        self.dibujar_campos()
        self.dibujar_botones()
        self.dibujar_mensaje((40, 245))
        self.dibujar_inventario(40, 285)

        # Comprensión de listas hecha en estructuras.py.
        codigos = estructuras.obtener_codigos_por_sala(self.inventario, "Estanterias")
        dibujar_texto(self.pantalla, self.fuentes["pequena"], f"Códigos de esta sala (comprensión de listas): {codigos}", (40, 560), AZUL)

    def accion_estanterias(self, accion):
        """Ejecuta la operación de lista que eligió el jugador."""
        if accion == "ordenar":
            self.inventario = estructuras.ordenar_fragmentos(self.inventario)
            self.mensaje = "Inventario ordenado de menor a mayor código."
            return

        if accion == "terminar":
            if len(self.inventario) == 0:
                self.mensaje = "Error: agrega al menos un fragmento antes de terminar la sala."
            else:
                self.terminar_sala()
            return

        codigo = self.leer_entero(0, "Código", minimo=1)
        if codigo is None:
            return

        if accion == "agregar":
            valor = self.leer_entero(2, "Valor", minimo=0)
            if valor is None:
                return
            fragmento = estructuras.crear_fragmento(codigo, self.campos[1].texto, "Estanterias", valor)
            if estructuras.agregar_fragmento(self.inventario, fragmento):
                self.mensaje = f"Fragmento {codigo} agregado al inventario."
            else:
                self.mensaje = f"Error: ya existe un fragmento con el código {codigo}."

        elif accion == "buscar":
            fragmento = estructuras.buscar_fragmento(self.inventario, codigo)
            if fragmento is None:
                self.mensaje = f"Error: no hay ningún fragmento con el código {codigo}."
            else:
                self.mensaje = f"Encontrado: {codigo} - {fragmento['titulo']} (valor {fragmento['valor']})."

        elif accion == "eliminar":
            if estructuras.eliminar_fragmento(self.inventario, codigo):
                self.mensaje = f"Fragmento {codigo} eliminado."
            else:
                self.mensaje = f"Error: no hay ningún fragmento con el código {codigo}."

    # ------------------------------------------------------------------
    # Sala de Mapas: tuplas
    # ------------------------------------------------------------------
    def abrir_mapas(self):
        """Prepara la cuadrícula y el recorrido de la Sala de Mapas."""
        self.estado = "mapas"
        self.mensaje = ""
        self.foco = 0
        self.reto_superado = False
        self.recorrido = [estructuras.crear_posicion(0, 0)]
        self.campos = [
            CampoTexto("Fila", pygame.Rect(40, 125, 140, 42)),
            CampoTexto("Columna", pygame.Rect(200, 125, 140, 42)),
        ]
        self.botones = [
            Boton("mover", "Mover", pygame.Rect(360, 125, 140, 42)),
            Boton("terminar", "Terminar sala", pygame.Rect(760, 595, 200, 42)),
        ]

    def dibujar_mapas(self):
        """Muestra la cuadrícula, la posición actual y el recorrido."""
        self.dibujar_encabezado(
            "Sala de Mapas",
            "Cada posición es una tupla (fila, columna). No se modifica: cada paso crea una tupla nueva.",
        )
        self.dibujar_campos()
        self.dibujar_botones()
        self.dibujar_mensaje((40, 185))

        dibujar_texto(self.pantalla, self.fuentes["normal"], "Pista del fragmento:", (40, 230), NARANJA)
        dibujar_texto(self.pantalla, self.fuentes["pequena"], "La fila es la mitad de 6 y la columna es 2 + 2.", (40, 262))

        dibujar_texto(self.pantalla, self.fuentes["normal"], "Recorrido (lista de tuplas):", (40, 310), NARANJA)
        for indice, posicion in enumerate(self.recorrido[-8:]):
            fila, columna = estructuras.desempaquetar_posicion(posicion)
            linea = f"{posicion}  ->  fila = {fila}, columna = {columna}"
            dibujar_texto(self.pantalla, self.fuentes["pequena"], linea, (40, 342 + indice * 26))

        # Cuadrícula de la biblioteca.
        celda = 65
        origen_x = 560
        origen_y = 130
        actual = self.recorrido[-1]
        for fila in range(TAMANO_MAPA):
            dibujar_texto(self.pantalla, self.fuentes["pequena"], str(fila), (origen_x - 22, origen_y + fila * celda + 22), GRIS)
            for columna in range(TAMANO_MAPA):
                if fila == 0:
                    dibujar_texto(self.pantalla, self.fuentes["pequena"], str(columna), (origen_x + columna * celda + 28, origen_y - 24), GRIS)
                posicion = (fila, columna)
                rectangulo = pygame.Rect(origen_x + columna * celda, origen_y + fila * celda, celda - 4, celda - 4)
                color = PANEL
                if posicion in self.recorrido:
                    color = PANEL_CLARO
                if posicion == actual:
                    color = NARANJA
                if self.reto_superado and posicion == self.objetivo:
                    color = VERDE
                pygame.draw.rect(self.pantalla, color, rectangulo, border_radius=6)

    def accion_mapas(self, accion):
        """Mueve al jugador a la posición escrita o termina la sala."""
        if accion == "terminar":
            if not self.reto_superado:
                self.mensaje = "Error: primero encuentra la posición del fragmento."
            else:
                self.terminar_sala()
            return

        fila = self.leer_entero(0, "Fila")
        if fila is None:
            return
        columna = self.leer_entero(1, "Columna")
        if columna is None:
            return
        if fila >= TAMANO_MAPA or columna >= TAMANO_MAPA:
            self.mensaje = f"Error: el mapa solo tiene filas y columnas de 0 a {TAMANO_MAPA - 1}."
            return

        # La posición es una tupla nueva; el recorrido es la lista de tuplas visitadas.
        posicion = estructuras.crear_posicion(fila, columna)
        self.recorrido.append(posicion)
        fila, columna = estructuras.desempaquetar_posicion(posicion)

        if posicion == self.objetivo:
            self.reto_superado = True
            self.mensaje = f"¡Encontraste el fragmento en {posicion}! Ya puedes terminar la sala."
            return

        objetivo_fila, objetivo_columna = estructuras.desempaquetar_posicion(self.objetivo)
        if objetivo_fila > fila:
            vertical = "más abajo"
        elif objetivo_fila < fila:
            vertical = "más arriba"
        else:
            vertical = "en esta fila"

        if objetivo_columna > columna:
            horizontal = "más a la derecha"
        elif objetivo_columna < columna:
            horizontal = "más a la izquierda"
        else:
            horizontal = "en esta columna"

        self.mensaje = f"Aquí no está. El fragmento está {vertical} y {horizontal}."

    # ------------------------------------------------------------------
    # Sala de Fichas: diccionarios
    # ------------------------------------------------------------------
    def abrir_fichas(self):
        """Prepara la consulta de fichas por código y por clave."""
        self.estado = "fichas"
        self.mensaje = ""
        self.foco = 0
        self.reto_superado = False
        self.ficha_actual = None
        self.campos = [
            CampoTexto("Código del fragmento", pygame.Rect(40, 125, 200, 42)),
            CampoTexto("Clave (codigo, titulo, sala, valor...)", pygame.Rect(270, 125, 300, 42)),
        ]
        self.botones = [
            Boton("consultar", "Consultar ficha", pygame.Rect(590, 125, 180, 42)),
            Boton("clave", "Consultar clave", pygame.Rect(785, 125, 175, 42)),
            Boton("terminar", "Terminar sala", pygame.Rect(760, 595, 200, 42)),
        ]

    def dibujar_fichas(self):
        """Muestra la ficha consultada y el inventario disponible."""
        self.dibujar_encabezado(
            "Sala de Fichas",
            "Cada ficha es un diccionario. Consulta un fragmento por su código y luego pide una clave.",
        )
        self.dibujar_campos()
        self.dibujar_botones()
        self.dibujar_mensaje((40, 185))

        panel = pygame.Rect(40, 225, 430, 190)
        pygame.draw.rect(self.pantalla, PANEL, panel, border_radius=14)
        dibujar_texto(self.pantalla, self.fuentes["normal"], "Ficha consultada", (60, 238), NARANJA)
        if self.ficha_actual is None:
            dibujar_texto(self.pantalla, self.fuentes["pequena"], "Escribe un código y presiona Consultar ficha.", (60, 275), GRIS)
        else:
            for indice, clave in enumerate(estructuras.CLAVES_FRAGMENTO):
                valor = estructuras.consultar_ficha(self.ficha_actual, clave)
                dibujar_texto(self.pantalla, self.fuentes["normal"], f"{clave}: {valor}", (60, 275 + indice * 32))

        self.dibujar_inventario(510, 225, maximo=10)

    def accion_fichas(self, accion):
        """Consulta una ficha completa o una sola clave de la ficha."""
        if accion == "terminar":
            if not self.reto_superado:
                self.mensaje = "Error: consulta al menos una ficha que exista."
            else:
                self.terminar_sala()
            return

        if accion == "consultar":
            codigo = self.leer_entero(0, "Código", minimo=1)
            if codigo is None:
                return
            ficha = estructuras.buscar_fragmento(self.inventario, codigo)
            if ficha is None:
                self.mensaje = f"Error: el código {codigo} no existe en el inventario."
            else:
                self.ficha_actual = ficha
                self.reto_superado = True
                self.mensaje = f"Ficha {codigo} encontrada."

        elif accion == "clave":
            if self.ficha_actual is None:
                self.mensaje = "Error: primero consulta una ficha por su código."
                return
            clave = self.campos[1].texto.strip()
            valor = estructuras.consultar_ficha(self.ficha_actual, clave)
            if valor is None:
                self.mensaje = f"Error: la clave '{clave}' no existe en la ficha. Las claves son: codigo, titulo, sala y valor."
            else:
                self.mensaje = f"{clave} = {valor}"

    # ------------------------------------------------------------------
    # Sala de Sellos: conjuntos
    # ------------------------------------------------------------------
    def abrir_sellos(self):
        """Prepara las pistas y las operaciones de conjuntos."""
        self.estado = "sellos"
        self.mensaje = ""
        self.campos = []
        self.reto_superado = False
        self.resultados_sellos = []
        self.botones = [
            Boton("duplicados", "Quitar repetidos", pygame.Rect(40, 215, 200, 42)),
            Boton("union", "Unión", pygame.Rect(255, 215, 150, 42)),
            Boton("interseccion", "Intersección", pygame.Rect(420, 215, 150, 42)),
            Boton("diferencia", "Diferencia A - B", pygame.Rect(585, 215, 190, 42)),
            Boton("terminar", "Terminar sala", pygame.Rect(760, 595, 200, 42)),
        ]

    def dibujar_sellos(self):
        """Muestra las dos pistas y los resultados de las operaciones."""
        self.dibujar_encabezado(
            "Sala de Sellos",
            "Las pistas son grupos de códigos. Un conjunto quita los repetidos y permite compararlas.",
        )
        dibujar_texto(self.pantalla, self.fuentes["normal"], f"Pista A: {self.pistas['a']}", (40, 110))
        dibujar_texto(self.pantalla, self.fuentes["normal"], f"Pista B: {self.pistas['b']}", (40, 145))
        self.dibujar_botones()
        self.dibujar_mensaje((40, 275))

        for indice, linea in enumerate(self.resultados_sellos[-8:]):
            dibujar_texto(self.pantalla, self.fuentes["normal"], linea, (40, 315 + indice * 32))

        dibujar_texto(self.pantalla, self.fuentes["pequena"], "Nota: un conjunto no guarda orden; aquí se muestra ordenado solo para leerlo mejor.", (40, 565), GRIS)

    def accion_sellos(self, accion):
        """Ejecuta la operación de conjuntos elegida."""
        if accion == "terminar":
            if not self.reto_superado:
                self.mensaje = "Error: primero quita los códigos repetidos de las pistas."
            else:
                self.terminar_sala()
            return

        if accion == "duplicados":
            unicos_a, repetidos_a = estructuras.eliminar_duplicados(self.pistas["a"])
            unicos_b, repetidos_b = estructuras.eliminar_duplicados(self.pistas["b"])
            self.resultados_sellos.append(f"Pista A sin repetidos: {sorted(unicos_a)}  (se eliminaron {repetidos_a})")
            self.resultados_sellos.append(f"Pista B sin repetidos: {sorted(unicos_b)}  (se eliminaron {repetidos_b})")
            self.reto_superado = True
            self.mensaje = f"Se eliminaron {repetidos_a + repetidos_b} códigos repetidos en total."
            return

        resultado = estructuras.operaciones_conjuntos(self.pistas["a"], self.pistas["b"])
        if accion == "union":
            self.resultados_sellos.append(f"Unión A | B: {sorted(resultado['union'])}")
        elif accion == "interseccion":
            self.resultados_sellos.append(f"Intersección A & B: {sorted(resultado['interseccion'])}")
        elif accion == "diferencia":
            self.resultados_sellos.append(f"Diferencia A - B: {sorted(resultado['diferencia_a_b'])}")
        self.mensaje = ""

    # ------------------------------------------------------------------
    # Sala Central: reconstrucción del catálogo
    # ------------------------------------------------------------------
    def abrir_sala_central(self, guardar_antes=True):
        """Abre la Sala Central y reconstruye el catálogo con la partida guardada.

        Parámetros:
            guardar_antes: True escribe el inventario actual en JSON antes de leerlo.
        Retorna:
            None.
        """
        self.estado = "sala_central"
        self.mensaje = ""
        self.foco = 0
        self.campos = [CampoTexto("Código a buscar", pygame.Rect(40, 508, 240, 42))]
        self.botones = [
            Boton("buscar", "Buscar", pygame.Rect(300, 508, 150, 42)),
            Boton("reconstruir", "Reconstruir", pygame.Rect(530, 595, 210, 42)),
            Boton("terminar", "Ver puntajes", pygame.Rect(760, 595, 200, 42)),
        ]
        self.reconstruir_sala_central(guardar_antes)

    def reconstruir_sala_central(self, guardar_antes=True):
        """Carga el JSON, depura los fragmentos y muestra cada paso del árbol.

        Parámetros:
            guardar_antes: True actualiza data/partida.json con la partida en curso.
        Retorna:
            None. Un fallo de lectura o de datos deja el juego abierto y muestra el motivo.
        """
        self.arbol_catalogo = None
        self.ubicaciones_catalogo = {}
        self.pasos_sala = []

        try:
            if guardar_antes and not persistencia.guardar_partida(self.datos_partida()):
                self.pasos_sala.append(
                    "No se pudo escribir la partida actual. Se lee el archivo que ya estaba guardado."
                )

            fragmentos, error = leer_fragmentos_guardados()
            if error:
                detalle = error.removeprefix("Error: ")
                self.pasos_sala.append(f"1. Carga: {detalle}")
                self.mensaje = error
                return

            if len(fragmentos) == 0:
                self.pasos_sala.append("1. Carga: el archivo se leyó, pero no hay fragmentos guardados.")
                self.mensaje = "Error: no hay fragmentos guardados para reconstruir el catálogo."
                return

            resultado = reconstruir_fragmentos(fragmentos)
            self.pasos_sala.append(
                f"1. Carga: se leyeron {len(fragmentos)} fragmentos desde data/partida.json."
            )
            self.pasos_sala.extend(resultado["pasos"])
            self.arbol_catalogo = resultado["arbol"]
            self.ubicaciones_catalogo = resultado["ubicaciones"]
            self.mensaje = resultado["mensaje"]
        except Exception:
            self.arbol_catalogo = None
            self.ubicaciones_catalogo = {}
            if len(self.pasos_sala) == 0:
                self.pasos_sala.append("La reconstrucción se detuvo por un error y la partida sigue abierta.")
            self.mensaje = "Error: no se pudo reconstruir el catálogo."

    def buscar_catalogo(self):
        """Busca un código en el árbol y muestra cuántas comparaciones hizo.

        Parámetros:
            Ninguno. El código sale del campo de texto de la Sala Central.
        Retorna:
            None. El resultado queda en el mensaje de la pantalla.
        """
        if self.arbol_catalogo is None:
            self.mensaje = "Error: no hay un catálogo reconstruido para buscar."
            return

        codigo = self.leer_entero(0, "Código", minimo=1)
        if codigo is None:
            return

        try:
            fragmento, comparaciones = self.arbol_catalogo.buscar(codigo)
            if fragmento is None:
                self.mensaje = (
                    f"Error: el código {codigo} no está en el catálogo. "
                    f"El árbol hizo {comparaciones} comparaciones."
                )
                return

            posicion = self.ubicaciones_catalogo.get(codigo)
            if isinstance(posicion, tuple):
                estante, nivel = estructuras.desempaquetar_posicion(posicion)
                lugar = f" en el estante {estante}, nivel {nivel}"
            else:
                lugar = ""

            titulo = fragmento["titulo"]
            if len(titulo) > 32:
                titulo = titulo[:31] + "..."
            self.mensaje = (
                f"Código {codigo} encontrado{lugar}: {titulo}. "
                f"Comparaciones del árbol: {comparaciones}."
            )
        except (TypeError, ValueError, KeyError):
            self.mensaje = "Error: no se pudo buscar ese código en el catálogo."

    def dibujar_sala_central(self):
        """Muestra los pasos de reconstrucción y la búsqueda por código."""
        self.dibujar_encabezado(
            "Sala Central",
            "Los fragmentos guardados se ordenan en un árbol binario de búsqueda.",
        )
        if len(self.pasos_sala) == 0:
            dibujar_texto(
                self.pantalla,
                self.fuentes["pequena"],
                "Todavía no hay una reconstrucción.",
                (40, 105),
                GRIS,
            )
        else:
            for indice, linea in enumerate(self.pasos_sala[:14]):
                dibujar_texto(self.pantalla, self.fuentes["pequena"], linea, (40, 105 + indice * 22))
            if len(self.pasos_sala) > 14:
                dibujar_texto(self.pantalla, self.fuentes["pequena"], "...", (40, 105 + 14 * 22), GRIS)

        self.dibujar_mensaje((40, 452))
        self.dibujar_campos()
        self.dibujar_botones()

    def accion_sala_central(self, accion):
        """Reconstruye el catálogo, busca un código o abre la tabla de puntajes.

        Parámetros:
            accion: nombre del botón presionado.
        Retorna:
            None.
        """
        if accion == "reconstruir":
            self.reconstruir_sala_central(guardar_antes=True)
        elif accion == "buscar":
            self.buscar_catalogo()
        elif accion == "terminar":
            self.abrir_fin()

    # ------------------------------------------------------------------
    # Ciclo principal
    # ------------------------------------------------------------------
    def dibujar(self):
        """Dibuja la pantalla que corresponde al estado actual."""
        if self.estado == "menu":
            self.dibujar_menu()
        elif self.estado == "registro":
            self.dibujar_registro()
        elif self.estado == "bienvenida":
            self.dibujar_bienvenida()
        elif self.estado == "estanterias":
            self.dibujar_estanterias()
        elif self.estado == "mapas":
            self.dibujar_mapas()
        elif self.estado == "fichas":
            self.dibujar_fichas()
        elif self.estado == "sellos":
            self.dibujar_sellos()
        elif self.estado == "pregunta":
            self.dibujar_pregunta()
        elif self.estado == "respuesta":
            self.dibujar_respuesta()
        elif self.estado == "sala_central":
            self.dibujar_sala_central()
        elif self.estado == "fin":
            self.dibujar_fin()

    def ejecutar_accion(self, accion):
        """Envía la acción del botón a la pantalla activa sin dejar que un error cierre el juego."""
        if accion == "guardar":
            self.guardar()
            return

        try:
            if self.estado == "estanterias":
                self.accion_estanterias(accion)
            elif self.estado == "mapas":
                self.accion_mapas(accion)
            elif self.estado == "fichas":
                self.accion_fichas(accion)
            elif self.estado == "sellos":
                self.accion_sellos(accion)
            elif self.estado == "pregunta":
                numero = int(accion.replace("opcion_", ""))
                self.responder(numero)
            elif self.estado == "respuesta":
                self.avanzar_sala()
            elif self.estado == "sala_central":
                self.accion_sala_central(accion)
            elif self.estado == "fin":
                self.accion_fin(accion)
        except (TypeError, ValueError) as error:
            # estructuras.py lanza estos errores cuando un dato no es válido.
            self.mensaje = f"Error: {error}"

    def atender_clic(self, posicion):
        """Envía el clic a la pantalla que esté activa."""
        # Un clic sobre un campo de texto le da el foco del teclado.
        for indice, campo in enumerate(self.campos):
            if campo.rectangulo.collidepoint(posicion):
                self.foco = indice
                return

        accion = self.boton_presionado(posicion)
        if accion is not None:
            self.ejecutar_accion(accion)
        elif self.estado == "menu":
            self.clic_menu(posicion)
        elif self.estado == "registro":
            if self.boton_registrar.collidepoint(posicion):
                self.registrar_jugador()
        elif self.estado == "bienvenida":
            self.clic_bienvenida(posicion)

    def atender_tecla(self, evento):
        """Escribe en el campo con foco y atiende TAB, BORRAR y ENTER."""
        if len(self.campos) == 0:
            return

        campo = self.campos[self.foco]
        if evento.key == pygame.K_TAB:
            self.foco = (self.foco + 1) % len(self.campos)
        elif evento.key == pygame.K_BACKSPACE:
            campo.texto = campo.texto[:-1]
        elif evento.key == pygame.K_RETURN:
            if self.estado == "registro":
                self.registrar_jugador()
            elif self.estado == "estanterias":
                self.ejecutar_accion("agregar")
            elif self.estado == "mapas":
                self.ejecutar_accion("mover")
            elif self.estado == "fichas":
                self.ejecutar_accion("consultar")
            elif self.estado == "sala_central":
                self.ejecutar_accion("buscar")
        elif evento.unicode != "" and evento.unicode.isprintable() and len(campo.texto) < 30:
            campo.texto += evento.unicode

    def ejecutar(self):
        """Ejecuta el ciclo de eventos hasta que el jugador cierre el juego."""
        while self.ejecutando:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    self.ejecutando = False
                elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                    self.atender_clic(evento.pos)
                elif evento.type == pygame.KEYDOWN:
                    self.atender_tecla(evento)

            self.dibujar()
            pygame.display.flip()
            self.reloj.tick(FPS)

        pygame.quit()


def ejecutar_juego():
    """Crea el juego y lo ejecuta."""
    Juego().ejecutar()
    sys.exit(0)
