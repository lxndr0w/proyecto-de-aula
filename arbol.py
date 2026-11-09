"""Árbol binario de búsqueda para reconstruir el catálogo.

El árbol se implementa desde cero, sin librerías externas.
La clave de ordenamiento es el código numérico de cada fragmento.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Nodo:
    """Nodo del árbol binario.

    Parámetros:
        fragmento: diccionario del fragmento almacenado.
        izquierdo: subárbol con códigos menores.
        derecho: subárbol con códigos mayores.
    Retorna:
        No aplica; representa un nodo del árbol.
    """

    fragmento: dict[str, Any]
    izquierdo: Nodo | None = None
    derecho: Nodo | None = None

    @property
    def codigo(self) -> int:
        """Obtiene el código del fragmento guardado en el nodo.

        Parámetros:
            Ninguno.
        Retorna:
            Código entero del fragmento.
        """
        return self.fragmento["codigo"]


class ArbolBinarioBusqueda:
    """Árbol binario de búsqueda ordenado por código de fragmento."""

    def __init__(self) -> None:
        """Inicializa un árbol vacío.

        Parámetros:
            Ninguno.
        Retorna:
            None.
        """
        self.raiz: Nodo | None = None
        self.tamano = 0

    def insertar(self, fragmento: dict[str, Any]) -> bool:
        """Inserta un fragmento según su código.

        Parámetros:
            fragmento: diccionario con código, título, sala y valor.
        Retorna:
            True si se insertó; False si el código ya existía.
        """
        self._validar_fragmento(fragmento)
        copia = dict(fragmento)

        if self.raiz is None:
            self.raiz = Nodo(copia)
            self.tamano = 1
            return True

        actual = self.raiz
        while True:
            if copia["codigo"] == actual.codigo:
                return False
            if copia["codigo"] < actual.codigo:
                if actual.izquierdo is None:
                    actual.izquierdo = Nodo(copia)
                    self.tamano += 1
                    return True
                actual = actual.izquierdo
            else:
                if actual.derecho is None:
                    actual.derecho = Nodo(copia)
                    self.tamano += 1
                    return True
                actual = actual.derecho

    def buscar(self, codigo: int) -> tuple[dict[str, Any] | None, int]:
        """Busca un fragmento y cuenta las comparaciones de códigos.

        Parámetros:
            codigo: código entero positivo que se desea localizar.
        Retorna:
            Tupla (fragmento, comparaciones). El fragmento es None si no existe.
        """
        self._validar_codigo(codigo)
        actual = self.raiz
        comparaciones = 0

        while actual is not None:
            comparaciones += 1
            if codigo == actual.codigo:
                return dict(actual.fragmento), comparaciones
            if codigo < actual.codigo:
                actual = actual.izquierdo
            else:
                actual = actual.derecho

        return None, comparaciones

    def inorden(self) -> list[dict[str, Any]]:
        """Recorre el árbol en inorden y devuelve los fragmentos ordenados.

        Parámetros:
            Ninguno.
        Retorna:
            Lista de fragmentos ordenada de menor a mayor código.
        """
        resultado: list[dict[str, Any]] = []
        pila: list[Nodo] = []
        actual = self.raiz

        # La pila conserva los nodos pendientes mientras bajamos por la izquierda.
        while actual is not None or pila:
            while actual is not None:
                pila.append(actual)
                actual = actual.izquierdo

            actual = pila.pop()
            resultado.append(dict(actual.fragmento))
            actual = actual.derecho

        return resultado

    def verificar_orden(self) -> bool:
        """Comprueba que el recorrido inorden tenga códigos estrictamente crecientes.

        Parámetros:
            Ninguno.
        Retorna:
            True si el resultado está ordenado y no contiene claves repetidas.
        """
        codigos = [fragmento["codigo"] for fragmento in self.inorden()]
        return all(codigos[i] < codigos[i + 1] for i in range(len(codigos) - 1))

    def altura(self) -> int:
        """Calcula la altura del árbol en número de niveles.

        Parámetros:
            Ninguno.
        Retorna:
            Cero si el árbol está vacío; en otro caso, el número de niveles.
        """
        if self.raiz is None:
            return 0

        maximo = 0
        pendientes: list[tuple[Nodo, int]] = [(self.raiz, 1)]

        # Cada elemento de la pila contiene el nodo y el nivel en que está.
        while pendientes:
            nodo, nivel = pendientes.pop()
            maximo = max(maximo, nivel)

            if nodo.izquierdo is not None:
                pendientes.append((nodo.izquierdo, nivel + 1))
            if nodo.derecho is not None:
                pendientes.append((nodo.derecho, nivel + 1))

        return maximo

    @staticmethod
    def busqueda_secuencial(fragmentos: list[dict[str, Any]], codigo: int) -> tuple[dict[str, Any] | None, int]:
        """Busca un código en una lista y cuenta las comparaciones.

        Parámetros:
            fragmentos: lista de fragmentos por revisar.
            codigo: identificador buscado.
        Retorna:
            Tupla (fragmento, comparaciones).
        """
        ArbolBinarioBusqueda._validar_codigo(codigo)
        comparaciones = 0
        for fragmento in fragmentos:
            comparaciones += 1
            if fragmento["codigo"] == codigo:
                return dict(fragmento), comparaciones
        return None, comparaciones

    @staticmethod
    def _validar_codigo(codigo: int) -> None:
        """Valida un identificador numérico positivo.

        Parámetros:
            codigo: código por validar.
        Retorna:
            None. Lanza TypeError o ValueError si el dato no es válido.
        """
        if isinstance(codigo, bool) or not isinstance(codigo, int):
            raise TypeError("El código debe ser un entero.")
        if codigo <= 0:
            raise ValueError("El código debe ser mayor que cero.")

    @classmethod
    def _validar_fragmento(cls, fragmento: dict[str, Any]) -> None:
        """Valida la forma mínima de un fragmento del catálogo.

        Parámetros:
            fragmento: diccionario por validar.
        Retorna:
            None. Lanza TypeError o ValueError si falta algún dato.
        """
        if not isinstance(fragmento, dict):
            raise TypeError("El fragmento debe ser un diccionario.")
        for clave in ("codigo", "titulo", "sala", "valor"):
            if clave not in fragmento:
                raise ValueError(f"Falta la clave obligatoria: {clave}.")
        cls._validar_codigo(fragmento["codigo"])
        if not isinstance(fragmento["titulo"], str) or not fragmento["titulo"].strip():
            raise ValueError("El título no puede estar vacío.")
        if not isinstance(fragmento["sala"], str) or not fragmento["sala"].strip():
            raise ValueError("La sala no puede estar vacía.")
        if isinstance(fragmento["valor"], bool) or not isinstance(fragmento["valor"], int) or fragmento["valor"] < 0:
            raise ValueError("El valor debe ser un entero no negativo.")


def reconstruir_catalogo(fragmentos: list[dict[str, Any]]) -> dict[str, Any]:
    """Depura fragmentos y construye un árbol binario de búsqueda.

    Parámetros:
        fragmentos: lista de diccionarios leídos desde una partida.
    Retorna:
        Diccionario con árbol, fragmentos únicos, cantidad descartada y ubicaciones.
    """
    codigos_vistos: set[int] = set()
    unicos: list[dict[str, Any]] = []
    descartados = 0

    for fragmento in fragmentos:
        ArbolBinarioBusqueda._validar_fragmento(fragmento)
        codigo = fragmento["codigo"]
        if codigo in codigos_vistos:
            descartados += 1
            continue
        codigos_vistos.add(codigo)
        unicos.append(dict(fragmento))

    # Las posiciones se representan como tuplas (estante, nivel).
    ubicaciones: dict[int, tuple[int, int]] = {}
    for indice, fragmento in enumerate(sorted(unicos, key=lambda f: f["codigo"])):
        ubicaciones[fragmento["codigo"]] = (indice // 5 + 1, indice % 5 + 1)

    arbol = ArbolBinarioBusqueda()
    # Insertar en orden alternado ayuda a evitar un árbol degenerado para este catálogo.
    orden_insercion = sorted(unicos, key=lambda f: f["codigo"])
    orden_insercion = _orden_balanceado(orden_insercion)
    for fragmento in orden_insercion:
        arbol.insertar(fragmento)

    return {
        "arbol": arbol,
        "fragmentos": unicos,
        "descartados": descartados,
        "ubicaciones": ubicaciones,
    }


def _orden_balanceado(fragmentos: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Genera orden de inserción mediano-primero para obtener un árbol equilibrado.

    Parámetros:
        fragmentos: lista de fragmentos ordenados por código.
    Retorna:
        Una lista en orden mediano-primero.
    """
    resultado: list[dict[str, Any]] = []

    def agregar_rango(inicio: int, fin: int) -> None:
        """Agrega primero el elemento central de cada rango.

        Parámetros:
            inicio: índice inicial inclusivo.
            fin: índice final exclusivo.
        Retorna:
            None.
        """
        if inicio >= fin:
            return
        medio = (inicio + fin) // 2
        resultado.append(fragmentos[medio])
        agregar_rango(inicio, medio)
        agregar_rango(medio + 1, fin)

    agregar_rango(0, len(fragmentos))
    return resultado


