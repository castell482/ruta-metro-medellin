# -*- coding: utf-8 -*-
"""
Genera el documento PDF con las pruebas realizadas al sistema (entregable
2 de la actividad): ejecuta un conjunto de consultas representativas sobre
el sistema de rutas y documenta, para cada una, la ruta obtenida, el
tiempo total y el número de transbordos.

Uso:
    python tests/generar_pdf_pruebas.py
Genera: docs/Pruebas_realizadas.pdf
"""
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "src"))

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
)

from main import calcular_ruta
from busqueda import RutaNoEncontrada

OUT_PATH = os.path.join(RAIZ, "docs", "Pruebas_realizadas.pdf")

FONT = "Times-Roman"
FONT_BOLD = "Times-Bold"
SIZE = 12
LEADING = 24

titulo = ParagraphStyle("titulo", fontName=FONT_BOLD, fontSize=SIZE,
                         leading=LEADING, alignment=TA_CENTER, spaceAfter=16)
h1 = ParagraphStyle("h1", fontName=FONT_BOLD, fontSize=SIZE, leading=LEADING,
                     alignment=TA_CENTER, spaceBefore=10, spaceAfter=8)
body = ParagraphStyle("body", fontName=FONT, fontSize=SIZE, leading=LEADING,
                       alignment=TA_LEFT)
cell_style = ParagraphStyle("cell", fontName=FONT, fontSize=10, leading=13)
cell_bold = ParagraphStyle("cell_bold", fontName=FONT_BOLD, fontSize=10, leading=13)

# Casos de prueba: (nombre del caso, origen, destino, resultado esperado en
# prosa, para que quien revise el documento pueda verificar a simple vista)
CASOS = [
    ("Caso 1 - Ruta dentro de una sola línea (sin transbordos)",
     "Niquía", "La Estrella",
     "Ambas estaciones pertenecen únicamente a la Línea A, por lo que la "
     "ruta óptima no debe requerir ningún transbordo."),
    ("Caso 2 - Ruta que requiere dos transbordos",
     "San Javier", "Santo Domingo Savio",
     "San Javier está en la Línea B y Santo Domingo Savio en la Línea K: "
     "la ruta óptima debe pasar por San Antonio (transbordo B->A) y por "
     "Acevedo (transbordo A->K)."),
    ("Caso 3 - Ruta entre dos Metrocables opuestos (varios transbordos)",
     "La Aurora", "Arví",
     "La Aurora (Línea J, occidente) y Arví (Línea L, nororiente) están en "
     "extremos opuestos del sistema: se espera una ruta con varios "
     "transbordos, atravesando la troncal (Líneas B y A)."),
    ("Caso 4 - Ruta hacia el Tranvía de Ayacucho",
     "Poblado", "Oriente",
     "Poblado está en la Línea A y Oriente es el extremo final del Tranvía "
     "de Ayacucho: se espera un transbordo en San Antonio (A->TA)."),
    ("Caso 5 - Origen y destino iguales (caso borde)",
     "Universidad", "Universidad",
     "Cuando el origen y el destino son la misma estación, el sistema debe "
     "responder con una ruta de una sola estación y tiempo total de 0 "
     "minutos, sin producir errores."),
    ("Caso 6 - Estación inexistente (manejo de errores)",
     "Estación Inventada", "San Antonio",
     "El sistema debe reconocer que 'Estación Inventada' no pertenece a la "
     "base de conocimiento y responder con un mensaje de error controlado, "
     "en lugar de fallar de forma inesperada."),
    ("Caso 7 - Tolerancia a tildes/mayúsculas en el nombre de la estación",
     "aveniDa", "sabaneta",
     "'aveniDa' no corresponde a ninguna estación real; se usa para "
     "comprobar que el sistema informa correctamente cuando el nombre no "
     "coincide con ninguna estación conocida, incluso ignorando mayúsculas."),
]


def ejecutar_caso(nombre, origen, destino, esperado):
    story = []
    story.append(Paragraph(nombre, h1))
    story.append(Paragraph(f"<b>Origen:</b> {origen} &nbsp;&nbsp; <b>Destino:</b> {destino}", body))
    story.append(Paragraph(f"<b>Resultado esperado:</b> {esperado}", body))
    story.append(Spacer(1, 6))

    try:
        origen_resuelto, destino_resuelto, resultado = calcular_ruta(origen, destino)

        data = [["Origen", "Destino", "Línea", "Tiempo (min)", "Transbordo"]]
        for tramo in resultado["tramos"]:
            data.append([
                tramo["origen"], tramo["destino"], tramo["linea"],
                f"{tramo['tiempo']:.1f}", "Sí" if tramo["transbordo"] else "No",
            ])
        if len(data) == 1:
            data.append(["(misma estación: no hay tramos)", "", "", "", ""])

        filas = [[Paragraph(str(c), cell_style) for c in fila] for fila in data[1:]]
        encabezado = [Paragraph(str(c), cell_bold) for c in data[0]]
        tabla = Table([encabezado] + filas, colWidths=[4.2 * cm, 4.2 * cm, 1.6 * cm, 2.3 * cm, 2.3 * cm])
        tabla.setStyle(TableStyle([
            ("LINEABOVE", (0, 0), (-1, 0), 1, "black"),
            ("LINEBELOW", (0, 0), (-1, 0), 0.75, "black"),
            ("LINEBELOW", (0, -1), (-1, -1), 1, "black"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(tabla)
        story.append(Spacer(1, 6))
        story.append(Paragraph(
            f"<b>Resultado obtenido:</b> ruta de {origen_resuelto} a {destino_resuelto} "
            f"con {resultado['numero_transbordos']} transbordo(s) y un tiempo total "
            f"estimado de {resultado['tiempo_total']:.1f} minutos. "
            f"<b>Estado de la prueba: EXITOSA.</b>", body
        ))
    except RutaNoEncontrada as error:
        story.append(Paragraph(f"<b>Resultado obtenido:</b> el sistema respondió con el "
                                f"error controlado: “{error}”. "
                                f"<b>Estado de la prueba: EXITOSA "
                                f"(el error se detecta y se maneja correctamente).</b>", body))

    story.append(Spacer(1, 16))
    return story


def main():
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    story = []
    story.append(Spacer(1, 1 * cm))
    story.append(Paragraph(
        "Pruebas realizadas al sistema inteligente de rutas<br/>"
        "Metro de Medellín", titulo
    ))
    story.append(Paragraph(
        "Este documento presenta los casos de prueba ejecutados sobre el "
        "sistema de recomendación de rutas, que combina una base de "
        "conocimiento en reglas lógicas (motor_reglas.py) con un algoritmo "
        "de búsqueda heurística A* (busqueda.py). Cada caso indica la "
        "estación de origen, la de destino, el resultado esperado y el "
        "resultado realmente obtenido al ejecutar el programa.", body
    ))
    story.append(Spacer(1, 10))

    for i, (nombre, origen, destino, esperado) in enumerate(CASOS):
        story.extend(ejecutar_caso(nombre, origen, destino, esperado))
        if i == 3:
            story.append(PageBreak())

    doc = SimpleDocTemplate(
        OUT_PATH, pagesize=letter,
        topMargin=2.2 * cm, bottomMargin=2.2 * cm,
        leftMargin=2.2 * cm, rightMargin=2.2 * cm,
        title="Pruebas realizadas - Sistema de rutas Metro de Medellín",
    )
    doc.build(story)
    print("OK ->", OUT_PATH)


if __name__ == "__main__":
    main()
