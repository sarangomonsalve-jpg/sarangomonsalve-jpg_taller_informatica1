"""Item 4: validacion de campos con expresiones regulares."""
import re

PATRONES = {
    "id": re.compile(r"^ID-\d{3}$"),            # ID-001
    "fr": re.compile(r"^\d{1,3} Años$"),        # 18 Años
    "fc": re.compile(r"^\d{3}ppm$"),            # 090ppm
    "spo2": re.compile(r"^(100|\d{2})%$"),      # 95%
}

EJEMPLOS = {"id": "ID-001", "fr": "18 Años", "fc": "090ppm", "spo2": "95%"}


def validar_campo(campo, valor):
    patron = PATRONES.get(campo)
    return bool(patron and isinstance(valor, str) and patron.fullmatch(valor))


def validar_registro(registro):
    """Devuelve (es_valido, lista_de_errores)."""
    errores = []
    for campo in PATRONES:
        if campo not in registro:
            errores.append(f"Falta el campo '{campo}'")
        elif not validar_campo(campo, registro[campo]):
            errores.append(
                f"Campo '{campo}' invalido: {registro[campo]!r} (ejemplo: {EJEMPLOS[campo]!r})"
            )
    return (not errores), errores


def validar_lista(registros):
    """Separa una lista en (validos, invalidos). invalidos = [(registro, errores)]."""
    validos, invalidos = [], []
    for reg in registros:
        ok, errores = validar_registro(reg)
        if ok:
            validos.append(reg)
        else:
            invalidos.append((reg, errores))
    return validos, invalidos
