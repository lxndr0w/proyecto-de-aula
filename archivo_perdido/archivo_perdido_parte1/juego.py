"""Interfaz inicial y vestíbulo de El Archivo Perdido."""

from dataclasses import dataclass
import sys
from typing import Optional, Tuple

import pygame


# Configuración de la ventana
ANCHO = 900
ALTO = 620
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
    """Representa el estado inicial del jugador.

    Atributos:
        nombre: nombre escrito por el jugador.
        vida: cantidad de intentos disponibles.
        puntaje: puntos acumulados.
        nivel: nivel actual de la partida.
        precision: porcentaje de precisión inicial.
        activo: indica si la partida continúa activa.
    """

    nombre: str
    vida: int
    puntaje: int
    nivel: int
    precision: float
    activo: bool


def convertir_entero(valor: str, minimo: int = 0) -> Tuple[bool, Optional[int], str]:
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


def convertir_decimal(
    valor: str, minimo: float = 0.0, maximo: float = 100.0
) -> Tuple[bool, Optional[float], str]:
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


def crear_jugador(nombre: str, vida_texto: str, precision_texto: str) -> Tuple[Optional[Jugador], str]:
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
        vida=vida,  # int
        puntaje=0,  # int
        nivel=1,  # int
        precision=precision,  # float
        activo=True,  # bool
    )
    return jugador, ""


def dibujar_texto(
    pantalla: pygame.Surface,
    fuente: pygame.font.Font,
    texto: str,
    posicion: Tuple[int, int],
    color: Tuple[int, int, int] = BLANCO,
) -> None:
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


def dibujar_campo(
    pantalla: pygame.Surface,
    fuente: pygame.font.Font,
    etiqueta: str,
    valor: str,
    rectangulo: pygame.Rect,
    enfocado: bool,
) -> None:
    """Dibuja la etiqueta y el campo de entrada.

    Parámetros:
        pantalla: superficie sobre la que se dibuja.
        fuente: fuente tipográfica que se utilizará.
        etiqueta: nombre del dato solicitado.
        valor: contenido actual del campo.
        rectangulo: límites del campo en pantalla.
        enfocado: indica si el campo recibe el teclado.
    Retorna:
        None.
    """
    dibujar_texto(pantalla, fuente, etiqueta, (rectangulo.x, rectangulo.y - 29), GRIS)
    borde = NARANJA if enfocado else (83, 101, 132)
    pygame.draw.rect(pantalla, PANEL_CLARO, rectangulo, border_radius=10)
    pygame.draw.rect(pantalla, borde, rectangulo, width=2, border_radius=10)
    texto = fuente.render(valor, True, BLANCO)
    pantalla.blit(texto, (rectangulo.x + 14, rectangulo.y + 11))


def dibujar_vestibulo(
    pantalla: pygame.Surface,
    fuentes: dict,
    valores: list,
    campos: list,
    foco: int,
    mensaje: str,
) -> None:
    """Muestra la pantalla de registro del vestíbulo.

    Parámetros:
        pantalla: superficie principal de Pygame.
        fuentes: fuentes tipográficas disponibles.
        valores: textos escritos en los tres campos.
        campos: rectángulos de los campos.
        foco: índice del campo que recibe el teclado.
        mensaje: mensaje de validación que se muestra al usuario.
    Retorna:
        None.
    """
    pantalla.fill(FONDO)
    pygame.draw.rect(pantalla, NARANJA, (0, 0, ANCHO, 9))

    dibujar_texto(pantalla, fuentes["pequena"], "PROYECTO DE ESTRUCTURAS DE DATOS", (65, 43), AZUL)
    dibujar_texto(pantalla, fuentes["titulo"], "EL ARCHIVO PERDIDO", (62, 76))
    dibujar_texto(
        pantalla,
        fuentes["normal"],
        "El catálogo de la biblioteca ha desaparecido. Ayúdanos a reconstruirlo.",
        (65, 132),
        GRIS,
    )

    panel = pygame.Rect(65, 205, 770, 340)
    pygame.draw.rect(pantalla, PANEL, panel, border_radius=18)
    dibujar_texto(pantalla, fuentes["subtitulo"], "Vestíbulo", (100, 235))
    dibujar_texto(pantalla, fuentes["normal"], "Primero, registra los datos de tu explorador.", (100, 275), GRIS)

    etiquetas = ["Nombre del jugador", "Vidas iniciales (entero)", "Precisión inicial (0 a 100)"]
    for indice, rectangulo in enumerate(campos):
        dibujar_campo(
            pantalla,
            fuentes["normal"],
            etiquetas[indice],
            valores[indice],
            rectangulo,
            enfocado=(indice == foco),
        )

    if mensaje:
        dibujar_texto(pantalla, fuentes["pequena"], mensaje, (100, 490), ROJO)
    else:
        dibujar_texto(
            pantalla,
            fuentes["pequena"],
            "Usa TAB para cambiar de campo y ENTER para continuar.",
            (100, 490),
            GRIS,
        )

    boton = pygame.Rect(650, 575, 185, 38)
    pygame.draw.rect(pantalla, NARANJA, boton, border_radius=10)
    etiqueta_boton = fuentes["pequena"].render("COMENZAR  [ENTER]", True, FONDO)
    pantalla.blit(etiqueta_boton, etiqueta_boton.get_rect(center=boton.center))