def comparar_busquedas(fragmentos: list[dict[str, Any]], codigo: int) -> dict[str, Any]:
    """Compara búsquedas secuenciales y en un árbol construido mediano-primero.

    Parámetros:
        fragmentos: catálogo sin duplicados.
        codigo: código que se desea buscar.
    Retorna:
        Resultados, incluyendo comparaciones y diferencia entre ambos métodos.
    """
    arbol = ArbolBinarioBusqueda()
    fragmentos_ordenados = sorted(fragmentos, key=lambda fragmento: fragmento["codigo"])
    for fragmento in _orden_balanceado(fragmentos_ordenados):
        arbol.insertar(fragmento)

    _, comparaciones_arbol = arbol.buscar(codigo)
    _, comparaciones_lista = ArbolBinarioBusqueda.busqueda_secuencial(fragmentos, codigo)

    return {
        "codigo": codigo,
        "comparaciones_arbol": comparaciones_arbol,
        "comparaciones_secuencial": comparaciones_lista,
        "altura_arbol": arbol.altura(),
    }


def experimento_comparaciones(tamanos: tuple[int, ...] = (10, 100, 1000)) -> list[dict[str, int | float]]:
    """Mide comparaciones promedio y altura en árboles equilibrados y degenerados.

    Parámetros:
        tamanos: cantidades de fragmentos que se desean evaluar.
    Retorna:
        Lista de resultados con tamaño, promedios de comparaciones y alturas.
    """
    resultados: list[dict[str, int | float]] = []

    for cantidad in tamanos:
        if isinstance(cantidad, bool) or not isinstance(cantidad, int) or cantidad < 1:
            raise ValueError("Cada tamaño debe ser un entero mayor que cero.")

        catalogo = [
            {
                "codigo": indice + 1,
                "titulo": f"Libro {indice + 1}",
                "sala": "Prueba",
                "valor": 10,
            }
            for indice in range(cantidad)
        ]

        # Caso equilibrado: insertar primero las medianas y luego sus mitades.
        arbol_equilibrado = ArbolBinarioBusqueda()
        for fragmento in _orden_balanceado(catalogo):
            arbol_equilibrado.insertar(fragmento)

        # Caso degenerado: insertar códigos crecientes produce una sola rama derecha.
        arbol_degenerado = ArbolBinarioBusqueda()
        for fragmento in catalogo:
            arbol_degenerado.insertar(fragmento)

        total_secuencial = 0
        total_equilibrado = 0
        total_degenerado = 0

        for fragmento in catalogo:
            codigo = fragmento["codigo"]
            _, comparaciones = ArbolBinarioBusqueda.busqueda_secuencial(catalogo, codigo)
            total_secuencial += comparaciones

            _, comparaciones = arbol_equilibrado.buscar(codigo)
            total_equilibrado += comparaciones

            _, comparaciones = arbol_degenerado.buscar(codigo)
            total_degenerado += comparaciones

        resultados.append(
            {
                "cantidad": cantidad,
                "promedio_secuencial": round(total_secuencial / cantidad, 2),
                "promedio_arbol_equilibrado": round(total_equilibrado / cantidad, 2),
                "promedio_arbol_degenerado": round(total_degenerado / cantidad, 2),
                "altura_equilibrado": arbol_equilibrado.altura(),
                "altura_degenerado": arbol_degenerado.altura(),
            }
        )

    return resultados
