"""Verifica el contrato del CSV sin modificar la base ni las pantallas.

Ejecutar: python -m scripts.verificar_contrato data/Base_SAS_Equipo3.csv
Un error termina con código de salida 1, útil para GitHub Actions.
"""
from __future__ import annotations

import argparse
import csv
import math
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from src import config as C


# Son convenciones de lectura, no afirmaciones de que todos aparezcan en el CSV.
MARCADORES_AUSENCIA = frozenset({"", "NA", "N/A", "NULL", "NONE", "NAN", "?", "-", "S/D"})
COLUMNAS_NUMERICAS = tuple(C.COLUMNAS_ESPERADAS)
COLUMNAS_ENTERAS = frozenset({"MISSED_PAYMENTS_12M", "DELINQ_90", "BANKRUPTCY_FLAG", "DEFAULT"})
COLUMNAS_BINARIAS = frozenset({"BANKRUPTCY_FLAG", "DEFAULT"})
COLUMNAS_OBLIGATORIAS = frozenset({C.OBJETIVO, *C.VARIABLES_CLAVE})


class ErrorContrato(ValueError):
    """El CSV no cumple una regla bloqueante del contrato de datos."""


@dataclass(frozen=True)
class Resultado:
    filas: int
    columnas: int
    ausencias: dict[str, int]


def convertir_numerico(texto: str | None, columna: str) -> float | None:
    """Convierte una celda numérica; un token desconocido nunca pasa como texto."""
    valor = "" if texto is None else str(texto).strip()
    if valor.upper() in MARCADORES_AUSENCIA:
        return None
    try:
        numero = float(valor)
    except (TypeError, ValueError) as exc:
        raise ErrorContrato(f"{columna}: valor no numérico {valor[:40]!r}") from exc
    if not math.isfinite(numero):
        raise ErrorContrato(f"{columna}: valor no finito {valor[:40]!r}")
    if columna in COLUMNAS_ENTERAS and not numero.is_integer():
        raise ErrorContrato(f"{columna}: se esperaba un entero, llegó {valor[:40]!r}")
    if columna in COLUMNAS_BINARIAS and numero not in (0.0, 1.0):
        raise ErrorContrato(f"{columna}: solo se admite 0 o 1, llegó {valor[:40]!r}")
    return numero


def validar_archivo(ruta: Path) -> Resultado:
    """Valida encabezados, tipos, ausencias críticas y mínimo de registros."""
    ruta = Path(ruta)
    if not ruta.is_file():
        raise ErrorContrato(f"No existe el CSV: {ruta}")
    errores: list[str] = []
    ausencias: Counter[str] = Counter()
    filas = 0
    try:
        with ruta.open("r", encoding="utf-8-sig", newline="") as archivo:
            lector = csv.DictReader(archivo)
            encabezados = lector.fieldnames or []
            faltantes = [c for c in COLUMNAS_NUMERICAS if c not in encabezados]
            extras = [c for c in encabezados if c not in COLUMNAS_NUMERICAS]
            repetidos = [c for c, n in Counter(encabezados).items() if n > 1]
            if faltantes or extras or repetidos:
                raise ErrorContrato(
                    f"Esquema inválido. Faltan: {faltantes}; extras: {extras}; repetidas: {repetidos}"
                )
            for num_fila, registro in enumerate(lector, start=2):
                filas += 1
                if None in registro:
                    errores.append(f"Fila {num_fila}: contiene más campos que el encabezado")
                for columna in COLUMNAS_NUMERICAS:
                    try:
                        numero = convertir_numerico(registro.get(columna), columna)
                    except ErrorContrato as exc:
                        errores.append(f"Fila {num_fila}: {exc}")
                        continue
                    if numero is None:
                        ausencias[columna] += 1
                        if columna in COLUMNAS_OBLIGATORIAS:
                            errores.append(f"Fila {num_fila}: {columna} es obligatorio y llegó vacío")
                if len(errores) >= 15:
                    break
    except UnicodeError as exc:
        raise ErrorContrato("El archivo no tiene codificación UTF-8 válida") from exc

    if filas < C.N_MINIMO:
        errores.append(f"Solo hay {filas} filas; se requieren al menos {C.N_MINIMO}")
    if errores:
        raise ErrorContrato("FALLO DEL CONTRATO DE DATOS:\n- " + "\n- ".join(errores))
    return Resultado(filas, len(COLUMNAS_NUMERICAS), dict(ausencias))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verifica los tipos de la base de AutoCredit Advisor")
    parser.add_argument("ruta", nargs="?", type=Path, default=C.RUTA_DATOS)
    args = parser.parse_args(argv)
    try:
        resultado = validar_archivo(args.ruta)
    except ErrorContrato as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"OK: {resultado.filas:,} filas; {resultado.columnas} columnas numéricas verificadas.")
    if resultado.ausencias:
        print("Ausencias no críticas convertidas a None:", resultado.ausencias)
    else:
        print("No se encontraron marcadores de ausencia en las columnas validadas.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
