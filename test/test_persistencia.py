
import json
import tempfile
import unittest
from pathlib import Path

from persistencia import (
    cargar_partida,
    cargar_puntajes,
    guardar_partida,
    guardar_puntaje
)


class TestPersistencia(unittest.TestCase):

    def setUp(self):
        self.carpeta = tempfile.TemporaryDirectory()
        self.ruta = Path(self.carpeta.name)

    def tearDown(self):
        self.carpeta.cleanup()

    def test_guardar_partida(self):
        ruta = self.ruta / "partida.json"

        datos = {
            "jugador": {"nombre": "jugador", "vida": 3, "puntaje": 50},
            "posicion": (2, 3),
            "codigos_obtenidos": {"A1", "B2"}
        }

        self.assertTrue(guardar_partida(datos, ruta))
        self.assertTrue(ruta.exists())

    def test_cargar_partida(self):
        ruta = self.ruta / "partida.json"

        datos = {
            "jugador": {"nombre": "jugador", "vida": 3},
            "posicion": (2, 3),
            "codigos_obtenidos": {"A1", "B2"}
        }

        guardar_partida(datos, ruta)
        resultado = cargar_partida(ruta)

        self.assertEqual(resultado, {
            "jugador": datos["jugador"],
            "posicion": datos["posicion"],
            "codigos_obtenidos": datos["codigos_obtenidos"]
        })

    def test_partida_inexistente(self):
        resultado = cargar_partida(self.ruta / "inexistente.json")
        self.assertIsNone(resultado)

    def test_json_danado(self):
        ruta = self.ruta / "danado.json"
        ruta.write_text("{ archivo incorrecto", encoding="utf-8")

        resultado = cargar_partida(ruta)
        self.assertIsNone(resultado)

    def test_guardar_puntaje(self):
        ruta = self.ruta / "puntajes.json"
        inicial = {"nombre": "Jugador", "puntaje": 100}
        nuevo = {"nombre": "jugador", "puntaje": 200}

        ruta.write_text(json.dumps([inicial]), encoding="utf-8")

        self.assertTrue(guardar_puntaje(nuevo, ruta))

        puntajes = json.loads(ruta.read_text(encoding="utf-8"))

        self.assertEqual(len(puntajes), 2)
        self.assertEqual(puntajes[-1], nuevo)

    def test_cargar_puntajes(self):
        ruta = self.ruta / "puntajes.json"
        datos = [
            {"nombre": "jugador", "puntaje": 200},
            {"nombre": "Jugador2", "puntaje": 150}
        ]

        ruta.write_text(json.dumps(datos), encoding="utf-8")

        self.assertEqual(cargar_puntajes(ruta), datos)

    def test_puntajes_sin_archivo(self):
        resultado = cargar_puntajes(self.ruta / "inexistente.json")
        self.assertEqual(resultado, [])

    def test_rutas_temporales(self):
        ruta_partida = self.ruta / "pruebas" / "partida.json"
        ruta_puntajes = self.ruta / "pruebas" / "puntajes.json"

        guardar_partida({"jugador": {"nombre": "jugador"}}, ruta_partida)
        guardar_puntaje({"nombre": "jugador", "puntaje": 100}, ruta_puntajes)

        self.assertTrue(ruta_partida.exists())
        self.assertTrue(ruta_puntajes.exists())


if __name__ == "__main__":
    unittest.main()
