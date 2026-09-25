# -*- coding: utf-8 -*-
"""
Base de conocimiento del sistema de transporte masivo de Medellín
(Metro, Metrocable y Tranvía de Ayacucho).

Este módulo NO contiene lógica de inferencia ni de búsqueda: solo declara
los HECHOS del dominio (líneas, estaciones, tipo de línea, coordenadas
esquemáticas y tiempos de referencia). El motor de reglas (motor_reglas.py)
usa estos hechos para derivar, mediante reglas lógicas, el grafo de
conexiones que luego consume el algoritmo de búsqueda heurística
(busqueda.py).

Fuente de la topología de líneas y estaciones: Metro de Medellín / artículos
de referencia sobre el Metro, Metrocable y Tranvía de Ayacucho (2026).

Las coordenadas (COORDENADAS) son ESQUEMÁTICAS, no coordenadas GPS reales:
se construyeron para representar, de forma aproximada, la disposición
geográfica relativa de las líneas (Línea A en sentido norte-sur por el
valle, Línea B de oriente a occidente, los Metrocables ascendiendo hacia
las laderas) con el único fin de poder calcular una heurística de distancia
en línea recta para el algoritmo A* (ver busqueda.py). No deben usarse como
coordenadas reales de navegación.
"""

# ---------------------------------------------------------------------------
# 1. Líneas del sistema y sus estaciones, en orden, de un extremo a otro.
# ---------------------------------------------------------------------------
LINEAS = {
    "A": [  # Metro - La Estrella <-> Niquía
        "La Estrella", "Sabaneta", "Itagüí", "Envigado", "Ayurá", "Aguacatala",
        "Poblado", "Industriales", "Exposiciones", "Alpujarra", "San Antonio",
        "Parque Berrío", "Prado", "Hospital", "Universidad", "Caribe",
        "Tricentenario", "Acevedo", "Madera", "Bello", "Niquía",
    ],
    "B": [  # Metro - San Javier <-> San Antonio
        "San Javier", "Santa Lucía", "Floresta", "Estadio", "Suramericana",
        "Cisneros", "San Antonio",
    ],
    "K": [  # Metrocable - Acevedo <-> Santo Domingo Savio
        "Acevedo", "Andalucía", "Popular", "Santo Domingo Savio",
    ],
    "P": [  # Metrocable - Acevedo <-> El Progreso
        "Acevedo", "SENA", "Doce de Octubre", "El Progreso",
    ],
    "L": [  # Metrocable - Santo Domingo Savio <-> Arví
        "Santo Domingo Savio", "Arví",
    ],
    "J": [  # Metrocable - San Javier <-> La Aurora
        "San Javier", "Juan XXIII", "Vallejuelos", "La Aurora",
    ],
    "TA": [  # Tranvía de Ayacucho - San Antonio <-> Oriente
        "San Antonio", "San José", "Pabellón del Agua EPM", "Bicentenario",
        "Buenos Aires", "Miraflores", "Loyola", "Alejandro Echavarría",
        "Oriente",
    ],
    "M": [  # Metrocable - Miraflores <-> Trece de Noviembre
        "Miraflores", "El Pinal", "Trece de Noviembre",
    ],
    "H": [  # Metrocable - Oriente <-> Villa Sierra
        "Oriente", "Las Torres", "Villa Sierra",
    ],
}

# ---------------------------------------------------------------------------
# 2. Tipo de tecnología de cada línea (afecta el tiempo promedio por tramo).
# ---------------------------------------------------------------------------
TIPO_LINEA = {
    "A": "metro", "B": "metro",
    "K": "metrocable", "P": "metrocable", "L": "metrocable",
    "J": "metrocable", "M": "metrocable", "H": "metrocable",
    "TA": "tranvia",
}

NOMBRE_LINEA = {
    "A": "Línea A (metro)", "B": "Línea B (metro)",
    "K": "Línea K (metrocable)", "P": "Línea P (metrocable)",
    "L": "Línea L (metrocable)", "J": "Línea J (metrocable)",
    "M": "Línea M (metrocable)", "H": "Línea H (metrocable)",
    "TA": "Tranvía de Ayacucho",
}

