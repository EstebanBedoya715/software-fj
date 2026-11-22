"""
logger.py
---------
Configuración del archivo de logs. Todos los eventos y errores del sistema
se registran en logs/software_fj.log (único uso de archivos permitido).
"""

import logging
from pathlib import Path

# Carpeta y archivo de logs, junto a este módulo.
CARPETA_LOGS = Path(__file__).resolve().parent / "logs"
ARCHIVO_LOG = CARPETA_LOGS / "software_fj.log"


def obtener_logger(nombre="software_fj"):
    """Devuelve el logger de la aplicación, creándolo una sola vez."""
    logger = logging.getLogger(nombre)

    # Si ya tiene manejadores, ya fue configurado: se reutiliza.
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    # Se crea la carpeta de logs si no existe.
    CARPETA_LOGS.mkdir(exist_ok=True)

    # Manejador que escribe en el archivo (modo "a": agrega al final).
    manejador = logging.FileHandler(ARCHIVO_LOG, mode="a", encoding="utf-8")
    formato = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(message)s", "%Y-%m-%d %H:%M:%S"
    )
    manejador.setFormatter(formato)
    logger.addHandler(manejador)
    return logger
