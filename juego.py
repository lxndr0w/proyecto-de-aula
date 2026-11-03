"""Interfaz gráfica y navegación de El Archivo Perdido.

Este módulo dibuja las pantallas con Pygame y llama a las funciones de
estructuras.py. No repite la lógica de las estructuras de datos.
"""

from dataclasses import dataclass
import sys

import pygame

import estructuras


# Configuración de la ventana
ANCHO = 1000
ALTO = 680
FPS = 60

# Orden en que se recorren las cinco etapas de recolección.
SALAS = ["vestibulo", "estanterias", "mapas", "fichas", "sellos"]

# Tamaño de la cuadrícula de la Sala de Mapas.
TAMANO_MAPA = 6

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


@dataclass
class Jugador:
    """Representa el estado del jugador.

    Atributos:
        nombre: nombre escrito por el jugador.
        vida: cantidad de intentos disponibles.
        puntaje: puntos acumulados.
        nivel: nivel actual de la partida.
        precision: porcentaje de respuestas correctas.
        activo: indica si la partida continúa activa.
    """

    nombre: str
    vida: int
    puntaje: int
    nivel: int
    precision: float
    activo: bool


@dataclass
class CampoTexto:
    """Caja de texto sencilla, porque Pygame no trae una.

    Atributos:
        etiqueta: texto que se muestra encima de la caja.
        rectangulo: límites de la caja en pantalla.
        texto: contenido escrito por el jugador.
    """

    etiqueta: str
    rectangulo: pygame.Rect
    texto: str = ""


def convertir_entero(valor: str, minimo: int = 0):
    """Convierte un texto a entero y comprueba su valor mínimo.

    Parámetros:
        valor: texto que se desea convertir.
        minimo: valor entero mínimo permitido.
    Retorna:
        Una tupla con el resultado de la validación, el entero o None y un mensaje.
    """
    try:
        numero = int(valor.strip())
    except ValueError:
        return False, None, "Escribe un número entero válido."

    if numero < minimo:
        return False, None, f"El valor debe ser como mínimo {minimo}."

    return True, numero, ""


def convertir_decimal(valor: str, minimo: float = 0.0, maximo: float = 100.0):
    """Convierte un texto a decimal y comprueba que esté dentro del rango.

    Parámetros:
        valor: texto que se desea convertir.
        minimo: límite inferior permitido.
        maximo: límite superior permitido.
    Retorna:
        Una tupla con el resultado de la validación, el decimal o None y un mensaje.
    """
    try:
        # Se acepta tanto coma como punto decimal.
        numero = float(valor.strip().replace(",", "."))
    except ValueError:
        return False, None, "Escribe un número decimal válido (ejemplo: 95.5)."

    if not minimo <= numero <= maximo:
        return False, None, f"El valor debe estar entre {minimo:g} y {maximo:g}."

    return True, numero, ""


def crear_jugador(nombre: str, vida_texto: str, precision_texto: str):
    """Valida los datos del formulario y crea el jugador.

    Parámetros:
        nombre: nombre ingresado por el usuario.
        vida_texto: cantidad de vidas ingresada como texto.
        precision_texto: precisión ingresada como texto.
    Retorna:
        Una tupla con el jugador creado o None y el mensaje de validación.
    """
    nombre_limpio = nombre.strip()
    if not nombre_limpio:
        return None, "El nombre no puede quedar vacío."

    vida_valida, vida, mensaje = convertir_entero(vida_texto, minimo=1)
    if not vida_valida:
        return None, f"Vida: {mensaje}"

    precision_valida, precision, mensaje = convertir_decimal(precision_texto)
    if not precision_valida:
        return None, f"Precisión: {mensaje}"

    jugador = Jugador(
        nombre=nombre_limpio,
        vida=vida,
        puntaje=0,
        nivel=1,
        precision=precision,
        activo=True,
    )
    return jugador, ""


def dibujar_texto(pantalla, fuente, texto, posicion, color=BLANCO) -> None:
    """Dibuja una línea de texto en la ventana.

    Parámetros:
        pantalla: superficie sobre la que se dibuja.
        fuente: fuente tipográfica que se utilizará.
        texto: contenido que se mostrará.
        posicion: coordenadas x e y del texto.
        color: color RGB del texto.
    Retorna:
        None.
    """
    superficie = fuente.render(texto, True, color)
    pantalla.blit(superficie, posicion)


