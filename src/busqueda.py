# -*- coding: utf-8 -*-
"""
Búsqueda heurística (algoritmo A*) sobre el grafo de conexiones derivado
por el motor de reglas (ver Benítez, 2014, cap. 9 "Técnicas basadas en
búsquedas heurísticas").

La "mejor ruta" entre un punto A y un punto B se define como la ruta de
MENOR TIEMPO TOTAL DE VIAJE, donde el tiempo total incluye:
  - el tiempo de cada tramo entre estaciones consecutivas (hechos
    "conexion" inferidos por el motor de reglas), y
  - una penalización fija (TIEMPO_TRANSBORDO) cada vez que la ruta cambia
    de línea en una estación de transbordo.

A* combina el costo real acumulado g(n) con una heurística admisible h(n)
que estima (sin sobrestimar) el costo restante hasta el destino, usando la
distancia en línea recta entre las coordenadas esquemáticas de las
estaciones (ver base_conocimiento.COORDENADAS).
"""

import heapq
import math

from base_conocimiento import COORDENADAS, TIEMPO_TRANSBORDO


def distancia_euclidiana(a, b):
    (x1, y1), (x2, y2) = a, b
    return math.hypot(x2 - x1, y2 - y1)


def calcular_factor_heuristico(grafo, coordenadas):
    """
    Calcula automáticamente el factor (minutos por unidad de distancia
    esquemática) más pequeño observado entre todas las conexiones directas
    del grafo. Usar este factor mínimo para estimar el costo restante
    garantiza que la heurística NUNCA sobrestime el costo real, es decir,
    que sea ADMISIBLE (condición necesaria para que A* encuentre la ruta
    óptima).
    """
    factor_minimo = float("inf")
    for origen, vecinos in grafo.items():
        for destino, datos in vecinos.items():
            d = distancia_euclidiana(coordenadas[origen], coordenadas[destino])
            if d > 0:
                factor_minimo = min(factor_minimo, datos["tiempo"] / d)
    if factor_minimo == float("inf"):
        factor_minimo = 0.0
    return factor_minimo


class RutaNoEncontrada(Exception):
    pass


def buscar_ruta(grafo, origen, destino, coordenadas=None):
    """
    Ejecuta A* sobre 'grafo' (ver MotorInferencia.construir_grafo) y
    devuelve un diccionario con:
        "estaciones": lista de estaciones en la ruta óptima, en orden.
        "tramos": lista de dicts {origen, destino, linea, tiempo, transbordo}
        "tiempo_total": tiempo total estimado en minutos.
        "numero_transbordos": cantidad de cambios de línea en la ruta.
    Lanza RutaNoEncontrada si no existe camino entre origen y destino, o si
    alguna de las dos estaciones no existe en el grafo.
    """
    coordenadas = coordenadas or COORDENADAS

    if origen not in grafo:
        raise RutaNoEncontrada(f"La estación de origen '{origen}' no existe en el sistema.")
    if destino not in grafo:
        raise RutaNoEncontrada(f"La estación de destino '{destino}' no existe en el sistema.")

    factor_h = calcular_factor_heuristico(grafo, coordenadas)

    def h(nodo):
        return distancia_euclidiana(coordenadas[nodo], coordenadas[destino]) * factor_h

    # Estado de A*: (f_score, contador, nodo, linea_de_llegada)
    # 'linea_de_llegada' se necesita porque el costo de un tramo depende de
    # si la línea cambia respecto al tramo anterior (penalización de
    # transbordo), por lo que el mismo nodo puede reabrirse con distinta
    # "línea actual".
    contador = 0
    origen_estado = (origen, None)
    g_score = {origen_estado: 0.0}
    f_inicial = h(origen)
    frontera = [(f_inicial, contador, origen_estado)]
    procedencia = {}  # estado -> (estado_anterior, linea_usada)
    visitados = set()

    estado_final = None
    while frontera:
        f_actual, _, estado_actual = heapq.heappop(frontera)
        nodo_actual, linea_actual = estado_actual

        if estado_actual in visitados:
            continue
        visitados.add(estado_actual)

        if nodo_actual == destino:
            estado_final = estado_actual
            break

        for vecino, datos in grafo.get(nodo_actual, {}).items():
            linea_tramo = datos["linea"]
            costo_tramo = datos["tiempo"]
            if linea_actual is not None and linea_tramo != linea_actual:
                costo_tramo += TIEMPO_TRANSBORDO

            nuevo_g = g_score[estado_actual] + costo_tramo
            estado_vecino = (vecino, linea_tramo)

            if nuevo_g < g_score.get(estado_vecino, float("inf")):
                g_score[estado_vecino] = nuevo_g
                procedencia[estado_vecino] = (estado_actual, linea_tramo)
                contador += 1
                f_score = nuevo_g + h(vecino)
                heapq.heappush(frontera, (f_score, contador, estado_vecino))

    if estado_final is None:
        raise RutaNoEncontrada(f"No existe una ruta entre '{origen}' y '{destino}'.")

    # Reconstrucción de la ruta a partir de 'procedencia'
    tramos_inv = []
    estado = estado_final
    while estado in procedencia:
        estado_anterior, linea_usada = procedencia[estado]
        tramos_inv.append({
            "origen": estado_anterior[0],
            "destino": estado[0],
            "linea": linea_usada,
        })
        estado = estado_anterior
    tramos = list(reversed(tramos_inv))

    # Anotar transbordos y tiempos por tramo
    linea_previa = None
    tiempo_total = 0.0
    numero_transbordos = 0
    for tramo in tramos:
        datos = grafo[tramo["origen"]][tramo["destino"]]
        tiempo_tramo = datos["tiempo"]
        es_transbordo = linea_previa is not None and tramo["linea"] != linea_previa
        if es_transbordo:
            tiempo_tramo += TIEMPO_TRANSBORDO
            numero_transbordos += 1
        tramo["tiempo"] = tiempo_tramo
        tramo["transbordo"] = es_transbordo
        tiempo_total += tiempo_tramo
        linea_previa = tramo["linea"]

    estaciones = [origen] + [t["destino"] for t in tramos]

    return {
        "estaciones": estaciones,
        "tramos": tramos,
        "tiempo_total": round(tiempo_total, 1),
        "numero_transbordos": numero_transbordos,
    }
