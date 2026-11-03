"""Estructuras de datos utilizadas en las salas de El Archivo Perdido.

Este módulo contiene las operaciones de listas, tuplas, diccionarios y
conjuntos. No importa Pygame para poder probarse de forma independiente.
"""

from __future__ import annotations

from typing import Iterable, TypeAlias

# Un fragmento es un diccionario con datos de texto y datos numéricos.
Fragmento: TypeAlias = dict[str, int | str]

# Estas son las cuatro claves obligatorias de cada fragmento.
CLAVES_FRAGMENTO = ("codigo", "titulo", "sala", "valor")


def _validar_codigo(codigo: int) -> None:
    """Comprueba que un código sea un entero positivo.

    Parámetros:
        codigo: identificador que se desea validar.
    Retorna:
        None. Lanza TypeError o ValueError si el código no es válido.
    """
    if isinstance(codigo, bool) or not isinstance(codigo, int):
        raise TypeError("El código debe ser un número entero.")
    if codigo <= 0:
        raise ValueError("El código debe ser mayor que cero.")


def crear_fragmento(codigo: int, titulo: str, sala: str, valor: int) -> Fragmento:
    """Crea y valida el diccionario que representa un fragmento.

    Parámetros:
        codigo: identificador entero positivo del fragmento.
        titulo: nombre del libro o documento.
        sala: sala donde se encontró el fragmento.
        valor: puntaje entero no negativo que aporta el fragmento.
    Retorna:
        Un diccionario con las claves codigo, titulo, sala y valor.
    """
    _validar_codigo(codigo)

    if not isinstance(titulo, str) or not titulo.strip():
        raise ValueError("El título debe ser un texto que no esté vacío.")
    if not isinstance(sala, str) or not sala.strip():
        raise ValueError("La sala debe ser un texto que no esté vacío.")
    if isinstance(valor, bool) or not isinstance(valor, int) or valor < 0:
        raise ValueError("El valor debe ser un entero igual o mayor que cero.")

    return {
        "codigo": codigo,
        "titulo": titulo.strip(),
        "sala": sala.strip(),
        "valor": valor,
    }


def _validar_fragmento(fragmento: Fragmento) -> Fragmento:
    """Comprueba los campos de un fragmento y devuelve una copia válida.

    Parámetros:
        fragmento: diccionario que se desea comprobar.
    Retorna:
        Una copia del fragmento con sus cuatro campos normalizados.
    """
    if not isinstance(fragmento, dict):
        raise TypeError("Cada elemento del inventario debe ser un diccionario.")

    faltantes = [clave for clave in CLAVES_FRAGMENTO if clave not in fragmento]
    if faltantes:
        raise ValueError(f"Al fragmento le faltan estas claves: {faltantes}.")

    return crear_fragmento(
        fragmento["codigo"],
        fragmento["titulo"],
        fragmento["sala"],
        fragmento["valor"],
    )


def _validar_inventario(inventario: list[Fragmento]) -> None:
    """Comprueba que el inventario sea una lista de fragmentos válidos.

    Parámetros:
        inventario: lista que contiene las fichas recolectadas.
    Retorna:
        None. Lanza TypeError o ValueError si la lista no es válida.
    """
    if not isinstance(inventario, list):
        raise TypeError("El inventario debe ser una lista.")

    for fragmento in inventario:
        _validar_fragmento(fragmento)


def agregar_fragmento(inventario: list[Fragmento], fragmento: Fragmento) -> bool:
    """Agrega un fragmento si su código todavía no está en el inventario.

    Parámetros:
        inventario: lista donde se guardan los fragmentos.
        fragmento: diccionario que se desea insertar.
    Retorna:
        True si lo agregó; False si ya existía un fragmento con ese código.
    """
    _validar_inventario(inventario)
    nuevo_fragmento = _validar_fragmento(fragmento)

    codigo = nuevo_fragmento["codigo"]
    if buscar_fragmento(inventario, codigo) is not None:
        return False

    inventario.append(nuevo_fragmento)
    return True


def eliminar_fragmento(inventario: list[Fragmento], codigo: int) -> bool:
    """Elimina del inventario el fragmento que tenga el código indicado.

    Parámetros:
        inventario: lista de fragmentos recolectados.
        codigo: identificador del fragmento que se desea eliminar.
    Retorna:
        True si eliminó un fragmento; False si el código no aparece.
    """
    _validar_inventario(inventario)
    _validar_codigo(codigo)

    for indice, fragmento in enumerate(inventario):
        if fragmento["codigo"] == codigo:
            del inventario[indice]
            return True

    return False


def buscar_fragmento(inventario: list[Fragmento], codigo: int) -> Fragmento | None:
    """Busca un fragmento por código recorriendo la lista de principio a fin.

    Parámetros:
        inventario: lista donde se realizará la búsqueda.
        codigo: identificador que se desea encontrar.
    Retorna:
        El diccionario encontrado o None si no existe ese código.
    """
    _validar_inventario(inventario)
    _validar_codigo(codigo)

    for fragmento in inventario:
        if fragmento["codigo"] == codigo:
            return fragmento

    return None


