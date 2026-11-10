"""Pruebas de la reconstrucción que muestra la Sala Central."""

import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

import estructuras
import juego
import persistencia


def fragmento(codigo, titulo="Libro"):
    """Crea un fragmento válido para las pruebas.

    Parámetros:
        codigo: identificador entero del fragmento.
        titulo: nombre que se muestra en la Sala Central.
    Retorna:
        Un diccionario con las cuatro claves del catálogo.
    """
    return estructuras.crear_fragmento(codigo, titulo, "Estanterias", 10)


class PruebasReconstruccion(unittest.TestCase):
    """Comprueba la carga, la depuración, las ubicaciones y el inorden."""

    def test_descarta_repetidos_asigna_tuplas_y_ordena(self):
        """Un conjunto quita los códigos repetidos y el inorden queda ascendente."""
        fragmentos = [
            fragmento(4, "Cuarto"),
            fragmento(4, "Repetido"),
            fragmento(2, "Segundo"),
            fragmento(9, "Noveno"),
            fragmento(2, "Otro"),
            {"codigo": 0, "titulo": "Invalido", "sala": "Estanterias", "valor": 1},
        ]
        resultado = juego.reconstruir_fragmentos(fragmentos)

        self.assertEqual(resultado["ordenado"], True)
        self.assertIsNotNone(resultado["arbol"])
        self.assertEqual(
            [item["codigo"] for item in resultado["arbol"].inorden()],
            [2, 4, 9],
        )
        self.assertEqual(resultado["ubicaciones"][2], (1, 1))
        self.assertEqual(resultado["ubicaciones"][4], (1, 2))
        self.assertEqual(resultado["ubicaciones"][9], (1, 3))
        self.assertIn("descartó 2", resultado["pasos"][0])
        self.assertTrue(any("datos incorrectos" in paso for paso in resultado["pasos"]))
        self.assertIn("ordenado", resultado["mensaje"])

    def test_el_sexto_fragmento_abre_el_estante_dos(self):
        """Cinco niveles llenan el estante 1 y el siguiente pasa al estante 2."""
        resultado = juego.reconstruir_fragmentos([fragmento(codigo) for codigo in range(1, 7)])
        self.assertEqual(resultado["ubicaciones"][1], estructuras.crear_posicion(1, 1))
        self.assertEqual(resultado["ubicaciones"][5], estructuras.crear_posicion(1, 5))
        self.assertEqual(resultado["ubicaciones"][6], estructuras.crear_posicion(2, 1))
        self.assertTrue(all(isinstance(posicion, tuple) for posicion in resultado["ubicaciones"].values()))

    def test_busqueda_existente_e_inexistente_cuentan_comparaciones(self):
        """Una búsqueda informa el fragmento o su ausencia y las comparaciones."""
        resultado = juego.reconstruir_fragmentos([fragmento(8, "Unico")])
        encontrado, comparaciones = resultado["arbol"].buscar(8)
        self.assertEqual(encontrado["titulo"], "Unico")
        self.assertEqual(comparaciones, 1)

        ausente, comparaciones_ausente = resultado["arbol"].buscar(3)
        self.assertIsNone(ausente)
        self.assertEqual(comparaciones_ausente, 1)

    def test_lista_vacia_y_datos_que_no_son_fragmentos(self):
        """Sin fragmentos utilizables no se crea un árbol y el mensaje lo explica."""
        vacio = juego.reconstruir_fragmentos([])
        self.assertIsNone(vacio["arbol"])
        self.assertIn("no hay fragmentos válidos", vacio["mensaje"])

        invalido = juego.reconstruir_fragmentos("no es una lista")
        self.assertIsNone(invalido["arbol"])
        self.assertIn("incompletos", invalido["mensaje"])

    def test_lectura_de_archivo_inexistente_danado_y_vacio(self):
        """La lectura distingue un archivo ausente, uno dañado y una lista vacía."""
        with tempfile.TemporaryDirectory() as carpeta:
            ausente = Path(carpeta) / "no_esta.json"
            fragmentos, mensaje = juego.leer_fragmentos_guardados(ausente)
            self.assertIsNone(fragmentos)
            self.assertIn("no existe", mensaje)

            danado = Path(carpeta) / "danado.json"
            danado.write_text("{", encoding="utf-8")
            fragmentos, mensaje = juego.leer_fragmentos_guardados(danado)
            self.assertIsNone(fragmentos)
            self.assertIn("incorrectos", mensaje)

            incompleto = Path(carpeta) / "incompleto.json"
            incompleto.write_text('{"jugador": {"nombre": "Ana"}}', encoding="utf-8")
            fragmentos, mensaje = juego.leer_fragmentos_guardados(incompleto)
            self.assertIsNone(fragmentos)
            self.assertIn("incompletos", mensaje)

            vacio = Path(carpeta) / "vacio.json"
            self.assertTrue(persistencia.guardar_partida({"fragmentos": []}, vacio))
            fragmentos, mensaje = juego.leer_fragmentos_guardados(vacio)
            self.assertEqual(fragmentos, [])
            self.assertEqual(mensaje, "")


