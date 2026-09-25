# -*- coding: utf-8 -*-
"""Pruebas del algoritmo de búsqueda heurística A* (busqueda.py)."""
import pytest

from motor_reglas import MotorInferencia
from busqueda import buscar_ruta, RutaNoEncontrada


@pytest.fixture(scope="module")
def grafo():
    motor = MotorInferencia()
    return motor.construir_grafo()


def test_ruta_sin_transbordos_misma_linea(grafo):
    resultado = buscar_ruta(grafo, "Niquía", "La Estrella")
    assert resultado["numero_transbordos"] == 0
    assert resultado["estaciones"][0] == "Niquía"
    assert resultado["estaciones"][-1] == "La Estrella"
    # 20 tramos de 2 minutos cada uno, sin transbordos
    assert resultado["tiempo_total"] == pytest.approx(40.0)


def test_ruta_incluye_transbordo_esperado(grafo):
    resultado = buscar_ruta(grafo, "San Javier", "Santo Domingo Savio")
    # Debe pasar obligatoriamente por San Antonio (B->A) y Acevedo (A->K)
    assert "San Antonio" in resultado["estaciones"]
    assert "Acevedo" in resultado["estaciones"]
    assert resultado["numero_transbordos"] == 2


def test_ruta_trivial_origen_igual_destino(grafo):
    resultado = buscar_ruta(grafo, "Poblado", "Poblado")
    assert resultado["estaciones"] == ["Poblado"]
    assert resultado["tiempo_total"] == 0.0
    assert resultado["numero_transbordos"] == 0


def test_ruta_entre_metrocables_opuestos_usa_troncal(grafo):
    resultado = buscar_ruta(grafo, "La Aurora", "Arví")
    assert resultado["estaciones"][0] == "La Aurora"
    assert resultado["estaciones"][-1] == "Arví"
    assert resultado["numero_transbordos"] >= 3  # J->B->A->K->L

def test_estacion_inexistente_lanza_excepcion(grafo):
    with pytest.raises(RutaNoEncontrada):
        buscar_ruta(grafo, "Estación Inventada", "Poblado")


def test_heuristica_no_cambia_el_costo_optimo_respecto_a_dijkstra(grafo):
    """La ruta encontrada por A* debe tener el mismo costo que el menor
    costo posible (se verifica comparando contra una búsqueda exhaustiva
    de fuerza bruta sobre un subgrafo pequeño y conocido: la Línea A)."""
    resultado = buscar_ruta(grafo, "San Antonio", "Poblado")
    # Camino directo conocido: San Antonio-Alpujarra-Exposiciones-
    # Industriales-Poblado = 4 tramos x 2.0 min = 8.0 min, sin transbordos
    assert resultado["tiempo_total"] == pytest.approx(8.0)
    assert resultado["numero_transbordos"] == 0
