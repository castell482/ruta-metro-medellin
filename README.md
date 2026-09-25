# Sistema inteligente de rutas — Metro de Medellín

Actividad de Inteligencia Artificial: sistema inteligente que, a partir de
una **base de conocimiento escrita en reglas lógicas**, calcula la mejor
ruta entre dos puntos (estaciones) del sistema de transporte masivo de
Medellín (Metro, Metrocable y Tranvía de Ayacucho), usando una **técnica de
búsqueda heurística (algoritmo A\*)**.

Autor: Carlos Mario Castellanos Rivillas
Curso: Inteligencia Artificial — Corporación Universitaria Iberoamericana

## 1. Descripción del proyecto

El sistema se divide en tres componentes, siguiendo el enfoque visto en el
curso (Benítez, 2014):

| Módulo | Contenido del curso que aplica | Qué hace |
|---|---|---|
| `src/base_conocimiento.py` | Cap. 2 — Lógica y representación del conocimiento | Declara los **hechos** del dominio: líneas, estaciones, tipo de línea y coordenadas esquemáticas. |
| `src/motor_reglas.py` | Cap. 3 — Sistemas basados en reglas | Motor de inferencia por **encadenamiento hacia adelante**: aplica reglas lógicas ("SI... ENTONCES...") sobre los hechos para deducir el grafo de conexiones y los puntos de transbordo. |
| `src/busqueda.py` | Cap. 9 — Técnicas basadas en búsquedas heurísticas | Implementa el algoritmo **A\*** para encontrar la ruta de menor tiempo total entre dos estaciones, usando una heurística admisible basada en distancia en línea recta. |
| `src/main.py` | — | Punto de entrada: arma los tres módulos anteriores y expone una interfaz de línea de comandos. |

### Reglas lógicas implementadas

1. **Regla de conexión directa**: si dos estaciones son consecutivas dentro
   de la lista ordenada de una misma línea, se infiere que existe una
   conexión directa entre ambas (en los dos sentidos), con un tiempo de
   viaje asociado al tipo de línea (metro, metrocable o tranvía).
2. **Regla de transbordo**: si una estación pertenece a dos o más líneas
   distintas, se infiere que es un **punto de transbordo**. Esto no está
   codificado a mano: se deduce automáticamente comparando los hechos
   `pertenece(estación, línea)`.

El algoritmo de búsqueda usa estas reglas para construir el grafo, y
además aplica una **penalización de tiempo por transbordo** cada vez que
la ruta cambia de línea, de forma que la "mejor ruta" sea siempre la de
menor tiempo total estimado (no solo la de menos estaciones).

### Alcance de la base de conocimiento

Incluye las líneas A y B del Metro, los Metrocables J, K, L, M, P y H, y el
Tranvía de Ayacucho (TA), con sus estaciones oficiales y sus puntos de
transbordo reales. Las **coordenadas usadas para la heurística son
esquemáticas** (no son coordenadas GPS reales): se construyeron para
respetar la disposición geográfica relativa de las líneas y permitir
calcular una heurística de distancia en línea recta válida para A*. Esto
se explica también en el docstring de `base_conocimiento.py`.

## 2. Instrucciones de instalación y ejecución

Requiere Python 3.9 o superior.

```bash
# 1. Clonar el repositorio
git clone https://github.com/castell482/ruta-metro-medellin.git
cd ruta-metro-medellin

# 2. (Opcional pero recomendado) crear un entorno virtual
python3 -m venv venv
source venv/bin/activate        # En Windows: venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt
```

### Ejecutar el sistema de forma interactiva

```bash
python src/main.py
```

El programa pedirá una estación de origen y una de destino, y mostrará la
ruta óptima, tramo por tramo, indicando la línea usada y avisando cada
transbordo.

### Ejecutar el sistema pasando origen y destino como argumentos

```bash
python src/main.py "San Javier" "Santo Domingo Savio"
```

### Ejecutar las pruebas automatizadas

```bash
pytest tests/ -v
```

### Generar el documento PDF con las pruebas realizadas

```bash
python tests/generar_pdf_pruebas.py
```

Esto genera `docs/Pruebas_realizadas.pdf`, con 7 casos de prueba
documentados (rutas dentro de una misma línea, rutas con varios
transbordos, casos borde y manejo de errores).

## 3. Estructura del repositorio

```
ruta-metro-medellin/
├── README.md
├── requirements.txt
├── src/
│   ├── base_conocimiento.py   # Hechos: líneas, estaciones, tiempos, coordenadas
│   ├── motor_reglas.py        # Motor de inferencia (reglas lógicas)
│   ├── busqueda.py            # Algoritmo A* (búsqueda heurística)
│   └── main.py                # Interfaz de línea de comandos
├── tests/
│   ├── test_motor_reglas.py
│   ├── test_busqueda.py
│   └── generar_pdf_pruebas.py # Genera docs/Pruebas_realizadas.pdf
└── docs/
    └── Pruebas_realizadas.pdf
```

## 4. Referencias

- Benítez, R. (2014). *Inteligencia artificial avanzada*. Editorial UOC.
  (Cap. 2: Lógica y representación del conocimiento; Cap. 3: Sistemas
  basados en reglas; Cap. 9: Técnicas basadas en búsquedas heurísticas).
- Metro de Medellín. Información oficial de líneas y estaciones del
  sistema Metro, Metrocable y Tranvía de Ayacucho.
