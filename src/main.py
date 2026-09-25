# -*- coding: utf-8 -*-
"""
Punto de entrada del sistema inteligente de rutas del transporte masivo de
Medellín (Metro, Metrocable y Tranvía de Ayacucho).

Uso interactivo:
    python src/main.py

Uso por línea de comandos (sin modo interactivo):
    python src/main.py "San Javier" "Santo Domingo Savio"

El programa:
    1. Carga la base de conocimiento (base_conocimiento.py).
    2. Construye el grafo de conexiones aplicando el motor de reglas
       lógicas (motor_reglas.py).
    3. Calcula la mejor ruta entre el origen y el destino con búsqueda
       heurística A* (busqueda.py).
    4. Imprime la ruta resultante, tramo por tramo, indicando la línea
       usada y avisando los transbordos.
"""

import sys
import unicodedata

from base_conocimiento import obtener_todas_las_estaciones, NOMBRE_LINEA
from motor_reglas import MotorInferencia
from busqueda import buscar_ruta, RutaNoEncontrada


def _normalizar(texto):
    """Quita tildes/mayúsculas para que la búsqueda por nombre de estación
    sea más tolerante a como el usuario la escriba."""
    texto = texto.strip().lower()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return texto


def resolver_nombre_estacion(nombre_usuario, estaciones_validas):
    """Encuentra el nombre 'oficial' de una estación a partir de lo que
    escribió el usuario (tolerante a tildes/mayúsculas). Devuelve None si
    no hay coincidencia."""
    objetivo = _normalizar(nombre_usuario)
    for estacion in estaciones_validas:
        if _normalizar(estacion) == objetivo:
            return estacion
    return None


def imprimir_ruta(resultado, origen, destino):
    print(f"\nRuta óptima: {origen}  ->  {destino}")
    print("-" * 60)
    linea_previa = None
    for tramo in resultado["tramos"]:
        aviso = ""
        if tramo["transbordo"]:
            aviso = f"   <-- TRANSBORDO a {NOMBRE_LINEA[tramo['linea']]}"
        elif linea_previa is None:
            aviso = f"   (se toma {NOMBRE_LINEA[tramo['linea']]})"
        print(f"  {tramo['origen']:28s} -> {tramo['destino']:28s} "
              f"[{tramo['linea']:>2s}]  {tramo['tiempo']:.1f} min{aviso}")
        linea_previa = tramo["linea"]

    print("-" * 60)
    print(f"Estaciones recorridas : {len(resultado['estaciones'])}")
    print(f"Transbordos           : {resultado['numero_transbordos']}")
    print(f"Tiempo total estimado : {resultado['tiempo_total']:.1f} minutos")


def calcular_ruta(origen_usuario, destino_usuario):
    """Función de alto nivel reutilizable desde pruebas y desde el script
    que genera el PDF de pruebas: recibe dos nombres de estación (tal cual
    los escribe un usuario) y devuelve el resultado de buscar_ruta, ya con
    los nombres oficiales resueltos."""
    motor = MotorInferencia()
    grafo = motor.construir_grafo()
    estaciones_validas = obtener_todas_las_estaciones()

    origen = resolver_nombre_estacion(origen_usuario, estaciones_validas)
    destino = resolver_nombre_estacion(destino_usuario, estaciones_validas)
    if origen is None:
        raise RutaNoEncontrada(f"No se reconoce la estación de origen '{origen_usuario}'.")
    if destino is None:
        raise RutaNoEncontrada(f"No se reconoce la estación de destino '{destino_usuario}'.")

    resultado = buscar_ruta(grafo, origen, destino)
    return origen, destino, resultado


def main():
    if len(sys.argv) == 3:
        origen_usuario, destino_usuario = sys.argv[1], sys.argv[2]
    else:
        print("Sistema inteligente de rutas - Metro de Medellín")
        print("(escribe 'salir' en el origen para terminar)\n")
        origen_usuario = input("Estación de origen : ")
        if _normalizar(origen_usuario) == "salir":
            return
        destino_usuario = input("Estación de destino: ")

    try:
        origen, destino, resultado = calcular_ruta(origen_usuario, destino_usuario)
        imprimir_ruta(resultado, origen, destino)
    except RutaNoEncontrada as error:
        print(f"\n[ERROR] {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
