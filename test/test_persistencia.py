"""Pruebas automatizadas para la carga y conversión de partidas."""

import json
from pathlib import Path
import tempfile
import unittest

import persistencia


class PruebasPersistencia(unittest.TestCase):
    """Verifica que la carga convierta datos válidos y rechace datos dañados."""

    def test_cargar_partida_rechaza_datos_incompatibles(self) -> None:
        """Un valor no hashable en los códigos debe tratarse como archivo dañado."""
        with tempfile.TemporaryDirectory() as directorio:
            ruta = Path(directorio) / "partida.json"
            ruta.write_text(
                json.dumps({"codigos_obtenidos": [[]]}), encoding="utf-8"
            )

            self.assertIsNone(persistencia.cargar_partida(ruta))

    def test_cargar_partida_recupera_tupla_y_conjunto(self) -> None:
        """La carga conserva las conversiones de tipos guardados como listas JSON."""
        with tempfile.TemporaryDirectory() as directorio:
            ruta = Path(directorio) / "partida.json"
            ruta.write_text(
                json.dumps(
                    {"posicion": [3, 4], "codigos_obtenidos": ["A1", "B2"]}
                ),
                encoding="utf-8",
            )

            datos = persistencia.cargar_partida(ruta)

            self.assertEqual(datos["posicion"], (3, 4))
            self.assertEqual(datos["codigos_obtenidos"], {"A1", "B2"})


if __name__ == "__main__":
    unittest.main()