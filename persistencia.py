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
        return {clave: convertir_json(valor) for clave, valor in datos.items()}
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

    Path(ruta).parent.mkdir(parents=True, exist_ok=True)
    datos = convertir_json(datos_partida)

    try:
        with open(ruta, "w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, indent=4)
        return True
    except Exception:
        return False

def cargar_partida(ruta=None):
    if ruta is None:
        ruta = RUTA_PARTIDA

    try:
        with open(ruta, "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
        return recuperar_datos(datos)
    except FileNotFoundError:
        print("No se encontró una partida guardada.")
        return None
    except json.JSONDecodeError:
        print("El archivo está dañado.")
        return None
    except (TypeError, ValueError):
        print("El archivo está dañado.")
        return None

def guardar_puntaje(registro, ruta=None):
    if ruta is None:
        ruta = RUTA_PUNTAJES

   Path(ruta).parent.mkdir(parents=True, exist_ok=True)

    try:
        try:
            with open(ruta, "r", encoding="utf-8") as archivo:
                puntajes = json.load(archivo)
        except FileNotFoundError:
            puntajes = []

        puntajes.append(registro)

        with open(ruta, "w", encoding="utf-8") as archivo:
            json.dump(puntajes, archivo, indent=4)
        return True
    except Exception:
        return False

def cargar_puntajes(ruta=None):
    if ruta is None:
        ruta = RUTA_PUNTAJES

    try:
        with open(ruta, "r", encoding="utf-8") as archivo:
            puntajes = json.load(archivo)
        return puntajes
    except FileNotFoundError:
        print("No se encontraron puntajes.")
        return []
    except json.JSONDecodeError:
        print("El archivo de puntajes está dañado.")
        return []
