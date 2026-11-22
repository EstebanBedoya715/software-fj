"""
reserva.py
----------
Clase Reserva: integra cliente, servicio, duración y estado.
Implementa confirmación, cancelación y procesamiento con manejo de
excepciones (try/except/else/finally y encadenamiento con "raise ... from").
"""

from enum import Enum

from cliente import Cliente
from entidad import Entidad
from excepciones import (
    CalculoInconsistenteError,
    OperacionNoPermitidaError,
    ReservaInvalidaError,
    ServicioInvalidoError,
    ServicioNoDisponibleError,
    SoftwareFJError,
)
from logger import obtener_logger
from servicio import Servicio

log = obtener_logger()


class EstadoReserva(Enum):
    """Estados posibles de una reserva."""
    PENDIENTE = "Pendiente"
    CONFIRMADA = "Confirmada"
    CANCELADA = "Cancelada"
    PROCESADA = "Procesada"


class Reserva(Entidad):
    """Reserva de un servicio por parte de un cliente."""

    PREFIJO = "RES"

    def __init__(self, cliente, servicio, horas, **parametros):
        # Se verifican los tipos de los objetos recibidos.
        if not isinstance(cliente, Cliente):
            raise ReservaInvalidaError("La reserva requiere un cliente válido.")
        if not isinstance(servicio, Servicio):
            raise ReservaInvalidaError("La reserva requiere un servicio válido.")
        # El servicio debe estar disponible.
        if not servicio.disponible:
            raise ServicioNoDisponibleError(f"El servicio '{servicio.nombre}' no está disponible.")

        # Se validan los parámetros; si fallan, se encadena la causa original.
        try:
            servicio.validar_parametros(horas, **parametros)
        except ServicioInvalidoError as error:
            raise ReservaInvalidaError(f"Parámetros de reserva inválidos: {error.mensaje}") from error

        self.__cliente = cliente
        self.__servicio = servicio
        self.__horas = horas
        self.__parametros = parametros
        self.__estado = EstadoReserva.PENDIENTE
        self.__costo_total = None
        super().__init__()

    # ---------- propiedades de solo lectura ----------
    @property
    def cliente(self):
        return self.__cliente

    @property
    def servicio(self):
        return self.__servicio

    @property
    def horas(self):
        return self.__horas

    @property
    def estado(self):
        return self.__estado

    @property
    def costo_total(self):
        return self.__costo_total

    # ---------- operaciones ----------
    def confirmar(self):
        """PENDIENTE -> CONFIRMADA."""
        if self.__estado is not EstadoReserva.PENDIENTE:
            raise OperacionNoPermitidaError(
                f"No se puede confirmar {self.id}: estado actual '{self.__estado.value}'."
            )
        self.__estado = EstadoReserva.CONFIRMADA
        log.info("Reserva %s confirmada.", self.id)

    def cancelar(self, motivo="Sin motivo"):
        """PENDIENTE o CONFIRMADA -> CANCELADA."""
        if self.__estado in (EstadoReserva.CANCELADA, EstadoReserva.PROCESADA):
            raise OperacionNoPermitidaError(
                f"No se puede cancelar {self.id}: estado actual '{self.__estado.value}'."
            )
        self.__estado = EstadoReserva.CANCELADA
        log.info("Reserva %s cancelada. Motivo: %s", self.id, motivo)

    def procesar(self, impuesto=Servicio.IVA_DEFECTO, descuento=0.0, cupon=None):
        """CONFIRMADA -> PROCESADA, calculando el costo final."""
        if self.__estado is not EstadoReserva.CONFIRMADA:
            raise OperacionNoPermitidaError(
                f"No se puede procesar {self.id}: debe estar confirmada (actual '{self.__estado.value}')."
            )
        try:
            # Intento de cálculo (puede lanzar errores de negocio o inesperados).
            costo = self.__servicio.calcular_costo(
                self.__horas, impuesto, descuento, cupon=cupon, **self.__parametros
            )
        except SoftwareFJError as error:
            # Error controlado: se encadena con la causa original.
            raise ReservaInvalidaError(f"No fue posible procesar {self.id}: {error.mensaje}") from error
        except Exception as error:
            # Error inesperado: se convierte en una excepción propia.
            raise CalculoInconsistenteError(f"Fallo inesperado al procesar {self.id}: {error}") from error
        else:
            # Solo si no hubo errores se actualiza el estado.
            self.__costo_total = costo
            self.__estado = EstadoReserva.PROCESADA
            log.info("Reserva %s procesada. Costo total: $%s", self.id, f"{costo:,.2f}")
            return costo
        finally:
            # Se ejecuta siempre: deja trazabilidad del intento.
            log.debug("Intento de procesamiento de %s finalizado (estado: %s).", self.id, self.__estado.value)

    def describir(self):
        costo = f"${self.__costo_total:,.2f}" if self.__costo_total is not None else "por calcular"
        return (f"Reserva {self.id}: {self.__cliente.nombre} -> {self.__servicio.nombre} "
                f"({self.__horas} h) | {self.__estado.value} | costo {costo}")
