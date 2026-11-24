"""Item 3: herramientas del sistema (os, pathlib, io): carpetas, movimiento de archivos y log."""
import os
import shutil
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
SUBCARPETAS = {
    ".txt": DATA_DIR / "txt",
    ".csv": DATA_DIR / "csv",
    ".json": DATA_DIR / "json",
}
LOG_FILE = BASE_DIR / "log.txt"
PROTEGIDOS = {"log.txt", "requirements.txt"}  # nunca se mueven


def registrar_log(accion, nivel="INFO"):
    """Agrega una linea con fecha/hora a log.txt."""
    try:
        marca = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{marca}] [{nivel}] {accion}\n")
    except OSError as e:
        print(f"No se pudo escribir en el log: {e}")


def crear_estructura():
    """Crea data/txt, data/csv y data/json si no existen."""
    for carpeta in SUBCARPETAS.values():
        try:
            carpeta.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            registrar_log(f"Error creando {carpeta}: {e}", "ERROR")
            raise
    registrar_log("Estructura de carpetas verificada: " + ", ".join(
        str(c.relative_to(BASE_DIR)) for c in SUBCARPETAS.values()))


def organizar_archivos():
    """Mueve los .txt/.csv/.json generados en la raiz a su carpeta data/<ext>."""
    crear_estructura()
    movidos = []
    for archivo in BASE_DIR.iterdir():
        if not archivo.is_file() or archivo.name in PROTEGIDOS:
            continue
        destino_dir = SUBCARPETAS.get(archivo.suffix.lower())
        if destino_dir is None:
            continue
        destino = destino_dir / archivo.name
        try:
            if destino.exists():
                destino.unlink()
            shutil.move(str(archivo), str(destino))
            movidos.append(destino)
            registrar_log(f"Archivo movido: {archivo.name} -> {destino.relative_to(BASE_DIR)}")
        except (OSError, shutil.Error) as e:
            registrar_log(f"Error moviendo {archivo.name}: {e}", "ERROR")
    return movidos


def localizar_archivo(nombre):
    """Busca un archivo en la raiz o en data/<ext>. Devuelve Path o None."""
    candidatos = [BASE_DIR / nombre]
    carpeta = SUBCARPETAS.get(Path(nombre).suffix.lower())
    if carpeta:
        candidatos.append(carpeta / nombre)
    candidatos.append(Path(nombre))
    for c in candidatos:
        if os.path.isfile(c):
            return c
    return None
