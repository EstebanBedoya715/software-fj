"""
servicio.py
-----------
Clase abstracta Servicio y tres servicios especializados:
  - ReservaSala      (reserva de salas)
  - AlquilerEquipo   (alquiler de equipos)
  - Asesoria         (asesorías especializadas)

Aquí se aplican: abstracción, herencia, polimorfismo (métodos sobrescritos)
y sobrecarga simulada de calcular_costo() mediante argumentos opcionales.
"""

import math
from abc import ABC, abstractmethod

from entidad import Entidad
from excepciones import (
    CalculoInconsistenteError,
    OperacionNoPermitidaError,
    ParametroFaltanteError,
    ServicioInvalidoError,
)

# Cupones de descuento válidos (código -> porcentaje).
CUPONES = {"FJ10": 0.10, "FJ20": 0.20}


def _es_numero(valor):
    """True si es int o float (excluye bool, que en Python es subclase de int)."""
    return isinstance(valor, (int, float)) and not isinstance(valor, bool)


class Servicio(Entidad, ABC):
    """Servicio abstracto que ofrece Software FJ."""

    PREFIJO = "SRV"
    IVA_DEFECTO = 0.19

    def __init__(self, nombre, tarifa_hora, disponible=True):
        # Validaciones comunes a todos los servicios.
        if not isinstance(nombre, str) or len(nombre.strip()) < 3:
            raise ServicioInvalidoError("El nombre del servicio debe tener al menos 3 caracteres.")
        if not _es_numero(tarifa_hora) or tarifa_hora <= 0:
            raise ServicioInvalidoError(f"Tarifa por hora inválida: {tarifa_hora!r}.")
        # Atributos privados (encapsulación).
        self.__nombre = nombre.strip()
        self.__tarifa_hora = float(tarifa_hora)
        self.__disponible = bool(disponible)
        super().__init__()

    # ---------- propiedades ----------
    @property
    def nombre(self):
        return self.__nombre

    @property
    def tarifa_hora(self):
        return self.__tarifa_hora

    @property
    def disponible(self):
        return self.__disponible

    @disponible.setter
    def disponible(self, valor):
        self.__disponible = bool(valor)

    # ---------- métodos abstractos (se sobrescriben en cada hijo) ----------
    @abstractmethod
    def validar_parametros(self, horas, **extra):
        """Valida duración y parámetros propios del servicio."""

    @abstractmethod
    def costo_base(self, horas, **extra):
        """Costo sin impuestos ni descuentos (cada servicio lo calcula distinto)."""

    @abstractmethod
    def describir(self):
        """Descripción textual del servicio."""

    # ---------- método sobrecargado ----------
    def calcular_costo(self, horas, *args, cupon=None, **extra):
        """
        Cálculo de costo con varias variantes (sobrecarga simulada):
            calcular_costo(h)                      -> costo base
            calcular_costo(h, impuesto)            -> base + impuesto
            calcular_costo(h, impuesto, descuento) -> base - descuento + impuesto
            calcular_costo(h, cupon="FJ10")        -> aplica cupón de descuento
        Los porcentajes se dan como decimales (0.19 = 19 %).
        """
        # Se valida la duración y los parámetros propios del servicio.
        self.validar_parametros(horas, **extra)

        # Se interpretan los argumentos posicionales según cuántos lleguen.
        if len(args) > 2:
            raise OperacionNoPermitidaError("calcular_costo admite como máximo impuesto y descuento.")
        impuesto = args[0] if len(args) >= 1 else 0.0
        descuento = args[1] if len(args) == 2 else 0.0

        for nombre, valor in (("impuesto", impuesto), ("descuento", descuento)):
            if not _es_numero(valor) or not 0 <= valor <= 1:
                raise CalculoInconsistenteError(f"El {nombre} debe estar entre 0 y 1 (recibido {valor!r}).")

        # Cupón opcional: se suma al descuento.
        if cupon is not None:
            if cupon not in CUPONES:
                raise ServicioInvalidoError(f"Cupón inválido: '{cupon}'.")
            descuento += CUPONES[cupon]

        # Regla de negocio: el descuento total no puede superar el 50 %.
        if descuento > 0.5:
            raise CalculoInconsistenteError(f"Descuento total excesivo: {descuento:.0%} (máximo 50 %).")

        base = self.costo_base(horas, **extra)
        total = round(base * (1 - descuento) * (1 + impuesto), 2)

        # Verificación final de consistencia del resultado.
        if not math.isfinite(total) or total <= 0:
            raise CalculoInconsistenteError(f"Costo calculado inconsistente: {total}.")
        return total

    def _validar_horas(self, horas, minimo, maximo):
        """Utilidad común: valida que la duración sea entera y esté en rango."""
        if horas is None:
            raise ParametroFaltanteError("Falta la duración (horas) del servicio.")
        if isinstance(horas, bool) or not isinstance(horas, int):
            raise ServicioInvalidoError(f"Las horas deben ser un entero (recibido {horas!r}).")
        if not minimo <= horas <= maximo:
            raise ServicioInvalidoError(
                f"{self.nombre}: la duración debe estar entre {minimo} y {maximo} horas (recibido {horas})."
            )