# ---------------------------------------------------------------------------
# 3. Tiempos de referencia (minutos), usados por el motor de reglas para
#    calcular el costo de cada conexión.
# ---------------------------------------------------------------------------
TIEMPO_POR_TRAMO = {
    "metro": 2.0,       # minutos promedio entre dos estaciones consecutivas
    "metrocable": 3.0,  # los cables son más lentos por tramo
    "tranvia": 2.0,
}
TIEMPO_TRANSBORDO = 4.0  # minutos de penalización por cambiar de línea

# ---------------------------------------------------------------------------
# 4. Coordenadas esquemáticas (x, y) en unidades arbitrarias -> ver aviso
#    en el docstring del módulo.
# ---------------------------------------------------------------------------
COORDENADAS = {
    # Línea A (x = 0, y de sur a norte)
    "La Estrella": (0.0, -6.0), "Sabaneta": (0.0, -4.0), "Itagüí": (0.0, -1.5),
    "Envigado": (0.0, 0.5), "Ayurá": (0.0, 2.0), "Aguacatala": (0.0, 3.5),
    "Poblado": (0.0, 5.0), "Industriales": (0.0, 6.5), "Exposiciones": (0.0, 7.5),
    "Alpujarra": (0.0, 8.5), "San Antonio": (0.0, 9.5), "Parque Berrío": (0.0, 10.5),
    "Prado": (0.0, 11.5), "Hospital": (0.0, 12.5), "Universidad": (0.0, 13.5),
    "Caribe": (0.0, 15.0), "Tricentenario": (0.0, 17.0), "Acevedo": (0.0, 19.0),
    "Madera": (0.0, 21.0), "Bello": (0.0, 23.0), "Niquía": (0.0, 25.0),

    # Línea B (de occidente hacia San Antonio)
    "San Javier": (-7.0, 9.7), "Santa Lucía": (-5.7, 9.6), "Floresta": (-4.3, 9.6),
    "Estadio": (-3.0, 9.6), "Suramericana": (-1.7, 9.55), "Cisneros": (-0.8, 9.5),

    # Metrocable K (Acevedo -> nororiente, ladera)
    "Andalucía": (1.2, 19.8), "Popular": (2.3, 20.6), "Santo Domingo Savio": (3.2, 21.3),

    # Metrocable P (Acevedo -> noroccidente, ladera)
    "SENA": (-1.1, 19.6), "Doce de Octubre": (-2.2, 20.3), "El Progreso": (-3.2, 21.0),

    # Metrocable L (Santo Domingo Savio -> Parque Arví)
    "Arví": (5.0, 24.0),

    # Metrocable J (San Javier -> occidente, ladera)
    "Juan XXIII": (-8.2, 10.4), "Vallejuelos": (-9.3, 11.1), "La Aurora": (-10.3, 11.8),

    # Tranvía de Ayacucho (San Antonio -> oriente)
    "San José": (0.9, 9.4), "Pabellón del Agua EPM": (1.8, 9.3),
    "Bicentenario": (2.7, 9.25), "Buenos Aires": (3.6, 9.2),
    "Miraflores": (4.5, 9.15), "Loyola": (5.4, 9.1),
    "Alejandro Echavarría": (6.3, 9.05), "Oriente": (7.2, 9.0),

    # Metrocable M (Miraflores -> suroriente, ladera)
    "El Pinal": (5.3, 8.3), "Trece de Noviembre": (6.1, 7.5),

    # Metrocable H (Oriente -> oriente, ladera)
    "Las Torres": (8.1, 8.3), "Villa Sierra": (9.0, 7.6),
}


def obtener_todas_las_estaciones():
    """Devuelve el conjunto de nombres únicos de estaciones del sistema."""
    estaciones = set()
    for lista in LINEAS.values():
        estaciones.update(lista)
    return estaciones