def ordenar_fragmentos(inventario: list[Fragmento]) -> list[Fragmento]:
    """Devuelve una nueva lista ordenada por el código de cada fragmento.

    Parámetros:
        inventario: lista original de fragmentos.
    Retorna:
        Una nueva lista ordenada de menor a mayor código.
    """
    _validar_inventario(inventario)
    return sorted(inventario, key=lambda fragmento: fragmento["codigo"])


def obtener_codigos_por_sala(inventario: list[Fragmento], sala: str) -> list[int]:
    """Obtiene con comprensión de listas los códigos que pertenecen a una sala.

    Parámetros:
        inventario: lista de fragmentos que se desea filtrar.
        sala: nombre de la sala que se quiere consultar.
    Retorna:
        Lista de códigos de esa sala, sin distinguir mayúsculas y minúsculas.
    """
    _validar_inventario(inventario)
    if not isinstance(sala, str) or not sala.strip():
        raise ValueError("El nombre de la sala no puede estar vacío.")

    sala_buscada = sala.strip().casefold()
    return [
        fragmento["codigo"]
        for fragmento in inventario
        if fragmento["sala"].casefold() == sala_buscada
    ]


def crear_posicion(fila: int, columna: int) -> tuple[int, int]:
    """Crea una posición inmutable de la biblioteca usando una tupla.

    Parámetros:
        fila: número entero no negativo de la fila.
        columna: número entero no negativo de la columna.
    Retorna:
        Una tupla con el formato (fila, columna).
    """
    if isinstance(fila, bool) or not isinstance(fila, int) or fila < 0:
        raise ValueError("La fila debe ser un entero no negativo.")
    if isinstance(columna, bool) or not isinstance(columna, int) or columna < 0:
        raise ValueError("La columna debe ser un entero no negativo.")

    return (fila, columna)


def desempaquetar_posicion(posicion: tuple[int, int]) -> tuple[int, int]:
    """Separa una tupla de posición en las variables fila y columna.

    Parámetros:
        posicion: tupla con exactamente dos coordenadas enteras.
    Retorna:
        Una tupla (fila, columna) con las coordenadas validadas.
    """
    if not isinstance(posicion, tuple) or len(posicion) != 2:
        raise ValueError("La posición debe ser una tupla de dos elementos.")
    if any(
        isinstance(coordenada, bool) or not isinstance(coordenada, int)
        or coordenada < 0
        for coordenada in posicion
    ):
        raise ValueError("Las coordenadas deben ser enteros no negativos.")

    fila, columna = posicion
    return fila, columna


def consultar_ficha(fragmento: Fragmento, clave: str) -> int | str | None:
    """Consulta un campo del diccionario sin fallar si la clave no existe.

    Parámetros:
        fragmento: diccionario que contiene los datos de la ficha.
        clave: nombre del campo que se desea consultar.
    Retorna:
        El valor asociado a la clave o None si la clave no está definida.
    """
    ficha_validada = _validar_fragmento(fragmento)
    if not isinstance(clave, str) or not clave:
        raise ValueError("La clave de consulta debe ser un texto no vacío.")

    return ficha_validada.get(clave)


def _convertir_a_lista_de_codigos(codigos: Iterable[int]) -> list[int]:
    """Convierte una colección iterable en lista y valida sus códigos.

    Parámetros:
        codigos: colección de códigos que se desea comprobar.
    Retorna:
        Una lista de códigos enteros positivos.
    """
    if isinstance(codigos, (str, bytes)):
        raise TypeError("Los códigos deben venir en una colección de números.")

    try:
        lista_codigos = list(codigos)
    except TypeError as error:
        raise TypeError("Los códigos deben ser una colección iterable.") from error

    for codigo in lista_codigos:
        _validar_codigo(codigo)

    return lista_codigos


def eliminar_duplicados(codigos: Iterable[int]) -> tuple[set[int], int]:
    """Quita los códigos repetidos convirtiendo la colección en un conjunto.

    Parámetros:
        codigos: colección de códigos enteros positivos, posiblemente repetidos.
    Retorna:
        Una tupla con el conjunto de códigos únicos y el total de repetidos.
    """
    lista_codigos = _convertir_a_lista_de_codigos(codigos)
    conjunto_unico = set(lista_codigos)
    cantidad_repetidos = len(lista_codigos) - len(conjunto_unico)

    return conjunto_unico, cantidad_repetidos


def operaciones_conjuntos(
    codigos_a: Iterable[int], codigos_b: Iterable[int]
) -> dict[str, set[int]]:
    """Calcula unión, intersección y diferencia entre dos grupos de códigos.

    Parámetros:
        codigos_a: primera colección de códigos.
        codigos_b: segunda colección de códigos.
    Retorna:
        Diccionario con los resultados union, interseccion y diferencia_a_b.
    """
    conjunto_a = set(_convertir_a_lista_de_codigos(codigos_a))
    conjunto_b = set(_convertir_a_lista_de_codigos(codigos_b))

    return {
        "union": conjunto_a | conjunto_b,
        "interseccion": conjunto_a & conjunto_b,
        "diferencia_a_b": conjunto_a - conjunto_b,
    }
