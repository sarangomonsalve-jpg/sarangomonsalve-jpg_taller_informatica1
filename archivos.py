"""Item 2: gestion de archivos TXT, CSV y JSON con manejo de excepciones."""
import csv
import json
from pathlib import Path

from sistema import BASE_DIR, localizar_archivo, registrar_log

CAMPOS = ["id", "fr", "fc", "spo2"]


def _verificar_ruta_escritura(ruta: Path):
    if not ruta.parent.exists():
        raise FileNotFoundError(f"La carpeta destino no existe: {ruta.parent}")
    if ruta.exists() and ruta.is_dir():
        raise IsADirectoryError(f"La ruta es una carpeta: {ruta}")


def guardar_txt(registros, nombre="datos_ordenados.txt"):
    ruta = BASE_DIR / nombre
    try:
        _verificar_ruta_escritura(ruta)
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(" | ".join(CAMPOS) + "\n")
            for r in registros:
                f.write(" | ".join(r[c] for c in CAMPOS) + "\n")
        registrar_log(f"TXT guardado: {nombre} ({len(registros)} registros)")
        return ruta
    except (OSError, KeyError) as e:
        registrar_log(f"Error guardando TXT: {e}", "ERROR")
        print(f"Error guardando TXT: {e}")
        return None


def guardar_csv(registros, nombre="datos_ordenados.csv"):
    ruta = BASE_DIR / nombre
    try:
        _verificar_ruta_escritura(ruta)
        with open(ruta, "w", newline="", encoding="utf-8") as f:
            escritor = csv.DictWriter(f, fieldnames=CAMPOS)
            escritor.writeheader()
            escritor.writerows({c: r[c] for c in CAMPOS} for r in registros)
        registrar_log(f"CSV guardado: {nombre} ({len(registros)} registros)")
        return ruta
    except (OSError, KeyError) as e:
        registrar_log(f"Error guardando CSV: {e}", "ERROR")
        print(f"Error guardando CSV: {e}")
        return None


def exportar_json(registros, nombre="datos.json"):
    ruta = BASE_DIR / nombre
    try:
        _verificar_ruta_escritura(ruta)
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(registros, f, ensure_ascii=False, indent=4)
        registrar_log(f"JSON exportado: {nombre} ({len(registros)} registros)")
        return ruta
    except (OSError, TypeError) as e:
        registrar_log(f"Error exportando JSON: {e}", "ERROR")
        print(f"Error exportando JSON: {e}")
        return None


def exportar_json_generico(datos, nombre):
    """Exporta cualquier estructura serializable (p. ej. resultados de Mongo)."""
    ruta = BASE_DIR / nombre
    try:
        _verificar_ruta_escritura(ruta)
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=4, default=str)
        registrar_log(f"JSON exportado: {nombre}")
        return ruta
    except (OSError, TypeError) as e:
        registrar_log(f"Error exportando JSON: {e}", "ERROR")
        print(f"Error exportando JSON: {e}")
        return None


def importar_json(nombre="datos.json"):
    ruta = localizar_archivo(nombre)
    if ruta is None:
        registrar_log(f"Importacion JSON fallida, no existe: {nombre}", "ERROR")
        print(f"No se encontro el archivo '{nombre}'.")
        return None
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            datos = json.load(f)
        if not isinstance(datos, list) or not all(isinstance(d, dict) for d in datos):
            raise ValueError("El JSON debe ser una lista de objetos")
        registrar_log(f"JSON importado: {ruta.name} ({len(datos)} registros)")
        return datos
    except (OSError, ValueError) as e:  # JSONDecodeError hereda de ValueError
        registrar_log(f"Error importando JSON: {e}", "ERROR")
        print(f"Error importando JSON: {e}")
        return None


def importar_csv(nombre="datos_ordenados.csv"):
    ruta = localizar_archivo(nombre)
    if ruta is None:
        registrar_log(f"Importacion CSV fallida, no existe: {nombre}", "ERROR")
        print(f"No se encontro el archivo '{nombre}'.")
        return None
    try:
        with open(ruta, "r", newline="", encoding="utf-8") as f:
            datos = list(csv.DictReader(f))
        registrar_log(f"CSV importado: {ruta.name} ({len(datos)} registros)")
        return datos
    except (OSError, csv.Error) as e:
        registrar_log(f"Error importando CSV: {e}", "ERROR")
        print(f"Error importando CSV: {e}")
        return None
