"""
cliente.py
----------
Clase Cliente con encapsulación de datos personales y validaciones estrictas.
"""

import re

from entidad import Entidad
from excepciones import ClienteInvalidoError

# Solo letras (incluye tildes y ñ) y espacios.
_PATRON_NOMBRE = re.compile(r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ ]+$")
# Estructura básica de un correo electrónico.
_PATRON_EMAIL = re.compile(r"^[\w.+-]+@[\w-]+(\.[\w-]+)+$")


class Cliente(Entidad):
    """Cliente de Software FJ. Sus datos son privados y se validan al asignarse."""

    PREFIJO = "CLI"

    def __init__(self, nombre, documento, email, telefono):
        # Se validan los datos ANTES de consumir un identificador:
        # al asignar a las propiedades se ejecutan los setters con validación.
        self.__nombre = None
        self.__documento = None
        self.__email = None
        self.__telefono = None
        self.nombre = nombre
        self.documento = documento
        self.email = email
        self.telefono = telefono
        # Solo si todo es válido se genera el id de la entidad.
        super().__init__()

    # ---------- nombre ----------
    @property
    def nombre(self):
        return self.__nombre

    @nombre.setter
    def nombre(self, valor):
        if not isinstance(valor, str) or not valor.strip():
            raise ClienteInvalidoError("El nombre es obligatorio y debe ser texto.")
        valor = " ".join(valor.split())  # elimina espacios repetidos
        if len(valor) < 3 or not _PATRON_NOMBRE.match(valor):
            raise ClienteInvalidoError(
                f"Nombre inválido '{valor}': mínimo 3 letras, sin números ni símbolos."
            )
        self.__nombre = valor.title()

    # ---------- documento ----------
    @property
    def documento(self):
        return self.__documento

    @documento.setter
    def documento(self, valor):
        texto = str(valor).strip() if valor is not None else ""
        if not texto.isdigit() or not 6 <= len(texto) <= 12:
            raise ClienteInvalidoError(
                f"Documento inválido '{valor}': debe tener entre 6 y 12 dígitos."
            )
        self.__documento = texto

    # ---------- email ----------
    @property
    def email(self):
        return self.__email

    @email.setter
    def email(self, valor):
        if not isinstance(valor, str) or not _PATRON_EMAIL.match(valor.strip()):
            raise ClienteInvalidoError(f"Correo electrónico inválido: '{valor}'.")
        self.__email = valor.strip().lower()

    # ---------- teléfono ----------
    @property
    def telefono(self):
        return self.__telefono

    @telefono.setter
    def telefono(self, valor):
        texto = str(valor).strip() if valor is not None else ""
        # Celular colombiano: 10 dígitos que inician en 3.
        if not (texto.isdigit() and len(texto) == 10 and texto.startswith("3")):
            raise ClienteInvalidoError(
                f"Teléfono inválido '{valor}': debe tener 10 dígitos e iniciar en 3."
            )
        self.__telefono = texto

    def describir(self):
        return f"Cliente {self.id}: {self.nombre} (doc. {self.documento}, {self.email})"
