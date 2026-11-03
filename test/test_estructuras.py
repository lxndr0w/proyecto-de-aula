"""Pruebas automatizadas para las estructuras de datos del proyecto."""

import unittest

import estructuras


class PruebasEstructuras(unittest.TestCase):
    """Verifica las operaciones de listas, tuplas, diccionarios y conjuntos."""

    def setUp(self) -> None:
        """Prepara un inventario nuevo antes de ejecutar cada prueba.

        Parámetros:
            Ninguno.
        Retorna:
            None.
        """
        self.inventario = [
            estructuras.crear_fragmento(105, "Libro C", "Estanterias", 20),
            estructuras.crear_fragmento(101, "Libro A", "Estanterias", 10),
        ]

    def test_crear_fragmento_y_validar_datos(self) -> None:
        """Comprueba el formato del fragmento y el rechazo de datos inválidos."""
        fragmento = estructuras.crear_fragmento(200, "Libro", "Mapas", 15)
        self.assertEqual(
            fragmento,
            {"codigo": 200, "titulo": "Libro", "sala": "Mapas", "valor": 15},
        )
        with self.assertRaises(ValueError):
            estructuras.crear_fragmento(0, "Libro", "Mapas", 15)
        with self.assertRaises(ValueError):
            estructuras.crear_fragmento(201, "   ", "Mapas", 15)

    def test_agregar_fragmento_y_evitar_codigos_repetidos(self) -> None:
        """Comprueba que se inserte un fragmento y no se repita su código."""
        nuevo = estructuras.crear_fragmento(103, "Libro B", "Fichas", 12)
        self.assertTrue(estructuras.agregar_fragmento(self.inventario, nuevo))
        self.assertFalse(estructuras.agregar_fragmento(self.inventario, nuevo))
        self.assertEqual(len(self.inventario), 3)

    def test_buscar_fragmento_existente_e_inexistente(self) -> None:
        """Comprueba que la búsqueda devuelva el fragmento o None."""
        encontrado = estructuras.buscar_fragmento(self.inventario, 105)
        self.assertIsNotNone(encontrado)
        self.assertEqual(encontrado["titulo"], "Libro C")
        self.assertIsNone(estructuras.buscar_fragmento(self.inventario, 999))

    def test_eliminar_fragmento_existente_e_inexistente(self) -> None:
        """Comprueba que la eliminación informe si encontró el código."""
        self.assertTrue(estructuras.eliminar_fragmento(self.inventario, 105))
        self.assertFalse(estructuras.eliminar_fragmento(self.inventario, 999))
        self.assertEqual([f["codigo"] for f in self.inventario], [101])

    def test_ordenar_sin_modificar_lista_original(self) -> None:
        """Comprueba el orden ascendente y que se conserve la lista original."""
        ordenados = estructuras.ordenar_fragmentos(self.inventario)
        self.assertEqual([f["codigo"] for f in ordenados], [101, 105])
        self.assertEqual([f["codigo"] for f in self.inventario], [105, 101])

    def test_comprension_de_listas_por_sala(self) -> None:
        """Comprueba que se obtengan los códigos de una sala concreta."""
        codigos = estructuras.obtener_codigos_por_sala(
            self.inventario, "estanterias"
        )
        self.assertEqual(codigos, [105, 101])

    def test_crear_y_desempaquetar_tupla(self) -> None:
        """Comprueba la tupla (fila, columna) y su desempaquetado."""
        posicion = estructuras.crear_posicion(3, 5)
        fila, columna = estructuras.desempaquetar_posicion(posicion)
        self.assertEqual(posicion, (3, 5))
        self.assertEqual((fila, columna), (3, 5))
        with self.assertRaises(TypeError):
            posicion[0] = 9  # type: ignore[index]

    def test_validar_coordenadas_invalidas(self) -> None:
        """Comprueba que no se acepten filas o columnas negativas."""
        with self.assertRaises(ValueError):
            estructuras.crear_posicion(-1, 2)
        with self.assertRaises(ValueError):
            estructuras.desempaquetar_posicion((1, -2))

    def test_consultar_clave_existente_e_inexistente(self) -> None:
        """Comprueba que get devuelva el dato o None si falta la clave."""
        ficha = self.inventario[0]
        self.assertEqual(estructuras.consultar_ficha(ficha, "titulo"), "Libro C")
        self.assertIsNone(estructuras.consultar_ficha(ficha, "autor"))

    def test_eliminar_duplicados_y_contarlos(self) -> None:
        """Comprueba que el conjunto quite repetidos y permita contarlos."""
        conjunto, repetidos = estructuras.eliminar_duplicados([1, 2, 2, 3, 3])
        self.assertEqual(conjunto, {1, 2, 3})
        self.assertEqual(repetidos, 2)

    def test_union_interseccion_y_diferencia(self) -> None:
        """Comprueba las tres operaciones entre dos conjuntos de códigos."""
        resultado = estructuras.operaciones_conjuntos(
            [1, 2, 3], [2, 3, 4]
        )
        self.assertEqual(resultado["union"], {1, 2, 3, 4})
        self.assertEqual(resultado["interseccion"], {2, 3})
        self.assertEqual(resultado["diferencia_a_b"], {1})

    def test_rechazar_codigos_invalidos(self) -> None:
        """Comprueba que no se acepten códigos cero, negativos o no enteros."""
        with self.assertRaises(ValueError):
            estructuras.eliminar_duplicados([1, 0, 2])
        with self.assertRaises(TypeError):
            estructuras.operaciones_conjuntos([1, "dos"], [2])


if __name__ == "__main__":
    unittest.main()
