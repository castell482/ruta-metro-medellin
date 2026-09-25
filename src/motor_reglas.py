# -*- coding: utf-8 -*-
"""
Motor de inferencia basado en reglas lógicas (encadenamiento hacia adelante).

Este módulo representa el conocimiento del dominio como HECHOS (tuplas) y
aplica REGLAS lógicas de la forma "SI <condición> ENTONCES <se infiere un
nuevo hecho>" hasta alcanzar un punto fijo (ya no se pueden derivar hechos
nuevos). Es una implementación simple de un sistema experto basado en
reglas (ver Benítez, 2014, cap. 2 "Lógica y representación del
conocimiento" y cap. 3 "Sistemas basados en reglas").

Hechos que maneja el motor:
    ("pertenece", estacion, linea)
        Hecho base: la estación pertenece a esa línea (se carga desde
        base_conocimiento.LINEAS).
    ("conexion", origen, destino, linea, tiempo)
        Hecho inferido por la Regla 1: existe una conexión directa (un
        tramo) entre "origen" y "destino" dentro de la misma línea, con un
        tiempo de viaje en minutos.
    ("transbordo", estacion)
        Hecho inferido por la Regla 2: la estación permite cambiar de línea
        porque pertenece a 2 o más líneas distintas.

El motor NO decide la ruta: solo construye, a partir de las reglas, el
grafo de conexiones (nodos = estaciones, aristas = hechos "conexion"). La
búsqueda de la mejor ruta la realiza el módulo busqueda.py con el algoritmo
A* (búsqueda heurística), consumiendo estos hechos.
"""

from base_conocimiento import LINEAS, TIPO_LINEA, TIEMPO_POR_TRAMO


class MotorInferencia:
    """Motor de encadenamiento hacia adelante (forward chaining)."""

    def __init__(self, lineas=None, tipo_linea=None, tiempo_por_tramo=None):
        self.lineas = lineas or LINEAS
        self.tipo_linea = tipo_linea or TIPO_LINEA
        self.tiempo_por_tramo = tiempo_por_tramo or TIEMPO_POR_TRAMO
        self.hechos = set()
        self._reglas = [
            self._regla_1_conexion_misma_linea,
            self._regla_2_punto_transbordo,
        ]
        self._cargar_hechos_base()

    # ---------------------- hechos base ----------------------------------
    def _cargar_hechos_base(self):
        """Hecho base: 'pertenece(estacion, linea)' para cada línea."""
        for linea, estaciones in self.lineas.items():
            for estacion in estaciones:
                self.hechos.add(("pertenece", estacion, linea))

    # ---------------------- reglas -----------------------------------
    def _regla_1_conexion_misma_linea(self):
        """
        Regla 1 (adyacencia):
        SI la estación E2 aparece inmediatamente después de E1 en la lista
           ordenada de estaciones de una línea L
        ENTONCES existe una conexión directa E1 <-> E2 por la línea L, con
           un tiempo de viaje igual al tiempo de referencia del tipo de
           línea L.
        """
        nuevos = set()
        for linea, estaciones in self.lineas.items():
            tipo = self.tipo_linea[linea]
            tiempo = self.tiempo_por_tramo[tipo]
            for i in range(len(estaciones) - 1):
                origen, destino = estaciones[i], estaciones[i + 1]
                nuevos.add(("conexion", origen, destino, linea, tiempo))
                nuevos.add(("conexion", destino, origen, linea, tiempo))
        return nuevos

    def _regla_2_punto_transbordo(self):
        """
        Regla 2 (transbordo):
        SI una estación E tiene 2 o más hechos ("pertenece", E, L)  con L
           distintas
        ENTONCES E es un punto de transbordo: infiere ("transbordo", E).
        """
        lineas_por_estacion = {}
        for hecho in self.hechos:
            if hecho[0] == "pertenece":
                _, estacion, linea = hecho
                lineas_por_estacion.setdefault(estacion, set()).add(linea)

        nuevos = set()
        for estacion, lineas in lineas_por_estacion.items():
            if len(lineas) >= 2:
                nuevos.add(("transbordo", estacion))
        return nuevos

    # ---------------------- ciclo de inferencia ---------------------------
    def inferir(self):
        """Aplica las reglas repetidamente hasta que no se generen hechos
        nuevos (punto fijo). Devuelve el conjunto final de hechos."""
        cambiado = True
        while cambiado:
            cambiado = False
            for regla in self._reglas:
                nuevos = regla()
                si_nuevos = nuevos - self.hechos
                if si_nuevos:
                    self.hechos |= si_nuevos
                    cambiado = True
        return self.hechos

    # ---------------------- consultas sobre los hechos ---------------------
    def construir_grafo(self):
        """
        A partir de los hechos ("conexion", ...) ya inferidos, construye un
        grafo de adyacencia:
            grafo[estacion] = { estacion_vecina: {"linea": L, "tiempo": t}, ... }
        Si dos estaciones están conectadas por más de una línea (caso
        excepcional), se conserva el tramo de menor tiempo.
        """
        self.inferir()
        grafo = {}
        for hecho in self.hechos:
            if hecho[0] != "conexion":
                continue
            _, origen, destino, linea, tiempo = hecho
            grafo.setdefault(origen, {})
            grafo.setdefault(destino, {})
            actual = grafo[origen].get(destino)
            if actual is None or tiempo < actual["tiempo"]:
                grafo[origen][destino] = {"linea": linea, "tiempo": tiempo}
        return grafo

    def estaciones_de_transbordo(self):
        """Devuelve el conjunto de estaciones marcadas como transbordo."""
        self.inferir()
        return {h[1] for h in self.hechos if h[0] == "transbordo"}

    def lineas_de(self, estacion):
        """Devuelve el conjunto de líneas a las que pertenece una estación."""
        return {h[2] for h in self.hechos if h[0] == "pertenece" and h[1] == estacion}
