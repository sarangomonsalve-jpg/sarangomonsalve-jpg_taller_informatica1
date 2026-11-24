"""Item 1: generacion de registros biomedicos aleatorios y ordenamiento."""
import random


def generar_registros(n=50):
    """Genera n registros con el formato exigido en el taller.

    id   -> 'ID-001'
    fr   -> '18 Años'   (campo de edad, tal como lo nombra el enunciado)
    fc   -> '090ppm'
    spo2 -> '95%'
    """
    if n < 50:
        n = 50  # el enunciado exige al menos 50 registros
    registros = []
    for i in range(1, n + 1):
        registros.append({
            "id": f"ID-{i:03d}",
            "fr": f"{random.randint(18, 90)} Años",
            "fc": f"{random.randint(50, 130):03d}ppm",
            "spo2": f"{random.randint(88, 100)}%",
        })
    return registros


def valor_numerico(texto):
    """Extrae el numero de campos como '090ppm', '95%' o '18 Años'."""
    digitos = "".join(c for c in str(texto) if c.isdigit())
    return int(digitos) if digitos else 0


def merge_sort(lista, clave):
    """Algoritmo de ordenamiento Merge Sort (estable, O(n log n))."""
    if len(lista) <= 1:
        return lista[:]
    medio = len(lista) // 2
    izq = merge_sort(lista[:medio], clave)
    der = merge_sort(lista[medio:], clave)
    resultado, i, j = [], 0, 0
    while i < len(izq) and j < len(der):
        if clave(izq[i]) <= clave(der[j]):
            resultado.append(izq[i])
            i += 1
        else:
            resultado.append(der[j])
            j += 1
    resultado.extend(izq[i:])
    resultado.extend(der[j:])
    return resultado


def ordenar_por_fc(registros, descendente=False):
    """Ordena los registros por frecuencia cardiaca."""
    ordenados = merge_sort(registros, lambda r: valor_numerico(r["fc"]))
    return ordenados[::-1] if descendente else ordenados