def dibujar_bienvenida(pantalla: pygame.Surface, fuentes: dict, jugador: Jugador) -> None:
    """Muestra el resumen del jugador después de validar el registro.

    Parámetros:
        pantalla: superficie principal de Pygame.
        fuentes: fuentes tipográficas disponibles.
        jugador: objeto con los datos ya validados.
    Retorna:
        None.
    """
    pantalla.fill(FONDO)
    pygame.draw.rect(pantalla, NARANJA, (0, 0, ANCHO, 9))

    dibujar_texto(pantalla, fuentes["pequena"], "EL ARCHIVO PERDIDO", (65, 48), AZUL)
    dibujar_texto(pantalla, fuentes["titulo"], f"¡Bienvenido, {jugador.nombre}!", (65, 92))
    dibujar_texto(pantalla, fuentes["normal"], "Tu explorador quedó registrado correctamente.", (68, 150), GRIS)

    panel = pygame.Rect(65, 220, 770, 230)
    pygame.draw.rect(pantalla, PANEL, panel, border_radius=18)
    dibujar_texto(pantalla, fuentes["subtitulo"], "Estado inicial del jugador", (100, 250))

    datos = [
        f"Nombre (str): {jugador.nombre}",
        f"Vida (int): {jugador.vida}       Puntaje (int): {jugador.puntaje}       Nivel (int): {jugador.nivel}",
        f"Precisión (float): {jugador.precision:.1f}%",
        f"Partida activa (bool): {jugador.activo}",
    ]
    for indice, dato in enumerate(datos):
        dibujar_texto(pantalla, fuentes["normal"], dato, (105, 305 + indice * 38), BLANCO)

    dibujar_texto(pantalla, fuentes["normal"], "¿Por qué hay que validar antes de utilizar el puntaje?", (68, 492), VERDE)
    dibujar_texto(pantalla, fuentes["pequena"], "Piensa en tu respuesta y continúa para terminar el vestíbulo.", (68, 530), GRIS)

    boton_continuar = pygame.Rect(580, 565, 155, 40)
    boton_salir = pygame.Rect(750, 565, 85, 40)
    pygame.draw.rect(pantalla, NARANJA, boton_continuar, border_radius=10)
    pygame.draw.rect(pantalla, PANEL_CLARO, boton_salir, border_radius=10)
    texto_continuar = fuentes["pequena"].render("CONTINUAR", True, FONDO)
    texto_salir = fuentes["pequena"].render("SALIR", True, BLANCO)
    pantalla.blit(texto_continuar, texto_continuar.get_rect(center=boton_continuar.center))
    pantalla.blit(texto_salir, texto_salir.get_rect(center=boton_salir.center))


def dibujar_final(pantalla: pygame.Surface, fuentes: dict) -> None:
    """Muestra la confirmación de que terminó la primera parte."""
    pantalla.fill(FONDO)
    pygame.draw.rect(pantalla, NARANJA, (0, 0, ANCHO, 9))
    dibujar_texto(pantalla, fuentes["titulo"], "Vestíbulo completado", (65, 110))
    dibujar_texto(pantalla, fuentes["normal"], "Esta entrega termina aquí. ¡Gracias por jugar!", (68, 180), GRIS)
    boton_salir = pygame.Rect(350, 285, 200, 48)
    pygame.draw.rect(pantalla, NARANJA, boton_salir, border_radius=10)
    texto_salir = fuentes["normal"].render("SALIR DEL JUEGO", True, FONDO)
    pantalla.blit(texto_salir, texto_salir.get_rect(center=boton_salir.center))


def ejecutar_juego() -> None:
    """Inicializa Pygame y ejecuta el vestíbulo del juego.

    Parámetros:
        Ninguno.
    Retorna:
        None.
    """
    pygame.init()
    pygame.display.set_caption("El Archivo Perdido - Parte 1")
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    reloj = pygame.time.Clock()

    fuentes = {
        "titulo": pygame.font.SysFont("arial", 42, bold=True),
        "subtitulo": pygame.font.SysFont("arial", 27, bold=True),
        "normal": pygame.font.SysFont("arial", 20),
        "pequena": pygame.font.SysFont("arial", 16),
    }

    valores = ["", "3", "95.0"]
    campos = [
        pygame.Rect(100, 345, 700, 42),
        pygame.Rect(100, 430, 330, 42),
        pygame.Rect(470, 430, 330, 42),
    ]
    foco = 0
    mensaje = ""
    jugador: Optional[Jugador] = None
    estado = "registro"

    ejecutando = True
    while ejecutando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando = False

            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    ejecutando = False

                elif estado == "registro":
                    if evento.key == pygame.K_TAB:
                        foco = (foco + 1) % len(valores)
                        mensaje = ""
                    elif evento.key == pygame.K_BACKSPACE:
                        valores[foco] = valores[foco][:-1]
                        mensaje = ""
                    elif evento.key == pygame.K_RETURN:
                        jugador, mensaje = crear_jugador(valores[0], valores[1], valores[2])
                        if jugador is not None:
                            estado = "bienvenida"
                    elif evento.unicode and evento.unicode.isprintable():
                        # Se permite escribir el contenido para que la validación
                        # pueda mostrar un mensaje claro si el formato es incorrecto.
                        if len(valores[foco]) < 28:
                            valores[foco] += evento.unicode
                            mensaje = ""

            elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if estado == "bienvenida":
                    if pygame.Rect(580, 565, 155, 40).collidepoint(evento.pos):
                        estado = "final"
                    elif pygame.Rect(750, 565, 85, 40).collidepoint(evento.pos):
                        ejecutando = False
                elif estado == "final" and pygame.Rect(350, 285, 200, 48).collidepoint(evento.pos):
                    ejecutando = False

        if estado == "registro":
            dibujar_vestibulo(pantalla, fuentes, valores, campos, foco, mensaje)
        elif jugador is not None:
            if estado == "bienvenida":
                dibujar_bienvenida(pantalla, fuentes, jugador)
            else:
                dibujar_final(pantalla, fuentes)

        pygame.display.flip()
        reloj.tick(FPS)

    pygame.quit()
    sys.exit(0)