class ReservaSala(Servicio):
    """Reserva de salas de reuniones o capacitación."""

    def __init__(self, nombre, tarifa_hora, capacidad, disponible=True):
        if isinstance(capacidad, bool) or not isinstance(capacidad, int) or capacidad <= 0:
            raise ServicioInvalidoError(f"Capacidad de sala inválida: {capacidad!r}.")
        self.__capacidad = capacidad
        super().__init__(nombre, tarifa_hora, disponible)

    @property
    def capacidad(self):
        return self.__capacidad

    def validar_parametros(self, horas, **extra):
        # Una sala se reserva de 1 a 8 horas.
        self._validar_horas(horas, 1, 8)
        asistentes = extra.get("asistentes")
        if asistentes is not None and (not isinstance(asistentes, int) or not 1 <= asistentes <= self.capacidad):
            raise ServicioInvalidoError(
                f"{self.nombre}: asistentes ({asistentes}) exceden la capacidad ({self.capacidad})."
            )

    def costo_base(self, horas, **extra):
        total = self.tarifa_hora * horas
        # Recargo fijo por uso de proyector/sonido.
        if extra.get("proyector"):
            total += 20000
        return total

    def describir(self):
        estado = "disponible" if self.disponible else "NO disponible"
        return f"Sala {self.id}: {self.nombre}, capacidad {self.capacidad}, ${self.tarifa_hora:,.0f}/h ({estado})"


class AlquilerEquipo(Servicio):
    """Alquiler de equipos tecnológicos (portátiles, proyectores, etc.)."""

    def __init__(self, nombre, tarifa_hora, tipo_equipo, disponible=True):
        if not isinstance(tipo_equipo, str) or len(tipo_equipo.strip()) < 3:
            raise ServicioInvalidoError("El tipo de equipo es obligatorio (mínimo 3 caracteres).")
        self.__tipo_equipo = tipo_equipo.strip()
        super().__init__(nombre, tarifa_hora, disponible)

    @property
    def tipo_equipo(self):
        return self.__tipo_equipo

    def validar_parametros(self, horas, **extra):
        # Un equipo se alquila de 1 hasta 72 horas (3 días).
        self._validar_horas(horas, 1, 72)

    def costo_base(self, horas, **extra):
        total = self.tarifa_hora * horas
        # Seguro opcional equivalente al 5 % del alquiler.
        if extra.get("seguro"):
            total *= 1.05
        return total

    def describir(self):
        estado = "disponible" if self.disponible else "NO disponible"
        return f"Equipo {self.id}: {self.nombre} ({self.tipo_equipo}), ${self.tarifa_hora:,.0f}/h ({estado})"


class Asesoria(Servicio):
    """Asesoría especializada con un consultor junior o senior."""

    NIVELES = {"junior": 1.0, "senior": 1.25}

    def __init__(self, nombre, tarifa_hora, especialista, nivel="junior", disponible=True):
        if not isinstance(especialista, str) or len(especialista.strip()) < 3:
            raise ServicioInvalidoError("El nombre del especialista es obligatorio.")
        if nivel not in self.NIVELES:
            raise ServicioInvalidoError(f"Nivel inválido '{nivel}'. Use: {', '.join(self.NIVELES)}.")
        self.__especialista = especialista.strip()
        self.__nivel = nivel
        super().__init__(nombre, tarifa_hora, disponible)

    @property
    def especialista(self):
        return self.__especialista

    @property
    def nivel(self):
        return self.__nivel

    def validar_parametros(self, horas, **extra):
        # Una asesoría dura de 1 a 6 horas.
        self._validar_horas(horas, 1, 6)

    def costo_base(self, horas, **extra):
        # El nivel senior tiene un recargo del 25 %.
        return self.tarifa_hora * horas * self.NIVELES[self.nivel]

    def describir(self):
        estado = "disponible" if self.disponible else "NO disponible"
        return (f"Asesoría {self.id}: {self.nombre} con {self.especialista} ({self.nivel}), "
                f"${self.tarifa_hora:,.0f}/h ({estado})")
