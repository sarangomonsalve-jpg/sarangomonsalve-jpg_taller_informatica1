"""Item 6: integracion final. Menu principal del sistema de signos vitales."""
from archivos import (exportar_json, exportar_json_generico, guardar_csv,
                      guardar_txt, importar_csv, importar_json)
from generador import generar_registros, ordenar_por_fc
from mongo_db import GestorMongo
from sistema import crear_estructura, organizar_archivos, registrar_log
from validacion import EJEMPLOS, validar_campo, validar_lista

MENU = """
========== SIGNOS VITALES ==========
 1. Generar registros aleatorios (>= 50) y ordenar por FC
 2. Ingresar un registro manualmente
 3. Ver registros en memoria
 4. Validar datos (expresiones regulares)
 5. Guardar datos en TXT y CSV
 6. Exportar datos a JSON
 7. Importar datos (JSON o CSV)
 8. Organizar archivos en /data
 9. Conectar a MongoDB Atlas e insertar registros validados
10. Consultas MongoDB (promedio FC y SpO2 < 94) -> resultados_mongo.json
11. Consultar un registro en MongoDB por ID
 0. Salir
====================================
"""

NOMBRES = {"id": "ID", "fr": "Edad (fr)", "fc": "Frecuencia cardiaca", "spo2": "SpO2"}


def mostrar(registros, limite=None):
    if not registros:
        print("No hay registros en memoria.")
        return
    print(f"{'ID':<8}{'fr':<10}{'fc':<9}{'spo2':<6}")
    for r in registros[:limite]:
        print(f"{r.get('id', '?'):<8}{r.get('fr', '?'):<10}{r.get('fc', '?'):<9}{r.get('spo2', '?'):<6}")
    print(f"Total: {len(registros)} registros")


def ingresar_registro(registros):
    nuevo = {}
    for campo in ("id", "fr", "fc", "spo2"):
        while True:
            valor = input(f"{NOMBRES[campo]} (ej. {EJEMPLOS[campo]}): ").strip()
            if not validar_campo(campo, valor):
                print(f"  Formato invalido, use por ejemplo {EJEMPLOS[campo]!r}")
            elif campo == "id" and any(r.get("id") == valor for r in registros):
                print("  Ese ID ya existe.")
            else:
                nuevo[campo] = valor
                break
    registros.append(nuevo)
    registros[:] = ordenar_por_fc(registros)
    registrar_log(f"Registro ingresado manualmente: {nuevo['id']}")
    print("Registro agregado y datos reordenados por FC.")


def validar(registros):
    validos, invalidos = validar_lista(registros)
    print(f"Validos: {len(validos)} | Invalidos: {len(invalidos)}")
    for reg, errores in invalidos:
        print(f"  {reg.get('id', '?')}: " + "; ".join(errores))
    registrar_log(f"Validacion: {len(validos)} validos, {len(invalidos)} invalidos")
    return validos


def main():
    crear_estructura()
    registrar_log("Programa iniciado")
    registros = []
    mongo = GestorMongo()

    while True:
        print(MENU)
        op = input("Seleccione una opcion: ").strip()

        if op == "1":
            try:
                n = int(input("Cantidad de registros (minimo 50) [50]: ") or 50)
            except ValueError:
                n = 50
            registros = ordenar_por_fc(generar_registros(n))
            registrar_log(f"Generados {len(registros)} registros y ordenados por FC")
            mostrar(registros, 10)
            print("(mostrando los primeros 10, ordenados por FC)")
        elif op == "2":
            ingresar_registro(registros)
        elif op == "3":
            mostrar(registros)
        elif op == "4":
            validar(registros)
        elif op == "5":
            if not registros:
                print("No hay datos. Genere o importe registros primero.")
                continue
            guardar_txt(registros)
            guardar_csv(registros)
            for p in organizar_archivos():
                print("Guardado:", p)
        elif op == "6":
            if not registros:
                print("No hay datos para exportar.")
                continue
            exportar_json(registros)
            for p in organizar_archivos():
                print("Guardado:", p)
        elif op == "7":
            tipo = input("Formato a importar (json/csv) [json]: ").strip().lower() or "json"
            if tipo == "csv":
                nombre = input("Nombre del archivo [datos_ordenados.csv]: ").strip() or "datos_ordenados.csv"
                datos = importar_csv(nombre)
            else:
                nombre = input("Nombre del archivo [datos.json]: ").strip() or "datos.json"
                datos = importar_json(nombre)
            if datos is not None:
                validos = validar(datos)
                registros = ordenar_por_fc(validos)
                print(f"Se cargaron {len(registros)} registros validos.")
        elif op == "8":
            movidos = organizar_archivos()
            print(f"{len(movidos)} archivo(s) organizados." if movidos else "No hay archivos por mover.")
        elif op == "9":
            if not registros:
                print("No hay datos. Genere o importe registros primero.")
                continue
            if not mongo.conectado and not mongo.conectar():
                continue
            validos = validar(registros)
            print(f"{mongo.insertar_registros(validos)} documentos insertados en 'signos_vitales'.")
        elif op == "10":
            if not mongo.conectado and not mongo.conectar():
                continue
            promedio = mongo.promedio_fc()
            bajos = mongo.spo2_menor_a(94)
            print(f"Promedio de frecuencia cardiaca: {promedio} ppm")
            print(f"Documentos con SpO2 < 94: {len(bajos)}")
            mostrar(bajos)
            exportar_json_generico({
                "promedio_frecuencia_cardiaca": promedio,
                "spo2_menor_a_94": bajos,
            }, "resultados_mongo.json")
            organizar_archivos()
            print("Resultados exportados a data/json/resultados_mongo.json")
        elif op == "11":
            if not mongo.conectado and not mongo.conectar():
                continue
            id_reg = input("ID a consultar (ej. ID-001): ").strip().upper()
            if not validar_campo("id", id_reg):
                print("Formato de ID invalido.")
                continue
            doc = mongo.buscar_por_id(id_reg)
            print(doc if doc else "No existe un documento con ese ID.")
        elif op == "0":
            mongo.cerrar()
            registrar_log("Programa finalizado")
            print("Hasta luego.")
            break
        else:
            print("Opcion invalida.")


if __name__ == "__main__":
    main()
