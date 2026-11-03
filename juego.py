"""Interfaz gráfica y navegación de El Archivo Perdido.

Este módulo dibuja las pantallas con Pygame y llama a las funciones de
estructuras.py. No repite la lógica de las estructuras de datos.
"""

from dataclasses import dataclass
import sys

import pygame


# Configuración de la ventana
ANCHO = 1000
ALTO = 680
FPS = 60

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
            # Pendiente: pasar a la Sala de Estanterías.
            pass

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

        if self.estado == "menu":
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
