"""
gestor.py
---------
SistemaGestion: administra clientes, servicios y reservas en listas internas
(sin base de datos). Cada operación se ejecuta de forma segura: si algo falla,
el error se registra en el log y el sistema continúa funcionando.
"""

from cliente import Cliente
from excepciones import (
    ClienteInvalidoError,
    ParametroFaltanteError,
    ReservaInvalidaError,
    ServicioInvalidoError,
    SoftwareFJError,
)
from logger import obtener_logger
from reserva import Reserva
from servicio import Asesoria, AlquilerEquipo, ReservaSala

log = obtener_logger()


class SistemaGestion:
    """Núcleo de la aplicación: gestiona las tres listas internas."""

    # Tipos de servicio disponibles y la clase que los construye.
    TIPOS_SERVICIO = {"sala": ReservaSala, "equipo": AlquilerEquipo, "asesoria": Asesoria}

    def __init__(self):
        self.clientes = []
        self.servicios = []
        self.reservas = []
        # Contadores para el resumen final.
        self.exitos = 0
        self.fallos = 0

    # ------------------------------------------------------------------
    # Ejecución segura: mantiene la aplicación estable ante cualquier error
    # ------------------------------------------------------------------
    def _ejecutar(self, descripcion, funcion, *args, **kwargs):
        """Ejecuta una operación; captura y registra errores sin detener el programa."""
        try:
            resultado = funcion(*args, **kwargs)
        except SoftwareFJError as error:
            # Error controlado del dominio.
            self.fallos += 1
            log.warning("%s FALLÓ -> %s", descripcion, error)
            # Si hay una causa encadenada (raise ... from), también se registra.
            if error.__cause__ is not None:
                log.warning("   causa original: %r", error.__cause__)
            print(f"  [ERROR controlado] {descripcion}: {error}")
            return None
        except Exception as error:  # noqa: BLE001 - se captura todo a propósito
            # Error inesperado: se registra con traza completa y se continúa.
            self.fallos += 1
            log.error("%s FALLÓ de forma inesperada: %r", descripcion, error, exc_info=True)
            print(f"  [ERROR inesperado] {descripcion}: {error!r}")
            return None
        else:
            self.exitos += 1
            log.info("%s OK", descripcion)
            print(f"  [OK] {descripcion}")
            return resultado
        finally:
            log.debug("Operación finalizada: %s", descripcion)

    # ------------------------------------------------------------------
    # Búsquedas internas
    # ------------------------------------------------------------------
    def _buscar(self, lista, identificador, error_clase, etiqueta):
        for elemento in lista:
            if elemento.id == identificador:
                return elemento
        raise error_clase(f"{etiqueta} '{identificador}' no existe.")

    # ------------------------------------------------------------------
    # Clientes
    # ------------------------------------------------------------------
    def registrar_cliente(self, **datos):
        """Registra un cliente validando datos y documento duplicado."""
        def _registrar():
            # Se revisa el documento duplicado antes de crear el objeto,
            # para no consumir identificadores con clientes rechazados.
            documento = str(datos.get("documento", "")).strip()
            if any(c.documento == documento for c in self.clientes):
                raise ClienteInvalidoError(f"Ya existe un cliente con documento {documento}.")
            try:
                cliente = Cliente(**datos)
            except TypeError as error:
                # Faltan o sobran parámetros: se traduce a una excepción propia.
                raise ParametroFaltanteError(f"Datos de cliente incompletos: {error}") from error
            self.clientes.append(cliente)
            return cliente
        return self._ejecutar(f"Registrar cliente {datos.get('nombre')!r}", _registrar)

    # ------------------------------------------------------------------
    # Servicios
    # ------------------------------------------------------------------
    def crear_servicio(self, tipo, **datos):
        """Crea un servicio de tipo 'sala', 'equipo' o 'asesoria'."""
        def _crear():
            clase = self.TIPOS_SERVICIO.get(tipo)
            if clase is None:
                raise ServicioInvalidoError(
                    f"Tipo de servicio '{tipo}' no existe. Use: {', '.join(self.TIPOS_SERVICIO)}."
                )
            try:
                servicio = clase(**datos)
            except TypeError as error:
                raise ParametroFaltanteError(f"Datos de servicio incompletos: {error}") from error
            self.servicios.append(servicio)
            return servicio
        return self._ejecutar(f"Crear servicio {tipo!r} {datos.get('nombre')!r}", _crear)

    # ------------------------------------------------------------------
    # Reservas
    # ------------------------------------------------------------------
    def crear_reserva(self, id_cliente, id_servicio, horas, **parametros):
        """Crea una reserva PENDIENTE para un cliente y un servicio existentes."""
        def _crear():
            cliente = self._buscar(self.clientes, id_cliente, ClienteInvalidoError, "Cliente")
            servicio = self._buscar(self.servicios, id_servicio, ServicioInvalidoError, "Servicio")
            reserva = Reserva(cliente, servicio, horas, **parametros)
            self.reservas.append(reserva)
            return reserva
        return self._ejecutar(f"Crear reserva ({id_cliente} -> {id_servicio}, {horas} h)", _crear)

    def confirmar_reserva(self, id_reserva):
        def _confirmar():
            self._buscar(self.reservas, id_reserva, ReservaInvalidaError, "Reserva").confirmar()
            return True
        return self._ejecutar(f"Confirmar reserva {id_reserva}", _confirmar)

    def cancelar_reserva(self, id_reserva, motivo="Solicitud del cliente"):
        def _cancelar():
            self._buscar(self.reservas, id_reserva, ReservaInvalidaError, "Reserva").cancelar(motivo)
            return True
        return self._ejecutar(f"Cancelar reserva {id_reserva}", _cancelar)

    def procesar_reserva(self, id_reserva, impuesto=0.19, descuento=0.0, cupon=None):
        def _procesar():
            reserva = self._buscar(self.reservas, id_reserva, ReservaInvalidaError, "Reserva")
            return reserva.procesar(impuesto, descuento, cupon)
        return self._ejecutar(f"Procesar reserva {id_reserva}", _procesar)

    # ------------------------------------------------------------------
    # Reportes
    # ------------------------------------------------------------------
    def resumen(self):
        """Imprime el estado final de las tres listas y los contadores."""
        print("\n=== CLIENTES ===")
        for c in self.clientes:
            print(" ", c)
        print("\n=== SERVICIOS (polimorfismo: describir()) ===")
        for s in self.servicios:
            print(" ", s)
        print("\n=== RESERVAS ===")
        for r in self.reservas:
            print(" ", r)
        print(f"\nOperaciones exitosas: {self.exitos} | Operaciones con error controlado: {self.fallos}")
