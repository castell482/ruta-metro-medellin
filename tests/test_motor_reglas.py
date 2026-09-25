# -*- coding: utf-8 -*-
"""Pruebas del motor de reglas: verifica que las reglas lógicas infieran
correctamente las conexiones y los puntos de transbordo esperados."""
from motor_reglas import MotorInferencia


def test_conexion_directa_misma_linea():
    motor = MotorInferencia()
    grafo = motor.construir_grafo()
    # San Antonio y Parque Berrío son consecutivas en la Línea A
    assert "Parque Berrío" in grafo["San Antonio"]
    assert grafo["San Antonio"]["Parque Berrío"]["linea"] == "A"


def test_conexion_es_bidireccional():
    motor = MotorInferencia()
    grafo = motor.construir_grafo()
    assert "San Antonio" in grafo["Parque Berrío"]
    assert "Parque Berrío" in grafo["San Antonio"]


def test_estaciones_no_adyacentes_no_conectadas_directamente():
    motor = MotorInferencia()
    grafo = motor.construir_grafo()
    # Niquía y La Estrella son los extremos opuestos de la Línea A
    assert "La Estrella" not in grafo["Niquía"]


def test_puntos_de_transbordo_inferidos_correctamente():
    motor = MotorInferencia()
    transbordos = motor.estaciones_de_transbordo()
    esperados = {
        "San Antonio", "Acevedo", "San Javier",
        "Santo Domingo Savio", "Miraflores", "Oriente",
    }
    assert esperados.issubset(transbordos)


def test_estacion_normal_no_es_transbordo():
    motor = MotorInferencia()
    transbordos = motor.estaciones_de_transbordo()
    assert "Poblado" not in transbordos
    assert "Villa Sierra" not in transbordos


def test_lineas_de_estacion_transbordo():
    motor = MotorInferencia()
    motor.inferir()
    assert motor.lineas_de("San Antonio") == {"A", "B", "TA"}
    assert motor.lineas_de("Acevedo") == {"A", "K", "P"}
