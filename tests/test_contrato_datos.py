"""Pruebas del contrato de datos para la rúbrica Build / Test."""
import csv

import pytest

from src import config as C
from scripts.verificar_contrato import (
    COLUMNAS_NUMERICAS, ErrorContrato, convertir_numerico, validar_archivo,
)


def base_de_prueba(tmp_path, alteracion=None):
    ruta = tmp_path / "Base_SAS_Equipo3.csv"
    modelo = {col: "0" for col in COLUMNAS_NUMERICAS}
    modelo.update({"SAVINGS_BALANCE": "25000.50", "YEARS_CREDIT_HISTORY": "8.5"})
    with ruta.open("w", encoding="utf-8", newline="") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=COLUMNAS_NUMERICAS)
        escritor.writeheader()
        for fila in range(C.N_MINIMO):
            registro = modelo.copy()
            registro["DEFAULT"] = str(fila % 2)
            if fila == 0 and alteracion:
                registro.update(alteracion)
            escritor.writerow(registro)
    return ruta


def test_contrato_cubre_las_12_columnas():
    assert len(COLUMNAS_NUMERICAS) == 12
    assert set(COLUMNAS_NUMERICAS) == set(C.COLUMNAS_ESPERADAS)


def test_convierte_numeros_y_marcadores_a_tipo_correcto():
    assert convertir_numerico("25.50", "SAVINGS_BALANCE") == 25.5
    assert convertir_numerico("NA", "FINANCIAL_LITERACY_SCORE") is None
    assert convertir_numerico("", "FINANCIAL_LITERACY_SCORE") is None


def test_base_correcta_pasa(tmp_path):
    resultado = validar_archivo(base_de_prueba(tmp_path))
    assert resultado.filas == C.N_MINIMO
    assert resultado.columnas == 12


def test_texto_en_columna_numerica_bloquea(tmp_path):
    with pytest.raises(ErrorContrato, match="valor no numérico"):
        validar_archivo(base_de_prueba(tmp_path, {"SAVINGS_BALANCE": "NO_ES_UN_NUMERO"}))


def test_objetivo_fuera_de_0_y_1_bloquea(tmp_path):
    with pytest.raises(ErrorContrato, match="solo se admite 0 o 1"):
        validar_archivo(base_de_prueba(tmp_path, {"DEFAULT": "2"}))


def test_vacio_en_columna_critica_bloquea(tmp_path):
    with pytest.raises(ErrorContrato, match="es obligatorio y llegó vacío"):
        validar_archivo(base_de_prueba(tmp_path, {"DEBT_TO_INCOME": "NA"}))


def test_vacio_no_critico_se_convierte_y_reporta(tmp_path):
    resultado = validar_archivo(base_de_prueba(tmp_path, {"FINANCIAL_LITERACY_SCORE": "N/A"}))
    assert resultado.ausencias["FINANCIAL_LITERACY_SCORE"] == 1


def test_base_real_cumple_el_contrato():
    resultado = validar_archivo(C.RUTA_DATOS)
    assert resultado.filas >= C.N_MINIMO
    assert resultado.columnas == 12
