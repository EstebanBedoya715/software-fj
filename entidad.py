"""
entidad.py
----------
Clase abstracta que representa cualquier entidad general del sistema
(clientes, servicios, reservas). Aporta un identificador único y obliga
a las clases hijas a implementar describir().
"""

from abc import ABC, abstractmethod


class Entidad(ABC):
    """Entidad abstracta: base de Cliente, Servicio y Reserva."""

    # Prefijo del identificador; cada clase hija lo redefine (CLI, SRV, RES).
    PREFIJO = "ENT"

    # Contadores por prefijo, compartidos por todas las entidades.
    _contadores = {}

    def __init__(self):
        # Se incrementa el contador del prefijo de la clase hija.
        numero = Entidad._contadores.get(self.PREFIJO, 0) + 1
        Entidad._contadores[self.PREFIJO] = numero
        # Atributo privado (encapsulación): solo se lee con la propiedad id.
        self.__id = f"{self.PREFIJO}-{numero:03d}"

    @property
    def id(self):
        """Identificador único de solo lectura."""
        return self.__id

    @abstractmethod
    def describir(self):
        """Devuelve una descripción en texto de la entidad."""

    def __str__(self):
        # Al imprimir cualquier entidad se muestra su descripción.
        return self.describir()
