"""Interfaz gráfica y navegación de El Archivo Perdido.

Este módulo dibuja las pantallas con Pygame y llama a las funciones de
estructuras.py. No repite la lógica de las estructuras de datos.
"""

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
            # Pendiente: abrir el registro del vestíbulo.
            pass
        elif self.botones_menu["cargar"].collidepoint(posicion):
            # Pendiente: conectar con persistencia.py.
            pass
        elif self.botones_menu["salir"].collidepoint(posicion):
            self.ejecutando = False

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

    def atender_clic(self, posicion) -> None:
        """Envía el clic a la pantalla que esté activa.

        Parámetros:
            posicion: coordenadas x e y del clic.
        Retorna:
            None.
        """
        if self.estado == "menu":
            self.clic_menu(posicion)

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
