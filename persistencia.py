import json
from pathlib import Path
from datetime import datetime


BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"

RUTA_PARTIDA = DATA_DIR / "partida.json"

RUTA_PUNTAJES = DATA_DIR / "puntajes.json"

def convertir_json(datos):

    if isinstance(datos, (set, tuple)):
        return list(datos)

    if isinstance(datos, list):
        return [convertir_json(x) for x in datos]

    if isinstance(datos, dict):
        return {
            clave: convertir_json(valor)
            for clave, valor in datos.items()
        }

    return datos

def recuperar_datos(datos):

  if isinstance(datos, list):
        return [recuperar_datos(x) for x in datos]

  if isinstance(datos, dict):
        for clave in datos:

            if clave == "posicion":
                datos[clave] = tuple(datos[clave])

            elif clave == "codigos_obtenidos":
                datos[clave] = set(datos[clave])

            else:
                datos[clave] = recuperar_datos(datos[clave])

        return datos

def guardar_partida(datos_partida, ruta=None):

    if ruta is None:
        ruta = RUTA_PARTIDA

    datos = convertir_json(datos_partida)

    try:
        archivo = open(ruta, "w", encoding="utf-8")
        json.dump(datos, archivo, indent=4)
        archivo.close()

        return True

    except:
        return False

def cargar_partida(ruta=None):

    if ruta is None:
        ruta = RUTA_PARTIDA

    try:
        archivo = open(ruta, "r")
        datos = json.load(archivo)
        archivo.close()

        datos = recuperar_datos(datos)

        return datos

    except FileNotFoundError:
        print("No se encontró una partida guardada.")
        return None

    except json.JSONDecodeError:
        print("El archivo está dañado.")
        return None

def guardar_puntaje(registro, ruta=None):

    if ruta is None:
        ruta = RUTA_PUNTAJES

    try:
        try:
            archivo = open(ruta, "r")
            puntajes = json.load(archivo)
            archivo.close()

        except FileNotFoundError:
            puntajes = []

        puntajes.append(registro)

        archivo = open(ruta, "w")
        json.dump(puntajes, archivo, indent=4)
        archivo.close()

        return True

    except:
        return False

def cargar_puntajes(ruta=None):

    if ruta is None:
        ruta = RUTA_PUNTAJES

    try:
        archivo = open(ruta, "r")
        puntajes = json.load(archivo)
        archivo.close()

        return puntajes

    except FileNotFoundError:
        print("No se encontraron puntajes.")
        return []

    except json.JSONDecodeError:
        print("El archivo de puntajes está dañado.")
        return []