class PruebasPantallaSalaCentral(unittest.TestCase):
    """Comprueba la navegación de la Sala Central sin tocar los JSON reales."""

    def setUp(self):
        """Prepara una ventana invisible y rutas temporales.

        Parámetros:
            Ninguno.
        Retorna:
            None.
        """
        self.temporal = tempfile.TemporaryDirectory()
        self._ruta_partida = persistencia.RUTA_PARTIDA
        self._ruta_puntajes = persistencia.RUTA_PUNTAJES
        persistencia.RUTA_PARTIDA = Path(self.temporal.name) / "partida.json"
        persistencia.RUTA_PUNTAJES = Path(self.temporal.name) / "puntajes.json"
        self.aplicacion = None
        try:
            self.aplicacion = juego.Juego()
        except pygame.error as error:
            self.tearDown()
            self.skipTest(str(error))

    def tearDown(self):
        """Cierra la ventana de prueba y restaura las rutas del proyecto.

        Parámetros:
            Ninguno.
        Retorna:
            None.
        """
        if self.aplicacion is not None:
            self.aplicacion.ejecutando = False
        if pygame.get_init():
            pygame.quit()
        persistencia.RUTA_PARTIDA = self._ruta_partida
        persistencia.RUTA_PUNTAJES = self._ruta_puntajes
        self.temporal.cleanup()

    def preparar_jugador(self):
        """Deja un jugador con tres fragmentos listos para reconstruir.

        Parámetros:
            Ninguno.
        Retorna:
            None.
        """
        self.aplicacion.jugador = juego.Jugador("Samuel", 3, 20, 5, 100.0, True)
        self.aplicacion.inventario = [
            fragmento(30, "Mapa"),
            fragmento(10, "Sello"),
            fragmento(20, "Ficha"),
        ]
        self.aplicacion.pistas = {"a": [101, 101], "b": [101]}
        self.aplicacion.aciertos = 5
        self.aplicacion.respondidas = 5
        self.aplicacion.intentos = 0

    def test_despues_de_sellos_abre_la_sala_y_el_inorden(self):
        """Completar Sellos abre la Sala Central con el recorrido ordenado."""
        self.preparar_jugador()
        self.aplicacion.sala_pregunta = "sellos"
        self.aplicacion.avanzar_sala()

        self.assertEqual(self.aplicacion.estado, "sala_central")
        self.assertEqual(
            [item["codigo"] for item in self.aplicacion.arbol_catalogo.inorden()],
            [10, 20, 30],
        )
        self.assertTrue(self.aplicacion.arbol_catalogo.verificar_orden())
        texto = " ".join(self.aplicacion.pasos_sala)
        self.assertIn("Carga", texto)
        self.assertIn("Depuración", texto)
        self.assertIn("Inorden", texto)
        self.assertTrue(persistencia.RUTA_PARTIDA.is_file())

        self.aplicacion.campos[0].texto = "20"
        self.aplicacion.buscar_catalogo()
        self.assertIn("encontrado", self.aplicacion.mensaje)
        self.assertIn("Comparaciones del árbol", self.aplicacion.mensaje)
        self.assertIn("estante", self.aplicacion.mensaje)

        self.aplicacion.campos[0].texto = "999"
        self.aplicacion.buscar_catalogo()
        self.assertTrue(self.aplicacion.mensaje.startswith("Error"))
        self.assertIn("comparaciones", self.aplicacion.mensaje)
        self.assertTrue(self.aplicacion.ejecutando)

    def test_sin_vidas_antes_de_sellos_sigue_al_resumen(self):
        """Perder todas las vidas en una sala intermedia no abre la Sala Central."""
        self.preparar_jugador()
        self.aplicacion.jugador.activo = False
        self.aplicacion.sala_pregunta = "fichas"
        self.aplicacion.avanzar_sala()
        self.assertEqual(self.aplicacion.estado, "fin")
        self.assertTrue(any(boton.accion == "guardar_puntaje" for boton in self.aplicacion.botones))

    def test_la_sala_central_puede_volver_a_la_tabla(self):
        """Ver puntajes abre el resumen y conserva la tabla de puntajes."""
        self.preparar_jugador()
        self.aplicacion.abrir_sala_central()
        self.aplicacion.accion_sala_central("terminar")
        self.assertEqual(self.aplicacion.estado, "fin")
        self.assertTrue(any(boton.accion == "guardar_puntaje" for boton in self.aplicacion.botones))
        self.assertTrue(any(boton.accion == "salir" for boton in self.aplicacion.botones))

    def test_archivo_ausente_vacio_o_danado_no_cierra_el_juego(self):
        """Un JSON ausente, vacío o dañado muestra el error y deja la partida abierta."""
        self.preparar_jugador()
        self.aplicacion.estado = "sala_central"
        self.aplicacion.campos = [juego.CampoTexto("Código", pygame.Rect(0, 0, 10, 10))]

        persistencia.RUTA_PARTIDA = Path(self.temporal.name) / "ausente.json"
        self.aplicacion.reconstruir_sala_central(guardar_antes=False)
        self.assertIn("no existe", self.aplicacion.mensaje)
        self.assertTrue(self.aplicacion.ejecutando)
        self.aplicacion.buscar_catalogo()
        self.assertIn("no hay un catálogo", self.aplicacion.mensaje)

        vacio = Path(self.temporal.name) / "vacio.json"
        vacio.write_text('{"fragmentos": []}', encoding="utf-8")
        persistencia.RUTA_PARTIDA = vacio
        self.aplicacion.reconstruir_sala_central(guardar_antes=False)
        self.assertIn("no hay fragmentos", self.aplicacion.mensaje)
        self.assertTrue(self.aplicacion.ejecutando)

        danado = Path(self.temporal.name) / "danado.json"
        danado.write_text("{", encoding="utf-8")
        persistencia.RUTA_PARTIDA = danado
        self.aplicacion.reconstruir_sala_central(guardar_antes=False)
        self.assertIn("incorrectos", self.aplicacion.mensaje)
        self.assertTrue(self.aplicacion.ejecutando)

    def test_un_fallo_interno_no_cierra_el_juego(self):
        """Si la reconstrucción lanza un error, la ventana sigue abierta."""
        self.preparar_jugador()
        self.aplicacion.estado = "sala_central"
        ruta = Path(self.temporal.name) / "partida.json"
        persistencia.guardar_partida({"fragmentos": [fragmento(1)]}, ruta)
        persistencia.RUTA_PARTIDA = ruta

        def explota(_fragmentos):
            raise RuntimeError("fallo de prueba")

        original = juego.reconstruir_fragmentos
        juego.reconstruir_fragmentos = explota
        try:
            self.aplicacion.reconstruir_sala_central(guardar_antes=False)
        finally:
            juego.reconstruir_fragmentos = original

        self.assertTrue(self.aplicacion.mensaje.startswith("Error"))
        self.assertIsNone(self.aplicacion.arbol_catalogo)
        self.assertTrue(self.aplicacion.ejecutando)

    def test_cargar_una_partida_que_ya_estaba_en_la_sala_central(self):
        """Cargar una partida guardada en la Sala Central vuelve a abrirla."""
        datos = {
            "jugador": {
                "nombre": "Lua",
                "vida": 2,
                "puntaje": 10,
                "nivel": 6,
                "precision": 80.0,
                "activo": True,
            },
            "sala_actual": "sala_central",
            "fragmentos": [fragmento(15, "Plano")],
            "pistas": {"a": [101], "b": [102]},
            "aciertos": 1,
            "respondidas": 1,
            "intentos": 0,
        }
        self.assertTrue(persistencia.guardar_partida(datos))
        self.aplicacion.cargar()
        self.assertEqual(self.aplicacion.estado, "sala_central")
        self.assertEqual(self.aplicacion.jugador.nombre, "Lua")
        self.assertIn("cargada", self.aplicacion.mensaje)
        self.assertEqual(
            [item["codigo"] for item in self.aplicacion.arbol_catalogo.inorden()],
            [15],
        )


if __name__ == "__main__":
    unittest.main()