def dibujar_boton(pantalla, fuente, texto, rectangulo, principal=True) -> None:
    """Dibuja un botón rectangular con su texto centrado.

    Parámetros:
        pantalla: superficie sobre la que se dibuja.
        fuente: fuente tipográfica del texto.
        texto: etiqueta del botón.
        rectangulo: límites del botón en pantalla.
        principal: True para el color naranja, False para el color de panel.
    Retorna:
        None.
    """
    color_fondo = NARANJA if principal else PANEL_CLARO
    color_texto = FONDO if principal else BLANCO
    pygame.draw.rect(pantalla, color_fondo, rectangulo, border_radius=10)
    etiqueta = fuente.render(texto, True, color_texto)
    pantalla.blit(etiqueta, etiqueta.get_rect(center=rectangulo.center))


def dibujar_campo(pantalla, fuente, campo, enfocado) -> None:
    """Dibuja la etiqueta y la caja de un campo de texto.

    Parámetros:
        pantalla: superficie sobre la que se dibuja.
        fuente: fuente tipográfica que se utilizará.
        campo: CampoTexto que se desea mostrar.
        enfocado: indica si el campo recibe el teclado.
    Retorna:
        None.
    """
    rectangulo = campo.rectangulo
    dibujar_texto(pantalla, fuente, campo.etiqueta, (rectangulo.x, rectangulo.y - 26), GRIS)
    borde = NARANJA if enfocado else (83, 101, 132)
    pygame.draw.rect(pantalla, PANEL_CLARO, rectangulo, border_radius=10)
    pygame.draw.rect(pantalla, borde, rectangulo, width=2, border_radius=10)
    texto = fuente.render(campo.texto, True, BLANCO)
    pantalla.blit(texto, (rectangulo.x + 12, rectangulo.y + 9))


