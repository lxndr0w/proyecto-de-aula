import unittest

from arbol import (ArbolBinarioBusqueda, comparar_busquedas, reconstruir_catalogo, experimento_comparaciones)


def fragmento(codigo):
    return {"codigo": codigo, "titulo": f"Libro {codigo}", "sala": "Estanterias", "valor": 10}


class PruebasArbol(unittest.TestCase):
    def setUp(self):
        self.datos = [fragmento(c) for c in (50, 30, 70, 20, 40, 60, 80)]

    def test_insertar_e_inorden(self):
        arbol = ArbolBinarioBusqueda()
        for dato in self.datos:
            self.assertTrue(arbol.insertar(dato))
        self.assertEqual([x["codigo"] for x in arbol.inorden()], [20, 30, 40, 50, 60, 70, 80])
        self.assertTrue(arbol.verificar_orden())

    def test_no_inserta_codigo_duplicado(self):
        arbol = ArbolBinarioBusqueda()
        self.assertTrue(arbol.insertar(fragmento(10)))
        self.assertFalse(arbol.insertar(fragmento(10)))
        self.assertEqual(arbol.tamano, 1)

    def test_buscar_cuenta_comparaciones(self):
        arbol = ArbolBinarioBusqueda()
        for dato in self.datos:
            arbol.insertar(dato)
        encontrado, comparaciones = arbol.buscar(60)
        self.assertEqual(encontrado["codigo"], 60)
        self.assertEqual(comparaciones, 3)

    def test_buscar_inexistente(self):
        arbol = ArbolBinarioBusqueda()
        for dato in self.datos:
            arbol.insertar(dato)
        encontrado, comparaciones = arbol.buscar(99)
        self.assertIsNone(encontrado)
        self.assertGreater(comparaciones, 0)

    def test_arbol_vacio(self):
        arbol = ArbolBinarioBusqueda()
        self.assertEqual(arbol.inorden(), [])
        self.assertEqual(arbol.altura(), 0)
        self.assertTrue(arbol.verificar_orden())

    def test_rechaza_codigo_invalido(self):
        arbol = ArbolBinarioBusqueda()
        with self.assertRaises(TypeError):
            arbol.buscar("10")
        with self.assertRaises(ValueError):
            arbol.insertar({"codigo": 0, "titulo": "X", "sala": "Y", "valor": 1})

    def test_reconstruccion_elimina_duplicados(self):
        resultado = reconstruir_catalogo([fragmento(2), fragmento(1), fragmento(2), fragmento(3)])
        self.assertEqual(resultado["descartados"], 1)
        self.assertEqual(len(resultado["fragmentos"]), 3)
        self.assertEqual([x["codigo"] for x in resultado["arbol"].inorden()], [1, 2, 3])

    def test_ubicaciones_son_tuplas(self):
        resultado = reconstruir_catalogo(self.datos)
        self.assertTrue(all(isinstance(pos, tuple) for pos in resultado["ubicaciones"].values()))

    def test_comparacion_de_busquedas(self):
        resultado = comparar_busquedas(self.datos, 60)
        self.assertIn("comparaciones_arbol", resultado)
        self.assertIn("comparaciones_secuencial", resultado)
        self.assertEqual(resultado["comparaciones_secuencial"], 6)
        self.assertEqual(resultado["comparaciones_arbol"], 3)

    def test_arbol_ordenado_se_degenera(self):
        arbol = ArbolBinarioBusqueda()
        for codigo in range(1, 8):
            arbol.insertar(fragmento(codigo))
        self.assertEqual(arbol.altura(), 7)
        encontrado, comparaciones = arbol.buscar(7)
        self.assertEqual(encontrado["codigo"], 7)
        self.assertEqual(comparaciones, 7)


    def test_experimento_tres_tamanos_y_degeneracion(self):
        resultados = experimento_comparaciones((10, 100, 1000))
        self.assertEqual([r["cantidad"] for r in resultados], [10, 100, 1000])
        for resultado in resultados:
            self.assertLessEqual(
                resultado["promedio_arbol_equilibrado"],
                resultado["promedio_secuencial"],
            )
            self.assertEqual(
                resultado["altura_degenerado"],
                resultado["cantidad"],
            )

    def test_experimento_rechaza_tamano_invalido(self):
        with self.assertRaises(ValueError):
            experimento_comparaciones((10, 0))


if __name__ == "__main__":
    unittest.main()
