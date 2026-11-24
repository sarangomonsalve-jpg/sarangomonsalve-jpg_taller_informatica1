"""Item 5: integracion de Python con MongoDB Atlas (coleccion 'signos_vitales')."""
import os

from generador import valor_numerico
from sistema import BASE_DIR, registrar_log

try:
    from pymongo import MongoClient
    from pymongo.errors import PyMongoError
except ImportError:  # permite usar el resto del programa sin pymongo
    MongoClient = None

    class PyMongoError(Exception):
        pass

NOMBRE_BD = "taller_informatica1"
NOMBRE_COLECCION = "signos_vitales"


def cargar_env():
    """Lee MONGO_URI desde un archivo .env (si existe) sin dependencias extra."""
    env = BASE_DIR / ".env"
    if env.is_file():
        for linea in env.read_text(encoding="utf-8").splitlines():
            linea = linea.strip()
            if linea and not linea.startswith("#") and "=" in linea:
                k, v = linea.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    return os.environ.get("MONGO_URI")


class GestorMongo:
    def __init__(self):
        self.cliente = None
        self.coleccion = None

    @property
    def conectado(self):
        return self.coleccion is not None

    def conectar(self, uri=None):
        if MongoClient is None:
            print("Falta instalar pymongo: pip install -r requirements.txt")
            return False
        uri = uri or cargar_env()
        if not uri:
            print("No hay MONGO_URI (defínela en .env o como variable de entorno).")
            return False
        try:
            self.cliente = MongoClient(uri, serverSelectionTimeoutMS=8000)
            self.cliente.admin.command("ping")
            self.coleccion = self.cliente[NOMBRE_BD][NOMBRE_COLECCION]
            registrar_log(f"Conexion a MongoDB Atlas exitosa (coleccion {NOMBRE_COLECCION})")
            return True
        except PyMongoError as e:
            self.cliente = self.coleccion = None
            registrar_log(f"Error conectando a MongoDB: {e}", "ERROR")
            print(f"No se pudo conectar a MongoDB: {e}")
            return False

    def insertar_registros(self, registros):
        """Inserta (upsert por id, sin duplicar) los registros ya validados."""
        if not self.conectado:
            print("Primero conectese a MongoDB.")
            return 0
        try:
            n = 0
            for r in registros:
                doc = dict(r)
                # valores numericos para poder consultar (promedio, SpO2 < 94)
                doc["fc_valor"] = valor_numerico(r["fc"])
                doc["spo2_valor"] = valor_numerico(r["spo2"])
                doc["edad_valor"] = valor_numerico(r["fr"])
                self.coleccion.replace_one({"id": doc["id"]}, doc, upsert=True)
                n += 1
            registrar_log(f"Insertados/actualizados {n} documentos en {NOMBRE_COLECCION}")
            return n
        except PyMongoError as e:
            registrar_log(f"Error insertando en MongoDB: {e}", "ERROR")
            print(f"Error insertando: {e}")
            return 0

    def promedio_fc(self):
        try:
            res = list(self.coleccion.aggregate(
                [{"$group": {"_id": None, "promedio": {"$avg": "$fc_valor"}}}]))
            prom = round(res[0]["promedio"], 2) if res else None
            registrar_log(f"Consulta promedio FC = {prom}")
            return prom
        except PyMongoError as e:
            registrar_log(f"Error en promedio FC: {e}", "ERROR")
            print(f"Error en la consulta: {e}")
            return None

    def spo2_menor_a(self, limite=94):
        try:
            docs = list(self.coleccion.find({"spo2_valor": {"$lt": limite}}, {"_id": 0})
                        .sort("spo2_valor", 1))
            registrar_log(f"Consulta SpO2 < {limite}: {len(docs)} documentos")
            return docs
        except PyMongoError as e:
            registrar_log(f"Error en consulta SpO2: {e}", "ERROR")
            print(f"Error en la consulta: {e}")
            return []

    def buscar_por_id(self, id_registro):
        try:
            doc = self.coleccion.find_one({"id": id_registro}, {"_id": 0})
            registrar_log(f"Consulta por ID {id_registro}: {'encontrado' if doc else 'no existe'}")
            return doc
        except PyMongoError as e:
            registrar_log(f"Error buscando ID: {e}", "ERROR")
            print(f"Error en la consulta: {e}")
            return None

    def cerrar(self):
        if self.cliente:
            self.cliente.close()
            registrar_log("Conexion a MongoDB cerrada")
            self.cliente = self.coleccion = None
