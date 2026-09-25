# -*- coding: utf-8 -*-
"""Permite que pytest encuentre los módulos de src/ sin instalar el
paquete (se agrega src/ al sys.path antes de correr las pruebas)."""
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(RAIZ, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)