class Juego:
    """Guarda el estado de la partida y controla las pantallas."""

    def __init__(self) -> None:
        """Crea la ventana, las fuentes y el estado inicial.

        Parámetros:
            Ninguno.
        Retorna:
            None.
        """
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

        # Botones de la sala actual: {accion: (texto, rectangulo)}.
        self.botones = {}
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

        self.botones_menu = {
            "iniciar": pygame.Rect(370, 300, 260, 50),
            "cargar": pygame.Rect(370, 370, 260, 50),
            "salir": pygame.Rect(370, 440, 260, 50),
        }

    # ------------------------------------------------------------------
    # Menú principal
    # ------------------------------------------------------------------
    def dibujar_menu(self) -> None:
        """Muestra el título y las opciones de inicio.

        Parámetros:
            Ninguno.
        Retorna:
            None.
        """
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

        dibujar_boton(self.pantalla, self.fuentes["normal"], "Iniciar partida", self.botones_menu["iniciar"])
        dibujar_boton(self.pantalla, self.fuentes["normal"], "Cargar partida", self.botones_menu["cargar"], False)
        dibujar_boton(self.pantalla, self.fuentes["normal"], "Salir", self.botones_menu["salir"], False)

        if self.mensaje:
            dibujar_texto(self.pantalla, self.fuentes["pequena"], self.mensaje, (370, 510), ROJO)

    def clic_menu(self, posicion) -> None:
        """Atiende los clics del menú principal.

        Parámetros:
            posicion: coordenadas x e y del clic.
        Retorna:
            None.
        """
        if self.botones_menu["iniciar"].collidepoint(posicion):
            self.abrir_registro()
        elif self.botones_menu["cargar"].collidepoint(posicion):
            # Pendiente: conectar con persistencia.py.
            pass
        elif self.botones_menu["salir"].collidepoint(posicion):
            self.ejecutando = False

    # ------------------------------------------------------------------
    # Ayudas comunes
    # ------------------------------------------------------------------
    def dibujar_encabezado(self, titulo, descripcion) -> None:
        """Limpia la pantalla y dibuja el título de la sala y el estado del jugador.

        Parámetros:
            titulo: nombre de la sala.
            descripcion: frase corta que explica el reto.
        Retorna:
            None.
        """
        self.pantalla.fill(FONDO)
        pygame.draw.rect(self.pantalla, NARANJA, (0, 0, ANCHO, 9))
        dibujar_texto(self.pantalla, self.fuentes["subtitulo"], titulo, (40, 25))
        dibujar_texto(self.pantalla, self.fuentes["pequena"], descripcion, (40, 62), GRIS)

        if self.jugador is not None:
            estado_jugador = (
                f"{self.jugador.nombre}  |  Vida: {self.jugador.vida}  |  "
                f"Puntaje: {self.jugador.puntaje}  |  Nivel: {self.jugador.nivel}  |  "
                f"Precisión: {self.jugador.precision:.1f}%"
            )
            dibujar_texto(self.pantalla, self.fuentes["pequena"], estado_jugador, (40, ALTO - 30), AZUL)

    def dibujar_campos(self) -> None:
        """Dibuja todos los campos de texto de la pantalla actual.

        Parámetros:
            Ninguno.
        Retorna:
            None.
        """
        for indice, campo in enumerate(self.campos):
            dibujar_campo(self.pantalla, self.fuentes["normal"], campo, indice == self.foco)

    def dibujar_botones(self) -> None:
        """Dibuja los botones de la sala actual.

        Parámetros:
            Ninguno.
        Retorna:
            None.
        """
        for accion, (texto, rectangulo) in self.botones.items():
            principal = accion == "terminar"
            dibujar_boton(self.pantalla, self.fuentes["normal"], texto, rectangulo, principal)

    def boton_presionado(self, posicion):
        """Indica qué botón de la sala se presionó.

        Parámetros:
            posicion: coordenadas x e y del clic.
        Retorna:
            El nombre de la acción del botón o None si no se tocó ninguno.
        """
        for accion, (_, rectangulo) in self.botones.items():
            if rectangulo.collidepoint(posicion):
                return accion
        return None

    def leer_entero(self, indice_campo, nombre, minimo=0):
        """Lee un número entero de un campo y guarda el error si no es válido.

        Parámetros:
            indice_campo: posición del campo en self.campos.
            nombre: nombre del dato para el mensaje de error.
            minimo: valor mínimo permitido.
        Retorna:
            El entero leído o None si el texto no es válido.
        """
        valido, numero, mensaje = convertir_entero(self.campos[indice_campo].texto, minimo)
        if not valido:
            self.mensaje = f"Error: {nombre}: {mensaje}"
            return None
        return numero

    def dibujar_inventario(self, x, y, maximo=8) -> None:
        """Muestra los fragmentos del inventario.

        Parámetros:
            x: coordenada horizontal del listado.
            y: coordenada vertical del listado.
            maximo: cantidad máxima de fragmentos que se muestran.
        Retorna:
            None.
        """
        titulo = f"Inventario ({len(self.inventario)} fragmentos)"
        dibujar_texto(self.pantalla, self.fuentes["normal"], titulo, (x, y), NARANJA)

        if not self.inventario:
            dibujar_texto(self.pantalla, self.fuentes["pequena"], "Todavía no hay fragmentos.", (x, y + 32), GRIS)
            return

        for indice, fragmento in enumerate(self.inventario[:maximo]):
            linea = (
                f"Código {fragmento['codigo']}  |  {fragmento['titulo']}  |  "
                f"{fragmento['sala']}  |  valor {fragmento['valor']}"
            )
            dibujar_texto(self.pantalla, self.fuentes["pequena"], linea, (x, y + 32 + indice * 26))

        if len(self.inventario) > maximo:
            restantes = len(self.inventario) - maximo
            dibujar_texto(
                self.pantalla, self.fuentes["pequena"], f"... y {restantes} más",
                (x, y + 32 + maximo * 26), GRIS,
            )

    def terminar_sala(self) -> None:
        """Muestra la pregunta conceptual de la sala que se acaba de superar.

        Parámetros:
            Ninguno.
        Retorna:
            None.
        """
        self.sala_pregunta = self.estado
        self.estado = "pregunta"
        self.mensaje = ""
        self.campos = []
        _, opciones, _ = PREGUNTAS[self.sala_pregunta]
        self.botones = {
            f"opcion_{indice}": (f"{indice + 1}. {opcion}", pygame.Rect(40, 230 + indice * 70, 920, 52))
            for indice, opcion in enumerate(opciones)
        }

    def responder(self, indice) -> None:
        """Revisa la respuesta, actualiza el puntaje y entrega el fragmento de la sala.

        Parámetros:
            indice: posición de la opción elegida.
        Retorna:
            None.
        """
        _, _, correcta = PREGUNTAS[self.sala_pregunta]
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
        self.botones = {"continuar": ("Continuar", pygame.Rect(760, 595, 200, 42))}

    def avanzar_sala(self) -> None:
        """Abre la sala que sigue a la última pregunta o la pantalla final.

        Parámetros:
            Ninguno.
        Retorna:
            None.
        """
        aperturas = {
            "estanterias": self.abrir_estanterias,
            "mapas": self.abrir_mapas,
            "fichas": self.abrir_fichas,
            "sellos": self.abrir_sellos,
        }
        indice = SALAS.index(self.sala_pregunta)

        if not self.jugador.activo or indice == len(SALAS) - 1:
            self.abrir_fin()
        else:
            aperturas[SALAS[indice + 1]]()

    def dibujar_pregunta(self) -> None:
        """Muestra la pregunta conceptual y sus opciones.

        Parámetros:
            Ninguno.
        Retorna:
            None.
        """
        pregunta, _, _ = PREGUNTAS[self.sala_pregunta]
        self.dibujar_encabezado("Pregunta de la sala", "Elige la opción correcta para ganar puntos.")
        dibujar_texto(self.pantalla, self.fuentes["subtitulo"], pregunta, (40, 140))
        for accion, (texto, rectangulo) in self.botones.items():
            dibujar_boton(self.pantalla, self.fuentes["normal"], texto, rectangulo, False)

    def dibujar_respuesta(self) -> None:
        """Informa si la respuesta fue correcta y muestra el avance.

        Parámetros:
            Ninguno.
        Retorna:
            None.
        """
        self.dibujar_encabezado("Resultado", "Así va tu partida.")
        if self.respuesta_correcta:
            dibujar_texto(self.pantalla, self.fuentes["titulo"], "¡Respuesta correcta!", (40, 110), VERDE)
            detalle = f"Ganaste {PUNTOS_POR_ACIERTO} puntos."
        else:
            dibujar_texto(self.pantalla, self.fuentes["titulo"], "Respuesta incorrecta", (40, 110), ROJO)
            _, opciones, correcta = PREGUNTAS[self.sala_pregunta]
            detalle = f"Perdiste una vida. La correcta era: {opciones[correcta]}"
        dibujar_texto(self.pantalla, self.fuentes["normal"], detalle, (40, 170))

        codigo, titulo, _ = PREMIOS[self.sala_pregunta]
        dibujar_texto(self.pantalla, self.fuentes["normal"], f"Fragmento obtenido: {codigo} - {titulo}", (40, 205), NARANJA)

        salas_superadas = SALAS.index(self.sala_pregunta) + 1
        dibujar_texto(
            self.pantalla, self.fuentes["normal"],
            f"Avance: {salas_superadas} de {len(SALAS)} etapas  |  Intentos fallidos: {self.intentos}",
            (40, 240), AZUL,
        )
        self.dibujar_inventario(40, 290)
        self.dibujar_botones()

    # ------------------------------------------------------------------
    # Pantalla final de la recolección
    # ------------------------------------------------------------------
    def abrir_fin(self) -> None:
        """Prepara la pantalla final de la semana 2.

        Parámetros:
            Ninguno.
        Retorna:
            None.
        """
        self.estado = "fin"
        self.mensaje = ""
        self.botones = {
            "guardar_puntaje": ("Guardar puntaje", pygame.Rect(530, 595, 210, 42)),
            "salir": ("Salir", pygame.Rect(760, 595, 200, 42)),
        }

    def dibujar_fin(self) -> None:
        """Muestra el resumen de la partida.

        Parámetros:
            Ninguno.
        Retorna:
            None.
        """
        self.dibujar_encabezado("Fin de la recolección", "La Sala Central se habilita en la semana 3.")
        if self.jugador.activo:
            dibujar_texto(self.pantalla, self.fuentes["titulo"], "¡Recolectaste los fragmentos!", (40, 110), VERDE)
        else:
            dibujar_texto(self.pantalla, self.fuentes["titulo"], "Te quedaste sin vidas", (40, 110), ROJO)

        resumen = (
            f"Puntaje: {self.jugador.puntaje}  |  Aciertos: {self.aciertos} de {self.respondidas}  |  "
            f"Intentos fallidos: {self.intentos}"
        )
        dibujar_texto(self.pantalla, self.fuentes["normal"], resumen, (40, 175))
        self.dibujar_inventario(40, 225, maximo=10)
        self.dibujar_mensaje((40, 560))
        self.dibujar_botones()

    def accion_fin(self, accion) -> None:
        """Atiende los botones de la pantalla final.

        Parámetros:
            accion: nombre del botón presionado.
        Retorna:
            None.
        """
        if accion == "guardar_puntaje":
            # Pendiente: conectar con persistencia.py.
            pass
        elif accion == "salir":
            self.ejecutando = False

    def dibujar_mensaje(self, posicion) -> None:
        """Muestra el último mensaje; en rojo si es un error y en verde si no.

        Parámetros:
            posicion: coordenadas x e y del mensaje.
        Retorna:
            None.
        """
        if self.mensaje:
            color = ROJO if self.mensaje.startswith("Error") else VERDE
            dibujar_texto(self.pantalla, self.fuentes["pequena"], self.mensaje, posicion, color)

    # ------------------------------------------------------------------
    # Vestíbulo: registro del jugador
    # ------------------------------------------------------------------
    def abrir_registro(self) -> None:
        """Prepara los campos del formulario de registro.

        Parámetros:
            Ninguno.
        Retorna:
            None.
        """
        self.estado = "registro"
        self.mensaje = ""
        self.foco = 0
        self.campos = [
            CampoTexto("Nombre del jugador", pygame.Rect(100, 250, 800, 42)),
            CampoTexto("Vidas iniciales (entero)", pygame.Rect(100, 340, 380, 42), "3"),
            CampoTexto("Precisión inicial (0 a 100)", pygame.Rect(520, 340, 380, 42), "100"),
        ]
        self.boton_registrar = pygame.Rect(700, 470, 200, 45)

    def dibujar_registro(self) -> None:
        """Muestra el formulario de registro del vestíbulo.

        Parámetros:
            Ninguno.
        Retorna:
            None.
        """
        self.dibujar_encabezado("Vestíbulo", "Registra los datos de tu explorador.")
        dibujar_texto(self.pantalla, self.fuentes["titulo"], "EL ARCHIVO PERDIDO", (100, 120))
        self.dibujar_campos()
        dibujar_texto(
            self.pantalla,
            self.fuentes["pequena"],
            "Usa TAB para cambiar de campo y ENTER para continuar.",
            (100, 410),
            GRIS,
        )
        self.dibujar_mensaje((100, 440))
        dibujar_boton(self.pantalla, self.fuentes["normal"], "Comenzar", self.boton_registrar)

    def registrar_jugador(self) -> None:
        """Valida el formulario y, si es correcto, crea el jugador.

        Parámetros:
            Ninguno.
        Retorna:
            None.
        """
        jugador, mensaje = crear_jugador(
            self.campos[0].texto, self.campos[1].texto, self.campos[2].texto
        )
        if jugador is None:
            # La partida no se cierra: se muestra el error y se puede corregir.
            self.mensaje = f"Error: {mensaje}"
            return

        self.jugador = jugador
        self.mensaje = ""
        self.campos = []
        self.estado = "bienvenida"

    def dibujar_bienvenida(self) -> None:
        """Muestra el resumen del jugador después de validar el registro.

        Parámetros:
            Ninguno.
        Retorna:
            None.
        """
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

        self.boton_continuar = pygame.Rect(700, 560, 200, 45)
        dibujar_boton(self.pantalla, self.fuentes["normal"], "Continuar", self.boton_continuar)

    def clic_bienvenida(self, posicion) -> None:
        """Atiende el botón para continuar después del registro.

        Parámetros:
            posicion: coordenadas x e y del clic.
        Retorna:
            None.
        """
        if self.boton_continuar.collidepoint(posicion):
            self.estado = "vestibulo"
            self.terminar_sala()

    # ------------------------------------------------------------------
    # Sala de Estanterías: listas
    # ------------------------------------------------------------------
    def abrir_estanterias(self) -> None:
        """Prepara los campos y botones de la Sala de Estanterías.

        Parámetros:
            Ninguno.
        Retorna:
            None.
        """
        self.estado = "estanterias"
        self.mensaje = ""
        self.foco = 0
        self.reto_superado = False
        self.campos = [
            CampoTexto("Código", pygame.Rect(40, 125, 200, 42)),
            CampoTexto("Título", pygame.Rect(270, 125, 420, 42)),
            CampoTexto("Valor", pygame.Rect(720, 125, 240, 42)),
        ]
        self.botones = {
            "agregar": ("Agregar", pygame.Rect(40, 185, 170, 42)),
            "buscar": ("Buscar", pygame.Rect(225, 185, 170, 42)),
            "eliminar": ("Eliminar", pygame.Rect(410, 185, 170, 42)),
            "ordenar": ("Ordenar", pygame.Rect(595, 185, 170, 42)),
            "terminar": ("Terminar sala", pygame.Rect(760, 595, 200, 42)),
        }

    def dibujar_estanterias(self) -> None:
        """Muestra el inventario y las operaciones de la lista.

        Parámetros:
            Ninguno.
        Retorna:
            None.
        """
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
        dibujar_texto(
            self.pantalla, self.fuentes["pequena"],
            f"Códigos de esta sala (comprensión de listas): {codigos}", (40, 560), AZUL,
        )

    def accion_estanterias(self, accion) -> None:
        """Ejecuta la operación de lista que eligió el jugador.

        Parámetros:
            accion: nombre del botón presionado.
        Retorna:
            None.
        """
        if accion == "ordenar":
            self.inventario = estructuras.ordenar_fragmentos(self.inventario)
            self.mensaje = "Inventario ordenado de menor a mayor código."
            return

        if accion == "terminar":
            if not self.inventario:
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
    def abrir_mapas(self) -> None:
        """Prepara la cuadrícula y el recorrido de la Sala de Mapas.

        Parámetros:
            Ninguno.
        Retorna:
            None.
        """
        self.estado = "mapas"
        self.mensaje = ""
        self.foco = 0
        self.reto_superado = False
        self.recorrido = [estructuras.crear_posicion(0, 0)]
        self.campos = [
            CampoTexto("Fila", pygame.Rect(40, 125, 140, 42)),
            CampoTexto("Columna", pygame.Rect(200, 125, 140, 42)),
        ]
        self.botones = {
            "mover": ("Mover", pygame.Rect(360, 125, 140, 42)),
            "terminar": ("Terminar sala", pygame.Rect(760, 595, 200, 42)),
        }

    def dibujar_mapas(self) -> None:
        """Muestra la cuadrícula, la posición actual y el recorrido.

        Parámetros:
            Ninguno.
        Retorna:
            None.
        """
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
        origen_x, origen_y = 560, 130
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

    def accion_mapas(self, accion) -> None:
        """Mueve al jugador a la posición escrita o termina la sala.

        Parámetros:
            accion: nombre del botón presionado.
        Retorna:
            None.
        """
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

        posicion = estructuras.crear_posicion(fila, columna)
        self.recorrido.append(posicion)
        fila, columna = estructuras.desempaquetar_posicion(posicion)

        if posicion == self.objetivo:
            self.reto_superado = True
            self.mensaje = f"¡Encontraste el fragmento en {posicion}! Ya puedes terminar la sala."
        else:
            objetivo_fila, objetivo_columna = estructuras.desempaquetar_posicion(self.objetivo)
            vertical = "más abajo" if objetivo_fila > fila else "más arriba" if objetivo_fila < fila else "en esta fila"
            horizontal = "más a la derecha" if objetivo_columna > columna else "más a la izquierda" if objetivo_columna < columna else "en esta columna"
            self.mensaje = f"Aquí no está. El fragmento está {vertical} y {horizontal}."

    # ------------------------------------------------------------------
    # Sala de Fichas: diccionarios
    # ------------------------------------------------------------------
    def abrir_fichas(self) -> None:
        """Prepara la consulta de fichas por código y por clave.

        Parámetros:
            Ninguno.
        Retorna:
            None.
        """
        self.estado = "fichas"
        self.mensaje = ""
        self.foco = 0
        self.reto_superado = False
        self.ficha_actual = None
        self.campos = [
            CampoTexto("Código del fragmento", pygame.Rect(40, 125, 200, 42)),
            CampoTexto("Clave (codigo, titulo, sala, valor...)", pygame.Rect(270, 125, 300, 42)),
        ]
        self.botones = {
            "consultar": ("Consultar ficha", pygame.Rect(590, 125, 180, 42)),
            "clave": ("Consultar clave", pygame.Rect(785, 125, 175, 42)),
            "terminar": ("Terminar sala", pygame.Rect(760, 595, 200, 42)),
        }

    def dibujar_fichas(self) -> None:
        """Muestra la ficha consultada y el inventario disponible.

        Parámetros:
            Ninguno.
        Retorna:
            None.
        """
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

        self.dibujar_inventario(40, 435, maximo=5)

    def accion_fichas(self, accion) -> None:
        """Consulta una ficha completa o una clave de la ficha.

        Parámetros:
            accion: nombre del botón presionado.
        Retorna:
            None.
        """
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
                self.mensaje = (
                    f"Error: la clave '{clave}' no existe en la ficha. "
                    "Las claves son: codigo, titulo, sala y valor."
                )
            else:
                self.mensaje = f"{clave} = {valor}"

    # ------------------------------------------------------------------
    # Sala de Sellos: conjuntos
    # ------------------------------------------------------------------
    def abrir_sellos(self) -> None:
        """Prepara las pistas y las operaciones de conjuntos.

        Parámetros:
            Ninguno.
        Retorna:
            None.
        """
        self.estado = "sellos"
        self.mensaje = ""
        self.campos = []
        self.reto_superado = False
        self.resultados_sellos = []
        self.botones = {
            "duplicados": ("Quitar repetidos", pygame.Rect(40, 215, 200, 42)),
            "union": ("Unión", pygame.Rect(255, 215, 150, 42)),
            "interseccion": ("Intersección", pygame.Rect(420, 215, 150, 42)),
            "diferencia": ("Diferencia A - B", pygame.Rect(585, 215, 190, 42)),
            "terminar": ("Terminar sala", pygame.Rect(760, 595, 200, 42)),
        }

    def dibujar_sellos(self) -> None:
        """Muestra las dos pistas y los resultados de las operaciones.

        Parámetros:
            Ninguno.
        Retorna:
            None.
        """
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

        dibujar_texto(
            self.pantalla, self.fuentes["pequena"],
            "Nota: un conjunto no guarda orden; aquí se muestra ordenado solo para leerlo mejor.",
            (40, 565), GRIS,
        )

    def accion_sellos(self, accion) -> None:
        """Ejecuta la operación de conjuntos elegida.

        Parámetros:
            accion: nombre del botón presionado.
        Retorna:
            None.
        """
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
    # Ciclo principal
    # ------------------------------------------------------------------
    def dibujar(self) -> None:
        """Dibuja la pantalla que corresponde al estado actual.

        Parámetros:
            Ninguno.
        Retorna:
            None.
        """
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
        elif self.estado == "fin":
            self.dibujar_fin()

    def ejecutar_accion(self, accion) -> None:
        """Envía la acción del botón a la sala activa sin dejar que un error cierre el juego.

        Parámetros:
            accion: nombre del botón presionado.
        Retorna:
            None.
        """
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
                self.responder(int(accion.split("_")[1]))
            elif self.estado == "respuesta":
                self.avanzar_sala()
            elif self.estado == "fin":
                self.accion_fin(accion)
        except (TypeError, ValueError) as error:
            # estructuras.py lanza estos errores cuando un dato no es válido.
            self.mensaje = f"Error: {error}"

    def atender_clic(self, posicion) -> None:
        """Envía el clic a la pantalla que esté activa.

        Parámetros:
            posicion: coordenadas x e y del clic.
        Retorna:
            None.
        """
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

    def atender_tecla(self, evento) -> None:
        """Escribe en el campo con foco y atiende TAB, BORRAR y ENTER.

        Parámetros:
            evento: evento KEYDOWN de Pygame.
        Retorna:
            None.
        """
        if not self.campos:
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
        elif evento.unicode and evento.unicode.isprintable() and len(campo.texto) < 30:
            campo.texto += evento.unicode

    def ejecutar(self) -> None:
        """Ejecuta el ciclo de eventos hasta que el jugador cierre el juego.

        Parámetros:
            Ninguno.
        Retorna:
            None.
        """
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


def ejecutar_juego() -> None:
    """Crea el juego y lo ejecuta.

    Parámetros:
        Ninguno.
    Retorna:
        None.
    """
    Juego().ejecutar()
    sys.exit(0)
